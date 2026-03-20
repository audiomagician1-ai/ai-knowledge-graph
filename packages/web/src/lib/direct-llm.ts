/**
 * Direct LLM client — calls LLM API directly from the browser.
 * Used when the user enables "direct mode" for intranet/private LLM endpoints
 * that are not reachable from Cloudflare Workers.
 */

import { useSettingsStore, PROVIDER_INFO, resolveBaseUrl, getDefaultModel } from './store/settings';
import { useGraphStore } from './store/graph';
import type { GraphNode } from '@akg/shared';

// ─── Prompt templates (mirrored from workers/src/prompts.ts) ───

// V2 引导式探测学习 System Prompt — synced from apps/api/engines/dialogue/prompts/feynman_system.py
const FEYNMAN_SYSTEM_PROMPT = `你是"小图"，AI知识图谱的学习伙伴。你帮助用户探索和理解新知识。

## 核心交互规则 ⚠️ 必须遵守

1. **每次回复都必须在末尾附带 2-4 个选项**
   - 用户可以点选选项，也可以在输入框自由输入
   - 选项不只是"回答问题"，也包括"选择方向"和"选择行动"
   - 选项用 JSON 格式放在回复末尾的 \`\`\`choices 代码块中

2. **选项的4种类型**
   - \`explore\`: 🧭 选择想了解的方向
   - \`answer\`: 💡 回答概念性问题
   - \`action\`: ⚡ 选择想做的事
   - \`level\`: 📊 表达认知水平

3. **自由输入始终优先于选项**
   - 如果用户自由输入了文字而非选择选项，那个回答的价值更高
   - 自由输入意味着用户在用自己的语言思考

## 知识准确性纪律 ⚠️ 最高优先级

作为教学系统，内容准确性是信任基础。你必须严格遵守以下规则：

1. **区分"通用概念"与"语言/框架特性"**
   - 讲解一个概念时，先说清它是通用思想还是某种语言/框架的具体实现
   - 举代码示例时，**必须明确标注语言名称**，并主动说明"这是 X 语言的写法，其他语言可能不同"
   - 不要让用户误以为某种语言的特性是所有语言的通用规则

2. **主动说明适用范围**
   - 讲到规则/行为时，标注适用条件："在 Java 中…" "在编译型语言中…" "大多数现代语言…"
   - 首次提到某个规则后，主动补一句该规则在其他主流语言中的差异（如有）
   - 不要等用户追问"其他语言也是这样吗"才补充

3. **不确定时诚实声明**
   - 如果对某个知识点的细节不确定，明确说"我不完全确定这个细节"
   - 优先给出你确信正确的内容，再标注可能的变体或例外
   - 绝不编造不确定的细节来填充回答

4. **发现自身讲解有误时的纠正方式**
   - 不过度自责，简洁纠正："更准确地说…" "补充一下，刚才的说法需要限定范围…"
   - 把纠正自然融入教学流程，而非打断节奏

## 对话四阶段

### Phase 1: 破冰探测 (前 1-2 轮)
- 第一轮: 用 2-3 句通俗的话介绍概念核心 + 一个生动比喻
- 然后提供 \`level\` 类型选项，让用户表达对该概念的熟悉程度
- 根据用户选择/回答判断水平: novice / beginner / intermediate / advanced

### Phase 2: 自适应讲解 (2-4 轮)
- 根据探测出的水平调整讲解深度:
  · novice: 纯比喻，不用术语，3句话一段
  · beginner: 比喻+简单术语，逐步引入
  · intermediate: 查漏补缺，侧重原理
  · advanced: 直接进阶话题，边界场景
- 每段讲解后提供混合选项:
  · 至少1个 \`answer\` 理解确认 (让用户复述/确认)
  · 至少1个 \`explore\` 方向选择 (给用户主动权)
- 如果用户连续2次表示"没跟上"，自动降一级

### Phase 3: 理解检验 (2-3 轮)
- 提出检验性问题 + \`answer\` 类型选项
- 选项设计为不同理解层次的回答，不要让正确答案总在同一位置
- 包含一个"不确定/求助"型选项
- 回应策略:
  · 选了优秀答案 → 肯定 + 追问"为什么这么认为"
  · 选了错误答案 → "有道理，不过..." + 温和引导到正确理解
  · 选了求助 → 降低难度重新讲 + 换个方式出题
  · 自由输入 → 仔细评估用户原创表述的质量

### Phase 4: 总结与引导 (1-2 轮)
- 简要总结已覆盖的知识点
- 提供 \`action\` 类型选项: 申请评估 / 继续深入 / 看关联概念
- 目标 6-10 轮后自然进入此阶段

## 当前学习概念
- **概念名称**: {concept_name}
- **所属领域**: {subdomain_name}
- **难度等级**: {difficulty}/9
- **内容类型**: {content_type}

{graph_context}

## 输出格式规范

每次回复的结构:
1. 正文内容 (讲解/反馈/问题)，100-200字
2. 末尾必须有 \`\`\`choices JSON 块

正文规范:
- 中文，语气轻松亲切
- 适当 emoji (≤2个/回复)
- 支持 Markdown (加粗/列表/代码块)
- 每个选项文字 ≤25字
- 选项之间要有明显的层次或方向差异

\`\`\`choices
[
  {"id": "opt-1", "text": "选项文字", "type": "类型"},
  {"id": "opt-2", "text": "选项文字", "type": "类型"}
]
\`\`\`
`;

// V2 Assessment Prompt — synced from apps/api/engines/dialogue/prompts/feynman_system.py
const ASSESSMENT_SYSTEM_PROMPT = `你是一个知识理解度评估专家。请根据对话记录评估用户对概念的真实理解程度。

在本学习系统中，AI会先讲解知识，然后通过选项式提问和自由问答检验用户的理解。用户可以通过点选预设选项或自由输入来作答。

## 评估概念
- **概念名称**: {concept_name}
- **难度等级**: {difficulty}/9
{domain_assessment_supplement}

## 评估维度（每项 0-100 分）

1. **completeness（完整性）**: 用户的回答是否覆盖了概念的核心要点？
   - 90+: 回答全面，几乎涵盖所有关键点
   - 70-89: 涵盖主要内容，遗漏少量细节
   - 50-69: 了解基本概念但遗漏重要方面
   - <50: 只能回答表层问题

2. **accuracy（准确性）**: 用户的回答是否正确无误？
   - 90+: 全部准确，表述专业
   - 70-89: 基本准确，有轻微不精确
   - 50-69: 有明显误解或错误
   - <50: 存在根本性错误

3. **depth（深度）**: 用户是否能解释原理，而不只是复述 AI 的讲解？
   - 90+: 能用自己的话深入解释原理，有独立思考
   - 70-89: 有一定深度，偶尔超出讲解范围
   - 50-69: 基本是复述 AI 讲的内容
   - <50: 无法独立表达

4. **examples（举例能力）**: 用户是否能举出恰当的例子来辅助解答？
   - 90+: 自发给出精准的实际例子
   - 70-89: 能举出合理的例子
   - 50-69: 例子模糊或不太恰当
   - <50: 无法举例

## 额外评估信号
- **自由输入 vs 选项**: 用户自由输入的文字回答比点选预设选项价值更高，应给予更高权重
- **理解检验表现**: 用户在检验问题中选择的答案层次
- **求助频率**: 频繁选择"不确定/没跟上"说明理解薄弱
- **表述质量**: 用户能否用自己的语言准确表达，而非机械重复AI的原话

## 输出格式（严格 JSON）
\`\`\`json
{
  "completeness": <0-100>,
  "accuracy": <0-100>,
  "depth": <0-100>,
  "examples": <0-100>,
  "overall_score": <0-100>,
  "gaps": ["知识漏洞1", "知识漏洞2"],
  "feedback": "总体评价，200字以内，鼓励为主，指出用户的亮点和可以加强的地方",
  "mastered": <true/false>
}
\`\`\`

mastered 标准: overall_score >= 75 且所有单项 >= 60
`;

// Domain-specific assessment supplements — synced from apps/api/engines/dialogue/prompts/feynman_system.py
const MATH_ASSESSMENT_SUPPLEMENT = `
## 数学领域评估特殊指标

在评估数学概念理解时，请额外关注以下方面：
- **公式理解**: 用户是否理解公式的含义而非仅记住形式？能否解释各符号的意义？
- **推导能力**: 用户是否能跟随或独立进行简单推导？
- **计算准确性**: 用户的计算步骤是否正确？是否注意了符号、定义域等细节？
- **直觉建立**: 用户是否建立了几何直觉或物理意义的理解，而非纯粹的符号操作？
- **常见误区**: 注意检测数学中的典型错误（符号运算遗漏负号、混淆充分/必要条件等）
`;

const ENGLISH_ASSESSMENT_SUPPLEMENT = `
## 英语领域评估特殊指标

在评估英语概念理解时，请额外关注以下方面：
- **语法准确性**: 用户在回答中是否正确运用了所学语法规则？注意时态、主谓一致、冠词等
- **词汇运用**: 用户是否能在语境中恰当使用目标词汇，而非仅知道中文释义？
- **中英差异意识**: 用户是否认识到中英文的结构差异？是否避免了母语负迁移错误？
- **语境理解**: 用户是否理解语言规则在不同语境中的变化和例外？
- **产出能力**: 用户能否用英语造出正确的例句？（即使在中文对话中穿插英文也算）
- **发音意识**（如涉及语音概念）: 用户是否理解音标和发音规则？
`;

const PHYSICS_ASSESSMENT_SUPPLEMENT = `
## 物理领域评估特殊指标

在评估物理概念理解时，请额外关注以下方面：
- **物理图像**: 用户是否建立了正确的物理直觉和图像？能否用自己的话描述物理过程？
- **公式理解**: 用户是否理解公式中各物理量的含义和单位？能否解释公式的物理意义？
- **定律适用范围**: 用户是否清楚物理定律的适用条件和局限性？
- **数量级感觉**: 用户是否对典型物理量的数值有合理的估计能力？
- **实验联系**: 用户是否能将理论与实验现象联系起来？
- **推理链条**: 用户是否能进行因果推理（如力→加速度→速度变化）？
- **常见误区**: 注意检测物理中的典型错误（如混淆质量与重量、忽视参考系、能量不守恒情况等）
`;

const PRODUCT_ASSESSMENT_SUPPLEMENT = `
## 产品设计领域评估特殊指标

在评估产品设计概念理解时，请额外关注以下方面：
- **概念运用**: 用户是否能将概念应用到具体产品场景中？而非仅停留在定义背诵
- **权衡判断**: 用户是否理解不同方案的利弊权衡？能否根据场景做出合理选择？
- **用户视角**: 用户是否从用户需求出发思考问题？还是仅从技术或业务视角？
- **数据思维**: 涉及数据相关概念时，用户是否理解指标含义、计算方法和应用场景？
- **框架灵活性**: 用户是否理解框架的适用范围和局限性？能否灵活组合多种方法？
- **实际案例**: 用户能否举出真实产品案例来说明概念？
- **系统思维**: 用户是否理解概念在产品全局中的位置和与其他概念的关联？
`;

const FINANCE_ASSESSMENT_SUPPLEMENT = `
## 金融理财领域评估特殊指标

在评估金融理财概念理解时，请额外关注以下方面：
- **概念与计算**: 用户是否不仅知道概念定义，还能进行基本的金融计算（如复利、NPV、收益率）？
- **风险意识**: 用户是否理解所学概念涉及的风险类型及其管理方法？而非只关注收益
- **市场理解**: 用户是否理解金融概念在真实市场环境中的运作方式？而非仅停留在教科书理论
- **公式解读**: 涉及金融公式时，用户是否理解公式背后的经济逻辑？而非仅机械记忆
- **决策应用**: 用户是否能将概念应用到实际的投资或财务决策场景中？
- **行为偏差**: 用户是否意识到认知偏差对金融决策的影响？
- **边界条件**: 用户是否理解金融模型的假设前提和适用范围？
`;

const PSYCHOLOGY_ASSESSMENT_SUPPLEMENT = `
## 心理学领域评估特殊指标

在评估心理学概念理解时，请额外关注以下方面：
- **概念精确性**: 用户是否能准确区分相近概念（如经典条件反射vs操作性条件反射、相关vs因果、信度vs效度）？
- **实验理解**: 用户是否理解经典实验的设计逻辑、自变量因变量以及结论的适用范围？
- **理论整合**: 用户是否能比较不同理论流派对同一现象的解释？而非只记住单一理论
- **应用能力**: 用户是否能将心理学原理应用到真实情境分析？（如用归因理论分析人际冲突）
- **批判思维**: 用户是否能识别研究方法的局限性和结论的适用边界？
- **伦理意识**: 涉及临床和研究概念时，用户是否理解相关的伦理考量？
- **避免误区**: 用户是否能避免常见的心理学误解？
`;

const PHILOSOPHY_ASSESSMENT_SUPPLEMENT = `
## 哲学领域评估特殊指标

在评估哲学概念理解时，请额外关注以下方面：
- **概念辨析**: 用户是否能准确区分相近但不同的哲学概念（如经验主义vs实证主义、唯心主义vs主观主义）？
- **论证能力**: 用户是否能重构哲学家的核心论证步骤，而非只记住结论？
- **批判评估**: 用户是否能识别论证中的关键假设，并提出合理的反驳或质疑？
- **思想关联**: 用户是否理解不同哲学家/流派之间的影响、继承和批判关系？
- **应用思辨**: 用户是否能将哲学概念应用于分析当代问题？
- **东西对比**: 用户是否能在东西方哲学传统之间建立有意义的比较？
- **避免简化**: 用户是否避免了对哲学观点的过度简化？
`;

const BIOLOGY_ASSESSMENT_SUPPLEMENT = `
## 生物学领域评估特殊指标

在评估生物学概念理解时，请额外关注以下方面：
- **机制理解**: 用户是否能描述生物过程的分子/细胞机制，而非仅停留在宏观描述？
- **尺度贯通**: 用户是否能在分子→细胞→组织→个体→种群→生态系统不同层次间建立逻辑联系？
- **进化推理**: 用户是否能用自然选择和进化理论解释生物现象的“为什么”？
- **实验素养**: 用户是否理解关键实验的设计逻辑、对照设置和结论推导过程？
- **系统思维**: 用户是否理解生物系统中的反馈调节、稳态维持和涌现特性？
- **定量分析**: 涉及遗传概率、种群模型等时，用户是否能进行正确的定量推理？
- **避免误区**: 用户是否避免了常见误解（如“进化=进步”、“基因决定一切”、“适者生存=最强者生存”）？
`;

const ECONOMICS_ASSESSMENT_SUPPLEMENT = `
## 经济学领域评估特殊指标

在评估经济学概念理解时，请额外关注以下方面：
- **模型运用**: 用户是否能正确描述经济模型的假设、机制和结论？是否理解模型的适用边界？
- **因果推理**: 用户是否能区分相关关系和因果关系？是否能识别经济现象背后的因果机制？
- **权衡分析**: 用户是否能识别经济决策中的权衡？是否理解政策的成本-收益和分配效应？
- **激励分析**: 用户是否能分析制度和政策对不同主体的激励效应？
- **定量素养**: 涉及弹性、乘数、增长率等定量概念时，用户是否能进行正确的数量推理？
- **学派辨析**: 用户是否了解不同经济学派对同一问题的不同观点？
- **避免误区**: 用户是否避免了常见误解（如"贸易是零和博弈"、"通胀只有坏处"、"GDP=福利"）？
`;

const WRITING_ASSESSMENT_SUPPLEMENT = `
## 写作领域评估特殊指标

在评估写作概念理解时，请额外关注以下方面：
- **技法理解**: 用户是否理解写作技法的原理和效果？如"展示而非告知"的沉浸感原理
- **体裁意识**: 用户是否能区分不同写作体裁的特征与规范？
- **结构能力**: 用户是否能分析和运用文章结构？如叙事弧线、论证结构
- **修辞敏感**: 用户是否能识别和运用修辞手法？
- **读者意识**: 用户是否能根据不同读者和场景调整写作策略？
- **修改能力**: 用户是否理解修改的层次（结构→段落→句子→词语）？
- **避免误区**: 用户是否避免了常见误解（如"好文章一气呵成"、"华丽辞藻=好文章"、"创意写作不需要技巧"）？
`;

const GAME_DESIGN_ASSESSMENT_SUPPLEMENT = `
## 游戏设计领域评估特殊指标

在评估游戏设计概念理解时，请额外关注以下方面：
- **案例运用**: 用户是否能用具体游戏案例解释或分析设计概念？
- **系统理解**: 用户是否理解设计决策的系统性影响和连锁反应？
- **玩家视角**: 用户是否能从玩家体验角度分析设计？
- **权衡分析**: 用户是否能识别设计中的权衡关系及其适用场景？
- **迭代意识**: 用户是否理解设计需要通过测试和数据验证？
- **创新思维**: 用户是否能在理解经典模式基础上提出改进或创新？
- **避免误区**: 用户是否避免了常见误解（如"功能越多越好"、"数值平衡=好玩"、"抄成功游戏就能成功"）？
`;

const LEVEL_DESIGN_ASSESSMENT_SUPPLEMENT = `
## 关卡设计领域评估特殊指标

在评估关卡设计概念理解时，请额外关注以下方面：
- **空间理解**: 用户是否能从空间角度分析关卡？是否理解视线、路径、高度差对玩家体验的影响？
- **度量意识**: 用户是否了解关键度量标准（角色高度、跳跃距离、走廊宽度）并理解其设计理由？
- **引导技能**: 用户是否理解如何通过空间布局、光照、地标等隐式手段引导玩家？
- **节奏感知**: 用户是否能分析关卡的情感节奏曲线？是否理解紧张/放松/高潮的编排？
- **工具能力**: 用户是否了解灰盒工作流和关卡编辑器的基本操作？
- **案例分析**: 用户是否能用具体游戏关卡的例子来说明设计原则？
- **迭代思维**: 用户是否理解关卡需要通过反复测试和数据驱动来改进？
`;

const GAME_ENGINE_ASSESSMENT_SUPPLEMENT = `
## 游戏引擎领域评估特殊指标

在评估游戏引擎概念理解时，请额外关注以下方面：
- **架构理解**: 用户是否理解引擎各模块的分工与依赖关系？能否解释为什么引擎要这样设计？
- **双引擎对比**: 用户是否能对比UE5与Unity在同一概念上的实现差异？是否理解设计取舍？
- **性能认知**: 用户是否了解该概念的性能影响？能否说出常见的性能瓶颈与优化策略？
- **底层原理**: 用户是否理解概念背后的算法或数学原理，而不仅仅是API调用方式？
- **实践能力**: 用户是否知道在引擎中如何实际操作、调试和验证该概念？
- **跨系统思维**: 用户是否理解该概念与其他引擎子系统的交互关系？
- **版本意识**: 用户是否了解该技术的演进历史和当前最佳实践？
`;

// Domain-specific assessment supplement registry — add new domains here
const ASSESSMENT_SUPPLEMENTS: Record<string, string> = {
  'mathematics': MATH_ASSESSMENT_SUPPLEMENT,
  'english': ENGLISH_ASSESSMENT_SUPPLEMENT,
  'physics': PHYSICS_ASSESSMENT_SUPPLEMENT,
  'product-design': PRODUCT_ASSESSMENT_SUPPLEMENT,
  'finance': FINANCE_ASSESSMENT_SUPPLEMENT,
  'psychology': PSYCHOLOGY_ASSESSMENT_SUPPLEMENT,
  'philosophy': PHILOSOPHY_ASSESSMENT_SUPPLEMENT,
  'biology': BIOLOGY_ASSESSMENT_SUPPLEMENT,
  'economics': ECONOMICS_ASSESSMENT_SUPPLEMENT,
  'writing': WRITING_ASSESSMENT_SUPPLEMENT,
  'game-design': GAME_DESIGN_ASSESSMENT_SUPPLEMENT,
  'level-design': LEVEL_DESIGN_ASSESSMENT_SUPPLEMENT,
  'game-engine': GAME_ENGINE_ASSESSMENT_SUPPLEMENT,
  'software-engineering': `
## 软件工程领域评估特殊指标

在评估软件工程概念理解时，请额外关注以下方面：
- **权衡分析**: 用户是否能分析方案的利弊？能否说出在什么场景下该方案不适用？
- **原则应用**: 用户是否理解SOLID等设计原则？能否识别代码中违反原则的地方？
- **模式识别**: 用户是否能识别代码中的设计模式？能否解释为什么在此场景使用该模式？
- **实践经验**: 用户是否有实际项目经验？能否用自己的项目举例说明概念的应用？
- **工具熟练度**: 用户是否了解相关工具(Git/CI/构建系统)的实际使用？
- **游戏行业理解**: 用户是否理解软件工程在游戏项目中的特殊挑战？
- **代码质量意识**: 用户是否能判断代码质量？能否提出具体的改进建议？
`,
  'computer-graphics': `
## 计算机图形学领域评估特殊指标

在评估图形学概念理解时，请额外关注以下方面：
- **数学理解**: 用户是否理解背后的数学原理？能否用公式或伪代码解释渲染过程？
- **管线定位**: 用户是否知道该概念在渲染管线中的位置？能否解释输入/输出数据格式？
- **性能权衡**: 用户是否了解该技术的性能开销？能否提出适合实时渲染的优化方案？
- **GPU思维**: 用户是否理解GPU并行执行模型？能否解释为什么某些算法适合/不适合GPU？
- **Shader能力**: 用户是否能用HLSL/GLSL描述核心算法？能否读懂简单的Shader代码？
- **对比分析**: 用户是否能对比同一问题的多种渲染方案(如AA的MSAA/TAA/FXAA)？
- **引擎实践**: 用户是否了解该技术在UE5/Unity中的实现方式和配置方法？
`,
  '3d-art': `
## 3D美术领域评估特殊指标

在评估3D美术概念理解时，请额外关注以下方面：
- **形体感知**: 用户是否能从剪影判断模型比例是否正确？能否识别形体问题？
- **拓扑理解**: 用户是否理解布线的目的？能否解释为什么某处需要更密的边环？
- **管线意识**: 用户是否理解当前步骤对下游的影响？能否解释布线如何影响UV展开和变形？
- **工具熟练度**: 用户是否能用具体的DCC工具操作实现概念？而非仅停留在理论层面？
- **游戏规范**: 用户是否了解游戏美术的特殊约束？能否根据项目需求调整制作标准？
- **审美判断**: 用户是否能评价资产质量？能否提出具体的改进建议？
- **问题解决**: 用户是否能诊断常见问题(烘焙瑕疵/UV拉伸/权重异常)并提出修复方案？
`,
  'concept-design': `
## 概念设计领域评估特殊指标

在评估概念设计概念理解时，请额外关注以下方面：
- **基础功底**: 用户是否理解解剖/透视/色彩/光影的基本原理？能否识别画面中的基础问题？
- **设计意识**: 用户是否能用形状语言/配色/剪影等工具有意识地传达设计意图？
- **叙事能力**: 用户是否能通过视觉元素讲故事——角色的经历、环境的历史、道具的功能？
- **流程理解**: 用户是否理解从缩略图到最终稿的完整流程？能否解释每个阶段的目的？
- **参考运用**: 用户是否能系统地收集和分析参考？能否将多源参考融合为原创设计？
- **风格一致性**: 用户是否理解项目风格统一的重要性？能否识别偏离风格的设计？
- **可执行性**: 用户的设计是否考虑了下游制作的可行性——3D建模/动画/引擎实现？
`,
  'animation': `
## 动画领域评估特殊指标

在评估动画概念理解时，请额外关注以下方面：
- **原理理解**: 用户是否真正理解12条动画原理？能否识别动画中违反原理的问题？
- **时间感知**: 用户是否理解timing和spacing对动画质量的影响？能否判断节奏是否合适？
- **重量表现**: 用户是否能区分不同重量物体的运动特征？能否通过姿势/时间表达重量感？
- **游戏约束**: 用户是否理解游戏动画与影视动画的区别？能否考虑实时性能/交互响应/循环等约束？
- **工具熟悉度**: 用户是否了解DCC工具和引擎中动画相关功能的使用方法和工作流？
- **管线理解**: 用户是否理解从建模→绑定→动画→引擎的完整管线？能否识别各环节的依赖关系？
- **调试能力**: 用户是否能识别和解决常见动画问题——穿模/滑步/权重异常/混合跳变？
`,
  'technical-art': `
## 技术美术领域评估特殊指标

在评估技术美术概念理解时，请额外关注以下方面：
- **Shader理解**: 用户是否理解GPU管线各阶段？能否读懂/编写基本的HLSL/GLSL代码？
- **性能意识**: 用户是否能识别常见的性能瓶颈(Draw Call/Overdraw/带宽)？能否提出合理的优化策略？
- **材质系统**: 用户是否理解PBR工作流？能否设计分层/可复用的材质系统？
- **工具能力**: 用户是否具备用Python/C#开发DCC/引擎工具的能力？能否设计面向美术师的工具界面？
- **管线设计**: 用户是否理解从建模到引擎的完整资产管线？能否制定合理的技术规范和预算？
- **PCG理解**: 用户是否理解程序化生成的基本原理？能否选择合适的PCG技术解决实际问题？
- **跨平台**: 用户是否了解不同平台(PC/主机/移动)的GPU架构差异及其对美术管线的影响？
`,
  'vfx': `
## 特效领域评估特殊指标

在评估特效概念理解时，请额外关注以下方面：
- **粒子系统**: 用户是否理解粒子生命周期、发射模式、力场系统？能否设计合理的粒子效果？
- **Shader特效**: 用户是否能编写/理解特效Shader(溶解、扭曲、UV滚动)？是否理解混合模式的原理？
- **物理模拟**: 用户是否理解流体、破碎等物理模拟的基本原理？能否选择合适的模拟精度？
- **性能意识**: 用户是否能识别Overdraw/粒子数量/DrawCall等特效性能瓶颈？能否提出优化方案？
- **后处理**: 用户是否理解Bloom/DoF/运动模糊等后处理原理？能否配置合理的后处理管线？
- **工作流**: 用户是否了解Houdini到引擎的特效烘焙流程？是否理解序列帧/VAT等预计算方案？
- **艺术表现**: 用户是否能分析特效的美术风格？能否在写实/风格化之间做出合理选择？
`,
  'game-audio-music': `
## 游戏音乐领域评估特殊指标

在评估游戏音乐概念理解时，请额外关注以下方面：
- **作曲能力**: 用户是否理解旋律/和声/节奏/配器的基本原理？能否为特定游戏场景设计合适的音乐？
- **自适应理解**: 用户是否理解水平重组/垂直分层/状态机等自适应音乐技术？能否设计动态音乐系统？
- **中间件实操**: 用户是否熟悉Wwise/FMOD的音乐系统功能？能否搭建交互式音乐播放逻辑？
- **主题设计**: 用户是否能为角色/场景设计有辨识度的音乐主题？是否理解主题变奏与发展的技法？
- **DAW技能**: 用户是否能使用DAW进行作曲/编曲/混音？是否了解虚拟乐器和采样库的使用？
- **风格认知**: 用户是否能辨别和分析不同音乐风格？能否根据游戏需求选择合适的风格方向？
- **技术意识**: 用户是否了解游戏音乐的内存/格式/流式播放等技术约束？能否优化音乐资源？
`,
};

export function getAssessmentSupplement(domainId: string | undefined): string {
  return (domainId && ASSESSMENT_SUPPLEMENTS[domainId]) || '';
}

// ─── Constants ───

/** Max messages to send to LLM (sliding window to prevent token overflow) */
const MAX_CONTEXT_MESSAGES = 20;

/**
 * Build the token-limit parameter for the request body.
 * OpenAI's newer models (o1, o3, chatgpt-4o-latest, chatgpt-5 series etc.)
 * require `max_completion_tokens` instead of `max_tokens`.
 */
export function tokenLimitParam(model: string, tokens: number): Record<string, number> {
  const m = model.toLowerCase();
  // Models that require max_completion_tokens
  if (/^(o[1-9]|chatgpt-)/.test(m) || /\/(o[1-9]|chatgpt-)/.test(m)) {
    return { max_completion_tokens: tokens };
  }
  return { max_tokens: tokens };
}

// ─── Helpers ───

/** Parse ```choices JSON block from LLM response content */
export function parseChoicesFromContent(text: string): { content: string; choices: Array<{ id: string; text: string; type: string }> } {
  if (!text) return { content: '', choices: [] };

  // Try to find ```choices ... ``` block
  const choicesPattern = /```choices\s*\n([\s\S]*?)```/;
  const match = text.match(choicesPattern);

  if (match) {
    const choicesJson = match[1].trim();
    const content = text.slice(0, match.index).trim();
    try {
      const parsed = JSON.parse(choicesJson);
      if (Array.isArray(parsed) && parsed.length >= 2) {
        const valid = parsed
          .filter((c: any) => c && typeof c.text === 'string' && c.text.trim())
          .slice(0, 4)
          .map((c: any, i: number) => ({
            id: c.id || `opt-${i + 1}`,
            text: String(c.text).slice(0, 60),
            type: ['explore', 'answer', 'action', 'level'].includes(c.type) ? c.type : 'explore',
          }));
        if (valid.length >= 2) return { content, choices: valid };
      }
    } catch { /* fallback to no choices */ }
    return { content, choices: [] };
  }

  return { content: text.trim(), choices: [] };
}

/** Apply sliding window to messages array — keep system prompt separate */
export function windowMessages(messages: Array<{ role: string; content: string }>): Array<{ role: string; content: string }> {
  if (messages.length <= MAX_CONTEXT_MESSAGES) return messages;
  // Always keep the first message (assistant opening) + last N messages
  return [messages[0], ...messages.slice(-MAX_CONTEXT_MESSAGES + 1)];
}

function fmt(template: string, vars: Record<string, string>): string {
  let result = template;
  for (const [key, value] of Object.entries(vars)) {
    result = result.replaceAll(`{${key}}`, value);
  }
  return result;
}

function resolveEndpoint(): { baseUrl: string; apiKey: string; model: string } {
  const { llmConfig } = useSettingsStore.getState();
  const key = llmConfig.apiKey;
  // Use provider-appropriate default model
  const model = llmConfig.model || getDefaultModel(llmConfig.provider);

  const rawBase = llmConfig.baseUrl || PROVIDER_INFO[llmConfig.provider].defaultBase;
  const baseUrl = resolveBaseUrl(rawBase, !!llmConfig.useProxy);
  return { baseUrl, apiKey: key, model };
}

/** Get concept info + graph context from the loaded graph store */
function getConceptContext(conceptId: string) {
  const { graphData } = useGraphStore.getState();
  if (!graphData) return null;

  const node = graphData.nodes.find(n => n.id === conceptId);
  if (!node) return null;

  // Build graph context
  const prereqs: string[] = [];
  const deps: string[] = [];
  const related: string[] = [];
  const idToLabel: Record<string, string> = {};
  for (const n of graphData.nodes) idToLabel[n.id] = n.label;

  for (const e of graphData.edges) {
    if (e.relation_type === 'prerequisite') {
      if (e.target === conceptId) prereqs.push(idToLabel[e.source] || e.source);
      if (e.source === conceptId) deps.push(idToLabel[e.target] || e.target);
    } else {
      if (e.source === conceptId) related.push(idToLabel[e.target] || e.target);
      else if (e.target === conceptId) related.push(idToLabel[e.source] || e.source);
    }
  }

  return { node, prereqs, deps, related };
}

// Domain-specific teaching supplement registry — synced from apps/api/engines/dialogue/prompts/feynman_system.py
const DOMAIN_SUPPLEMENTS: Record<string, string> = {
  'mathematics': `\n## 数学教学特殊规则\n\n1. **公式使用**: 讲解中使用 LaTeX 格式的数学公式（行内用 \`$...$\`，独立公式用 \`$$...$$\`）\n2. **证明引导**: 对定理类概念，引导用户理解证明思路而非仅记结论\n3. **计算验证**: 鼓励用户动手计算，提供数值例子\n4. **直觉优先**: 先给几何直觉或物理意义，再给严格定义\n5. **不要提及编程语言或代码**：这是纯数学教学\n`,
  'english': `\n## 英语教学特殊规则\n\n1. **双语讲解**: 用中文解释英语知识点，关键术语和例句保留英文原文并附中文翻译\n2. **例句丰富**: 每个知识点提供至少2-3个英文例句\n3. **对比教学**: 主动对比中英文差异，指出母语负迁移错误\n4. **语境导向**: 将语法规则放在真实语境中讲解\n5. **分层讲解**: 先给简单例子建立直觉，再讲规则细节和例外\n6. **不要使用LaTeX公式**：这是英语教学，用自然语言和英文例句\n`,
  'physics': `\n## 物理教学特殊规则\n\n1. **公式使用**: 使用 LaTeX 格式的物理公式，标注物理量的单位和量纲\n2. **直觉优先**: 先建立物理图像和直觉，再给数学表达。用类比、思想实验帮助理解\n3. **实验连接**: 将概念与真实实验或日常现象联系\n4. **单位和量纲**: 强调SI单位，进行量纲分析验证公式\n5. **近似与适用范围**: 明确定律的适用条件（如牛顿力学适用于低速宏观物体）\n6. **数值估算**: 鼓励数量级估算，培养物理直觉\n7. **历史脉络**: 适当介绍物理概念的发现历史\n`,
  'product-design': `\n## 产品设计教学特殊规则\n\n1. **案例驱动**: 每个概念尽量用真实产品案例说明（如微信、淘宝、Uber、Notion等）\n2. **框架与工具**: 介绍概念时同时说明对应的实用框架或工具\n3. **场景化教学**: 用"假设你是某产品的PM"的场景引导思考\n4. **权衡思维**: 明确指出各方案的利弊，培养权衡判断\n5. **避免教条**: 强调"取决于具体场景"，培养灵活运用能力\n6. **数据意识**: 涉及数据概念时用具体数字和计算示例\n7. **跨职能视角**: 适时引入设计、开发、运营等其他角色的关注点\n`,
  'finance': `\n## 金融理财教学特殊规则\n\n1. **数字驱动**: 金融概念必须配合具体数字和计算示例。如讲复利用"¥10,000年化8%，30年后≈¥100,627"\n2. **风险意识**: 始终强调风险与收益的权衡关系。每个投资概念都要明确指出潜在风险\n3. **公式与直觉并重**: 金融公式需同时解释数学形式和经济直觉。使用 LaTeX 公式如 $NPV = \\sum \\frac{CF_t}{(1+r)^t}$\n4. **真实案例**: 用真实市场案例说明概念（如2008金融危机、巴菲特的价值投资）\n5. **中国视角**: 优先使用中国市场案例（A股、沪深300、余额宝、LPR）\n6. **避免投资建议**: 教学目的是传授知识框架，不对具体投资品种做推荐\n7. **行为偏差**: 教学中穿插行为金融学洞察（损失厌恶、过度自信、锚定效应）\n`,
  'psychology': `\n## 心理学教学特殊规则\n\n1. **经典实验**: 心理学概念必须结合经典实验阐释。如讲从众引用Asch实验，讲依恋引用Ainsworth陌生情境实验\n2. **生活联系**: 将心理学概念与日常生活经验联系起来。如用"考试紧张"解释焦虑的认知成分\n3. **多视角分析**: 同一心理现象可从认知、行为、生物、社会等多个视角解释\n4. **批判性思维**: 引导用户质疑心理学研究的方法学局限（样本偏差、可重复性危机、相关≠因果）\n5. **去污名化**: 涉及心理障碍时使用中性、尊重的语言\n6. **实证导向**: 优先引用有实证支持的理论，对缺乏科学依据的观点应明确指出局限\n7. **跨文化视角**: 提醒心理学研究的WEIRD样本局限和文化差异影响\n`,
  'philosophy': `\n## 哲学教学特殊规则\n\n1. **原典引证**: 哲学概念必须结合原典文本阐释。如讲柏拉图引用洞穴寓言，讲康德引用定言命令的具体表述\n2. **思想实验**: 善用经典思想实验激发思考。如电车难题引入义务论vs功利主义争论，中文房间引入心灵哲学议题\n3. **对话传统**: 鼓励苏格拉底式追问，帮助用户发现自己立场中的隐含前提和潜在矛盾\n4. **东西互照**: 涉及西方哲学概念时主动联系中国哲学传统的类似讨论\n5. **论证结构**: 强调论证的逻辑结构。帮助用户区分前提和结论，识别有效论证与谬误\n6. **多元立场**: 对有争议的哲学问题呈现多种合理立场及其论据，避免灌输单一观点\n7. **概念精确**: 区分哲学术语的精确含义与日常用法（如"先验"≠"先天"，"唯物主义"≠"物质至上"）\n`,
  'biology': `\n## 生物学教学特殊规则\n\n1. **实验驱动**: 生物学概念尽可能结合经典实验阐述。如讲DNA结构引用Franklin X射线衍射、Watson-Crick模型构建过程\n2. **多尺度联系**: 生物学横跨分子→细胞→组织→个体→种群→生态系统多层次，主动建立尺度间的联系\n3. **进化视角**: 始终以进化为统一框架，解释结构和功能时追问"这个特征为什么被自然选择保留？"\n4. **类比与模型**: 善用类比帮助理解抽象的分子机制，但必须指明类比的局限性\n5. **医学关联**: 适时联系人类健康与疾病，增强学习的现实意义感\n6. **定量思维**: 生物学中涉及的数量关系要讲清楚（如Hardy-Weinberg方程、种群增长模型）\n7. **伦理维度**: 涉及基因编辑、转基因等技术时，主动讨论相关的伦理争议\n`,
  'economics': `\n## 经济学教学特殊规则\n\n1. **模型思维**: 经济学是通过简化模型理解复杂现实。讲解时先说明模型假设，再推导结论，最后讨论假设放松后的变化\n2. **数据驱动**: 尽可能用真实经济数据和案例支撑理论。如讲GDP用具体国家数据对比、讲通胀用历史通胀率曲线\n3. **权衡意识**: 经济学核心是权衡（trade-off）。每个政策都有成本和收益，要引导学生思考"谁受益、谁受损、有什么替代方案"\n4. **激励分析**: 始终追问"激励结构是什么？"。分析制度、政策时要考察其对不同主体的激励效应\n5. **边际思维**: 强调边际分析的核心地位。经济决策发生在边际上——边际成本、边际收益、边际效用\n6. **历史语境**: 经济理论产生于特定的历史背景。讲凯恩斯要联系大萧条，讲货币主义要联系70年代滞胀\n7. **政策连接**: 理论最终服务于政策分析。讲完理论后引导学生思考其政策含义\n`,
  'writing': `\n## 写作教学特殊规则\n\n1. **过程导向**: 写作是一个迭代过程（构思→起草→修改→校对）。教学中强调每个阶段的方法而非仅关注最终成品\n2. **读者意识**: 始终引导学生思考"谁在读？读者需要什么？"。不同体裁有不同的读者期待和文体规范\n3. **示例驱动**: 每个写作技法都用经典范文片段示范。如讲"展示而非告知"用海明威、汪曾祺\n4. **练习为本**: 写作是技能而非纯知识，必须通过练习习得。每讲一个技法后提供具体的练习建议\n5. **风格多元**: 尊重不同写作风格与传统。中国古典散文、现代白话文、英语写作传统各有特色\n6. **批判修改**: 培养批判性自我审视能力。引导学生学会诊断自己文章的问题\n7. **真实写作**: 鼓励联系真实写作情境。学术写作联系论文、职业写作联系工作场景、创意写作联系个人表达\n`,
  'game-design': `\n## 游戏设计教学特殊规则\n\n1. **案例驱动**: 每个概念用真实游戏案例说明（如塞尔达、暗黑、文明、英雄联盟、原神等）\n2. **系统思维**: 鼓励从系统视角分析设计，理解一个改动对多个子系统的连锁影响\n3. **玩家中心**: 所有设计决策服务于玩家体验，引导思考"这对玩家感觉如何？"\n4. **迭代思维**: 强调原型→测试→改进的循环，鼓励快速失败、快速学习\n5. **权衡意识**: 没有绝对正确的答案，只有权衡（深度vs可达性、自由度vs引导、公平vs有趣）\n6. **跨领域视角**: 融合心理学、经济学、叙事、美学等多学科知识分析设计问题\n7. **伦理意识**: 适时讨论道德设计、暗黑模式、成瘾防护等话题\n`,
  'level-design': `\n## 关卡设计教学特殊规则\n\n1. **空间思维**: 从3D空间角度思考——视线、路径、高度差、尺度感如何影响玩家体验\n2. **案例分析**: 用经典游戏关卡（《最后生还者》《塞尔达》《魂系列》《光环》《半条命》《超级马里奥》等）具体关卡说明设计原则\n3. **灰盒优先**: 先验证空间和流程，再叠加美术。"灰盒好玩的关卡才是好关卡"\n4. **度量意识**: 关卡有严格的度量标准（角色高度、跳跃距离、走廊宽度），引导理解每个数字的设计理由\n5. **引导设计**: 好的关卡让玩家自然走向目标而非依赖UI标记。光照、地标、布局等隐式引导是核心技能\n6. **节奏控制**: 紧张→放松→高潮的节奏设计决定玩家情感曲线。用图表化方式分析规划节奏\n7. **迭代测试**: 搭建→测试→修改的快速循环，用热力图和玩家反馈驱动改进\n`,
  'game-engine': `\n## 游戏引擎教学特殊规则\n\n1. **架构思维**: 从架构层面切入——模块划分、依赖关系、设计模式如何服务于引擎的可维护性与扩展性\n2. **双引擎对比**: 对比UE5与Unity在同一概念上的实现差异（如Actor-Component vs GameObject-Component），理解设计取舍\n3. **性能意识**: 每个概念关联其性能影响——CPU/GPU开销、内存占用、带宽消耗，培养"做任何事都先想性能代价"的习惯\n4. **实践导向**: 鼓励在真实引擎中动手验证。引用Profiler截图、调试视图、Stat命令等具体工具辅助理解\n5. **底层原理**: 对渲染管线、物理引擎等子系统，先讲清数学/算法原理再讲引擎中的实现\n6. **版本演进**: 引擎技术快速迭代（Nanite/Lumen/MetaSound等），注明技术的版本适用范围\n7. **跨系统协作**: 引导理解数据如何在子系统间流动，而非孤立看待每个模块\n`,
  'software-engineering': `\n## 软件工程教学特殊规则\n\n1. **原则先行**: 始终强调SOLID、DRY、KISS等原则的应用场景与边界——不存在银弹，每个选择都有代价\n2. **模式与反模式并讲**: 教设计模式时同时展示过度使用的后果和反模式\n3. **代码即示例**: 用具体代码片段解释概念，重构、设计模式等话题必须配合前后对比的代码示例\n4. **游戏行业视角**: 结合游戏开发的实际工程挑战——性能敏感、迭代速度快、资产规模大\n5. **工具链实践**: 版本控制、CI/CD、构建系统等话题应结合实际工具操作\n6. **渐进式复杂度**: 从简单场景引入概念，逐步展示真实项目中的复杂度\n7. **协作意识**: 从团队角度思考工程决策，强调代码审查/Git工作流/文档的协作价值\n`,
  '3d-art': `\n## 3D美术教学特殊规则\n\n1. **形体优先**: 强调"大形体→中形体→细节"的阶段化工作方法。始终从剪影和整体比例出发，避免过早陷入局部细节\n2. **管线思维**: 引导理解完整的资产管线，建模→雕刻→拓扑→UV→烘焙→纹理→引擎，每个步骤的决策如何影响下游\n3. **拓扑意识**: 布线不是随意的——每条边环都有目的。结合变形需求、细分行为、UV展开需求解释为什么这样布线\n4. **工具多元**: 3D美术涉及多个DCC工具(Blender/Maya/ZBrush/Substance)。关注原理而非工具，但针对学生使用的具体工具给出实操指导\n5. **视觉参考**: 鼓励建立视觉库——收集参考图、分析优秀作品的布线/比例/材质\n6. **游戏规范**: 强调游戏美术的特殊约束——面数预算、纹素密度、LOD层级、Draw Call性能\n7. **实战项目**: 鼓励通过实际项目学习——从简单道具到角色到场景，每个项目都要走完整管线\n`,
  'concept-design': `\n## 概念设计教学特殊规则\n\n1. **基本功优先**: 人体解剖、透视、色彩、光影是概念设计的四大基本功。教学时始终关联到这些基础——设计再华丽也要建立在扎实的绘画基础之上\n2. **形状语言**: 圆/方/三角传递不同性格信息。引导学生有意识地运用形状语言——角色剪影、道具轮廓、建筑外形都应服务于设计意图\n3. **剪影测试**: 好的设计在纯黑剪影下仍然辨识度高。鼓励学生在设计早期就进行剪影检查\n4. **叙事性设计**: 每个设计元素都应该讲故事——伤疤暗示经历、磨损暗示使用、颜色暗示阵营。避免无意义的装饰\n5. **迭代流程**: 概念设计不是一次成型——从大量缩略图→筛选→精炼→最终稿。鼓励广泛探索后再聚焦\n6. **参考驱动**: 参考不是抄袭。引导学生系统收集、分析、融合参考——从真实世界中提取设计语言\n7. **视觉开发思维**: 培养项目整体视觉一致性意识——色彩脚本、风格指南、世界观设定都是概念设计师的职责\n`,
  'animation': `\n## 动画教学特殊规则\n\n1. **12原则为纲**: 迪士尼12条动画原理是一切动画的基础。教学时始终将具体技术关联到基本原理——无论是手K还是动捕后处理\n2. **参考为先**: 动画制作永远从参考视频开始。鼓励学生拍摄/收集参考，培养对运动的敏感度\n3. **游戏特殊性**: 游戏动画需要考虑实时性能/循环/混合/交互响应等特殊约束。与影视动画有本质区别\n4. **Blocking优先**: 先确保关键姿势和节奏正确(Blocking)，再添加细节(Polish)。避免过早陷入细节\n5. **权重与时间**: 重量感通过timing和spacing传达——重物慢/轻物快，起止有缓冲。这是区分新手和专业的关键\n6. **手感优先**: 游戏动画的首要目标是让玩家感觉操控流畅——预备动作不能太长，响应必须及时\n7. **管线思维**: 动画不是孤立环节——需要与绑定/引擎/设计紧密协作。培养完整管线意识\n`,
  'technical-art': `\n## 技术美术教学特殊规则\n\n1. **桥梁角色**: 技术美术是美术与工程之间的桥梁。教学时始终强调跨职能沟通——用程序员能理解的方式描述美术需求，用美术师能理解的方式解释技术限制\n2. **性能意识**: 每个视觉效果都有性能代价。教学中始终关联性能影响——Shader指令数/Draw Call/内存/带宽\n3. **管线思维**: 技术美术不是孤立的——每个决策影响上下游。培养从DCC到引擎到发布的全管线视角\n4. **自动化优先**: 重复操作就应该自动化。鼓励用脚本/工具替代手工操作，提升团队效率\n5. **规范先行**: 技术规范要在项目早期制定，而非事后补救。标准/预算/命名是项目稳定运行的基础\n6. **实测为准**: 理论预期与实际性能可能有巨大差距。培养Profile驱动的优化习惯——先测量再优化\n7. **平台差异**: PC/主机/移动端有截然不同的GPU架构和限制。避免一刀切，培养针对性优化思维\n`,
  'vfx': `\n## 特效教学特殊规则\n\n1. **视觉参考先行**: 特效学习始终从视觉参考开始——分析AAA游戏和电影中的特效表现，理解"好特效"的标准\n2. **分层思维**: 好的特效是多层叠加的结果——底层粒子+中层Shader+顶层后处理。教学时分层拆解复杂特效\n3. **物理直觉**: 即使是卡通风格特效，也需要符合物理直觉。教学中培养对重力、空气阻力、惯性的感知\n4. **性能预算**: 特效是GPU开销的重灾区。始终强调Overdraw、粒子数量、Draw Call的控制，培养Profile习惯\n5. **引擎工具**: Niagara(UE5)/VFX Graph(Unity)是核心工具。教学中结合具体引擎工具讲解，但也传授通用原理\n6. **预计算vs实时**: 很多看似实时的特效实际是预计算(序列帧/VAT)。教学中培养在质量与性能间选择合适方案的能力\n7. **迭代优化**: 特效制作是不断迭代的过程——先实现核心效果，再逐步增加细节，最后优化性能\n`,
  'game-audio-music': `\n## 游戏音乐教学特殊规则\n\n1. **听觉先行**: 音乐学习始终从聆听开始——分析经典游戏配乐，理解不同风格/场景下的音乐设计思路\n2. **理论与实践并重**: 音乐理论(和声/曲式/配器)是基础，但必须结合DAW实操和中间件实现才能真正掌握\n3. **交互思维**: 游戏音乐不是线性的——教学中强调自适应/动态音乐的设计思维，音乐如何响应玩家行为\n4. **工具链完整**: 从DAW作曲→中间件(Wwise/FMOD)集成→引擎实现，教学覆盖完整的游戏音乐管线\n5. **主题动机驱动**: Leitmotif是游戏音乐的灵魂。教学中培养为角色/场景/事件设计和发展音乐主题的能力\n6. **风格多样性**: 游戏音乐涵盖管弦乐/电子/民族/摇滚等多种风格。教学中拓展风格视野，培养融合创新能力\n7. **技术约束**: 游戏音乐受内存/CPU/文件大小等技术约束。教学中培养在艺术表现与技术限制间平衡的能力\n`,
  'computer-graphics': `\n## 计算机图形学教学特殊规则\n\n1. **数学驱动**: 从数学公式出发——线性代数(矩阵变换)、微积分(渲染方程)、概率论(蒙特卡洛采样)，帮助建立"从公式到像素"的思维链\n2. **管线思维**: 引导理解数据如何从顶点→光栅化→片元→帧缓冲逐步流转，每个概念在管线中的位置和作用\n3. **实时vs离线**: 对比实时渲染(游戏)和离线渲染(电影)对同一问题的不同解法，培养根据场景选择方案的能力\n4. **GPU硬件意识**: 关联并行计算、显存带宽、Warp/Wave执行模型等硬件概念，解释为什么某些算法在GPU上高效/低效\n5. **Shader实战**: 鼓励用HLSL/GLSL编写Shader动手实验。使用ShaderToy、RenderDoc等工具观察和调试渲染效果\n6. **引擎实现**: 对接UE5/Unity中的实际渲染特性(Nanite/Lumen/URP/HDRP)，理解理论到工程实现的落差\n7. **视觉直觉**: 用对比图(开启/关闭效果)、分步渲染截图、调试视图辅助解释抽象概念\n`,
};

export function getDomainSupplement(domainId: string | undefined): string {
  return (domainId && DOMAIN_SUPPLEMENTS[domainId]) || '';
}

function buildSystemPrompt(node: GraphNode, prereqs: string[], deps: string[], related: string[]): string {
  const graphContext = `## 图谱上下文（帮助你理解这个概念在知识体系中的位置）
- **先修概念**: ${prereqs.join(', ') || '无'}
- **后续概念**: ${deps.join(', ') || '无'}
- **相关概念**: ${related.join(', ') || '无'}
- **是否为里程碑**: ${node.is_milestone ? '⭐ 是（里程碑节点）' : '否'}
`;

  // Domain-specific supplement (registry lookup)
  const domainId = 'domain_id' in node ? (node as { domain_id?: string }).domain_id : undefined;
  const domainSupplement = getDomainSupplement(domainId);

  return fmt(FEYNMAN_SYSTEM_PROMPT, {
    concept_name: node.label,
    subdomain_name: node.subdomain_id || '',
    difficulty: String(node.difficulty || 5),
    content_type: node.content_type || 'theory',
    graph_context: graphContext + domainSupplement,
  });
}

/** Opening user prompt — triggers LLM to generate Phase 1 probe */
const OPENING_USER_PROMPT = '开始学习「{concept_name}」';

/** Fallback opening when LLM call fails */
function getFallbackOpening(name: string): {
  text: string;
  choices: Array<{ id: string; text: string; type: string }>;
} {
  return {
    text: `👋 今天我们一起来探索「${name}」！\n\n这是一个很有意思的概念，让我先简单介绍一下，然后我们一步步深入。\n\n你之前对 ${name} 有了解吗？`,
    choices: [
      { id: 'opt-1', text: '完全没听说过', type: 'level' },
      { id: 'opt-2', text: '听过但说不太清楚', type: 'level' },
      { id: 'opt-3', text: '有一些了解，想深入', type: 'level' },
      { id: 'opt-4', text: '比较熟悉，直接进阶', type: 'level' },
    ],
  };
}

// ─── Public API ───

export interface DirectConversation {
  conversationId: string;
  conceptId: string;
  conceptName: string;
  systemPrompt: string;
  messages: Array<{ role: string; content: string }>;
  isMilestone: boolean;
}

// In-memory conversation storage for direct mode (max 20 conversations)
const directConversations = new Map<string, DirectConversation>();
const MAX_DIRECT_CONVERSATIONS = 20;

/** Clean up direct conversations map — evict oldest when exceeding limit */
function pruneDirectConversations(): void {
  if (directConversations.size <= MAX_DIRECT_CONVERSATIONS) return;
  const entries = Array.from(directConversations.entries());
  // Map preserves insertion order — delete oldest entries
  const toRemove = entries.slice(0, entries.length - MAX_DIRECT_CONVERSATIONS);
  for (const [key] of toRemove) directConversations.delete(key);
}

/** Clear a specific direct conversation (called by dialogue store reset) */
export function clearDirectConversation(conversationId: string): void {
  directConversations.delete(conversationId);
}

/** Clear all direct conversations */
export function clearAllDirectConversations(): void {
  directConversations.clear();
}

/** Create a new conversation in direct mode — LLM generates opening + choices */
export async function directCreateConversation(conceptId: string): Promise<{
  conversation_id: string;
  concept_id: string;
  concept_name: string;
  opening_message: string;
  opening_choices: Array<{ id: string; text: string; type: string }> | null;
  is_milestone: boolean;
} | null> {
  const ctx = getConceptContext(conceptId);
  if (!ctx) return null;

  const { node, prereqs, deps, related } = ctx;
  const systemPrompt = buildSystemPrompt(node, prereqs, deps, related);
  const convId = crypto.randomUUID();

  // Try to get LLM-generated opening with choices
  let openingText = '';
  let openingChoices: Array<{ id: string; text: string; type: string }> | null = null;

  try {
    const { baseUrl, apiKey, model } = resolveEndpoint();
    const userMsg = OPENING_USER_PROMPT.replace('{concept_name}', node.label);

    const res = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userMsg },
        ],
        temperature: 0.8,
        ...tokenLimitParam(model, 600),
      }),
      signal: AbortSignal.timeout(15000), // 15s timeout
    });

    // Guard: wrong URL may return 200 + HTML instead of JSON
    const openCT = res.headers.get('content-type') || '';
    if (res.ok && !openCT.includes('application/json')) {
      console.warn('LLM returned non-JSON content-type:', openCT);
    } else if (res.ok) {
      const data: any = await res.json();
      const raw = data.choices?.[0]?.message?.content || '';
      if (raw) {
        const parsed = parseChoicesFromContent(raw);
        openingText = parsed.content;
        openingChoices = parsed.choices.length >= 2 ? parsed.choices : null;
      } else {
        throw new Error('Empty LLM response');
      }
    } else {
      throw new Error(`LLM error ${res.status}`);
    }
  } catch {
    // Fallback to hardcoded opening
    const fallback = getFallbackOpening(node.label);
    openingText = fallback.text;
    openingChoices = fallback.choices;
  }

  const conv: DirectConversation = {
    conversationId: convId,
    conceptId,
    conceptName: node.label,
    systemPrompt,
    messages: [{ role: 'assistant', content: openingText }],
    isMilestone: node.is_milestone,
  };
  directConversations.set(convId, conv);
  pruneDirectConversations();

  return {
    conversation_id: convId,
    concept_id: conceptId,
    concept_name: node.label,
    opening_message: openingText,
    opening_choices: openingChoices,
    is_milestone: node.is_milestone,
  };
}

/** Stream chat in direct mode — returns a ReadableStream of SSE-like events */
export function directChatStream(
  conversationId: string,
  userMessage: string,
  signal?: AbortSignal,
): ReadableStream<Uint8Array> {
  const conv = directConversations.get(conversationId);
  const encoder = new TextEncoder();

  if (!conv) {
    return new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'chunk', content: '⚠️ 会话不存在' })}\n\n`));
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`));
        controller.close();
      }
    });
  }

  // Save user message
  conv.messages.push({ role: 'user', content: userMessage });
  const userTurns = conv.messages.filter(m => m.role === 'user').length;

  const { baseUrl, apiKey, model } = resolveEndpoint();
  // Apply sliding window to prevent token overflow
  const windowedMsgs = windowMessages(conv.messages);
  const allMessages = [
    { role: 'system', content: conv.systemPrompt },
    ...windowedMsgs,
  ];

  return new ReadableStream({
    async start(controller) {
      try {
        const res = await fetch(`${baseUrl}/chat/completions`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model,
            messages: allMessages,
            temperature: 0.75,
            ...tokenLimitParam(model, 800),
            stream: true,
          }),
          signal,
        });

        if (!res.ok) {
          const text = await res.text().catch(() => '');
          // Build user-friendly error message for common HTTP status codes
          let friendlyMsg = `⚠️ LLM 错误 ${res.status}: `;
          if (res.status === 401) {
            friendlyMsg += 'API Key 无效或已过期，请在设置中检查 Key 是否正确。';
          } else if (res.status === 402) {
            friendlyMsg += 'API 账户余额不足，请前往服务商充值后重试。';
          } else if (res.status === 429) {
            friendlyMsg += '请求过于频繁，请稍后再试。';
          } else if (res.status === 404) {
            friendlyMsg += '模型不存在或 Base URL 错误，请检查设置。';
          } else {
            friendlyMsg += text.slice(0, 200);
          }
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', content: friendlyMsg })}\n\n`
          ));
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`
          ));
          controller.close();
          return;
        }

        // Guard: wrong URL may return 200 + HTML instead of SSE/JSON
        const streamCT = res.headers.get('content-type') || '';
        if (!streamCT.includes('text/event-stream') && !streamCT.includes('application/json')) {
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', content: `⚠️ LLM 返回了非预期的 content-type: ${streamCT}，请检查 Base URL 设置。` })}\n\n`
          ));
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`
          ));
          controller.close();
          return;
        }

        if (!res.body) {
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', content: '⚠️ LLM 返回了空响应体' })}\n\n`
          ));
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`
          ));
          controller.close();
          return;
        }
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            const payload = line.slice(6).trim();
            if (payload === '[DONE]') continue;
            try {
              const chunk = JSON.parse(payload);
              const delta = chunk.choices?.[0]?.delta;
              if (delta?.content) {
                fullContent += delta.content;
                controller.enqueue(encoder.encode(
                  `data: ${JSON.stringify({ type: 'chunk', content: delta.content })}\n\n`
                ));
              }
            } catch { /* ignore */ }
          }
        }

        // Parse choices from response and save clean content
        if (fullContent) {
          const parsed = parseChoicesFromContent(fullContent);
          // Store clean content (without choices block) for conversation history
          conv.messages.push({ role: 'assistant', content: parsed.content || fullContent });
          // M-02 fix: Cap conversation messages to prevent unbounded memory growth
          if (conv.messages.length > MAX_CONTEXT_MESSAGES * 2) {
            conv.messages = [conv.messages[0], ...conv.messages.slice(-(MAX_CONTEXT_MESSAGES * 2 - 1))];
          }

          // Send choices event if parsed successfully
          if (parsed.choices.length >= 2) {
            controller.enqueue(encoder.encode(
              `data: ${JSON.stringify({ type: 'choices', choices: parsed.choices })}\n\n`
            ));
          }
        }

        controller.enqueue(encoder.encode(
          `data: ${JSON.stringify({ type: 'done', suggest_assess: userTurns >= 4, turn: userTurns })}\n\n`
        ));
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          // Intentional cancellation
        } else {
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', content: '抱歉，我刚才走神了 😅 你能再说一遍吗？' })}\n\n`
          ));
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`
          ));
        }
      } finally {
        controller.close();
      }
    }
  });
}

/** Assess understanding in direct mode */
export async function directAssess(conversationId: string): Promise<Record<string, unknown>> {
  const conv = directConversations.get(conversationId);
  if (!conv) return { error: '会话不存在' };

  const userTurns = conv.messages.filter(m => m.role === 'user').length;
  if (userTurns < 2) return { error: '请至少进行 2 轮对话后再评估', current_turns: userTurns };

  const ctx = getConceptContext(conv.conceptId);
  const difficulty = ctx?.node.difficulty || 5;
  const domainId = ctx?.node && 'domain_id' in ctx.node ? (ctx.node as { domain_id?: string }).domain_id : undefined;

  const systemPrompt = fmt(ASSESSMENT_SYSTEM_PROMPT, {
    concept_name: conv.conceptName,
    difficulty: String(difficulty),
    domain_assessment_supplement: getAssessmentSupplement(domainId),
  });

  // Truncate dialogue to prevent exceeding LLM context window
  // (matches FastAPI evaluator 8000 char limit and Workers dialogue.ts)
  // Role labels match FastAPI evaluator.py: user=学习者, AI=学习伙伴/老师
  const MAX_DIALOGUE_CHARS = 8000;
  let totalChars = 0;
  const dialogueLines: string[] = [];
  // Prioritize recent messages by iterating in reverse, use push+reverse for O(n)
  for (let i = conv.messages.length - 1; i >= 0; i--) {
    const m = conv.messages[i];
    const line = `[${m.role === 'user' ? '用户（学习者）' : 'AI（学习伙伴/老师）'}]: ${m.content}`;
    if (totalChars + line.length > MAX_DIALOGUE_CHARS) break;
    dialogueLines.push(line);
    totalChars += line.length;
  }
  dialogueLines.reverse();
  const dialogueText = dialogueLines.join('\n\n');

  const { baseUrl, apiKey, model } = resolveEndpoint();

  try {
    // m-07 fix: Add timeout to prevent indefinite "评估中..." UI state
    const res = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: `以下是用户在费曼对话中的完整对话记录，请评估用户对「${conv.conceptName}」的理解程度：\n\n${dialogueText}` },
        ],
        temperature: 0.2,
        ...tokenLimitParam(model, 1024),
      }),
      signal: AbortSignal.timeout(30_000),
    });

    if (!res.ok) throw new Error(`LLM error ${res.status}`);
    // Guard: wrong URL may return 200 + HTML instead of JSON
    const evalCT = res.headers.get('content-type') || '';
    if (!evalCT.includes('application/json')) {
      throw new Error(`LLM returned non-JSON (${evalCT}). Check your Base URL.`);
    }
    const data: any = await res.json();
    const text = data.choices?.[0]?.message?.content || '';

    // Parse assessment JSON
    const result = parseAssessmentJSON(text);
    if (result) {
      return { concept_id: conv.conceptId, concept_name: conv.conceptName, turns: userTurns, ...result };
    }
  } catch { /* fallback */ }

  // Fallback — mastered logic must match backend evaluator._validate_result:
  // overall_score >= 75 AND all dimensions >= 60
  const base = Math.min(40 + userTurns * 8, 85);
  const dims = { completeness: base, accuracy: base - 5, depth: base - 10, examples: base - 15 };
  const overall = base - 5;
  const mastered = overall >= 75 && Object.values(dims).every(s => s >= 60);
  return {
    concept_id: conv.conceptId, concept_name: conv.conceptName, turns: userTurns,
    ...dims, overall_score: overall,
    gaps: ['评估服务暂时不可用'], feedback: `你进行了 ${userTurns} 轮对话，表现不错！`,
    mastered,
  };
}

/** Validate and normalize assessment result — clamp scores, recalculate mastered
 *  (matches FastAPI evaluator.validate_result and Workers validateAssessment) */
function validateAssessment(result: any): any {
  for (const k of ['completeness', 'accuracy', 'depth', 'examples', 'overall_score']) {
    const v = result[k];
    const raw = (v === null || v === undefined) ? NaN : Number(v);
    result[k] = Math.max(0, Math.min(100, Math.round(Number.isFinite(raw) ? raw : 50)));
  }
  result.mastered = result.overall_score >= 75 && ['completeness', 'accuracy', 'depth', 'examples'].every((k: string) => result[k] >= 60);
  result.gaps = Array.isArray(result.gaps) ? result.gaps : [];
  result.feedback = result.feedback || '评估完成';
  return result;
}

export function parseAssessmentJSON(text: string): any | null {
  try { return validateAssessment(JSON.parse(text)); } catch { /* */ }
  if (text.includes('```json')) {
    const start = text.indexOf('```json') + 7;
    const end = text.indexOf('```', start);
    try { return validateAssessment(JSON.parse(text.slice(start, end).trim())); } catch { /* */ }
  }
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}') + 1;
  if (start >= 0 && end > start) {
    try { return validateAssessment(JSON.parse(text.slice(start, end))); } catch { /* */ }
  }
  return null;
}
