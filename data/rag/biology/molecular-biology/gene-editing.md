---
id: "gene-editing"
concept: "基因编辑"
domain: "biology"
subdomain: "molecular-biology"
subdomain_name: "分子生物学"
difficulty: 4
is_milestone: false
tags: ["前沿"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 基因编辑

## 概述

基因编辑（Gene Editing）是指对生物体基因组特定位点进行精准碱基增添、删除或替换的分子生物学技术。与20世纪的随机诱变育种（X射线照射、化学诱变剂EMS处理）根本不同，现代基因编辑可在人类基因组约32亿碱基对中精确定位并修改单个核苷酸，错误率可低至0.1%以下。

2012年，Jennifer Doudna（加州大学伯克利分校）与 Emmanuelle Charpentier（马克斯·普朗克研究所）在《Science》杂志发表题为"A Programmable Dual-RNA–Guided DNA Endonuclease in Adaptive Bacterial Immunity"的论文，首次证明 CRISPR-Cas9 系统可作为体外可编程基因组编辑工具（Jinek et al., 2012）。两人因此于2020年共同获得诺贝尔化学奖，是该奖项历史上首次由两名女性共同获奖。

在成本与效率维度，CRISPR-Cas9 实现了质的飞跃：锌指核酸酶（ZFN）时代设计一对新型 ZFN 需耗资约5万美元、历时3~6个月；CRISPR 将这一成本压缩至200美元以内、时间缩短至1~2周。这一变化使全球超过10,000个实验室将基因编辑纳入常规实验流程，发表的 CRISPR 相关论文数量从2013年的不足100篇增长至2022年的逾25,000篇。

---

## 核心原理

### CRISPR-Cas9 的分子机制

CRISPR（Clustered Regularly Interspaced Short Palindromic Repeats，成簇规律间隔短回文重复序列）最初于1987年由日本科学家石野良純在研究大肠杆菌碱性磷酸酶基因时偶然发现，2005年 Ruud Jansen 正式命名该序列。其天然功能是细菌和古菌的适应性免疫系统——当病毒入侵时，细菌将病毒 DNA 片段整合到自身 CRISPR 阵列中作为"记忆"，再次感染时通过 Cas 蛋白切割病毒 DNA。

Cas9 是来源于化脓性链球菌（*Streptococcus pyogenes*，SpCas9）的 RNA 引导核酸内切酶，分子量约158 kDa，包含两个独立核酸酶结构域：**RuvC 结构域**切割非互补链，**HNH 结构域**切割互补链。整个切割机制依赖一条人工合成的**单链向导 RNA（sgRNA）**，由约100个核苷酸组成，可分为：

- **间隔区（Spacer）**：5'端约20个核苷酸，与靶 DNA 互补配对，决定切割特异性。
- **支架区（Scaffold）**：模拟天然 crRNA:tracrRNA 双链结构，形成茎环，与 Cas9 蛋白结合。

靶位点的识别还依赖**PAM 序列（Protospacer Adjacent Motif）**：SpCas9 要求靶序列3'端紧邻 5'-NGG-3' 三联体。切割位点位于 PAM 上游第3个碱基处，产生平末端双链断裂（Blunt-end DSB）。这一限制意味着，在人类基因组中约每8 bp 即出现一个可用的 NGG-PAM 位点，覆盖度相当高。

### 两种主要 DNA 修复途径

双链断裂（DSB）发生后，细胞通过两条竞争性途径完成修复，编辑者可利用这种竞争关系实现不同编辑目标：

**非同源末端连接（NHEJ，Non-Homologous End Joining）**：细胞在无需模板的情况下直接将断裂末端重新连接，过程中由 Ku70/Ku80 异二聚体识别并保护断端，DNA-PKcs 激活后招募 Artemis 核酸酶进行末端加工，最终由 DNA 连接酶IV/XRCC4 完成连接。此过程极易在断口处产生随机插入或缺失（InDel），长度通常为1~20 bp，导致移码突变（frameshift），从而**敲除**目标基因的开放阅读框。NHEJ 在细胞周期全程均可发生，效率可达90%以上。

**同源定向修复（HDR，Homology-Directed Repair）**：当外源提供含有目标碱基改变的**供体模板（Donor Template）**——通常为含左右各500~1000 bp 同源臂的双链 DNA（dsDNA）或单链寡聚核苷酸（ssODN）——细胞可精确复制模板序列，实现特定碱基替换或外源基因敲入。HDR 效率在细胞类型和周期阶段差异显著，分裂旺盛的细胞系（如HEK293T）可达5%~10%，原代细胞（如造血干细胞）通常低于1%，且仅限 S/G2 期。

### 第二代与第三代精准编辑工具

为规避双链断裂带来的细胞毒性和大片段基因组重排风险，David Liu 团队（Broad Institute）先后开发了两类重要衍生工具：

**碱基编辑器（Base Editor，BE）**（Komor et al., 2016）：将切口酶 nCas9（D10A 突变，仅切割非互补链）与脱氨酶融合，无需 DSB 即可直接化学修饰碱基：
- **胞嘧啶碱基编辑器（CBE）**：nCas9 融合 APOBEC1 脱氨酶，将靶窗口（PAM 上游第4~8位）内 C 脱氨为 U，经错配修复后实现 **C·G → T·A** 转换，效率可达15%~75%。
- **腺嘌呤碱基编辑器（ABE）**：nCas9 融合进化改造的 TadA 脱氨酶，将 A 脱氨为 I（次黄嘌呤），实现 **A·T → G·C** 转换，是目前已知效率最高的单碱基替换工具。

**先导编辑（Prime Editing，PE）**（Anzalone et al., 2019）：使用 pegRNA（先导编辑向导 RNA，同时携带引物结合位点和编辑模板）与逆转录酶-nCas9 融合蛋白。系统首先切割非互补链，以 pegRNA 3'端的 RT 模板为蓝本进行逆转录，将含目标改变的新链整合回基因组。理论上可实现全部12种碱基置换及最长约44 bp 的精确插入和缺失，被 David Liu 本人描述为"基因组的搜索与替换（Search-and-Replace）"功能。

---

## 关键公式与算法

### 编辑效率的定量计算

基因编辑实验完成后，通常通过**深度测序（Amplicon Deep Sequencing）**统计各等位基因的编辑情况，NHEJ 效率用以下公式表示：

$$\text{Editing efficiency (\%)} = \frac{\text{reads with InDel}}{\text{total reads}} \times 100\%$$

**脱靶评分（Off-target Score）**通常采用 MIT 评分模型（Hsu et al., 2013），综合考虑 sgRNA 各位点的错配权重：

$$S_{\text{guide}} = \prod_{i=1}^{N} \left(1 - e_i\right) \times \frac{1}{\frac{19}{19-d_{\text{mean}}} \cdot n + 1}$$

其中 $e_i$ 为第 $i$ 位错配惩罚系数，$d_{\text{mean}}$ 为错配间平均距离，$n$ 为脱靶位点总数。实践中可使用 Benchling、CRISPOR 或 CRISPRscan 等在线工具快速计算全基因组潜在脱靶位点得分。

### sgRNA 设计的 Python 代码示例

以下代码展示如何在给定基因组序列中搜索所有 NGG-PAM 位点并提取候选 sgRNA：

```python
def find_sgrna_candidates(sequence, guide_length=20):
    """
    在给定DNA序列中搜索所有NGG-PAM位点，
    返回候选sgRNA列表（PAM上游20 nt）。
    """
    candidates = []
    sequence = sequence.upper()
    for i in range(len(sequence) - guide_length - 2):
        pam = sequence[i + guide_length: i + guide_length + 3]
        if pam[1:] == "GG":   # 匹配N-G-G
            guide = sequence[i: i + guide_length]
            gc_content = (guide.count("G") + guide.count("C")) / guide_length
            if 0.40 <= gc_content <= 0.80:  # GC含量过滤：40%~80%
                candidates.append({
                    "position": i,
                    "guide_seq": guide,
                    "pam": pam,
                    "gc": round(gc_content * 100, 1)
                })
    return candidates

# 示例：在HBB基因第6密码子附近搜索
hbb_fragment = "ATGGTGCACCTGACTCCTGAGGAGAAGTCTGCCGTTACTGCCCTGTGGGGCAAGGTG"
results = find_sgrna_candidates(hbb_fragment)
for r in results:
    print(f"位置{r['position']}: {r['guide_seq']} | PAM: {r['pam']} | GC: {r['gc']}%")
```

GC 含量建议控制在40%~70%区间；sgRNA 5'端是否为 G 也会影响 U6 启动子驱动的转录效率。

---

## 实际应用

### 遗传性血液病治疗：首个获批临床应用

镰刀型细胞贫血症（SCD）和 β-地中海贫血的根本原因分别是 HBB 基因第6位密码子 GAG→GTG 错义突变（Glu6Val）和 HBB 基因不同位置的功能缺失突变。研究者利用 CRISPR 靶向敲除 BCL11A 基因增强子区域（位于染色体2q16.1，红细胞特异性增强子+58位点），解除其对胎儿血红蛋白（HbF，γ-珠蛋白）的抑制，使患者红细胞中 HbF 水平从正常成人的<1%提升至30%~50%，从而补偿 HbB 缺陷。

2023年12月8日，FDA 正式批准 Vertex 制药与 CRISPR Therapeutics 联合开发的 **Casgevy（exa-cel，exagamglogene autotemcel）**，成为全球首款获批的 CRISPR 基因编辑疗法，用于治疗12岁及以上 SCD 和 β-地中海贫血患者。在关键临床试验中，接受治疗的29名重度 SCD 患者中28名在12个月随访期内完全无血管闭塞危象发作（VOC-free）；54名 β-地中海贫血患者中39名完全摆脱输血依赖，此疗法定价约220万美元/人。

### 农业育种：抗病与品质改良

2016年，宾夕法尼亚州立大学 Yiping Qi 团队利用 CRISPR 敲除蘑菇（*Agaricus bisporus*）中控制褐变的多酚氧化酶基因（PPO），使其货架期延长30%，该蘑菇成为全球首例获得美国农业部（USDA）豁免监管的 CRISPR 编辑农产品。2021年，日本京都大学 Yiigo Ezura 团队利用 CRISPR 敲除番茄 GABA 代谢通路中的 *SlGAD2* 和 *SlGAD3* 基因，培育出 GABA 含量是普通番茄5倍以上的"Sicilian Rouge High GABA"，2021年9月上市销售，是全球首款获准商业销售的 CRISPR 编辑食品。

### 癌症免疫治疗：CAR-T 细胞的通用化改造

异体 CAR-T 疗法需同时对供体 T 细胞进行多位点编辑：敲除 TCRα/β 链（避免移植物抗宿主病）、敲除 MHC-I 类分子 β₂m（逃避受者免疫排斥）、敲入 CAR 结构（靶向肿瘤抗原如 CD19 或 BCMA）。2022年，Intellia Therapeutics 报告使用体内（in vivo）CRISPR 给药方式（脂质纳米颗粒 LNP 递送），直接在患者