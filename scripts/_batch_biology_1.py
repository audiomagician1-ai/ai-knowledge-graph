"""Batch rewrite biology concepts: dna-replication, photosynthesis, mitosis, mendelian-genetics, natural-selection."""
import json, re, yaml
from pathlib import Path
from datetime import datetime

PROJECT = Path("D:/echoagent/projects/ai-knowledge-graph")
RAG_ROOT = PROJECT / "data" / "rag"

concepts = {
    "dna-replication": {
        "domain": "biology",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - DNA replication", "url": "https://en.wikipedia.org/wiki/DNA_replication"},
            {"type": "textbook-online", "ref": "NCBI Bookshelf - DNA Replication Mechanisms", "url": "https://www.ncbi.nlm.nih.gov/books/NBK26850/"},
            {"type": "educational", "ref": "Khan Academy - Molecular mechanism of DNA replication", "url": "https://www.khanacademy.org/science/ap-biology/gene-expression-and-regulation/replication/a/molecular-mechanism-of-dna-replication"},
        ],
        "body": """# DNA复制

## 概述

DNA复制（DNA Replication）是细胞精确复制其DNA分子的过程，发生在细胞周期的**S期**（合成期）。这一过程对于生物遗传、细胞分裂和损伤组织修复至关重要——它确保每个新产生的子细胞都获得一份完整的DNA拷贝（Wikipedia: DNA replication）。

DNA复制是**半保留复制**（semiconservative replication）：双螺旋的两条链分别作为模板，各自合成一条新的互补链。因此每个子代DNA分子都包含一条来自亲代的原始链和一条新合成的链。这一机制由 Meselson 和 Stahl 在 1958 年通过同位素密度梯度离心实验证实（Khan Academy）。

## 核心知识点

### DNA结构基础

DNA由两条反向平行的核苷酸链组成双螺旋结构。四种碱基通过氢键配对：**腺嘌呤(A)-胸腺嘧啶(T)**（2个氢键）、**鸟嘌呤(G)-胞嘧啶(C)**（3个氢键）。每条链有方向性：5'端和3'端，两条链反向平行排列（Wikipedia: DNA replication）。

### 复制机器——关键酶和蛋白质

**解旋酶（Helicase）**：在复制起始位点（origin of replication）解开双螺旋，形成**复制叉**（replication fork），复制叉向两个方向双向延伸。

**DNA聚合酶（DNA Polymerase）**：核心复制酶，按5'→3'方向合成新链，具有**校对功能**（proofreading，3'→5'外切核酸酶活性）。原核生物中 DNA Pol III 是主要复制酶，真核生物中 DNA Pol ε（前导链）和 DNA Pol δ（滞后链）执行主要合成（NCBI Bookshelf）。

**引物酶（Primase）**：合成短的RNA引物（约10个核苷酸），为DNA聚合酶提供3'-OH起始点——因为DNA聚合酶**不能从头合成**，只能延伸已有的链。

**拓扑异构酶（Topoisomerase）**：缓解解旋产生的超螺旋张力。

### 前导链 vs 滞后链

由于DNA聚合酶只能5'→3'合成：
- **前导链（Leading strand）**：朝向复制叉方向连续合成，仅需一个引物
- **滞后链（Lagging strand）**：远离复制叉方向不连续合成，产生多个短片段——**冈崎片段**（Okazaki fragments），原核生物约1000-2000核苷酸/片段，真核生物约100-200核苷酸/片段
- **DNA连接酶（Ligase）**：将冈崎片段连接成完整链

### 复制保真性

DNA复制的错误率极低：约 10⁻⁹ ~ 10⁻¹⁰ 每碱基对每次复制。保真机制包括：
1. **碱基选择**：聚合酶活性位点的几何约束（错误率 ~10⁻⁴）
2. **校对**：3'→5'外切核酸酶立即纠正错配（降低 ~100倍）
3. **错配修复（MMR）**：复制后修复系统检测并纠正残余错误（再降低 ~100倍）

## 关键要点

1. DNA复制是半保留的——每个子代分子含一条旧链和一条新链（Meselson-Stahl 1958）
2. DNA聚合酶只能 5'→3' 合成，导致前导链连续合成、滞后链不连续合成（冈崎片段）
3. 复制起始于特定位点（origin），双向进行形成复制叉
4. 引物酶合成RNA引物是必须的——DNA聚合酶不能从头起始
5. 三重保真机制使错误率达到约 10⁻⁹ ~ 10⁻¹⁰/碱基对/复制

## 常见误区

1. **"DNA聚合酶可以双向合成"**——聚合酶只能 5'→3' 方向添加核苷酸，这是滞后链必须不连续合成的根本原因
2. **"复制从DNA任意位置开始"**——复制起始于特定的起始位点（大肠杆菌有1个，人类细胞有约30,000-50,000个）
3. **"RNA引物会留在DNA中"**——引物在合成后被DNA聚合酶I（原核）或RNase H（真核）去除，空隙由DNA填补

## 知识衔接

- **先修**：DNA结构、碱基配对规则
- **后续**：基因表达（转录和翻译）、DNA修复机制、PCR技术"""
    },

    "photosynthesis": {
        "domain": "biology",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - Photosynthesis", "url": "https://en.wikipedia.org/wiki/Photosynthesis"},
            {"type": "encyclopedia", "ref": "Wikipedia - Calvin cycle", "url": "https://en.wikipedia.org/wiki/Calvin_cycle"},
        ],
        "body": """# 光合作用

## 概述

光合作用（Photosynthesis）是植物、藻类和蓝细菌利用光能将二氧化碳和水转化为有机物（主要是葡萄糖）并释放氧气的生物化学过程。其总反应方程式为：

**6CO₂ + 6H₂O + 光能 → C₆H₁₂O₆ + 6O₂**

光合作用是地球上几乎所有生命的能量基础。全球光合作用捕获的平均能量约为 **130 太瓦（TW）**，大约是人类文明总能耗的 **8 倍**。光合生物每年将约 **1000-1150 亿吨**碳固定为生物量（Wikipedia: Photosynthesis）。

光合作用于 1779 年由 **Jan Ingenhousz** 发现——他证明植物需要光而不仅是土壤和水。

## 核心知识点

### 光反应（Light-Dependent Reactions）

发生在叶绿体的**类囊体膜**上：

1. **光系统II（PSII）**：吸收 680nm 光（P680），利用光能裂解水分子：2H₂O → O₂ + 4H⁺ + 4e⁻。这是地球大气中**氧气的来源**
2. **电子传递链**：电子经过质体醌（PQ）→ 细胞色素 b6f → 质体蓝素（PC），传递过程中将 H⁺ 泵入类囊体腔
3. **光系统I（PSI）**：吸收 700nm 光（P700），将电子传给铁氧还蛋白，最终由 **NADP⁺还原酶** 将 NADP⁺ 还原为 **NADPH**
4. **ATP合酶**：H⁺ 沿浓度梯度经 ATP 合酶回流，驱动 ADP + Pi → **ATP**（化学渗透假说，Mitchell 1961）

### Calvin 循环（暗反应/碳反应）

发生在叶绿体**基质**中，不直接需要光但需要光反应产物（ATP 和 NADPH）：

1. **碳固定**：RuBisCO 酶催化 CO₂ + RuBP（5C）→ 2 × 3-磷酸甘油酸（3C）。RuBisCO 是地球上**最丰富的蛋白质**
2. **还原**：3-磷酸甘油酸被 ATP 和 NADPH 还原为甘油醛-3-磷酸（G3P）
3. **再生**：每固定 3 个 CO₂，产出 6 个 G3P，其中 5 个用于再生 RuBP，1 个为净产出

**总结**：固定 1 个 CO₂ 需要 3 ATP + 2 NADPH；合成 1 分子葡萄糖需要 6 轮 Calvin 循环（Wikipedia: Calvin cycle）。

### C4 和 CAM 光合途径

**C4 途径**（如玉米、甘蔗）：先在叶肉细胞中由 PEP 羧化酶固定 CO₂ 为 4 碳化合物，再转运到维管束鞘细胞释放 CO₂ 给 Calvin 循环。避免了 RuBisCO 的**光呼吸**问题。

**CAM 途径**（如仙人掌、景天）：夜间开放气孔固定 CO₂，白天关闭气孔进行 Calvin 循环。适应干旱环境。

## 关键要点

1. 光反应在类囊体膜上产生 ATP 和 NADPH；Calvin 循环在基质中用它们固定 CO₂
2. 水的光解（PSII）是大气 O₂ 的来源
3. RuBisCO 是碳固定的关键酶也是地球上最丰富的蛋白质，但效率不高（也催化光呼吸）
4. 全球光合作用捕获约 130 TW 能量 ≈ 人类总能耗的 8 倍
5. C4 和 CAM 途径是对高温/干旱环境中 RuBisCO 光呼吸问题的进化解决方案

## 常见误区

1. **"暗反应在黑暗中进行"**——"暗反应"（Calvin循环）不直接使用光但需要光反应产物ATP和NADPH，因此实际在白天进行
2. **"光合作用只发生在叶子中"**——任何含叶绿体的绿色组织都能光合，包括茎和未成熟果实
3. **"植物白天光合晚上呼吸"**——植物 24 小时都在呼吸，白天光合速率通常大于呼吸速率所以净释放 O₂

## 知识衔接

- **先修**：细胞器结构（叶绿体）、ATP 与能量代谢
- **后续**：细胞呼吸（糖酵解+三羧酸循环）、碳循环生态学"""
    },

    "mitosis": {
        "domain": "biology",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - Cell division / Mitosis", "url": "https://en.wikipedia.org/wiki/Cell_division"},
            {"type": "educational", "ref": "Khan Academy - Phases of mitosis", "url": "https://www.khanacademy.org/science/biology/cellular-molecular-biology/mitosis/a/phases-of-mitosis"},
        ],
        "body": """# 有丝分裂

## 概述

有丝分裂（Mitosis）是真核细胞将已复制的染色体均等分配到两个子核中的细胞分裂过程，是细胞周期的关键阶段。有丝分裂产生两个基因组成**完全相同**的子细胞，负责生物体的生长、组织修复和无性繁殖（Wikipedia: Cell division）。

有丝分裂是细胞周期中**M期（有丝分裂期）**的核分裂部分，紧随其后的**胞质分裂**（cytokinesis）将细胞质一分为二。完整的细胞周期包括：G1期 → S期（DNA复制）→ G2期 → M期（有丝分裂 + 胞质分裂）。

## 核心知识点

### 四个/五个阶段

**前期（Prophase）**：
- 染色质凝缩为可见的染色体，每条染色体由两条**姐妹染色单体**通过着丝粒连接
- 中心体（已在S期复制）向细胞两极移动，形成纺锤体
- 核仁消失

**前中期（Prometaphase）**——部分教科书将其单独列为第5阶段：
- 核膜破裂
- 纺锤体微管连接到染色体的**动粒**（kinetochore）

**中期（Metaphase）**：
- 所有染色体排列在细胞中央的**赤道板**（metaphase plate）上
- **纺锤体检查点**（Spindle Assembly Checkpoint）确认所有动粒都正确连接后才允许进入下一阶段（Khan Academy）

**后期（Anaphase）**：
- 着丝粒分裂，姐妹染色单体被拉向细胞两极
- 细胞伸长

**末期（Telophase）**：
- 染色体到达两极，开始去凝缩
- 核膜在每组染色体周围重新形成
- 核仁重新出现

### 胞质分裂

- **动物细胞**：收缩环（肌动蛋白+肌球蛋白）在赤道面处缢缩，形成**分裂沟**
- **植物细胞**：高尔基体囊泡在中央形成**细胞板**，最终发展为新的细胞壁

### 细胞周期调控

- **Cyclin-CDK 复合物**是细胞周期的核心调控器
- **G1检查点**（限制点）：评估细胞大小、营养和DNA完整性
- **G2检查点**：确认DNA复制完成且无损伤
- **纺锤体检查点**（中期→后期过渡）：确保所有染色体正确连接纺锤体

## 关键要点

1. 有丝分裂产生两个基因组完全相同的子细胞
2. 四主要阶段：前期（凝缩）→中期（排列）→后期（分离）→末期（重建核膜）
3. 纺锤体检查点是防止非整倍体（染色体数目异常）的关键保障
4. 有丝分裂 ≠ 细胞分裂——有丝分裂仅指核分裂，完整分裂还包括胞质分裂
5. 细胞周期受 Cyclin-CDK 复合物和多个检查点的严格调控

## 常见误区

1. **"有丝分裂 = 细胞分裂"**——有丝分裂只是核分裂，胞质分裂是单独的过程
2. **"DNA在有丝分裂期间复制"**——DNA复制发生在间期的S期，有丝分裂是分配已复制的DNA
3. **"有丝分裂产生单倍体细胞"**——有丝分裂维持倍性不变（2n→2n），产生单倍体的是减数分裂（meiosis）

## 知识衔接

- **先修**：DNA复制、染色体结构
- **后续**：减数分裂（meiosis）、细胞周期调控与癌症"""
    },

    "mendelian-genetics": {
        "domain": "biology",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - Gregor Mendel", "url": "https://en.wikipedia.org/wiki/Gregor_Mendel"},
            {"type": "educational", "ref": "Khan Academy - Mendel's law of segregation", "url": "https://www.khanacademy.org/science/ap-biology/heredity/mendelian-genetics-ap/a/the-law-of-segregation"},
            {"type": "reference", "ref": "NHGRI - Mendelian Inheritance", "url": "https://www.genome.gov/genetics-glossary/Mendelian-Inheritance"},
        ],
        "body": """# 孟德尔遗传学

## 概述

孟德尔遗传学（Mendelian Genetics）是基于**孟德尔遗传定律**的经典遗传学体系。奥地利修道士**格雷戈尔·孟德尔**（Gregor Mendel, 1822-1884）在1856-1863年间对豌豆进行了系统杂交实验，建立了遗传学的基本规律。他的工作于1866年发表，但直到1900年才被 de Vries、Correns 和 von Tschermak 独立重新发现（Wikipedia: Gregor Mendel）。

孟德尔的发现奠定了现代遗传学的基础——"基因"以离散颗粒（而非混合液体）传递的观点，后来成为现代综合进化论（Modern Synthesis）的核心支柱之一。

## 核心知识点

### 孟德尔三大定律

**分离定律（Law of Segregation）**：
- 每个个体携带两个等位基因（一个来自父方，一个来自母方）
- 形成配子时，等位基因对**分离**，每个配子只含一个等位基因
- 受精时两个配子随机结合，恢复成对
- 孟德尔的经典验证：Aa × Aa → 后代表型比 3:1（Khan Academy）

**自由组合定律（Law of Independent Assortment）**：
- 不同对的等位基因在配子形成时**独立分配**
- AaBb × AaBb → 后代表型比 9:3:3:1
- **限制条件**：仅适用于位于不同染色体或同一染色体上距离足够远的基因

**显性定律（Law of Dominance）**：
- 杂合子（Aa）的表型由显性等位基因（A）决定
- 隐性等位基因（a）只在纯合状态（aa）下表达

### 关键术语

| 术语 | 定义 |
|------|------|
| 基因型（Genotype） | 个体的等位基因组成（如 AA, Aa, aa） |
| 表型（Phenotype） | 可观察的性状表现 |
| 纯合子（Homozygous） | 两个等位基因相同（AA 或 aa） |
| 杂合子（Heterozygous） | 两个等位基因不同（Aa） |
| 测交（Test Cross） | 未知基因型个体 × 纯合隐性个体，通过后代比例推断基因型 |

### 超越简单孟德尔遗传

实际遗传远比孟德尔三定律复杂：
- **不完全显性**：Aa 表型介于 AA 和 aa 之间（如金鱼草花色）
- **共显性**：Aa 同时表达两种等位基因（如 ABO 血型的 IA IB 型）
- **多基因遗传**：多个基因共同影响一个性状（如身高、肤色）
- **连锁**：同一染色体上的基因倾向于一起遗传，违反自由组合定律
- **表观遗传学**：基因表达受环境调控的非DNA序列变化

## 关键要点

1. 孟德尔通过豌豆实验（1856-1863）发现遗传颗粒性，1900年被重新发现
2. 三大定律：分离（配子形成时等位基因对分离）、自由组合（不同基因对独立分配）、显性
3. 单基因杂合交叉：3:1 表型比；双基因：9:3:3:1
4. 测交是确定显性表型个体基因型的经典方法
5. 实际遗传有众多"非孟德尔"模式：不完全显性、连锁、多基因等

## 常见误区

1. **"显性 = 更好/更常见"**——显性只描述等位基因之间的表达关系，与适应性或频率无关
2. **"所有性状都遵循孟德尔定律"**——多基因性状（身高等）、连锁基因、表观遗传等都不符合简单孟德尔比例
3. **"孟德尔的发现立即被接受"**——他的论文在1866年发表后被忽视了34年，直到1900年才被重新发现

## 知识衔接

- **先修**：DNA结构、染色体与减数分裂
- **后续**：连锁与交换、群体遗传学、表观遗传学"""
    },

    "natural-selection": {
        "domain": "biology",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - Natural selection", "url": "https://en.wikipedia.org/wiki/Natural_selection"},
            {"type": "encyclopedia", "ref": "Wikipedia - On the Origin of Species", "url": "https://en.wikipedia.org/wiki/On_the_Origin_of_Species"},
        ],
        "body": """# 自然选择

## 概述

自然选择（Natural Selection）是进化的核心机制——由于个体之间存在可遗传的性状差异，那些在特定环境中具有**更高适应度**（fitness）的个体更可能存活并繁殖，从而使有利性状在种群中的频率逐代增加（Wikipedia: Natural selection）。

**达尔文**（Charles Darwin）和**华莱士**（Alfred Russel Wallace）于 1858 年在一次联合报告中首次提出自然选择理论。1859 年达尔文出版《物种起源》（On the Origin of Species）系统阐述了这一理论。达尔文将自然选择与**人工选择**类比——前者是无意识的，后者是人为定向的。

## 核心知识点

### 自然选择的四个必要条件

1. **变异**（Variation）：种群内个体之间存在性状差异
2. **遗传**（Heredity）：这些性状差异至少部分可遗传给后代
3. **差异繁殖**（Differential Reproduction）：具有某些性状的个体在生存和繁殖上更有优势
4. **时间**：足够多的世代使性状频率发生显著变化

当这四个条件同时满足时，种群的等位基因频率就会随时间发生定向变化——这就是进化。

### 选择的类型

**定向选择**（Directional Selection）：偏向一个极端表型。例如工业革命中英国椒花蛾从浅色到深色的转变。

**稳定化选择**（Stabilizing Selection）：偏向中间表型，淘汰极端值。例如人类新生儿的出生体重——过轻或过重的婴儿存活率较低。

**分裂选择**（Disruptive Selection）：同时偏向两个极端，淘汰中间表型。可以导致物种分化。

**性选择**（Sexual Selection）：基于交配偏好的选择。雄性孔雀的华丽尾羽不利于逃避捕食者，但增加了交配机会。

### 适应与适应度

**适应**（Adaptation）是自然选择的结果——种群在特定环境中的适应性特征。适应可以是结构性的（北极熊的白色皮毛）、生理性的（高海拔人群的血红蛋白含量）或行为性的（候鸟迁徙）。

**适应度**（Fitness）在进化生物学中特指个体对下一代基因库的贡献，通常用**相对繁殖成功率**衡量，而非日常含义的"强壮"。

### 现代综合进化论

达尔文时代缺乏遗传学理论。20世纪初，孟德尔遗传学与达尔文选择论的整合形成了**现代综合进化论**（Modern Synthesis），其核心贡献者包括 Fisher、Haldane 和 Wright。21世纪的**扩展进化综合论**进一步纳入了表观遗传、发育可塑性等因素（Wikipedia: Natural selection）。

## 关键要点

1. 自然选择需要四个条件同时满足：变异 + 遗传 + 差异繁殖 + 时间
2. 三种主要选择模式：定向、稳定化、分裂选择
3. 适应度 ≠ 强壮，而是对后代基因库的贡献（相对繁殖成功率）
4. 达尔文（1859）与华莱士独立提出，但达尔文缺乏遗传机制——现代综合论填补了这一空白
5. 性选择可以产生对生存不利但增加交配成功的性状（如孔雀尾羽）

## 常见误区

1. **"适者生存意味着最强者生存"**——"fit"在进化中是"适合环境的"而非"体能最好的"
2. **"自然选择有目的地使生物变得更好"**——自然选择没有方向或目的，环境变化时曾经有利的性状可能变为不利
3. **"个体可以进化"**——进化是种群水平的等位基因频率变化，个体不会进化，只是被选择

## 知识衔接

- **先修**：孟德尔遗传学、种群概念
- **后续**：群体遗传学、物种形成、分子进化"""
    },
}


def write_back(cid, info):
    domain = info["domain"]
    rag_dir = RAG_ROOT / domain
    candidates = list(rag_dir.rglob(f"{cid}.md"))
    if not candidates:
        print(f"  ERROR: not found {cid}.md in {rag_dir}")
        return False
    rag_file = candidates[0]
    print(f"  Writing: {rag_file.relative_to(PROJECT)}")
    content = rag_file.read_text(encoding="utf-8")
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    meta = {}
    if m:
        try:
            meta = yaml.safe_load(m.group(1)) or {}
        except:
            meta = {}
    meta["content_version"] = (meta.get("content_version", 1) or 1) + 1
    meta["generation_method"] = "research-rewrite-v2"
    meta["last_scored"] = datetime.now().strftime("%Y-%m-%d")
    meta["sources"] = info["sources"]
    yaml_lines = ["---"]
    for key in ["id", "concept", "domain", "subdomain", "subdomain_name", "difficulty", "is_milestone", "tags"]:
        if key in meta:
            val = meta[key]
            if isinstance(val, str):
                yaml_lines.append(f'{key}: "{val}"')
            elif isinstance(val, bool):
                yaml_lines.append(f'{key}: {"true" if val else "false"}')
            elif isinstance(val, list):
                yaml_lines.append(f'{key}: {json.dumps(val, ensure_ascii=False)}')
            else:
                yaml_lines.append(f'{key}: {val}')
    yaml_lines.append("")
    yaml_lines.append("# Quality Metadata (Schema v2)")
    yaml_lines.append(f'content_version: {meta.get("content_version", 2)}')
    yaml_lines.append('quality_tier: "pending-rescore"')
    yaml_lines.append(f'quality_score: {meta.get("quality_score", 0)}')
    yaml_lines.append('generation_method: "research-rewrite-v2"')
    yaml_lines.append(f'unique_content_ratio: {meta.get("unique_content_ratio", 0)}')
    yaml_lines.append(f'last_scored: "{datetime.now().strftime("%Y-%m-%d")}"')
    yaml_lines.append("")
    yaml_lines.append("sources:")
    for src in info["sources"]:
        yaml_lines.append(f'  - type: "{src["type"]}"')
        yaml_lines.append(f'    ref: "{src["ref"]}"')
        yaml_lines.append(f'    url: "{src["url"]}"')
    yaml_lines.append("---")
    new_content = "\n".join(yaml_lines) + "\n" + info["body"].strip() + "\n"
    rag_file.write_text(new_content, encoding="utf-8")
    return True

def main():
    print(f"Biology Batch Rewrite - {len(concepts)} concepts")
    print("=" * 60)
    success = 0
    for cid, info in concepts.items():
        print(f"\n[{cid}]")
        if write_back(cid, info):
            success += 1
            print("  OK")
        else:
            print("  FAILED")
    print(f"\n{'='*60}")
    print(f"Done: {success}/{len(concepts)} written")
    log_path = PROJECT / "data" / "research_rewrite_log.json"
    log = []
    if log_path.is_file():
        with open(log_path, "r", encoding="utf-8") as f:
            log = json.load(f)
    for cid, info in concepts.items():
        log.append({
            "concept_id": cid, "domain": info["domain"],
            "timestamp": datetime.now().isoformat(),
            "sources_count": len(info["sources"]),
            "generation_method": "research-rewrite-v2",
            "batch": "biology-batch-1"
        })
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"Log updated: {log_path}")

if __name__ == "__main__":
    main()
