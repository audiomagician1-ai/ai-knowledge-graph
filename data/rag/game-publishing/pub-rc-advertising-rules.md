---
id: "pub-rc-advertising-rules"
concept: "广告合规"
domain: "game-publishing"
subdomain: "rating-compliance"
subdomain_name: "评级/合规"
difficulty: 4
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 广告合规

## 概述

广告合规（Advertising Compliance）是指游戏发行商在营销推广活动中，必须遵循各国法律法规与行业自律规范，确保广告内容真实反映游戏实际体验的一整套强制性要求。其核心约束在于：游戏广告不得以预渲染CG演示视频、经专业美术修改的精选截图、或无法在实际游玩中复现的数值描述来影响玩家的消费决策。

**关键历史节点**：2012年，美国联邦贸易委员会（FTC）对Zynga、DeNA等手机游戏商发出正式执法警告，要求所有手机游戏广告必须清晰披露内购机制及价格上限，这是游戏广告合规监管史上具有里程碑意义的转折点。此后，欧盟《不公平商业行为指令》（UCPD，2005/29/EC）将游戏内购广告纳入消费者保护框架；英国广告标准局（ASA）于2019年明令禁止使用与实际游戏画面存在实质性差异的宣传素材（参见 ASA Ruling on Plarium Global Ltd, 2019）。2021年，Roblox因广告素材未清晰披露虚拟货币Robux与真实货币1:80换算比例，在荷兰、比利时等多个欧洲市场受到监管调查，最终支付超过300万欧元的和解金。

违规代价已形成可量化的行业风险：单次违规罚款范围从数万美元（FTC行政处罚）到营收总额的4%（GDPR框架下的连带处罚）不等；Google Play和苹果App Store对违规广告主实行"三振出局"下架机制，第三次违规将永久封禁开发者账户。

参考文献：Preston, I. L. (1994). *The Tangled Web They Weave: Truth, Falsity, and Advertisers*. University of Wisconsin Press；以及《互联网广告管理办法》（国家市场监督管理总局，2023年修订版）。

---

## 核心原理

### 真实性原则：实质性表述的法律边界

游戏广告合规的第一基础是**实质性表述原则**（Material Representation Doctrine），源自FTC Act第5条款。其判断标准为：若广告中某一表述对理性消费者的购买决策产生实质影响，则该表述必须准确无误。具体到游戏广告，FTC合规指引（FTC Guides Concerning the Use of Endorsements and Testimonials, 16 CFR Part 255）明确要求：

- 广告展示的战斗画面、画面质量、游戏节奏必须来源于**实际游玩录屏**，而非专用宣传CG；
- 苹果App Store和Google Play的开发者协议均要求广告主保留"广告素材与实际游戏相符"的证明材料**至少24个月**；
- 展示角色外观时，若该外观仅能通过充值1000元人民币以上的内购包获得，广告必须以清晰字体注明获取条件。

**典型违规案例**：2020年，战略游戏《Rise of Kingdoms》因广告素材中的城池渲染画质与实际手机端游戏相差超过300%的多边形密度，被英国ASA裁定违反CAP准则第3.1条（广告不得产生误导），被要求在48小时内撤回全部英国区域广告素材共计17组。2022年，《Homescapes》开发者Playrix因持续使用"广告玩法与实际游戏无关"的素材在Google广告平台被下架超过4000组广告创意。

### 概率披露：抽卡与战利品箱的透明度硬性要求

任何含有战利品箱（Loot Box）、抽卡池、随机奖励箱等概率性付费机制的游戏，广告中必须满足以下**强制披露义务**：

**中国监管框架**：国家新闻出版署于2017年发布《关于移动游戏不良内容及欺诈行为整治的通知》，要求所有涉及随机道具的广告画面必须注明"道具获取概率以游戏内公示页面为准"，且该声明文字高度不得低于广告画面最大字体的**60%**。2023年修订的《互联网广告管理办法》第12条进一步规定，包含概率性内容的游戏广告若在30天内投放规模超过100万次曝光，须向平台提交经第三方审计的概率公示报告。

**韩国监管框架**：《游戏产业振兴法》（게임산업진흥에 관한 법률）第33条第2款要求，所有含概率道具的游戏广告必须直接标注警示语：**"이 게임은 유료 확률형 아이템을 포함하고 있습니다"**（本游戏含有付费概率性道具），字体颜色须与背景色形成至少**4.5:1**的对比度（符合WCAG 2.1 AA标准）。

**欧洲通行合规公式**：广告中若展示某稀有道具，须同时显示：

$$P(\text{单次获得目标道具}) \leq X\%$$

其中 $X$ 必须为经过独立审计机构（如SGS、iTech Labs）验证的真实概率值，广告画面中该数值的字体尺寸不得小于正文字体的**80%**，且须持续展示不少于**3秒**（视频广告）或以固定文字形式出现（图文广告）。

### 面向未成年人的广告定向限制

基于前置概念**年龄验证**所建立的用户年龄数据，游戏广告的投放系统必须实施严格的年龄过滤机制：

英国ASA的CAP准则**第16.1条**明确禁止在13岁以下用户为主要受众（>25%）的媒体平台投放任何鼓励内购消费的游戏广告。美国儿童在线隐私保护法（COPPA）对13岁以下用户的广告定向收集行为设定了单次违规最高**51,744美元**（2023年调整值）的处罚上限。

广告投放系统中，年龄定向（Age-gating）的合规设置必须使用**已知年龄数据**（Known Age Data，即用户主动填写并经验证的年龄），而非基于行为推断的预测年龄（Inferred Age）。以下文案类型在面向未成年用户时属于各辖区**明确禁止**的诱导性商业行为（参见 EU UCPD Annex I, Blacklisted Practices）：

- 人为制造紧迫感："限时24小时""今日专属""错过不再有"
- 虚假社交压力："你的好友已获得此道具"（若系统无法实际核实）
- 奖励混淆："完成任务即可免费获得"（实为需内购激活的伪免费机制）

---

## 关键公式与合规检测算法

游戏广告合规审查中，可用以下**广告素材合规评分模型**进行系统化预审：

```python
def ad_compliance_score(ad_creative: dict) -> dict:
    """
    游戏广告合规评分模型（基于FTC/ASA/中国互联网广告管理办法三地标准）
    
    参数说明：
    - ad_creative['gameplay_authentic']: bool，广告画面是否来源于真实游玩录屏
    - ad_creative['probability_disclosed']: float，概率披露字体占比（0~1）
    - ad_creative['target_age_min']: int，定向投放最低年龄
    - ad_creative['urgency_language']: bool，是否含有紧迫感诱导文案
    - ad_creative['loot_box_present']: bool，是否含概率道具内容
    """
    score = 100
    issues = []

    # 规则1：真实性原则（FTC 16 CFR Part 255）
    if not ad_creative.get('gameplay_authentic', False):
        score -= 40
        issues.append("CRITICAL: 广告素材非实际游玩画面，违反FTC实质性表述原则")

    # 规则2：概率披露要求（中国《互联网广告管理办法》第12条）
    prob_ratio = ad_creative.get('probability_disclosed', 0)
    if ad_creative.get('loot_box_present', False):
        if prob_ratio < 0.60:
            score -= 30
            issues.append(f"概率披露字体占比{prob_ratio:.0%}，低于中国标准要求的60%")
        elif prob_ratio < 0.80:
            score -= 10
            issues.append(f"概率披露字体占比{prob_ratio:.0%}，低于欧洲标准要求的80%")

    # 规则3：未成年人保护（CAP准则16.1条）
    if ad_creative.get('target_age_min', 18) < 13:
        if ad_creative.get('urgency_language', False):
            score -= 25
            issues.append("CRITICAL: 面向13岁以下用户使用紧迫感诱导文案，违反CAP 16.1")

    return {
        'compliance_score': max(score, 0),
        'pass': score >= 70,
        'issues': issues
    }

# 示例：检测一个含抽卡机制但使用CG画面的广告素材
result = ad_compliance_score({
    'gameplay_authentic': False,
    'loot_box_present': True,
    'probability_disclosed': 0.55,
    'target_age_min': 12,
    'urgency_language': True
})
# 输出: {'compliance_score': 5, 'pass': False, 'issues': [3项违规]}
```

此模型对应三地核心法规的权重分配：真实性原则违规扣40分（最高权重，因属主动欺骗），概率披露不足最高扣30分，未成年人诱导扣25分，其余条款各扣5分，总分低于70分即判定广告素材不可上线投放。

---

## 实际应用：地域差异合规矩阵

游戏发行商在全球市场投放广告时，必须按地域建立独立的合规操作矩阵，主要差异对比如下：

| 辖区 | 主管机构 | 核心要求 | 违规最高处罚 |
|------|---------|---------|------------|
| 美国 | FTC | 网红推广须标注 #AD；赔偿性广告须有实质依据 | 单次 $51,744（COPPA）|
| 欧盟 | 各国NCA + EDPB | DSA要求广告算法逻辑对用户透明；战利品箱等同赌博须特别披露 | 营收4%（DSA第26条）|
| 英国 | ASA + CMA | CAP准则禁止画面误导；竞争与市场管理局2022年对游戏内购虚假宣传立案 | 无限额民事索赔 |
| 中国 | 国家市场监督管理总局 | 广告中"开始游戏"按钮须与广告内容视觉区分；概率强制披露 | 广告费用3倍以上罚款 |
| 韩国 | 游戏物管理委员会 | 广告须标注概率道具警示语；对比广告须提交第三方验证数据 | 营业额2%以下罚款 |
| 日本 | JARO（日本广告审查机构）| 自律为主；手机游戏广告须遵循JOGA（日本网络游戏协会）自律指引第4版 | 行业除名+媒体拒绝刊播 |

**例如**，某款出海手机RPG同时在美国和中国市场投放含有10连抽机制的广告视频：在中国版本中，视频第3~7秒必须固定显示"SSR角色获取概率：0.7%（含保底机制详见游戏内公告）"，字体高度须达到画面最大字体的60%以上；而在美国版本中，同一广告须在视频片尾加注"Odds of featured character: 0.7%. Pity system activates at 90 pulls."，并在Google Ads后台将年龄定向下限设置为17岁（对应ESRB T级以上游戏）。

---

## 常见误区

### 误区一：使用"仅供演示"免责声明可规避虚假宣传责任

许多发行商误认为在广告画面角落标注"画面仅供演示，实际效果以游戏内容为准"即可免责。FTC和ASA的一致立场是：**免责声明不能抵消广告主体内容的误导效果**。ASA在2019年对《Game of War》裁决中明确指出，若广告主体画面已对玩家形成强烈的错误认知，角落的小字免责声明在法律效力上无效。合规做法是确保广告主体画面本身就来源于真实游玩，而非依赖事后声明补救。

### 误区二：KOL/