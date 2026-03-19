"""Generate mathematics seed_graph.json — Phase 8.1"""
import json
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat()

DOMAIN = {
    "id": "mathematics",
    "name": "数学",
    "description": "从算术到高等数学的系统知识体系",
    "icon": "🔵",
    "color": "#3b82f6"
}

SUBDOMAINS = [
    {"id": "arithmetic",        "name": "算术基础",  "order": 1},
    {"id": "algebra",           "name": "代数",      "order": 2},
    {"id": "geometry",          "name": "几何",      "order": 3},
    {"id": "trigonometry",      "name": "三角学",    "order": 4},
    {"id": "analytic-geometry",  "name": "解析几何",  "order": 5},
    {"id": "calculus",          "name": "微积分",    "order": 6},
    {"id": "linear-algebra",    "name": "线性代数",  "order": 7},
    {"id": "probability",       "name": "概率论",    "order": 8},
    {"id": "statistics",        "name": "数理统计",  "order": 9},
    {"id": "discrete-math",     "name": "离散数学",  "order": 10},
    {"id": "number-theory",     "name": "数论",      "order": 11},
    {"id": "optimization",      "name": "最优化",    "order": 12},
]

def c(id, name, desc, sub, diff, mins=20, ctype="theory", tags=None, milestone=False):
    return {
        "id": id, "name": name, "description": desc,
        "domain_id": "mathematics", "subdomain_id": sub,
        "difficulty": diff, "estimated_minutes": mins,
        "content_type": ctype, "tags": tags or [],
        "is_milestone": milestone, "created_at": NOW
    }

def e(src, tgt, etype="prerequisite", strength=0.7):
    return {"source_id": src, "target_id": tgt, "relation_type": etype, "strength": strength}

concepts = []
edges = []

# ═══════════════════════════════════════════════════════════════
# 1. ARITHMETIC (算术基础) — 18 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("natural-numbers",     "自然数与整数",     "自然数、整数的概念及基本运算", "arithmetic", 1, tags=["基础"]),
    c("four-operations",     "四则运算",        "加减乘除及其运算律", "arithmetic", 1, tags=["基础"]),
    c("fractions",           "分数",           "分数的概念、运算与化简", "arithmetic", 2, tags=["基础"]),
    c("decimals",            "小数与百分数",    "小数运算与百分数转换", "arithmetic", 2, tags=["基础"]),
    c("ratio-proportion",    "比与比例",        "比的概念、正比例与反比例", "arithmetic", 2, tags=["基础"]),
    c("exponents-basics",    "指数与幂运算",    "正整数指数幂及其运算法则", "arithmetic", 3, tags=["基础"]),
    c("roots-basics",        "根号与开方",      "平方根、立方根及其性质", "arithmetic", 3, tags=["基础"]),
    c("scientific-notation", "科学记数法",      "大数和小数的科学记数表示", "arithmetic", 2, tags=["基础"]),
    c("number-line",         "数轴与绝对值",    "数轴表示、绝对值的几何意义", "arithmetic", 2, tags=["基础"]),
    c("divisibility",        "整除与因数分解",   "因数、倍数、质因数分解", "arithmetic", 3, tags=["基础"]),
    c("gcd-lcm",             "最大公因数与最小公倍数", "GCD/LCM的计算方法", "arithmetic", 3, tags=["基础"]),
    c("order-of-operations", "运算优先级",      "括号、指数、乘除、加减的优先顺序", "arithmetic", 1, tags=["基础"]),
    c("estimation-rounding", "估算与近似",      "四舍五入、有效数字、误差概念", "arithmetic", 2, tags=["基础"]),
    c("negative-numbers",    "负数",           "负数的引入、加减法则", "arithmetic", 2, tags=["基础"]),
    c("number-sets",         "数集分类",        "自然数、整数、有理数、无理数、实数的关系", "arithmetic", 3, milestone=True, tags=["里程碑"]),
    c("arithmetic-word-problems", "算术应用题",  "行程、工程、浓度等经典应用题", "arithmetic", 3, ctype="practice", tags=["应用"]),
    c("rational-operations", "有理数运算",      "有理数加减乘除与混合运算", "arithmetic", 3, tags=["基础"]),
    c("irrational-numbers",  "无理数",          "无理数的概念、π与√2的无理性", "arithmetic", 4, tags=["进阶"]),
])

edges.extend([
    e("natural-numbers", "four-operations"),
    e("natural-numbers", "negative-numbers"),
    e("natural-numbers", "number-line"),
    e("four-operations", "order-of-operations"),
    e("four-operations", "fractions"),
    e("four-operations", "decimals"),
    e("fractions", "ratio-proportion"),
    e("fractions", "rational-operations"),
    e("decimals", "estimation-rounding"),
    e("decimals", "scientific-notation"),
    e("negative-numbers", "number-line"),
    e("negative-numbers", "rational-operations"),
    e("number-line", "number-sets"),
    e("exponents-basics", "roots-basics"),
    e("exponents-basics", "scientific-notation"),
    e("rational-operations", "number-sets"),
    e("natural-numbers", "divisibility"),
    e("divisibility", "gcd-lcm"),
    e("number-sets", "irrational-numbers"),
    e("roots-basics", "irrational-numbers"),
    e("ratio-proportion", "arithmetic-word-problems"),
    e("four-operations", "arithmetic-word-problems"),
    e("fractions", "decimals", "related"),
    e("gcd-lcm", "fractions", "related"),
])

# ═══════════════════════════════════════════════════════════════
# 2. ALGEBRA (代数) — 28 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("variables-expressions", "变量与代数式",    "用字母表示未知数、代数式的构造", "algebra", 2, tags=["基础"]),
    c("linear-equations",     "一元一次方程",     "一元一次方程的解法与应用", "algebra", 3, tags=["基础"]),
    c("linear-inequalities",  "一元一次不等式",   "不等式的性质与解集", "algebra", 3, tags=["基础"]),
    c("systems-of-equations", "方程组",          "二元一次方程组的消元法", "algebra", 4, tags=["基础"]),
    c("quadratic-equations",  "一元二次方程",     "求根公式、韦达定理、判别式", "algebra", 5, milestone=True, tags=["里程碑"]),
    c("quadratic-functions",  "二次函数",        "y=ax²+bx+c的图像、顶点、对称轴", "algebra", 5, tags=["核心"]),
    c("polynomials",          "多项式",          "多项式运算、因式分解", "algebra", 4, tags=["核心"]),
    c("factoring",            "因式分解",        "提公因子、公式法、十字相乘法", "algebra", 4, tags=["核心"]),
    c("rational-expressions", "分式",            "分式的化简、运算与方程", "algebra", 5, tags=["进阶"]),
    c("radical-expressions",  "根式运算",        "根式化简、有理化、根号嵌套", "algebra", 5, tags=["进阶"]),
    c("function-concept",     "函数概念",        "函数的定义、定义域、值域、映射", "algebra", 4, milestone=True, tags=["里程碑"]),
    c("function-properties",  "函数的性质",      "单调性、奇偶性、周期性、有界性", "algebra", 5, tags=["核心"]),
    c("inverse-functions",    "反函数",          "反函数的存在条件与求法", "algebra", 5, tags=["进阶"]),
    c("composite-functions",  "复合函数",        "函数的复合、嵌套与分解", "algebra", 6, tags=["进阶"]),
    c("exponential-functions","指数函数",        "y=aˣ的图像与性质", "algebra", 5, tags=["核心"]),
    c("logarithmic-functions","对数函数",        "对数的定义、运算法则、换底公式", "algebra", 5, tags=["核心"]),
    c("power-functions",      "幂函数",          "y=xⁿ的图像与性质", "algebra", 4, tags=["核心"]),
    c("absolute-value-func",  "绝对值函数",      "|x|的图像变换与不等式", "algebra", 4, tags=["进阶"]),
    c("piecewise-functions",  "分段函数",        "分段定义的函数与图像", "algebra", 5, tags=["进阶"]),
    c("sequences-intro",      "数列基础",        "数列的通项公式与递推", "algebra", 4, tags=["核心"]),
    c("arithmetic-sequence",  "等差数列",        "通项公式、前n项和公式", "algebra", 5, tags=["核心"]),
    c("geometric-sequence",   "等比数列",        "通项公式、前n项和、无穷等比级数", "algebra", 5, tags=["核心"]),
    c("series-summation",     "级数与求和",      "求和公式、裂项法、错位相减法", "algebra", 6, tags=["进阶"]),
    c("mathematical-induction","数学归纳法",      "第一数学归纳法、第二归纳法", "algebra", 6, milestone=True, tags=["里程碑"]),
    c("binomial-theorem",     "二项式定理",      "二项展开式、组合数性质", "algebra", 6, tags=["进阶"]),
    c("inequality-techniques","不等式技巧",      "AM-GM、柯西、排序不等式", "algebra", 7, tags=["竞赛"]),
    c("parametric-equations", "参数方程",        "含参方程的讨论与消参", "algebra", 6, tags=["进阶"]),
    c("complex-numbers-intro","复数初步",        "虚数单位i、复数运算、复平面", "algebra", 6, tags=["进阶"]),
])

edges.extend([
    e("number-sets", "variables-expressions"),
    e("four-operations", "variables-expressions"),
    e("variables-expressions", "linear-equations"),
    e("linear-equations", "linear-inequalities"),
    e("linear-equations", "systems-of-equations"),
    e("variables-expressions", "polynomials"),
    e("polynomials", "factoring"),
    e("factoring", "quadratic-equations"),
    e("linear-equations", "quadratic-equations"),
    e("quadratic-equations", "quadratic-functions"),
    e("fractions", "rational-expressions"),
    e("polynomials", "rational-expressions"),
    e("roots-basics", "radical-expressions"),
    e("variables-expressions", "function-concept"),
    e("function-concept", "function-properties"),
    e("function-properties", "inverse-functions"),
    e("function-properties", "composite-functions"),
    e("exponents-basics", "exponential-functions"),
    e("function-concept", "exponential-functions"),
    e("exponential-functions", "logarithmic-functions"),
    e("function-concept", "power-functions"),
    e("function-concept", "absolute-value-func"),
    e("function-concept", "piecewise-functions"),
    e("function-concept", "sequences-intro"),
    e("sequences-intro", "arithmetic-sequence"),
    e("sequences-intro", "geometric-sequence"),
    e("arithmetic-sequence", "series-summation"),
    e("geometric-sequence", "series-summation"),
    e("series-summation", "mathematical-induction"),
    e("geometric-sequence", "binomial-theorem"),
    e("linear-inequalities", "inequality-techniques"),
    e("quadratic-equations", "parametric-equations"),
    e("irrational-numbers", "complex-numbers-intro"),
    e("quadratic-equations", "complex-numbers-intro"),
    e("quadratic-functions", "function-properties", "related"),
    e("logarithmic-functions", "exponential-functions", "related"),
])

# ═══════════════════════════════════════════════════════════════
# 3. GEOMETRY (几何) — 22 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("points-lines-planes",  "点线面基础",      "点、直线、射线、线段、平面的基本概念", "geometry", 1, tags=["基础"]),
    c("angles",               "角与角度",        "角的分类、度量、互余互补", "geometry", 2, tags=["基础"]),
    c("parallel-perpendicular","平行与垂直",      "平行线的判定与性质、垂直", "geometry", 2, tags=["基础"]),
    c("triangles",            "三角形",          "三角形分类、内角和、三边关系", "geometry", 3, tags=["基础"]),
    c("congruent-triangles",  "全等三角形",      "SSS/SAS/ASA/AAS判定、CPCTC", "geometry", 4, tags=["核心"]),
    c("similar-triangles",    "相似三角形",      "相似比、AA/SAS/SSS判定", "geometry", 5, milestone=True, tags=["里程碑"]),
    c("pythagorean-theorem",  "勾股定理",        "a²+b²=c²的证明与应用", "geometry", 4, milestone=True, tags=["里程碑"]),
    c("circles",              "圆",             "圆的基本元素、圆心角、弧", "geometry", 4, tags=["核心"]),
    c("circle-theorems",      "圆的定理",        "圆周角、切线定理、幂定理", "geometry", 6, tags=["进阶"]),
    c("quadrilaterals",       "四边形",          "平行四边形、矩形、菱形、梯形", "geometry", 3, tags=["基础"]),
    c("area-perimeter",       "面积与周长",      "常见图形的面积和周长公式", "geometry", 3, tags=["基础"]),
    c("volume-surface-area",  "体积与表面积",    "柱体、锥体、球体的体积和表面积", "geometry", 4, tags=["核心"]),
    c("symmetry-transformations","对称与变换",    "轴对称、中心对称、旋转、平移", "geometry", 4, tags=["核心"]),
    c("coordinate-geometry-intro","坐标几何初步", "直角坐标系、两点距离、中点公式", "geometry", 3, tags=["基础"]),
    c("geometric-proofs",     "几何证明",        "证明的逻辑结构、演绎推理", "geometry", 5, tags=["核心"]),
    c("solid-geometry",       "立体几何",        "空间直线与平面的位置关系", "geometry", 6, tags=["进阶"]),
    c("space-angles-distances","空间角与距离",    "线面角、二面角、点面距离", "geometry", 7, tags=["进阶"]),
    c("euler-formula-polyhedra","欧拉公式",      "V-E+F=2, 正多面体", "geometry", 5, tags=["进阶"]),
    c("geometric-constructions","尺规作图",       "基本尺规作图方法与不可能问题", "geometry", 4, tags=["经典"]),
    c("tessellations",        "密铺与镶嵌",      "正多边形密铺、准晶体", "geometry", 5, tags=["趣味"]),
    c("projective-geometry-intro","射影几何初步", "交比、射影变换、对偶原理", "geometry", 8, tags=["进阶"]),
    c("non-euclidean-intro",  "非欧几何初步",    "球面几何与双曲几何的直觉", "geometry", 8, tags=["拓展"]),
])

edges.extend([
    e("points-lines-planes", "angles"),
    e("points-lines-planes", "parallel-perpendicular"),
    e("angles", "triangles"),
    e("parallel-perpendicular", "triangles"),
    e("triangles", "congruent-triangles"),
    e("triangles", "pythagorean-theorem"),
    e("congruent-triangles", "similar-triangles"),
    e("similar-triangles", "circle-theorems"),
    e("triangles", "quadrilaterals"),
    e("quadrilaterals", "area-perimeter"),
    e("triangles", "area-perimeter"),
    e("circles", "circle-theorems"),
    e("circles", "area-perimeter"),
    e("area-perimeter", "volume-surface-area"),
    e("triangles", "symmetry-transformations"),
    e("points-lines-planes", "coordinate-geometry-intro"),
    e("congruent-triangles", "geometric-proofs"),
    e("parallel-perpendicular", "solid-geometry"),
    e("solid-geometry", "space-angles-distances"),
    e("volume-surface-area", "euler-formula-polyhedra"),
    e("solid-geometry", "euler-formula-polyhedra"),
    e("symmetry-transformations", "tessellations"),
    e("circle-theorems", "projective-geometry-intro"),
    e("parallel-perpendicular", "non-euclidean-intro"),
    e("geometric-proofs", "non-euclidean-intro"),
    e("angles", "geometric-constructions"),
    e("pythagorean-theorem", "coordinate-geometry-intro", "related"),
    e("similar-triangles", "pythagorean-theorem", "related"),
])

# ═══════════════════════════════════════════════════════════════
# 4. TRIGONOMETRY (三角学) — 20 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("trig-ratios",          "三角比",          "正弦、余弦、正切的定义(直角三角形)", "trigonometry", 4, tags=["基础"]),
    c("unit-circle",          "单位圆",          "用单位圆定义三角函数、弧度制", "trigonometry", 5, milestone=True, tags=["里程碑"]),
    c("radian-measure",       "弧度制",          "弧度与角度的转换、弧长公式", "trigonometry", 4, tags=["基础"]),
    c("trig-identities",      "三角恒等式",      "基本恒等式、毕达哥拉斯恒等式", "trigonometry", 5, tags=["核心"]),
    c("sum-difference-formulas","和差化积公式",   "sin(A±B)、cos(A±B)、tan(A±B)", "trigonometry", 6, tags=["核心"]),
    c("double-half-angle",    "倍角与半角公式",   "sin2θ、cos2θ、半角公式", "trigonometry", 6, tags=["核心"]),
    c("trig-equations",       "三角方程",        "三角方程的通解与特解", "trigonometry", 6, tags=["进阶"]),
    c("trig-graphs",          "三角函数图像",     "正弦余弦图像、振幅频率相移", "trigonometry", 5, tags=["核心"]),
    c("inverse-trig",         "反三角函数",      "arcsin、arccos、arctan的定义域与值域", "trigonometry", 6, tags=["进阶"]),
    c("law-of-sines",         "正弦定理",        "a/sinA = b/sinB = 2R", "trigonometry", 5, tags=["核心"]),
    c("law-of-cosines",       "余弦定理",        "c²=a²+b²-2ab·cosC", "trigonometry", 5, tags=["核心"]),
    c("trig-applications",    "三角函数应用",     "测量、导航、物理中的三角应用", "trigonometry", 5, ctype="practice", tags=["应用"]),
    c("polar-coordinates",    "极坐标",          "极坐标系、极坐标方程", "trigonometry", 6, tags=["进阶"]),
    c("complex-trig",         "复数的三角形式",   "复数的模与辐角、棣莫弗公式", "trigonometry", 7, tags=["进阶"]),
    c("hyperbolic-functions", "双曲函数",        "sinh、cosh、tanh的定义与性质", "trigonometry", 7, tags=["拓展"]),
    c("trig-inequalities",    "三角不等式",      "含三角函数的不等式求解", "trigonometry", 6, tags=["进阶"]),
    c("product-sum-formulas", "积化和差公式",     "sinA·sinB等的展开", "trigonometry", 6, tags=["核心"]),
    c("parametric-trig",      "三角参数化",      "圆和椭圆的三角参数方程", "trigonometry", 6, tags=["应用"]),
    c("fourier-intro",        "傅里叶级数初步",   "周期函数的三角级数展开思想", "trigonometry", 8, tags=["拓展"]),
    c("spherical-trig",       "球面三角",        "球面三角学基础概念", "trigonometry", 8, tags=["拓展"]),
])

edges.extend([
    e("pythagorean-theorem", "trig-ratios"),
    e("triangles", "trig-ratios"),
    e("trig-ratios", "unit-circle"),
    e("angles", "radian-measure"),
    e("unit-circle", "radian-measure"),
    e("unit-circle", "trig-identities"),
    e("trig-identities", "sum-difference-formulas"),
    e("sum-difference-formulas", "double-half-angle"),
    e("sum-difference-formulas", "product-sum-formulas"),
    e("trig-identities", "trig-equations"),
    e("unit-circle", "trig-graphs"),
    e("trig-graphs", "inverse-trig"),
    e("trig-ratios", "law-of-sines"),
    e("trig-ratios", "law-of-cosines"),
    e("pythagorean-theorem", "law-of-cosines"),
    e("law-of-sines", "trig-applications"),
    e("law-of-cosines", "trig-applications"),
    e("unit-circle", "polar-coordinates"),
    e("coordinate-geometry-intro", "polar-coordinates"),
    e("complex-numbers-intro", "complex-trig"),
    e("unit-circle", "complex-trig"),
    e("exponential-functions", "hyperbolic-functions"),
    e("trig-identities", "hyperbolic-functions"),
    e("trig-equations", "trig-inequalities"),
    e("polar-coordinates", "parametric-trig"),
    e("series-summation", "fourier-intro"),
    e("trig-graphs", "fourier-intro"),
    e("law-of-cosines", "spherical-trig"),
    e("solid-geometry", "spherical-trig"),
    e("inverse-trig", "trig-equations", "related"),
])

# ═══════════════════════════════════════════════════════════════
# 5. ANALYTIC GEOMETRY (解析几何) — 18 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("cartesian-plane",      "直角坐标系",      "笛卡尔坐标系的建立与平面点集", "analytic-geometry", 3, tags=["基础"]),
    c("distance-midpoint",    "距离与中点公式",   "两点距离、中点坐标公式", "analytic-geometry", 3, tags=["基础"]),
    c("slope-line-equation",  "直线的斜率与方程",  "点斜式、两点式、一般式", "analytic-geometry", 4, tags=["核心"]),
    c("parallel-perp-lines",  "平行与垂直的坐标条件","斜率关系判定平行与垂直", "analytic-geometry", 4, tags=["核心"]),
    c("line-intersection",    "直线的交点与位置关系","联立方程求交点、共线判定", "analytic-geometry", 4, tags=["核心"]),
    c("circle-equation",      "圆的方程",        "标准方程和一般方程、圆与直线", "analytic-geometry", 5, tags=["核心"]),
    c("ellipse",              "椭圆",           "标准方程、焦点、离心率", "analytic-geometry", 6, milestone=True, tags=["里程碑"]),
    c("hyperbola",            "双曲线",          "标准方程、渐近线、离心率", "analytic-geometry", 6, tags=["核心"]),
    c("parabola",             "抛物线",          "标准方程、焦点、准线", "analytic-geometry", 6, tags=["核心"]),
    c("conic-sections-unified","圆锥曲线统一定义", "焦点-准线定义、离心率统一", "analytic-geometry", 7, milestone=True, tags=["里程碑"]),
    c("tangent-normal-lines", "切线与法线",      "曲线在某点的切线方程", "analytic-geometry", 6, tags=["进阶"]),
    c("parametric-curves",    "参数曲线",        "用参数表示曲线、消参", "analytic-geometry", 6, tags=["进阶"]),
    c("polar-curves",         "极坐标曲线",      "极坐标方程与常见曲线", "analytic-geometry", 7, tags=["进阶"]),
    c("rotation-translation", "坐标变换",        "坐标旋转与平移变换", "analytic-geometry", 6, tags=["进阶"]),
    c("locus-problems",       "轨迹问题",        "动点轨迹方程的求法", "analytic-geometry", 7, tags=["综合"]),
    c("line-conic-intersection","直线与圆锥曲线",  "联立方程、韦达定理应用", "analytic-geometry", 7, tags=["综合"]),
    c("affine-transformations","仿射变换",        "线性变换与平移的组合", "analytic-geometry", 7, tags=["拓展"]),
    c("curve-families",       "曲线族与包络线",   "含参曲线族及其包络", "analytic-geometry", 8, tags=["拓展"]),
])

edges.extend([
    e("coordinate-geometry-intro", "cartesian-plane"),
    e("cartesian-plane", "distance-midpoint"),
    e("cartesian-plane", "slope-line-equation"),
    e("slope-line-equation", "parallel-perp-lines"),
    e("slope-line-equation", "line-intersection"),
    e("systems-of-equations", "line-intersection"),
    e("distance-midpoint", "circle-equation"),
    e("circle-equation", "ellipse"),
    e("quadratic-functions", "parabola"),
    e("circle-equation", "hyperbola"),
    e("ellipse", "conic-sections-unified"),
    e("hyperbola", "conic-sections-unified"),
    e("parabola", "conic-sections-unified"),
    e("slope-line-equation", "tangent-normal-lines"),
    e("parametric-equations", "parametric-curves"),
    e("polar-coordinates", "polar-curves"),
    e("symmetry-transformations", "rotation-translation"),
    e("conic-sections-unified", "locus-problems"),
    e("quadratic-equations", "line-conic-intersection"),
    e("conic-sections-unified", "line-conic-intersection"),
    e("rotation-translation", "affine-transformations"),
    e("parametric-curves", "curve-families"),
    e("ellipse", "parametric-trig", "related"),
])

# ═══════════════════════════════════════════════════════════════
# 6. CALCULUS (微积分) — 35 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("limits-concept",       "极限概念",        "数列极限与函数极限的ε-δ定义", "calculus", 5, tags=["核心"]),
    c("limit-laws",           "极限运算法则",     "极限的四则运算、夹逼定理", "calculus", 5, tags=["核心"]),
    c("continuity",           "连续性",          "函数连续的定义、间断点分类", "calculus", 5, tags=["核心"]),
    c("ivt-evt",              "介值定理与极值定理","连续函数的基本定理", "calculus", 6, tags=["定理"]),
    c("derivative-concept",   "导数概念",        "导数的定义、几何意义(切线斜率)、物理意义(瞬时速度)", "calculus", 5, milestone=True, tags=["里程碑"]),
    c("differentiation-rules","求导法则",        "和差积商、链式法则", "calculus", 5, tags=["核心"]),
    c("higher-derivatives",   "高阶导数",        "二阶导数、n阶导数、Leibniz公式", "calculus", 6, tags=["进阶"]),
    c("implicit-differentiation","隐函数求导",    "隐函数的导数求法", "calculus", 6, tags=["进阶"]),
    c("related-rates",        "相关变化率",      "应用导数求相关变化率问题", "calculus", 6, ctype="practice", tags=["应用"]),
    c("mean-value-theorems",  "中值定理",        "Rolle定理、Lagrange中值定理、Cauchy中值定理", "calculus", 7, milestone=True, tags=["里程碑"]),
    c("lhopitals-rule",       "洛必达法则",      "0/0和∞/∞型不定式的极限", "calculus", 6, tags=["核心"]),
    c("taylor-series",        "泰勒展开",        "泰勒公式、麦克劳林展开、余项估计", "calculus", 7, tags=["核心"]),
    c("curve-sketching",      "函数图像分析",     "利用导数分析单调性、极值、凹凸性、拐点", "calculus", 6, tags=["应用"]),
    c("optimization-calculus","最值问题",        "利用导数求最大值最小值", "calculus", 6, ctype="practice", tags=["应用"]),
    c("indefinite-integrals", "不定积分",        "原函数与不定积分的概念", "calculus", 5, tags=["核心"]),
    c("integration-techniques","积分技巧",       "换元法、分部积分法", "calculus", 6, tags=["核心"]),
    c("definite-integrals",   "定积分",          "Riemann和与定积分的定义", "calculus", 6, milestone=True, tags=["里程碑"]),
    c("ftc",                  "微积分基本定理",   "Newton-Leibniz公式、FTC I和II", "calculus", 6, milestone=True, tags=["里程碑"]),
    c("area-under-curve",     "曲线围面积",      "利用定积分求面积", "calculus", 6, ctype="practice", tags=["应用"]),
    c("volume-of-revolution", "旋转体体积",      "圆盘法和壳法", "calculus", 7, ctype="practice", tags=["应用"]),
    c("arc-length",           "弧长公式",        "参数曲线和显式曲线的弧长", "calculus", 7, tags=["应用"]),
    c("improper-integrals",   "广义积分",        "无穷区间和瑕积分的收敛判定", "calculus", 7, tags=["进阶"]),
    c("sequences-series-calc","级数与收敛",      "正项级数、交错级数、绝对收敛", "calculus", 7, tags=["核心"]),
    c("power-series",         "幂级数",          "收敛半径、Abel定理、逐项求导积分", "calculus", 7, tags=["进阶"]),
    c("partial-derivatives",  "偏导数",          "多元函数的偏导数与全微分", "calculus", 7, tags=["核心"]),
    c("gradient-directional", "梯度与方向导数",   "梯度向量、方向导数的几何意义", "calculus", 7, tags=["核心"]),
    c("multiple-integrals",   "重积分",          "二重积分与三重积分的计算", "calculus", 8, tags=["进阶"]),
    c("line-integrals",       "曲线积分",        "第一类和第二类曲线积分", "calculus", 8, tags=["进阶"]),
    c("surface-integrals",    "曲面积分",        "通量与散度定理(Gauss)", "calculus", 9, tags=["拓展"]),
    c("greens-theorem",       "格林公式",        "平面区域的曲线积分转化为面积分", "calculus", 8, tags=["进阶"]),
    c("stokes-theorem",       "斯托克斯定理",    "曲面积分与曲线积分的关系", "calculus", 9, tags=["拓展"]),
    c("differential-equations-intro","常微分方程初步","一阶ODE: 可分离变量、线性ODE", "calculus", 7, tags=["核心"]),
    c("second-order-ode",     "二阶常微分方程",   "常系数齐次与非齐次ODE", "calculus", 8, tags=["进阶"]),
    c("laplace-transform-intro","拉普拉斯变换初步","定义、基本性质、逆变换", "calculus", 8, tags=["拓展"]),
    c("epsilon-delta",        "ε-δ严格定义",     "极限的严格形式化定义与证明", "calculus", 7, tags=["理论"]),
])

edges.extend([
    e("function-concept", "limits-concept"),
    e("sequences-intro", "limits-concept"),
    e("limits-concept", "limit-laws"),
    e("limit-laws", "continuity"),
    e("continuity", "ivt-evt"),
    e("limits-concept", "derivative-concept"),
    e("derivative-concept", "differentiation-rules"),
    e("differentiation-rules", "higher-derivatives"),
    e("differentiation-rules", "implicit-differentiation"),
    e("derivative-concept", "related-rates"),
    e("derivative-concept", "mean-value-theorems"),
    e("continuity", "mean-value-theorems"),
    e("limit-laws", "lhopitals-rule"),
    e("derivative-concept", "lhopitals-rule"),
    e("higher-derivatives", "taylor-series"),
    e("series-summation", "taylor-series"),
    e("differentiation-rules", "curve-sketching"),
    e("higher-derivatives", "curve-sketching"),
    e("derivative-concept", "optimization-calculus"),
    e("differentiation-rules", "indefinite-integrals"),
    e("indefinite-integrals", "integration-techniques"),
    e("indefinite-integrals", "definite-integrals"),
    e("definite-integrals", "ftc"),
    e("derivative-concept", "ftc"),
    e("definite-integrals", "area-under-curve"),
    e("definite-integrals", "volume-of-revolution"),
    e("definite-integrals", "arc-length"),
    e("definite-integrals", "improper-integrals"),
    e("geometric-sequence", "sequences-series-calc"),
    e("limits-concept", "sequences-series-calc"),
    e("sequences-series-calc", "power-series"),
    e("taylor-series", "power-series"),
    e("derivative-concept", "partial-derivatives"),
    e("partial-derivatives", "gradient-directional"),
    e("definite-integrals", "multiple-integrals"),
    e("multiple-integrals", "line-integrals"),
    e("line-integrals", "greens-theorem"),
    e("line-integrals", "surface-integrals"),
    e("greens-theorem", "stokes-theorem"),
    e("surface-integrals", "stokes-theorem"),
    e("differentiation-rules", "differential-equations-intro"),
    e("integration-techniques", "differential-equations-intro"),
    e("differential-equations-intro", "second-order-ode"),
    e("improper-integrals", "laplace-transform-intro"),
    e("second-order-ode", "laplace-transform-intro"),
    e("limits-concept", "epsilon-delta"),
    e("ftc", "indefinite-integrals", "related"),
    e("tangent-normal-lines", "derivative-concept", "related"),
])

# ═══════════════════════════════════════════════════════════════
# 7. LINEAR ALGEBRA (线性代数) — 28 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("vectors-intro",        "向量基础",        "向量的概念、加法、数乘", "linear-algebra", 4, tags=["基础"]),
    c("dot-product",          "内积(点乘)",      "向量点积、投影、夹角", "linear-algebra", 5, tags=["核心"]),
    c("cross-product",        "外积(叉乘)",      "三维向量叉积、法向量、面积", "linear-algebra", 5, tags=["核心"]),
    c("matrices-intro",       "矩阵基础",        "矩阵的定义、加法、数乘、转置", "linear-algebra", 5, tags=["核心"]),
    c("matrix-multiplication","矩阵乘法",        "矩阵乘法规则、不可交换性", "linear-algebra", 5, tags=["核心"]),
    c("determinants",         "行列式",          "行列式的定义、展开、性质", "linear-algebra", 6, milestone=True, tags=["里程碑"]),
    c("inverse-matrix",       "逆矩阵",         "可逆条件、求逆方法(伴随矩阵、高斯消元)", "linear-algebra", 6, tags=["核心"]),
    c("linear-systems",       "线性方程组",      "高斯消元法、增广矩阵", "linear-algebra", 5, tags=["核心"]),
    c("row-echelon-form",     "行阶梯形与秩",    "行简化阶梯形、矩阵的秩", "linear-algebra", 6, tags=["核心"]),
    c("vector-spaces",        "向量空间",        "向量空间的定义与子空间", "linear-algebra", 7, milestone=True, tags=["里程碑"]),
    c("linear-independence",  "线性无关",        "线性相关与线性无关的判定", "linear-algebra", 6, tags=["核心"]),
    c("basis-dimension",      "基与维数",        "基的概念、维数、坐标表示", "linear-algebra", 7, tags=["核心"]),
    c("linear-transformations","线性变换",        "线性映射、核与像", "linear-algebra", 7, tags=["核心"]),
    c("eigenvalues-eigenvectors","特征值与特征向量","特征方程、特征多项式", "linear-algebra", 7, milestone=True, tags=["里程碑"]),
    c("diagonalization",      "对角化",          "矩阵对角化条件、相似变换", "linear-algebra", 7, tags=["进阶"]),
    c("inner-product-spaces", "内积空间",        "一般内积空间、正交性、Gram-Schmidt", "linear-algebra", 8, tags=["进阶"]),
    c("orthogonal-matrices",  "正交矩阵",       "正交矩阵、QR分解", "linear-algebra", 8, tags=["进阶"]),
    c("svd",                  "奇异值分解",      "SVD的定义、几何意义、应用", "linear-algebra", 8, tags=["应用"]),
    c("quadratic-forms",      "二次型",          "二次型的矩阵表示、正定性", "linear-algebra", 7, tags=["进阶"]),
    c("jordan-form",          "Jordan标准形",    "Jordan块、一般矩阵的分类", "linear-algebra", 9, tags=["拓展"]),
    c("null-column-row-spaces","四个基本子空间",  "零空间、列空间、行空间、左零空间", "linear-algebra", 7, tags=["核心"]),
    c("least-squares",        "最小二乘法",      "超定方程组、正规方程、投影矩阵", "linear-algebra", 7, tags=["应用"]),
    c("matrix-norms",         "矩阵范数",        "Frobenius范数、谱范数", "linear-algebra", 8, tags=["进阶"]),
    c("positive-definite",    "正定矩阵",        "正定性判定、Cholesky分解", "linear-algebra", 8, tags=["进阶"]),
    c("tensor-intro",         "张量初步",        "张量的直觉与多维数组", "linear-algebra", 8, tags=["拓展"]),
    c("cramers-rule",         "克莱姆法则",      "用行列式求解方程组", "linear-algebra", 6, tags=["经典"]),
    c("matrix-exponential",   "矩阵指数",        "e^A的定义与ODE中的应用", "linear-algebra", 8, tags=["拓展"]),
    c("abstract-vector-spaces","抽象向量空间",    "函数空间、多项式空间等例子", "linear-algebra", 8, tags=["理论"]),
])

edges.extend([
    e("number-sets", "vectors-intro"),
    e("systems-of-equations", "linear-systems"),
    e("vectors-intro", "dot-product"),
    e("vectors-intro", "cross-product"),
    e("vectors-intro", "matrices-intro"),
    e("matrices-intro", "matrix-multiplication"),
    e("matrix-multiplication", "determinants"),
    e("determinants", "inverse-matrix"),
    e("determinants", "cramers-rule"),
    e("matrices-intro", "linear-systems"),
    e("linear-systems", "row-echelon-form"),
    e("row-echelon-form", "vector-spaces"),
    e("vectors-intro", "linear-independence"),
    e("linear-independence", "basis-dimension"),
    e("basis-dimension", "vector-spaces"),
    e("matrix-multiplication", "linear-transformations"),
    e("vector-spaces", "linear-transformations"),
    e("determinants", "eigenvalues-eigenvectors"),
    e("linear-transformations", "eigenvalues-eigenvectors"),
    e("eigenvalues-eigenvectors", "diagonalization"),
    e("dot-product", "inner-product-spaces"),
    e("basis-dimension", "inner-product-spaces"),
    e("inner-product-spaces", "orthogonal-matrices"),
    e("eigenvalues-eigenvectors", "svd"),
    e("orthogonal-matrices", "svd"),
    e("matrix-multiplication", "quadratic-forms"),
    e("eigenvalues-eigenvectors", "quadratic-forms"),
    e("diagonalization", "jordan-form"),
    e("row-echelon-form", "null-column-row-spaces"),
    e("vector-spaces", "null-column-row-spaces"),
    e("inner-product-spaces", "least-squares"),
    e("null-column-row-spaces", "least-squares"),
    e("inner-product-spaces", "matrix-norms"),
    e("quadratic-forms", "positive-definite"),
    e("eigenvalues-eigenvectors", "positive-definite"),
    e("matrices-intro", "tensor-intro"),
    e("taylor-series", "matrix-exponential"),
    e("diagonalization", "matrix-exponential"),
    e("vector-spaces", "abstract-vector-spaces"),
    e("gradient-directional", "vectors-intro", "related"),
])

# ═══════════════════════════════════════════════════════════════
# 8. PROBABILITY (概率论) — 22 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("counting-principles",  "计数原理",        "加法原理和乘法原理", "probability", 3, tags=["基础"]),
    c("permutations",         "排列",           "排列数P(n,k)及其计算", "probability", 4, tags=["核心"]),
    c("combinations",         "组合",           "组合数C(n,k)及其性质", "probability", 4, tags=["核心"]),
    c("probability-basics",   "概率基础",        "样本空间、事件、古典概型", "probability", 4, tags=["核心"]),
    c("conditional-probability","条件概率",       "条件概率的定义与乘法公式", "probability", 5, milestone=True, tags=["里程碑"]),
    c("bayes-theorem",        "贝叶斯定理",      "全概率公式与贝叶斯公式", "probability", 6, milestone=True, tags=["里程碑"]),
    c("independence",         "事件的独立性",    "独立事件的定义与判定", "probability", 5, tags=["核心"]),
    c("random-variables",     "随机变量",        "离散与连续随机变量的概念", "probability", 5, tags=["核心"]),
    c("discrete-distributions","离散分布",       "伯努利、二项、泊松分布", "probability", 6, tags=["核心"]),
    c("continuous-distributions","连续分布",     "均匀、正态、指数分布", "probability", 6, tags=["核心"]),
    c("expectation-variance", "期望与方差",      "E(X)和Var(X)的计算与性质", "probability", 6, milestone=True, tags=["里程碑"]),
    c("normal-distribution",  "正态分布",        "N(μ,σ²)的密度函数、68-95-99.7法则", "probability", 6, tags=["核心"]),
    c("joint-distributions",  "联合分布",        "联合概率分布、边际分布、协方差", "probability", 7, tags=["进阶"]),
    c("law-of-large-numbers", "大数定律",        "弱大数定律与强大数定律", "probability", 7, tags=["定理"]),
    c("central-limit-theorem","中心极限定理",    "独立同分布的和趋向正态", "probability", 7, milestone=True, tags=["里程碑"]),
    c("moment-generating",    "矩母函数",        "矩母函数的定义与唯一性", "probability", 8, tags=["进阶"]),
    c("markov-chains-intro",  "马尔可夫链初步",   "状态转移矩阵、平稳分布", "probability", 8, tags=["应用"]),
    c("poisson-process",      "泊松过程",        "计数过程、事件间隔的指数分布", "probability", 8, tags=["进阶"]),
    c("chebyshev-inequality", "切比雪夫不等式",   "P(|X-μ|≥kσ)≤1/k²", "probability", 6, tags=["定理"]),
    c("generating-functions", "生成函数",        "概率生成函数与递推关系", "probability", 8, tags=["拓展"]),
    c("multivariate-normal",  "多元正态分布",    "多维高斯分布及其性质", "probability", 8, tags=["进阶"]),
    c("conditional-expectation","条件期望",      "条件期望的定义与全期望公式", "probability", 7, tags=["进阶"]),
])

edges.extend([
    e("four-operations", "counting-principles"),
    e("counting-principles", "permutations"),
    e("counting-principles", "combinations"),
    e("permutations", "combinations"),
    e("combinations", "probability-basics"),
    e("probability-basics", "conditional-probability"),
    e("conditional-probability", "bayes-theorem"),
    e("conditional-probability", "independence"),
    e("probability-basics", "random-variables"),
    e("random-variables", "discrete-distributions"),
    e("random-variables", "continuous-distributions"),
    e("definite-integrals", "continuous-distributions"),
    e("discrete-distributions", "expectation-variance"),
    e("continuous-distributions", "expectation-variance"),
    e("continuous-distributions", "normal-distribution"),
    e("random-variables", "joint-distributions"),
    e("expectation-variance", "law-of-large-numbers"),
    e("normal-distribution", "central-limit-theorem"),
    e("law-of-large-numbers", "central-limit-theorem"),
    e("expectation-variance", "moment-generating"),
    e("matrix-multiplication", "markov-chains-intro"),
    e("discrete-distributions", "poisson-process"),
    e("expectation-variance", "chebyshev-inequality"),
    e("binomial-theorem", "generating-functions"),
    e("power-series", "generating-functions"),
    e("normal-distribution", "multivariate-normal"),
    e("joint-distributions", "multivariate-normal"),
    e("conditional-probability", "conditional-expectation"),
    e("expectation-variance", "conditional-expectation"),
    e("combinations", "binomial-theorem", "related"),
])

# ═══════════════════════════════════════════════════════════════
# 9. STATISTICS (数理统计) — 20 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("descriptive-statistics","描述性统计",      "均值、中位数、众数、方差、标准差", "statistics", 3, tags=["基础"]),
    c("data-visualization",   "数据可视化基础",   "直方图、箱线图、散点图", "statistics", 3, tags=["基础"]),
    c("sampling-methods",     "抽样方法",        "简单随机、分层、系统、整群抽样", "statistics", 4, tags=["核心"]),
    c("sampling-distributions","抽样分布",       "样本均值的分布、t分布、χ²分布、F分布", "statistics", 6, tags=["核心"]),
    c("point-estimation",     "点估计",          "矩估计法、最大似然估计", "statistics", 6, milestone=True, tags=["里程碑"]),
    c("confidence-intervals", "置信区间",        "均值、比例的置信区间构造", "statistics", 6, tags=["核心"]),
    c("hypothesis-testing",   "假设检验",        "原假设/备择假设、p值、I/II类错误", "statistics", 7, milestone=True, tags=["里程碑"]),
    c("t-test",               "t检验",          "单样本/双样本t检验", "statistics", 7, tags=["核心"]),
    c("chi-square-test",      "卡方检验",        "拟合优度检验、独立性检验", "statistics", 7, tags=["核心"]),
    c("anova",                "方差分析",        "单因素/多因素ANOVA", "statistics", 7, tags=["进阶"]),
    c("linear-regression",    "线性回归",        "一元/多元线性回归、R²", "statistics", 6, milestone=True, tags=["里程碑"]),
    c("correlation",          "相关性分析",      "Pearson/Spearman相关系数", "statistics", 5, tags=["核心"]),
    c("nonparametric-tests",  "非参数检验",      "符号检验、秩和检验、K-S检验", "statistics", 7, tags=["进阶"]),
    c("bayesian-statistics",  "贝叶斯统计",      "先验/后验分布、共轭先验", "statistics", 8, tags=["进阶"]),
    c("experimental-design",  "实验设计",        "随机化、对照、重复、区组设计", "statistics", 6, tags=["方法"]),
    c("logistic-regression",  "逻辑回归",        "二分类问题、Sigmoid函数、最大似然", "statistics", 7, tags=["应用"]),
    c("bootstrap-methods",    "Bootstrap方法",   "重抽样与自助法置信区间", "statistics", 7, tags=["现代"]),
    c("sufficient-statistics","充分统计量",      "因子分解定理、完备性", "statistics", 8, tags=["理论"]),
    c("maximum-likelihood",   "最大似然估计详解", "似然函数、Fisher信息、渐近性质", "statistics", 8, tags=["理论"]),
    c("survival-analysis-intro","生存分析初步",  "Kaplan-Meier估计、Cox回归", "statistics", 8, tags=["应用"]),
])

edges.extend([
    e("expectation-variance", "descriptive-statistics"),
    e("descriptive-statistics", "data-visualization"),
    e("probability-basics", "sampling-methods"),
    e("normal-distribution", "sampling-distributions"),
    e("central-limit-theorem", "sampling-distributions"),
    e("sampling-distributions", "point-estimation"),
    e("sampling-distributions", "confidence-intervals"),
    e("confidence-intervals", "hypothesis-testing"),
    e("sampling-distributions", "t-test"),
    e("hypothesis-testing", "t-test"),
    e("hypothesis-testing", "chi-square-test"),
    e("hypothesis-testing", "anova"),
    e("least-squares", "linear-regression"),
    e("correlation", "linear-regression"),
    e("descriptive-statistics", "correlation"),
    e("hypothesis-testing", "nonparametric-tests"),
    e("bayes-theorem", "bayesian-statistics"),
    e("point-estimation", "bayesian-statistics"),
    e("sampling-methods", "experimental-design"),
    e("linear-regression", "logistic-regression"),
    e("sampling-distributions", "bootstrap-methods"),
    e("point-estimation", "sufficient-statistics"),
    e("point-estimation", "maximum-likelihood"),
    e("logistic-regression", "survival-analysis-intro"),
    e("t-test", "anova", "related"),
])

# ═══════════════════════════════════════════════════════════════
# 10. DISCRETE MATH (离散数学) — 22 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("propositional-logic",  "命题逻辑",        "命题、联结词、真值表、等价", "discrete-math", 4, tags=["基础"]),
    c("predicate-logic",      "谓词逻辑",        "量词、谓词、自由变量与约束变量", "discrete-math", 5, tags=["核心"]),
    c("proof-techniques",     "证明方法",        "直接证明、反证法、归纳法、构造法", "discrete-math", 5, milestone=True, tags=["里程碑"]),
    c("set-theory",           "集合论",          "集合运算、子集、幂集、笛卡尔积", "discrete-math", 4, tags=["基础"]),
    c("relations",            "关系",            "二元关系、等价关系、偏序关系", "discrete-math", 6, tags=["核心"]),
    c("functions-discrete",   "函数(离散)",      "单射、满射、双射、鸽巢原理", "discrete-math", 5, tags=["核心"]),
    c("graph-theory-basics",  "图论基础",        "图的定义、度、路径、连通", "discrete-math", 5, tags=["核心"]),
    c("trees",                "树",             "树的定义、生成树、二叉树", "discrete-math", 6, tags=["核心"]),
    c("euler-hamilton",       "欧拉路与哈密顿路", "欧拉回路定理、哈密顿路判定", "discrete-math", 6, tags=["经典"]),
    c("graph-coloring",       "图着色",          "顶点着色、色数、四色定理", "discrete-math", 7, tags=["经典"]),
    c("planar-graphs",        "平面图",          "Euler公式V-E+F=2, Kuratowski定理", "discrete-math", 7, tags=["进阶"]),
    c("boolean-algebra",      "布尔代数",        "布尔代数的公理系统与应用", "discrete-math", 5, tags=["核心"]),
    c("combinatorial-identities","组合恒等式",   "Vandermonde、Hockey Stick等经典恒等式", "discrete-math", 6, tags=["进阶"]),
    c("inclusion-exclusion",  "容斥原理",        "集合的容斥计数公式", "discrete-math", 6, tags=["核心"]),
    c("recurrence-relations", "递推关系",        "线性递推、特征方程法", "discrete-math", 6, tags=["核心"]),
    c("generating-func-disc", "生成函数(离散)",  "普通型与指数型生成函数", "discrete-math", 7, tags=["进阶"]),
    c("modular-arithmetic",   "模运算",          "同余、模加/乘、欧拉函数", "discrete-math", 5, tags=["核心"]),
    c("group-theory-intro",   "群论初步",        "群、子群、陪集、Lagrange定理", "discrete-math", 8, milestone=True, tags=["里程碑"]),
    c("lattice-order",        "格与偏序",        "格的定义、Hasse图、布尔格", "discrete-math", 7, tags=["进阶"]),
    c("automata-intro",       "自动机初步",      "DFA、NFA、正则语言", "discrete-math", 7, tags=["应用"]),
    c("computational-complexity-intro","计算复杂性初步","P, NP, NP-完全", "discrete-math", 8, tags=["拓展"]),
    c("catalan-numbers",      "卡特兰数",        "卡特兰数的递推、组合解释", "discrete-math", 7, tags=["经典"]),
])

edges.extend([
    e("number-sets", "set-theory"),
    e("propositional-logic", "predicate-logic"),
    e("propositional-logic", "proof-techniques"),
    e("mathematical-induction", "proof-techniques"),
    e("set-theory", "relations"),
    e("set-theory", "functions-discrete"),
    e("functions-discrete", "graph-theory-basics"),
    e("graph-theory-basics", "trees"),
    e("graph-theory-basics", "euler-hamilton"),
    e("graph-theory-basics", "graph-coloring"),
    e("graph-theory-basics", "planar-graphs"),
    e("euler-formula-polyhedra", "planar-graphs"),
    e("propositional-logic", "boolean-algebra"),
    e("combinations", "combinatorial-identities"),
    e("combinations", "inclusion-exclusion"),
    e("sequences-intro", "recurrence-relations"),
    e("recurrence-relations", "generating-func-disc"),
    e("generating-functions", "generating-func-disc"),
    e("divisibility", "modular-arithmetic"),
    e("gcd-lcm", "modular-arithmetic"),
    e("modular-arithmetic", "group-theory-intro"),
    e("relations", "lattice-order"),
    e("boolean-algebra", "lattice-order"),
    e("graph-theory-basics", "automata-intro"),
    e("proof-techniques", "computational-complexity-intro"),
    e("automata-intro", "computational-complexity-intro"),
    e("recurrence-relations", "catalan-numbers"),
    e("combinations", "catalan-numbers"),
    e("set-theory", "propositional-logic", "related"),
    e("trees", "euler-hamilton", "related"),
])

# ═══════════════════════════════════════════════════════════════
# 11. NUMBER THEORY (数论) — 18 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("primes",               "素数",           "素数的定义、算术基本定理", "number-theory", 3, tags=["基础"]),
    c("euclidean-algorithm",  "欧几里得算法",    "辗转相除法求GCD", "number-theory", 4, tags=["核心"]),
    c("bezout-identity",      "裴蜀等式",        "ax+by=gcd(a,b)的存在性与扩展欧几里得", "number-theory", 5, tags=["核心"]),
    c("congruences",          "同余理论",        "同余的基本性质与应用", "number-theory", 5, milestone=True, tags=["里程碑"]),
    c("fermats-little-theorem","费马小定理",     "a^(p-1)≡1(mod p)", "number-theory", 6, tags=["定理"]),
    c("euler-theorem",        "欧拉定理",        "a^φ(n)≡1(mod n)与欧拉函数", "number-theory", 7, tags=["定理"]),
    c("chinese-remainder",    "中国剩余定理",    "同余方程组的求解", "number-theory", 7, milestone=True, tags=["里程碑"]),
    c("quadratic-residues",   "二次剩余",        "Legendre符号、二次互反律", "number-theory", 8, tags=["进阶"]),
    c("diophantine-equations","丢番图方程",      "整数解的存在与求法", "number-theory", 7, tags=["经典"]),
    c("pythagorean-triples",  "勾股数组",        "本原勾股数的参数化表示", "number-theory", 5, tags=["经典"]),
    c("perfect-numbers",      "完全数",          "完全数与梅森素数的关系", "number-theory", 5, tags=["趣味"]),
    c("prime-distribution",   "素数分布",        "素数定理π(x)~x/ln(x)", "number-theory", 8, tags=["进阶"]),
    c("continued-fractions",  "连分数",          "有限与无限连分数、最佳有理逼近", "number-theory", 7, tags=["经典"]),
    c("p-adic-intro",         "p进数初步",       "p进绝对值与p进数的直觉", "number-theory", 9, tags=["拓展"]),
    c("cryptography-number-theory","密码学中的数论","RSA算法、离散对数", "number-theory", 7, tags=["应用"]),
    c("arithmetic-functions", "算术函数",        "φ(n)、μ(n)、σ(n)、Möbius反演", "number-theory", 7, tags=["进阶"]),
    c("sum-of-squares",       "平方和定理",      "两平方和与四平方和定理", "number-theory", 7, tags=["经典"]),
    c("fibonacci-properties", "Fibonacci数的性质","Fibonacci数论性质与黄金比例", "number-theory", 5, tags=["趣味"]),
])

edges.extend([
    e("divisibility", "primes"),
    e("gcd-lcm", "euclidean-algorithm"),
    e("euclidean-algorithm", "bezout-identity"),
    e("modular-arithmetic", "congruences"),
    e("primes", "congruences"),
    e("congruences", "fermats-little-theorem"),
    e("fermats-little-theorem", "euler-theorem"),
    e("congruences", "chinese-remainder"),
    e("congruences", "quadratic-residues"),
    e("bezout-identity", "diophantine-equations"),
    e("pythagorean-theorem", "pythagorean-triples"),
    e("congruences", "pythagorean-triples"),
    e("primes", "perfect-numbers"),
    e("primes", "prime-distribution"),
    e("limits-concept", "prime-distribution"),
    e("euclidean-algorithm", "continued-fractions"),
    e("congruences", "p-adic-intro"),
    e("euler-theorem", "cryptography-number-theory"),
    e("primes", "cryptography-number-theory"),
    e("euler-theorem", "arithmetic-functions"),
    e("primes", "arithmetic-functions"),
    e("congruences", "sum-of-squares"),
    e("recurrence-relations", "fibonacci-properties"),
    e("geometric-sequence", "fibonacci-properties", "related"),
])

# ═══════════════════════════════════════════════════════════════
# 12. OPTIMIZATION (最优化) — 18 nodes
# ═══════════════════════════════════════════════════════════════
concepts.extend([
    c("linear-programming",   "线性规划",        "线性目标函数、约束条件、可行域", "optimization", 5, tags=["核心"]),
    c("simplex-method",       "单纯形法",        "单纯形算法的步骤与几何解释", "optimization", 7, tags=["核心"]),
    c("duality-lp",           "对偶理论",        "线性规划的对偶问题与强对偶性", "optimization", 8, tags=["进阶"]),
    c("unconstrained-opt",    "无约束优化",      "极值条件、Hessian矩阵判定", "optimization", 6, milestone=True, tags=["里程碑"]),
    c("gradient-descent",     "梯度下降",        "梯度下降法、学习率、收敛条件", "optimization", 6, tags=["核心"]),
    c("newtons-method-opt",   "牛顿法(优化)",    "牛顿法求极值、二阶收敛", "optimization", 7, tags=["核心"]),
    c("constrained-opt",      "约束优化",        "等式约束与不等式约束问题", "optimization", 7, tags=["核心"]),
    c("lagrange-multipliers", "拉格朗日乘数法",   "等式约束的KKT条件前身", "optimization", 7, milestone=True, tags=["里程碑"]),
    c("kkt-conditions",       "KKT条件",        "不等式约束优化的必要条件", "optimization", 8, tags=["进阶"]),
    c("convex-optimization",  "凸优化",          "凸集、凸函数、全局最优性", "optimization", 8, tags=["核心"]),
    c("integer-programming",  "整数规划",        "整数约束、分支定界法", "optimization", 8, tags=["进阶"]),
    c("dynamic-programming-math","动态规划(数学)","最优子结构、Bellman方程", "optimization", 7, tags=["核心"]),
    c("calculus-of-variations","变分法",         "泛函极值、Euler-Lagrange方程", "optimization", 9, tags=["拓展"]),
    c("game-theory-intro",    "博弈论初步",      "零和博弈、纳什均衡、支付矩阵", "optimization", 7, tags=["应用"]),
    c("network-flows",        "网络流",          "最大流最小割定理、Ford-Fulkerson", "optimization", 7, tags=["应用"]),
    c("multi-objective-opt",  "多目标优化",      "Pareto最优、权重法、ε-约束法", "optimization", 8, tags=["进阶"]),
    c("stochastic-optimization","随机优化",      "随机梯度下降、模拟退火", "optimization", 8, tags=["应用"]),
    c("semidefinite-programming","半定规划",     "SDP的概念与应用", "optimization", 9, tags=["拓展"]),
])

edges.extend([
    e("systems-of-equations", "linear-programming"),
    e("linear-inequalities", "linear-programming"),
    e("linear-programming", "simplex-method"),
    e("simplex-method", "duality-lp"),
    e("partial-derivatives", "unconstrained-opt"),
    e("positive-definite", "unconstrained-opt"),
    e("gradient-directional", "gradient-descent"),
    e("unconstrained-opt", "gradient-descent"),
    e("unconstrained-opt", "newtons-method-opt"),
    e("inverse-matrix", "newtons-method-opt"),
    e("unconstrained-opt", "constrained-opt"),
    e("constrained-opt", "lagrange-multipliers"),
    e("lagrange-multipliers", "kkt-conditions"),
    e("kkt-conditions", "convex-optimization"),
    e("linear-programming", "integer-programming"),
    e("recurrence-relations", "dynamic-programming-math"),
    e("optimization-calculus", "dynamic-programming-math"),
    e("differential-equations-intro", "calculus-of-variations"),
    e("linear-programming", "game-theory-intro"),
    e("matrix-multiplication", "game-theory-intro"),
    e("graph-theory-basics", "network-flows"),
    e("linear-programming", "network-flows"),
    e("constrained-opt", "multi-objective-opt"),
    e("gradient-descent", "stochastic-optimization"),
    e("expectation-variance", "stochastic-optimization"),
    e("convex-optimization", "semidefinite-programming"),
    e("positive-definite", "semidefinite-programming"),
    e("convex-optimization", "gradient-descent", "related"),
])

# ═══════════════════════════════════════════════════════════════
# Validate & Build
# ═══════════════════════════════════════════════════════════════
# Dedup check
ids = [c["id"] for c in concepts]
assert len(ids) == len(set(ids)), f"Duplicate concept IDs: {[x for x in ids if ids.count(x)>1]}"

# Edge reference check
id_set = set(ids)
for edge in edges:
    assert edge["source_id"] in id_set, f"Invalid source: {edge['source_id']}"
    assert edge["target_id"] in id_set, f"Invalid target: {edge['target_id']}"

# Deduplicate edges
edge_keys = set()
deduped = []
for edge in edges:
    key = (edge["source_id"], edge["target_id"], edge["relation_type"])
    if key not in edge_keys:
        edge_keys.add(key)
        deduped.append(edge)
edges = deduped

# Count per subdomain
from collections import Counter
sub_counts = Counter(c["subdomain_id"] for c in concepts)
diff_counts = Counter(c["difficulty"] for c in concepts)
milestones = [c["id"] for c in concepts if c["is_milestone"]]

print(f"Total concepts: {len(concepts)}")
print(f"Total edges: {len(edges)}")
print(f"Milestones: {len(milestones)}")
print(f"Subdomains: {dict(sub_counts)}")
print(f"Difficulty: {dict(sorted(diff_counts.items()))}")

# Check connectivity (no orphans)
from collections import defaultdict
adj = defaultdict(set)
for e_ in edges:
    adj[e_["source_id"]].add(e_["target_id"])
    adj[e_["target_id"]].add(e_["source_id"])
orphans = [c for c in ids if c not in adj]
if orphans:
    print(f"WARNING: Orphan nodes: {orphans}")
else:
    print("✅ No orphan nodes")

meta = {
    "total_concepts": len(concepts),
    "total_edges": len(edges),
    "total_milestones": len(milestones),
    "subdomain_counts": dict(sub_counts),
    "difficulty_distribution": dict(sorted(diff_counts.items()))
}

graph = {
    "domain": DOMAIN,
    "subdomains": SUBDOMAINS,
    "concepts": concepts,
    "edges": edges,
    "meta": meta
}

out_path = "seed_graph.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)

print(f"\n✅ Generated {out_path}")
print(f"   {len(concepts)} concepts, {len(edges)} edges, {len(milestones)} milestones")
