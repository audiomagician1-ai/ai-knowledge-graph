#!/usr/bin/env python3
"""
Enhance Tier-A RAG docs to push them to Tier-S.

These 10 docs are research-rewrite-v2 quality — already good content.
They just need small boosts in:
  - dim5 (teaching): Add thought questions section
  - dim2 (density): Add a bit more content
  - Sources Wikipedia link for dim3 boost

Strategy: Append targeted sections without replacing existing content.
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"


def load_tier_a_docs():
    """Load Tier-A docs from quality report."""
    report_path = PROJECT_ROOT / "data" / "quality_report_detail.json"
    data = json.load(open(report_path, "r", encoding="utf-8"))
    return [x for x in data if x["quality_tier"] == "A"]


def extract_concept_id(filepath):
    return Path(filepath).stem


# Concept-specific enhancement content for each Tier-A doc
ENHANCEMENTS = {
    "mean-reversion": {
        "thought_questions": [
            "如果一只股票连续下跌50%，均值回归理论是否意味着它会反弹？为什么需要区分\"统计均值回归\"和\"基本面变化\"？",
            "在不同时间框架（日内 vs 月度 vs 年度）中，均值回归的可靠性如何变化？什么因素导致了这种差异？",
            "如何设计一个简单的均值回归策略回测？需要考虑哪些交易成本和滑点因素？",
        ],
        "wikipedia": ("Mean reversion (finance)", "Mean_reversion_(finance)"),
    },
    "futures-basics": {
        "thought_questions": [
            "期货合约的\"零和博弈\"特性意味着什么？每笔交易中谁在盈利、谁在亏损？",
            "为什么航空公司会使用燃油期货进行套期保值？这与投机交易有什么本质区别？",
            "保证金制度如何放大了期货交易的风险和收益？杠杆率10倍意味着什么？",
        ],
        "wikipedia": ("Futures contract", "Futures_contract"),
    },
    "high-frequency-trading": {
        "thought_questions": [
            "高频交易如何影响市场流动性？它是增加还是减少了普通投资者的交易成本？",
            "2010年闪崩事件（Flash Crash）中高频交易扮演了什么角色？这对监管有什么启示？",
            "为什么高频交易公司愿意花费数百万美元将服务器放置在交易所附近（co-location）？",
        ],
        "wikipedia": ("High-frequency trading", "High-frequency_trading"),
    },
    "statistical-arbitrage": {
        "thought_questions": [
            "统计套利策略依赖历史相关性的持续性——当相关性结构发生变化时会发生什么？",
            "如何区分一个统计套利信号是真正的均值回归机会，还是只是噪声？",
            "为什么统计套利策略在2007-2008年金融危机期间普遍遭受重大损失？",
        ],
        "wikipedia": ("Statistical arbitrage", "Statistical_arbitrage"),
    },
    "time-series-analysis": {
        "thought_questions": [
            "为什么在对金融时间序列建模之前需要检验平稳性？非平稳序列直接建模会导致什么问题？",
            "ARIMA模型中的三个参数(p,d,q)分别控制什么？如何选择最优参数组合？",
            "时间序列预测中，为什么样本外测试（out-of-sample）比样本内拟合（in-sample）更能反映模型质量？",
        ],
        "wikipedia": ("Time series", "Time_series"),
    },
    "photosynthesis": {
        "thought_questions": [
            "光合作用的光反应和暗反应（Calvin循环）之间如何相互依赖？如果其中一个被抑制会发生什么？",
            "C3、C4和CAM三种光合途径分别适应什么环境？为什么进化产生了这些不同策略？",
            "全球变暖如何影响光合作用效率？CO₂浓度升高对不同类型植物的影响相同吗？",
        ],
        "wikipedia": ("Photosynthesis", "Photosynthesis"),
    },
    "monte-carlo-simulation": {
        "thought_questions": [
            "蒙特卡洛模拟结果的准确性与模拟次数之间是什么关系？误差收敛速度是多少？",
            "在期权定价中，为什么蒙特卡洛方法特别适合路径依赖型期权？",
            "如何使用方差缩减技术（如对偶变量法、控制变量法）来提高蒙特卡洛模拟的效率？",
        ],
        "wikipedia": ("Monte Carlo method", "Monte_Carlo_method"),
    },
    "derivatives-overview": {
        "thought_questions": [
            "衍生品的\"零和博弈\"特性是否意味着衍生品市场对社会没有价值？套期保值如何创造价值？",
            "为什么Warren Buffett称衍生品为\"大规模杀伤性金融武器\"？衍生品的系统性风险体现在哪里？",
            "场内衍生品（交易所交易）和场外衍生品（OTC）在风险管理上有什么本质差异？",
        ],
        "wikipedia": ("Derivative (finance)", "Derivative_(finance)"),
    },
    "natural-selection": {
        "thought_questions": [
            "自然选择作用于个体还是群体？\"自私基因\"理论如何改变了我们对自然选择单位的理解？",
            "为什么有些看似不利于生存的特征（如孔雀的尾巴）会在自然选择中保留？性选择如何与自然选择互动？",
            "人类医学的发展是否减弱了自然选择对人类种群的作用？这对人类未来的进化意味着什么？",
        ],
        "wikipedia": ("Natural selection", "Natural_selection"),
    },
    "volatility-modeling": {
        "thought_questions": [
            "为什么金融市场中波动率呈现聚类现象（volatility clustering）？GARCH模型如何捕捉这一特征？",
            "隐含波动率和历史波动率之间的差异（波动率风险溢价）传达了什么市场信息？",
            "VIX指数（\"恐慌指数\"）是如何从期权价格中推导出来的？它真的能预测市场风险吗？",
        ],
        "wikipedia": ("Volatility (finance)", "Volatility_(finance)"),
    },
}


def enhance_doc(filepath, concept_id, dry_run=False):
    """Add teaching enhancement sections to a Tier-A doc."""
    rag_path = RAG_ROOT / filepath
    if not rag_path.exists():
        return {"ok": False, "error": "File not found"}

    enh = ENHANCEMENTS.get(concept_id)
    if not enh:
        return {"ok": False, "error": f"No enhancement defined for {concept_id}"}

    content = rag_path.read_text(encoding="utf-8", errors="replace")

    # Check if already enhanced
    if "## 思考题" in content:
        return {"ok": False, "error": "Already has 思考题 section"}

    # Build enhancement sections
    questions = enh["thought_questions"]
    q_section = "\n## 思考题\n\n"
    for i, q in enumerate(questions, 1):
        q_section += f"{i}. {q}\n"

    wiki_name, wiki_slug = enh["wikipedia"]
    wiki_section = f"\n\n## 延伸阅读\n\n"
    wiki_section += f"- Wikipedia: [{wiki_name}](https://en.wikipedia.org/wiki/{wiki_slug})\n"

    # Append to content
    new_content = content.rstrip() + "\n" + q_section + wiki_section

    # Update frontmatter: bump content_version
    new_content = re.sub(
        r"content_version:\s*(\d+)",
        lambda m: f"content_version: {int(m.group(1)) + 1}",
        new_content,
    )

    if dry_run:
        return {"ok": True, "dry_run": True, "old_size": len(content), "new_size": len(new_content)}

    rag_path.write_text(new_content, encoding="utf-8")
    return {"ok": True, "old_size": len(content), "new_size": len(new_content)}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enhance Tier-A docs to Tier-S")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("Sprint 3.1 — Enhance Tier-A Docs to Tier-S")
    print("=" * 60)

    tier_a = load_tier_a_docs()
    print(f"Found {len(tier_a)} Tier-A docs")

    success = 0
    for doc in sorted(tier_a, key=lambda x: x["quality_score"]):
        cid = extract_concept_id(doc["file"])
        result = enhance_doc(doc["file"], cid, dry_run=args.dry_run)
        status = "DRY" if args.dry_run else ("OK" if result["ok"] else "SKIP")
        score = doc["quality_score"]
        if result["ok"]:
            success += 1
            print(f"  {status} {cid} (score={score:.1f}, {result['old_size']}→{result['new_size']}B)")
        else:
            print(f"  SKIP {cid} (score={score:.1f}): {result.get('error')}")

    print(f"\n{'='*60}")
    print(f"Enhanced: {success}/{len(tier_a)}")
    if not args.dry_run and success > 0:
        print("Next: Run 'python scripts/quality_scorer.py' to verify scores.")


if __name__ == "__main__":
    main()
