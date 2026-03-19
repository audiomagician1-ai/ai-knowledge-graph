#!/usr/bin/env python3
"""Generate RAG teaching documents for the Physics knowledge sphere.

Creates one markdown file per concept with LaTeX formulas.
"""

import json
import os
from datetime import datetime

NOW = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_PATH = os.path.join(SCRIPT_DIR, "..", "..", "seed", "physics", "seed_graph.json")

# Subdomain-specific physics templates with LaTeX formulas
TEMPLATES = {
    "physical-quantities": """## 核心内容

**物理量**是用来描述物理现象的可测量属性。每个物理量都有**量纲**和**单位**。

**国际单位制（SI）**的七个基本单位：
- 长度: 米 (m)
- 质量: 千克 (kg)
- 时间: 秒 (s)
- 电流: 安培 (A)
- 温度: 开尔文 (K)
- 物质的量: 摩尔 (mol)
- 发光强度: 坎德拉 (cd)

**量纲分析**可以验证公式的正确性：方程两边的量纲必须一致。例如 $v = \\sqrt{2gh}$，左边量纲为 $[LT^{-1}]$，右边 $\\sqrt{[LT^{-2}][L]} = \\sqrt{[L^2T^{-2}]} = [LT^{-1}]$ ✓

**有效数字**规则确保测量精度的正确表达。""",

    "newtons-second-law": """## 核心内容

**牛顿第二定律**是经典力学的基石：
$$\\vec{F}_{\\text{net}} = m\\vec{a}$$

即物体的加速度与作用在其上的合力成正比，与其质量成反比。

**关键要点**：
1. $\\vec{F}_{\\text{net}}$ 是所有力的**矢量和**
2. 加速度方向与合力方向相同
3. 质量 $m$ 是惯性的度量

**自由体图**分析步骤：
- 隔离研究对象
- 画出所有外力（重力、法向力、摩擦力、张力等）
- 选择坐标系，分解力到各轴
- 列方程：$\\sum F_x = ma_x$，$\\sum F_y = ma_y$

**应用**：$F = ma$ 可以用来分析从简单的滑块到复杂的行星运动等各种问题。""",

    "energy-conservation": """## 核心内容

**机械能守恒定律**：在只有保守力做功的系统中，动能与势能之和不变。
$$E_{\\text{mech}} = K + U = \\text{const}$$

$$\\frac{1}{2}mv_1^2 + U_1 = \\frac{1}{2}mv_2^2 + U_2$$

**保守力**的特征：做功只取决于初末位置，与路径无关（如重力、弹力）。

**非保守力**（如摩擦力）会导致机械能耗散：
$$\\Delta E_{\\text{mech}} = W_{\\text{non-conservative}}$$

**功能关系**更一般地表述为：
$$W_{\\text{ext}} = \\Delta K + \\Delta U + \\Delta E_{\\text{thermal}}$$""",

    "schrodinger-equation": """## 核心内容

**薛定谔方程**是量子力学的核心方程，描述量子态的时间演化。

**含时薛定谔方程**：
$$i\\hbar\\frac{\\partial}{\\partial t}\\Psi(\\vec{r},t) = \\hat{H}\\Psi(\\vec{r},t)$$

其中 $\\hat{H}$ 是哈密顿算符：
$$\\hat{H} = -\\frac{\\hbar^2}{2m}\\nabla^2 + V(\\vec{r},t)$$

**定态薛定谔方程**（当势能不显含时间时）：
$$\\hat{H}\\psi(\\vec{r}) = E\\psi(\\vec{r})$$

**关键概念**：
- $|\\Psi(\\vec{r},t)|^2$ 是概率密度
- 波函数必须**归一化**：$\\int|\\Psi|^2 d^3r = 1$
- 能量 $E$ 是哈密顿算符的**本征值**""",

    "maxwells-equations": """## 核心内容

**麦克斯韦方程组**统一了电磁理论，由四个方程组成：

**高斯电场定律**（电荷产生电场）：
$$\\nabla \\cdot \\vec{E} = \\frac{\\rho}{\\varepsilon_0}$$

**高斯磁场定律**（无磁单极子）：
$$\\nabla \\cdot \\vec{B} = 0$$

**法拉第定律**（变化的磁场产生电场）：
$$\\nabla \\times \\vec{E} = -\\frac{\\partial \\vec{B}}{\\partial t}$$

**安培-麦克斯韦定律**（电流和变化的电场产生磁场）：
$$\\nabla \\times \\vec{B} = \\mu_0\\vec{J} + \\mu_0\\varepsilon_0\\frac{\\partial \\vec{E}}{\\partial t}$$

麦克斯韦加入的**位移电流** $\\varepsilon_0\\frac{\\partial \\vec{E}}{\\partial t}$ 预言了电磁波的存在。""",

    "entropy": """## 核心内容

**熵**（Entropy）是热力学中度量系统无序度的核心概念。

**克劳修斯定义**：
$$dS = \\frac{\\delta Q_{\\text{rev}}}{T}$$

**熵增原理**（热力学第二定律的熵表述）：
$$\\Delta S_{\\text{universe}} \\geq 0$$

孤立系统的总熵只增不减，等号仅在可逆过程中成立。

**玻尔兹曼统计诠释**：
$$S = k_B \\ln \\Omega$$

其中 $\\Omega$ 是系统的微观状态数，$k_B = 1.38 \\times 10^{-23} \\text{ J/K}$ 是玻尔兹曼常数。

**意义**：熵给出了过程的**方向性**——自然过程总是向熵增的方向进行。""",

    "special-relativity-postulates": """## 核心内容

**狭义相对论**建立在两条基本公设之上：

**公设一：相对性原理**
> 物理定律在所有惯性参考系中形式相同。

**公设二：光速不变原理**
> 真空中的光速 $c = 3 \\times 10^8$ m/s 在所有惯性参考系中相同，与光源运动状态无关。

**推论**：
- 同时性是相对的
- 运动的时钟变慢（时间膨胀）：$\\Delta t = \\gamma \\Delta t_0$
- 运动的尺子变短（长度收缩）：$L = L_0/\\gamma$

其中**洛伦兹因子**：
$$\\gamma = \\frac{1}{\\sqrt{1 - v^2/c^2}}$$""",

    "band-theory": """## 核心内容

**能带理论**是解释固体电子行为的关键理论。

**布洛赫定理**：周期势场中电子的波函数为
$$\\psi_{\\vec{k}}(\\vec{r}) = e^{i\\vec{k}\\cdot\\vec{r}} u_{\\vec{k}}(\\vec{r})$$

其中 $u_{\\vec{k}}$ 具有晶格的周期性。

**能带结构**将固体分为三类：
| 类型 | 特征 |
|:---|:---|
| **导体** | 导带与价带重叠或导带未满 |
| **半导体** | 带隙 $E_g < 3$ eV |
| **绝缘体** | 带隙 $E_g > 3$ eV |

**费米能** $E_F$ 是绝对零度时最高被占据能级。

**费米-狄拉克分布**：
$$f(E) = \\frac{1}{e^{(E-E_F)/k_BT} + 1}$$""",
}

# Generic template for concepts without specific templates
def generic_template(concept, subdomain_name):
    diff = concept["difficulty"]
    tags_str = "、".join(concept["tags"])
    desc = concept["description"]
    name = concept["name"]
    milestone_str = "里程碑概念" if concept.get("is_milestone") else "概念"

    # Physics-specific LaTeX content based on subdomain
    subdomain_id = concept["subdomain_id"]
    physics_hints = {
        "classical-mechanics": f"在经典力学中，{name}涉及力与运动的关系。牛顿力学的基本框架为 $\\vec{{F}} = m\\vec{{a}}$，能量守恒 $E_k + E_p = \\text{{const}}$。",
        "thermodynamics": f"在热力学中，{name}与能量转化和熵的概念密切相关。基本关系为 $dU = \\delta Q - \\delta W$，熵变 $dS \\geq \\delta Q/T$。",
        "waves-and-optics": f"在波动光学中，{name}涉及波的传播与干涉。波动方程 $\\frac{{\\partial^2 y}}{{\\partial t^2}} = v^2\\frac{{\\partial^2 y}}{{\\partial x^2}}$。",
        "electromagnetism": f"在电磁学中，{name}属于Maxwell方程组的框架。电场 $\\vec{{E}}$ 和磁场 $\\vec{{B}}$ 通过 $\\nabla \\times \\vec{{E}} = -\\frac{{\\partial \\vec{{B}}}}{{\\partial t}}$ 关联。",
        "modern-physics": f"在近代物理中，{name}涉及量子假说与相对论。关键关系包括 $E = h\\nu$、$E = mc^2$、$\\lambda = h/p$。",
        "quantum-mechanics": f"在量子力学中，{name}通过波函数 $\\Psi$ 和算符描述。基本方程为 $i\\hbar\\frac{{\\partial\\Psi}}{{\\partial t}} = \\hat{{H}}\\Psi$。",
        "nuclear-physics": f"在核物理中，{name}涉及原子核结构与衰变。质量亏损 $\\Delta m$ 对应结合能 $E_B = \\Delta m \\cdot c^2$。",
        "astrophysics": f"在天体物理中，{name}涉及恒星与宇宙的演化。引力势能 $U = -GMm/r$，光度 $L = 4\\pi R^2\\sigma T^4$。",
        "fluid-mechanics": f"在流体力学中，{name}描述流体的运动规律。连续性方程 $\\rho_1 A_1 v_1 = \\rho_2 A_2 v_2$，伯努利方程 $P + \\frac{{1}}{{2}}\\rho v^2 + \\rho gh = \\text{{const}}$。",
        "solid-state-physics": f"在固态物理中，{name}涉及晶体中电子与声子行为。布洛赫波函数 $\\psi_k(r) = e^{{ikr}}u_k(r)$。",
    }

    physics_content = physics_hints.get(subdomain_id, f"在物理学中，{name}是一个重要的基础概念。")

    return f"""## 概述

{name}是{subdomain_name}领域中的{milestone_str}，难度等级为 {diff}/9。

{desc}

## 核心内容

{physics_content}

### 关键要点

1. **基本定义**: {desc}
2. **物理意义**: {name}在物理学体系中具有重要地位
3. **数学表达**: 物理概念通过精确的数学公式来描述

### 学习建议

- 理解概念的物理意义，不要仅停留在数学公式
- 通过具体实例和实验来加深理解
- 注意与相关概念的联系与区别

## 常见误区

- 混淆{name}与相近概念的区别
- 忽视适用条件和范围限制
- 仅记忆公式而不理解物理本质

## 与相邻概念的关联

{name}在物理知识体系中与多个概念相互关联，建议结合相关前置知识一起学习。"""


def generate_rag_docs():
    """Generate one .md file per concept."""
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        seed = json.load(f)

    concepts = seed["concepts"]
    subdomains = {s["id"]: s["name"] for s in seed["subdomains"]}

    index = {"version": "1.0.0", "domain_id": "physics", "generated_at": NOW, "total_concepts": 0, "documents": [], "stats": {"total_docs": 0, "by_subdomain": {}}}
    total = 0

    for concept in concepts:
        cid = concept["id"]
        sub_id = concept["subdomain_id"]
        sub_name = subdomains.get(sub_id, sub_id)

        # Create subdomain directory
        sub_dir = os.path.join(SCRIPT_DIR, sub_id)
        os.makedirs(sub_dir, exist_ok=True)

        # Pick template
        if cid in TEMPLATES:
            body = TEMPLATES[cid]
        else:
            body = generic_template(concept, sub_name)

        # Build frontmatter
        frontmatter = f"""---
id: "{cid}"
name: "{concept['name']}"
subdomain: "{sub_id}"
subdomain_name: "{sub_name}"
difficulty: {concept['difficulty']}
is_milestone: {str(concept.get('is_milestone', False)).lower()}
tags: {json.dumps(concept['tags'], ensure_ascii=False)}
generated_at: "{NOW}"
---"""

        content = f"""{frontmatter}

# {concept['name']}

{body}
"""

        # Write file
        filepath = os.path.join(sub_dir, f"{cid}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # Update index
        index["documents"].append({
            "id": cid,
            "name": concept["name"],
            "domain_id": "physics",
            "subdomain_id": sub_id,
            "subdomain_name": sub_name,
            "difficulty": concept["difficulty"],
            "is_milestone": concept.get("is_milestone", False),
            "tags": concept["tags"],
            "file": f"physics/{sub_id}/{cid}.md",
            "exists": True,
            "char_count": len(content),
        })
        index["stats"]["by_subdomain"][sub_id] = index["stats"]["by_subdomain"].get(sub_id, 0) + 1
        total += 1

    index["stats"]["total_docs"] = total
    index["total_concepts"] = total

    # Write index
    index_path = os.path.join(SCRIPT_DIR, "_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated {total} RAG documents for physics domain")
    print(f"✅ Index written to {index_path}")
    for sub_id, count in sorted(index["stats"]["by_subdomain"].items()):
        print(f"   {sub_id}: {count} docs")


if __name__ == "__main__":
    generate_rag_docs()
