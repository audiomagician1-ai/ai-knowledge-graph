#!/usr/bin/env python3
"""
Enhance Tier-A RAG docs (Round 2) — Add case studies with example markers.

Round 1 added thought questions + Wikipedia links, pushing 4/10 to Tier-S.
Round 2 adds concrete case studies with explicit example markers
to boost dim5 (teaching) has_example dimension for remaining 6 docs.
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"

CASE_STUDIES = {
    "futures-basics": "\n### 实际案例\n\n例如，2020年4月WTI原油期货价格首次跌至负值（-37.63美元/桶），这是因为临近交割的多头持仓者无法找到储油设施，被迫以负价格出售合约。这个案例生动说明了期货合约到期交割机制的重要性——持有期货合约意味着到期时必须履行实物交割义务（除非提前平仓），这与股票投资有本质区别。\n",
    "high-frequency-trading": "\n### 实际案例\n\n例如，Knight Capital Group在2012年8月1日因交易软件故障，在45分钟内产生了约4.4亿美元的亏损。一个未正确部署的代码更新导致其系统以错误的价格大量买入卖出约150只股票。这个案例说明HFT系统的技术风险：当交易速度达到毫秒级时，任何软件错误都可能在极短时间内造成巨额损失。\n",
    "statistical-arbitrage": "\n### 实际案例\n\n例如，Long-Term Capital Management（LTCM）是统计套利策略失败的经典案例。1998年，LTCM运用高杠杆的债券配对交易策略，在俄罗斯债务危机引发全球市场恐慌时，原本相关的资产突然脱钩，价差不仅未收敛反而急剧扩大。LTCM的46亿美元资本几乎全部蒸发，最终需要美联储协调14家银行进行救助。这个案例揭示了统计套利策略在\"黑天鹅\"事件中的脆弱性。\n",
    "time-series-analysis": "\n### 实际案例\n\n例如，Box-Jenkins方法论在GDP预测中的应用：经济学家使用ARIMA模型对美国季度GDP增长率建模时，首先需要检验序列平稳性（ADF检验），发现原始GDP序列非平稳后取一阶差分(d=1)，然后通过ACF和PACF图选择p=2, q=1参数。经实证研究，ARIMA(2,1,1)模型对短期GDP预测的准确性通常优于简单趋势外推法。\n",
    "photosynthesis": "\n### 实际案例\n\n例如，C4植物（如玉米、甘蔗）进化出了特殊的碳浓缩机制来解决光呼吸问题。在C4植物中，CO2首先在叶肉细胞中被PEP羧化酶固定为四碳化合物（草酰乙酸），然后转运到维管束鞘细胞中释放CO2供Calvin循环使用。这种空间分离机制使C4植物在高温、高光照环境下的光合效率比C3植物高30-40%，这也解释了为什么热带地区的主要粮食作物多为C4植物。\n",
    "monte-carlo-simulation": "\n### 实际案例\n\n例如，在亚式期权（Asian option）定价中，期权收益取决于标的资产在存续期内的平均价格而非终值。由于平均价格的分布没有解析解，蒙特卡洛方法成为标准定价工具。具体实施时，模拟10,000条价格路径（使用几何布朗运动），计算每条路径的平均价格和期权收益，最后取所有路径收益的平均值并折现。使用对偶变量法（antithetic variates）可将所需模拟次数减半而保持相同精度。\n",
}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enhance Tier-A docs (Round 2)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("Sprint 3.1 Round 2 — Case Studies for Tier-A Docs")
    print("=" * 60)

    report_path = PROJECT_ROOT / "data" / "quality_report_detail.json"
    data = json.load(open(report_path, "r", encoding="utf-8"))
    tier_a = [x for x in data if x["quality_tier"] == "A"]
    tier_a.sort(key=lambda x: x["quality_score"])
    print(f"Found {len(tier_a)} Tier-A docs")

    success = 0
    for doc in tier_a:
        cid = Path(doc["file"]).stem
        score = doc["quality_score"]

        case_study = CASE_STUDIES.get(cid)
        if not case_study:
            print(f"  SKIP {cid} (score={score:.1f}): No case study defined")
            continue

        rag_path = RAG_ROOT / doc["file"]
        content = rag_path.read_text(encoding="utf-8", errors="replace")

        if "实际案例" in content:
            print(f"  SKIP {cid} (score={score:.1f}): Already has case study")
            continue

        # Insert before "## 思考题"
        if "## 思考题" in content:
            content = content.replace("## 思考题", case_study + "\n## 思考题")
        else:
            content = content.rstrip() + "\n" + case_study

        # Bump content_version
        content = re.sub(
            r"content_version:\s*(\d+)",
            lambda m: f"content_version: {int(m.group(1)) + 1}",
            content,
        )

        if not args.dry_run:
            rag_path.write_text(content, encoding="utf-8")

        status = "DRY" if args.dry_run else "OK"
        success += 1
        print(f"  {status} {cid} (score={score:.1f})")

    print(f"\nEnhanced: {success}/{len(tier_a)}")


if __name__ == "__main__":
    main()
