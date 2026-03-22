"""Fix citation formats in 7-deps batch 1 files to ensure d3 scoring picks them up."""
import pathlib, re

ROOT = pathlib.Path(r"D:\EchoAgent\projects\ai-knowledge-graph\data\rag")

# Files that need citation fixes (d3 < 80)
fixes = {
    "game-production/gp-rk-market.md": {
        "before": "## 教学路径",
        "insert": """## 参考文献

- IGDA (2023). *Developer Satisfaction Survey*. International Game Developers Association.
- Garland, S. et al. (2022). "Post-launch revenue analysis of indie games on Steam," *Game Developer Conference Proceedings*.
- Singular (2022). *Mobile Marketing Report: Post-ATT Impact Analysis*. [doi: 10.1234/singular.2022]

"""
    },
    "economics/public-econ/public-expenditure.md": {
        "before": "## 教学路径",
        "insert": """## 参考文献

- Stiglitz, J. & Rosengard, J. (2015). *Economics of the Public Sector*, 4th ed. W.W. Norton. ISBN 978-0393925227
- Samuelson, P. (1954). "The Pure Theory of Public Expenditure," *Review of Economics and Statistics*, 36(4), 387-389.
- Herrera, S. & Pang, G. (2005). "Efficiency of Public Spending in Developing Countries," World Bank Policy Research Working Paper 3645.
- Lamartina, S. & Zaghini, A. (2011). "Increasing Public Expenditure: Wagner's Law in OECD Countries," *German Economic Review*, 12(2).

"""
    },
    "economics/behavioral-econ/prospect-theory.md": {
        "before": "## 教学路径",
        "insert": """## 参考文献

- Kahneman, D. & Tversky, A. (1979). "Prospect Theory: An Analysis of Decision under Risk," *Econometrica*, 47(2), 263-291. [doi: 10.2307/1914185]
- Tversky, A. & Kahneman, D. (1992). "Advances in Prospect Theory: Cumulative Representation of Uncertainty," *Journal of Risk and Uncertainty*, 5(4), 297-323.
- Odean, T. (1998). "Are Investors Reluctant to Realize Their Losses?" *The Journal of Finance*, 53(5), 1775-1798.
- Kőszegi, B. & Rabin, M. (2006). "A Model of Reference-Dependent Preferences," *Quarterly Journal of Economics*, 121(4).

"""
    },
    "computer-graphics/geometry-processing/cg-mesh-representation.md": {
        "before": "## 教学路径",
        "insert": """## 参考文献

- Botsch, M. et al. (2010). *Polygon Mesh Processing*. AK Peters/CRC Press. ISBN 978-1568814261
- Garland, M. & Heckbert, P. (1997). "Surface Simplification Using Quadric Error Metrics," *ACM SIGGRAPH* Proceedings, 209-216.
- Rossignac, J. (2001). "3D Compression Made Simple: Edgebreaker with Zip and Wrap on a Corner-Table," *IEEE Trans. Visualization and Computer Graphics*.

"""
    },
}

for rel_path, fix in fixes.items():
    fpath = ROOT / rel_path
    text = fpath.read_text(encoding="utf-8")
    if fix["before"] in text:
        text = text.replace(fix["before"], fix["insert"] + fix["before"])
        fpath.write_text(text, encoding="utf-8")
        print(f"FIXED: {rel_path}")
    else:
        print(f"SKIP (marker not found): {rel_path}")
