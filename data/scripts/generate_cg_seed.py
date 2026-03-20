#!/usr/bin/env python3
"""Generate Computer Graphics (图形学) knowledge sphere seed graph.

Phase 22: 250 concepts, 12 subdomains, ~37 milestones
Domain: computer-graphics
"""

import json
import os

DOMAIN_ID = "computer-graphics"

SUBDOMAINS = [
    {"id": "rasterization",       "name": "光栅化",     "order": 1},
    {"id": "ray-tracing",         "name": "光线追踪",   "order": 2},
    {"id": "pbr-materials",       "name": "PBR材质",    "order": 3},
    {"id": "global-illumination", "name": "全局光照",   "order": 4},
    {"id": "post-processing",     "name": "后处理",     "order": 5},
    {"id": "gpu-architecture",    "name": "GPU架构",    "order": 6},
    {"id": "shader-programming",  "name": "Shader编程", "order": 7},
    {"id": "texture-techniques",  "name": "纹理技术",   "order": 8},
    {"id": "geometry-processing", "name": "几何处理",   "order": 9},
    {"id": "volume-rendering",    "name": "体积渲染",   "order": 10},
    {"id": "anti-aliasing",       "name": "抗锯齿",     "order": 11},
    {"id": "render-optimization", "name": "渲染优化",   "order": 12},
]

# ── Concepts per subdomain ──────────────────────────────────────────
# Each tuple: (id, name, description, difficulty, est_min, content_type, tags, is_milestone)

def _c(id, name, desc, diff, mins, ctype, tags, ms=False):
    return {
        "id": id,
        "name": name,
        "description": desc,
        "subdomain_id": None,  # filled later
        "domain_id": DOMAIN_ID,
        "difficulty": diff,
        "estimated_minutes": mins,
        "content_type": ctype,
        "tags": tags,
        "is_milestone": ms,
    }

CONCEPTS_BY_SUBDOMAIN = {
    # ── 1. 光栅化 (22 concepts) ────────────────────────────────
    "rasterization": [
        _c("cg-raster-intro",       "光栅化概述",           "光栅化渲染管线的定义、历史与基本流程", 1, 20, "theory", ["基础"], True),
        _c("cg-raster-pipeline",    "图形管线阶段",         "应用阶段→几何阶段→光栅化阶段→像素阶段的完整流程", 1, 25, "theory", ["基础"]),
        _c("cg-vertex-transform",   "顶点变换",             "模型空间→世界空间→观察空间→裁剪空间的矩阵变换链", 2, 30, "theory", ["数学"]),
        _c("cg-projection",         "投影变换",             "透视投影与正交投影的矩阵推导与应用场景", 2, 30, "theory", ["数学"]),
        _c("cg-clipping",           "裁剪",                 "Cohen-Sutherland、Sutherland-Hodgman等裁剪算法", 2, 25, "theory", ["算法"]),
        _c("cg-viewport-transform", "视口变换",             "NDC到屏幕坐标的映射与像素中心约定", 2, 20, "theory", ["基础"]),
        _c("cg-triangle-setup",     "三角形装配",           "图元组装、面剔除与三角形遍历", 2, 25, "theory", ["核心"]),
        _c("cg-scanline",           "扫描线转换",           "扫描线填充算法与边表数据结构", 2, 25, "theory", ["算法"]),
        _c("cg-interpolation",      "属性插值",             "重心坐标插值与透视校正插值", 3, 30, "theory", ["数学"], True),
        _c("cg-depth-buffer",       "深度缓冲",             "Z-Buffer算法、深度精度与反向Z", 2, 25, "theory", ["核心"]),
        _c("cg-stencil-buffer",     "模板缓冲",             "模板测试的原理与应用（轮廓、镜面、阴影体）", 3, 25, "theory", ["进阶"]),
        _c("cg-early-z",            "Early-Z优化",          "Early-Z测试与Hi-Z剔除的硬件实现", 3, 20, "theory", ["优化"]),
        _c("cg-blending",           "Alpha混合",            "混合方程、预乘Alpha与顺序无关透明", 2, 25, "theory", ["核心"]),
        _c("cg-msaa",               "多重采样抗锯齿",       "MSAA的硬件实现与性能特征", 3, 25, "theory", ["抗锯齿"]),
        _c("cg-forward-rendering",  "前向渲染",             "前向渲染的光照计算流程与多光源限制", 2, 25, "theory", ["架构"], True),
        _c("cg-deferred-rendering", "延迟渲染",             "G-Buffer架构、延迟光照与材质多样性问题", 3, 30, "theory", ["架构"], True),
        _c("cg-forward-plus",       "Forward+",             "分块光源剔除与Forward+渲染管线", 3, 30, "theory", ["架构"]),
        _c("cg-tiled-rendering",    "分块渲染",             "Tile-Based Deferred Rendering与移动端优化", 3, 25, "theory", ["移动端"]),
        _c("cg-clustered-rendering","簇式渲染",             "3D光源分簇与Clustered Forward/Deferred", 4, 30, "theory", ["进阶"]),
        _c("cg-visibility-buffer",  "可见性缓冲",           "Visibility Buffer渲染管线与材质解耦", 4, 30, "theory", ["前沿"]),
        _c("cg-indirect-draw",      "间接绘制",             "GPU-Driven Rendering与Indirect Draw Call", 4, 30, "theory", ["进阶"]),
        _c("cg-mesh-shader",        "Mesh Shader",          "网格着色器管线与传统管线对比", 4, 30, "theory", ["前沿"]),
    ],

    # ── 2. 光线追踪 (21 concepts) ──────────────────────────────
    "ray-tracing": [
        _c("cg-rt-intro",           "光线追踪概述",         "光线追踪的基本原理、历史与Whitted模型", 1, 20, "theory", ["基础"], True),
        _c("cg-ray-generation",     "光线生成",             "相机模型与主光线生成算法", 2, 25, "theory", ["核心"]),
        _c("cg-ray-intersection",   "光线求交",             "光线与球体、平面、三角形的交点计算", 2, 30, "theory", ["数学"]),
        _c("cg-bvh",                "BVH加速结构",          "层次包围盒的构建算法（SAH、LBVH）与遍历", 3, 35, "theory", ["算法"], True),
        _c("cg-kd-tree",            "KD-Tree",              "KD树空间划分与遍历策略", 3, 30, "theory", ["算法"]),
        _c("cg-rt-shadows",         "光追阴影",             "阴影光线与软阴影采样策略", 2, 25, "theory", ["光照"]),
        _c("cg-rt-reflection",      "光追反射",             "镜面反射与光泽反射的采样方法", 2, 25, "theory", ["光照"]),
        _c("cg-rt-refraction",      "光追折射",             "Snell定律、全内反射与色散模拟", 3, 25, "theory", ["光照"]),
        _c("cg-path-tracing",       "路径追踪",             "蒙特卡洛路径追踪与渲染方程的数值求解", 3, 35, "theory", ["核心"], True),
        _c("cg-importance-sampling","重要性采样",           "BRDF重要性采样与方差缩减技术", 4, 35, "theory", ["数学"]),
        _c("cg-mis",                "多重重要性采样",       "MIS权重函数与光源/BRDF联合采样", 4, 30, "theory", ["进阶"]),
        _c("cg-bidirectional-pt",   "双向路径追踪",         "BDPT算法与光子图连接策略", 4, 35, "theory", ["进阶"]),
        _c("cg-mlt",                "Metropolis光传输",     "MLT的马尔可夫链突变策略", 5, 35, "theory", ["前沿"]),
        _c("cg-photon-mapping",     "光子映射",             "两步法光子映射与焦散效果", 4, 30, "theory", ["算法"]),
        _c("cg-rt-denoising",       "光追降噪",             "时空降噪滤波器（SVGF、NRD）与AI降噪", 3, 30, "theory", ["实践"], True),
        _c("cg-rtx-hardware",       "RTX硬件加速",          "RT Core架构与DXR/Vulkan RT API", 3, 30, "theory", ["硬件"]),
        _c("cg-hybrid-rendering",   "混合渲染管线",         "光栅化+光线追踪的混合渲染架构", 3, 30, "theory", ["架构"], True),
        _c("cg-restir",             "ReSTIR",               "时空重采样的实时直接光照算法", 5, 35, "theory", ["前沿"]),
        _c("cg-sdf-tracing",        "SDF光线步进",          "有符号距离场的Sphere Tracing算法", 3, 30, "theory", ["技术"]),
        _c("cg-rt-gi",              "光追全局光照",         "基于光线追踪的实时GI方案（RTXGI、DDGI）", 4, 35, "theory", ["前沿"]),
        _c("cg-spectral-rendering", "光谱渲染",             "多波长光线追踪与色散精确模拟", 5, 30, "theory", ["前沿"]),
    ],

    # ── 3. PBR材质 (20 concepts) ───────────────────────────────
    "pbr-materials": [
        _c("cg-pbr-intro",          "PBR材质概述",          "物理渲染的核心原则——能量守恒与微表面理论", 1, 20, "theory", ["基础"], True),
        _c("cg-brdf",               "BRDF基础",             "双向反射分布函数的定义与性质", 2, 25, "theory", ["核心"]),
        _c("cg-cook-torrance",      "Cook-Torrance模型",    "微表面BRDF：D·F·G项的物理含义", 3, 30, "theory", ["核心"], True),
        _c("cg-ndf",                "法线分布函数",         "GGX/Beckmann/Blinn-Phong NDF的对比与选择", 3, 30, "theory", ["数学"]),
        _c("cg-fresnel",            "菲涅尔效应",           "Schlick近似与完整菲涅尔方程", 2, 25, "theory", ["物理"]),
        _c("cg-geometry-term",      "几何遮蔽项",           "Smith遮蔽函数与Height-Correlated模型", 3, 25, "theory", ["数学"]),
        _c("cg-metallic-workflow",  "金属度工作流",         "Metallic-Roughness工作流的参数含义与纹理制作", 2, 25, "theory", ["实践"]),
        _c("cg-specular-workflow",  "高光工作流",           "Specular-Glossiness工作流与金属度工作流对比", 2, 25, "theory", ["实践"]),
        _c("cg-subsurface",         "次表面散射",           "SSS的物理原理与屏幕空间/预积分近似", 4, 35, "theory", ["进阶"], True),
        _c("cg-clear-coat",         "清漆层",               "多层材质模型与清漆BRDF叠加", 3, 25, "theory", ["进阶"]),
        _c("cg-anisotropy",         "各向异性",             "各向异性BRDF与切线空间参数化", 3, 30, "theory", ["进阶"]),
        _c("cg-cloth-shading",      "布料着色",             "Ashikhmin/Charlie模型与布料BRDF特征", 3, 30, "theory", ["进阶"]),
        _c("cg-hair-shading",       "毛发着色",             "Marschner模型与双高光毛发渲染", 4, 35, "theory", ["进阶"]),
        _c("cg-eye-rendering",      "眼球渲染",             "虹膜折射、焦散与睫毛投影的专项技术", 4, 30, "theory", ["进阶"]),
        _c("cg-skin-rendering",     "皮肤渲染",             "预积分SSS、屏幕空间扩散与皮肤纹理", 4, 35, "theory", ["进阶"]),
        _c("cg-iridescence",        "薄膜干涉",             "薄膜干涉光学模型与彩虹色材质", 4, 25, "theory", ["前沿"]),
        _c("cg-energy-conservation","能量守恒",             "多散射补偿与能量守恒校正技术", 3, 25, "theory", ["核心"]),
        _c("cg-material-layering",  "材质分层",             "多层材质系统与层间能量传递", 4, 30, "theory", ["架构"]),
        _c("cg-disney-brdf",        "Disney BRDF",          "Disney Principled BRDF的参数设计与工业应用", 3, 30, "theory", ["核心"], True),
        _c("cg-btdf",               "透射BRDF",             "BTDF与BSDF统一框架、微表面折射模型", 4, 30, "theory", ["进阶"]),
    ],

    # ── 4. 全局光照 (21 concepts) ──────────────────────────────
    "global-illumination": [
        _c("cg-gi-intro",           "全局光照概述",         "直接光照与间接光照、渲染方程与GI方法分类", 1, 20, "theory", ["基础"], True),
        _c("cg-rendering-equation", "渲染方程",             "Kajiya渲染方程的数学形式与物理含义", 2, 30, "theory", ["核心"], True),
        _c("cg-radiometry",         "辐射度量学",           "辐射通量、辐照度、辐射亮度等基本量", 2, 30, "theory", ["物理"]),
        _c("cg-radiosity",          "辐射度方法",           "有限元辐射度方法与形状因子计算", 3, 30, "theory", ["经典"]),
        _c("cg-ambient-occlusion",  "环境光遮蔽",          "SSAO/HBAO/GTAO的原理与实现对比", 2, 30, "theory", ["实践"], True),
        _c("cg-irradiance-map",     "辐照度贴图",           "Irradiance Map预计算与球谐系数存储", 3, 25, "theory", ["技术"]),
        _c("cg-spherical-harmonics","球谐函数",             "SH基函数在光照表示中的应用", 3, 35, "theory", ["数学"]),
        _c("cg-light-probes",       "光探针",               "Light Probe的放置策略与运行时采样", 2, 25, "theory", ["实践"]),
        _c("cg-reflection-probes",  "反射探针",             "Reflection Probe的捕获与视差校正", 2, 25, "theory", ["实践"]),
        _c("cg-screen-space-gi",    "屏幕空间GI",           "SSGI/SSDO的原理、优势与伪影", 3, 30, "theory", ["技术"]),
        _c("cg-lpv",                "光传播体积",           "Light Propagation Volumes的实现与局限", 3, 30, "theory", ["技术"]),
        _c("cg-voxel-gi",           "体素全局光照",         "VXGI/SVOGI的体素化与锥追踪", 4, 35, "theory", ["进阶"], True),
        _c("cg-lumen",              "Lumen系统",            "UE5 Lumen的SDF追踪与屏幕追踪混合策略", 4, 35, "theory", ["引擎"]),
        _c("cg-ddgi",               "DDGI",                 "Dynamic Diffuse Global Illumination的探针更新机制", 4, 35, "theory", ["前沿"]),
        _c("cg-lightmap-baking",    "光照图烘焙",           "Lightmap的UV展开、烘焙参数与压缩方案", 2, 30, "theory", ["实践"]),
        _c("cg-irradiance-volume",  "辐照度体积",           "3D纹理存储的辐照度体积与SH编码", 3, 25, "theory", ["技术"]),
        _c("cg-caustics",           "焦散",                 "焦散效果的光子映射与SDF近似方法", 4, 30, "theory", ["进阶"]),
        _c("cg-sky-atmosphere",     "天空与大气",           "大气散射模型（Rayleigh/Mie）与天空盒渲染", 3, 30, "theory", ["环境"]),
        _c("cg-cloud-rendering",    "云渲染",               "体积云的Ray Marching与光照散射", 4, 35, "theory", ["环境"]),
        _c("cg-indirect-specular",  "间接高光",             "屏幕空间反射(SSR)与平面反射", 3, 30, "theory", ["技术"]),
        _c("cg-gi-hybrid",          "混合GI方案",           "离线烘焙+实时探针+屏幕空间的多层GI混合", 4, 30, "theory", ["架构"], True),
    ],

    # ── 5. 后处理 (21 concepts) ────────────────────────────────
    "post-processing": [
        _c("cg-pp-intro",           "后处理概述",           "后处理管线的定义、常见效果与性能考量", 1, 20, "theory", ["基础"], True),
        _c("cg-tone-mapping",       "色调映射",             "Reinhard/ACES/GT Filmic色调映射算子的对比", 2, 25, "theory", ["核心"], True),
        _c("cg-color-grading",      "色彩分级",             "LUT色彩查找表与ASC-CDL色彩校正", 2, 25, "theory", ["艺术"]),
        _c("cg-bloom",              "泛光",                 "高亮提取→高斯模糊→叠加的Bloom流程与阈值策略", 2, 25, "theory", ["效果"]),
        _c("cg-dof",                "景深",                 "Circle of Confusion、Bokeh形状与散景模拟", 3, 30, "theory", ["效果"], True),
        _c("cg-motion-blur",        "运动模糊",             "Per-Object与Camera Motion Blur的Velocity Buffer方案", 3, 30, "theory", ["效果"]),
        _c("cg-lens-flare",         "镜头光晕",             "Screen-Space Lens Flare与光学模拟", 2, 25, "theory", ["效果"]),
        _c("cg-chromatic-aberration","色散",                "色差效果的实现与艺术控制", 2, 20, "theory", ["效果"]),
        _c("cg-vignette",           "暗角",                 "光学暗角与艺术暗角的参数化控制", 1, 15, "theory", ["效果"]),
        _c("cg-film-grain",         "胶片颗粒",             "程序化颗粒噪点的生成与时间抖动", 2, 20, "theory", ["效果"]),
        _c("cg-sharpening",         "锐化",                 "CAS/RCAS锐化滤波器与Unsharp Mask", 2, 20, "theory", ["效果"]),
        _c("cg-exposure",           "自动曝光",             "直方图自动曝光与EV适应", 2, 25, "theory", ["核心"]),
        _c("cg-fog-pp",             "雾效",                 "线性/指数/高度雾与体积雾后处理", 2, 25, "theory", ["效果"]),
        _c("cg-ssr",                "屏幕空间反射",         "Screen-Space Reflection的Hi-Z Ray March实现", 3, 30, "theory", ["核心"]),
        _c("cg-outline",            "描边效果",             "基于深度/法线不连续性的边缘检测描边", 2, 25, "theory", ["风格化"]),
        _c("cg-cel-shading",        "赛璐璐着色",           "Toon Shading的阶梯化光照与轮廓线", 2, 25, "theory", ["风格化"]),
        _c("cg-pixel-art-filter",   "像素化滤镜",           "降分辨率+调色板量化的像素风格化", 2, 20, "theory", ["风格化"]),
        _c("cg-hdr-pipeline",       "HDR管线",              "线性HDR工作流与显示映射策略", 2, 25, "theory", ["架构"]),
        _c("cg-pp-volume",          "后处理体积",           "空间化的后处理参数混合与优先级", 3, 25, "theory", ["引擎"]),
        _c("cg-eye-adaptation",     "明暗适应",             "人眼明暗适应的模拟与过渡曲线", 3, 25, "theory", ["进阶"]),
        _c("cg-pp-stack",           "后处理栈设计",         "后处理效果的排序依赖与性能预算管理", 3, 25, "theory", ["架构"], True),
    ],

    # ── 6. GPU架构 (21 concepts) ───────────────────────────────
    "gpu-architecture": [
        _c("cg-gpu-intro",          "GPU架构概述",          "GPU与CPU的架构差异、SIMT执行模型", 1, 20, "theory", ["基础"], True),
        _c("cg-gpu-pipeline",       "GPU硬件管线",          "图形管线的硬件固定功能单元与可编程单元", 2, 25, "theory", ["核心"]),
        _c("cg-gpu-memory",         "GPU内存层级",          "VRAM/L2/L1/共享内存/寄存器的层级与带宽", 2, 25, "theory", ["核心"], True),
        _c("cg-warp-wavefront",     "Warp/Wavefront",       "线程束执行模型与分支发散代价", 3, 30, "theory", ["核心"]),
        _c("cg-occupancy",          "占用率",               "Occupancy的计算、寄存器压力与Latency Hiding", 3, 30, "theory", ["优化"]),
        _c("cg-gpu-scheduling",     "GPU调度",              "线程块调度与上下文切换的零开销模型", 3, 25, "theory", ["进阶"]),
        _c("cg-texture-unit",       "纹理单元",             "TMU的各向异性采样与缓存命中优化", 2, 25, "theory", ["硬件"]),
        _c("cg-rop",                "ROP",                  "光栅化输出单元的混合/深度/模板操作", 2, 20, "theory", ["硬件"]),
        _c("cg-tmu-cache",          "纹理缓存",             "纹理缓存的行为模式与Mipmap的缓存友好性", 3, 25, "theory", ["优化"]),
        _c("cg-compute-shader",     "Compute Shader",       "通用计算着色器的线程组模型与同步原语", 3, 30, "theory", ["核心"], True),
        _c("cg-async-compute",      "异步计算",             "Graphics/Compute/Copy队列的并行执行", 3, 25, "theory", ["进阶"]),
        _c("cg-gpu-driven",         "GPU Driven Pipeline",  "间接绘制/GPU剔除/Bindless的GPU驱动渲染", 4, 35, "theory", ["前沿"], True),
        _c("cg-bindless",           "Bindless资源",         "Bindless Texture/Buffer的描述符管理", 4, 30, "theory", ["进阶"]),
        _c("cg-dx12-vk",            "DX12/Vulkan基础",      "现代图形API的命令缓冲/描述符堆/管线状态对象", 3, 35, "theory", ["API"]),
        _c("cg-command-buffer",     "命令缓冲",             "命令录制、提交与多线程命令构建", 3, 30, "theory", ["API"]),
        _c("cg-render-pass",        "渲染Pass",             "Render Pass/Subpass的依赖声明与Tile Memory", 3, 25, "theory", ["API"]),
        _c("cg-descriptor-set",     "描述符集",             "Descriptor Set/Root Signature的绑定模型", 3, 25, "theory", ["API"]),
        _c("cg-pipeline-barrier",   "管线屏障",             "资源状态转换与内存屏障的正确使用", 4, 30, "theory", ["API"]),
        _c("cg-gpu-profiling",      "GPU性能分析",          "GPU Timer/PIX/NSight的Profiling方法论", 3, 30, "theory", ["实践"], True),
        _c("cg-mobile-gpu",         "移动端GPU",            "Tile-Based架构(Mali/Adreno)的渲染特性", 3, 30, "theory", ["移动端"]),
        _c("cg-ray-tracing-hw",     "光追硬件单元",         "RT Core/Ray Accelerator的BVH遍历硬件", 4, 30, "theory", ["硬件"]),
    ],

    # ── 7. Shader编程 (21 concepts) ────────────────────────────
    "shader-programming": [
        _c("cg-shader-intro",       "Shader概述",           "着色器的类型、编译流程与着色语言生态", 1, 20, "theory", ["基础"], True),
        _c("cg-vertex-shader",      "顶点着色器",           "顶点着色器的输入/输出语义与空间变换", 2, 25, "theory", ["核心"]),
        _c("cg-fragment-shader",    "片元着色器",           "片元着色器的光照计算与纹理采样", 2, 25, "theory", ["核心"], True),
        _c("cg-geometry-shader",    "几何着色器",           "几何着色器的图元扩展与性能陷阱", 3, 25, "theory", ["进阶"]),
        _c("cg-tessellation",       "细分着色器",           "Hull/Domain/Tessellation阶段与自适应LOD", 3, 30, "theory", ["进阶"], True),
        _c("cg-hlsl",               "HLSL",                 "High-Level Shading Language的语法与语义", 2, 30, "theory", ["语言"]),
        _c("cg-glsl",               "GLSL",                 "OpenGL Shading Language的特性与差异", 2, 25, "theory", ["语言"]),
        _c("cg-spirv",              "SPIR-V",               "跨平台中间表示与着色器编译工具链", 3, 25, "theory", ["工具"]),
        _c("cg-shader-model",       "Shader Model",         "SM 5.0/6.0+的特性演进与硬件对应", 3, 25, "theory", ["核心"]),
        _c("cg-uber-shader",        "Uber Shader",          "静态/动态分支的大型着色器设计与变体管理", 3, 30, "theory", ["架构"]),
        _c("cg-shader-permutation", "着色器变体",           "宏驱动变体爆炸与PSO缓存管理", 3, 30, "theory", ["优化"]),
        _c("cg-material-graph",     "材质图编辑器",         "节点式材质编辑器的设计与代码生成", 3, 30, "theory", ["工具"], True),
        _c("cg-surface-shader",     "表面着色器",           "Unity Surface Shader的抽象层与自动生成", 2, 25, "theory", ["引擎"]),
        _c("cg-material-function",  "材质函数",             "可复用材质函数/子图的设计模式", 2, 25, "theory", ["实践"]),
        _c("cg-shader-debug",       "着色器调试",           "RenderDoc/PIX/NSight中的着色器单步调试", 2, 25, "theory", ["实践"]),
        _c("cg-custom-lighting",    "自定义光照模型",       "在引擎中实现非PBR光照模型（卡通/NPR）", 3, 30, "theory", ["风格化"]),
        _c("cg-procedural-shader",  "程序化着色器",         "噪声函数（Perlin/Simplex/Worley）与程序纹理", 3, 30, "theory", ["技术"]),
        _c("cg-shader-optimization","着色器优化",           "ALU/TEX平衡、half精度、分支优化策略", 3, 30, "theory", ["优化"], True),
        _c("cg-wave-intrinsics",    "Wave Intrinsics",      "跨线程数据交换与Wave-level归约操作", 4, 30, "theory", ["进阶"]),
        _c("cg-shader-interop",     "着色器互操作",         "Compute-Graphics数据共享与UAV", 3, 25, "theory", ["进阶"]),
        _c("cg-slang",              "Slang语言",            "Slang着色器语言的可组合性与自动微分", 4, 25, "theory", ["前沿"]),
    ],

    # ── 8. 纹理技术 (21 concepts) ──────────────────────────────
    "texture-techniques": [
        _c("cg-tex-intro",          "纹理映射概述",         "纹理映射的基本原理、UV坐标与采样器", 1, 20, "theory", ["基础"], True),
        _c("cg-mipmap",             "Mipmap",               "多级纹理细节的生成算法与LOD偏移", 2, 25, "theory", ["核心"], True),
        _c("cg-aniso-filtering",    "各向异性过滤",         "各向异性纹理过滤的原理与质量级别", 2, 25, "theory", ["核心"]),
        _c("cg-normal-mapping",     "法线贴图",             "切线空间法线贴图的原理与TBN矩阵", 2, 30, "theory", ["核心"], True),
        _c("cg-parallax-mapping",   "视差贴图",             "Parallax Mapping与Parallax Occlusion Mapping", 3, 30, "theory", ["进阶"]),
        _c("cg-displacement-map",   "置换贴图",             "真实几何置换与Tessellation配合", 3, 25, "theory", ["进阶"]),
        _c("cg-cube-mapping",       "立方体贴图",           "环境映射、天空盒与反射的立方体纹理", 2, 25, "theory", ["核心"]),
        _c("cg-texture-compression","纹理压缩",             "BC1-7/ASTC/ETC2压缩格式的特性与选择", 2, 25, "theory", ["优化"]),
        _c("cg-virtual-texture",    "虚拟纹理",             "Virtual Texturing/Sparse Texture的流式加载", 4, 35, "theory", ["前沿"], True),
        _c("cg-texture-atlas",      "纹理图集",             "Atlas打包策略与UV边界处理", 2, 25, "theory", ["实践"]),
        _c("cg-texture-streaming",  "纹理流式加载",         "Mip Streaming的优先级与内存预算管理", 3, 30, "theory", ["实践"]),
        _c("cg-procedural-texture", "程序纹理",             "Noise-based程序纹理生成与实时应用", 3, 25, "theory", ["技术"]),
        _c("cg-detail-mapping",     "细节贴图",             "多层细节纹理的混合与UV缩放", 2, 20, "theory", ["实践"]),
        _c("cg-texture-projection", "纹理投影",             "Projective Texture与贴花系统基础", 2, 25, "theory", ["技术"]),
        _c("cg-decal-system",       "贴花系统",             "Deferred Decal与Screen-Space Decal的实现", 3, 25, "theory", ["技术"]),
        _c("cg-triplanar",          "三平面映射",           "无UV展开的世界空间纹理投影方法", 2, 25, "theory", ["技术"]),
        _c("cg-texture-synthesis",  "纹理合成",             "基于样本的纹理合成与无缝平铺", 3, 30, "theory", ["进阶"]),
        _c("cg-sdf-texture",        "SDF纹理",              "有符号距离场纹理在文字/UI中的应用", 3, 25, "theory", ["技术"]),
        _c("cg-material-textures",  "材质纹理集",           "Albedo/Normal/Roughness/Metallic/AO贴图工作流", 2, 25, "theory", ["实践"]),
        _c("cg-texture-baking",     "纹理烘焙",             "高模→低模的法线/AO/Curvature烘焙流程", 2, 30, "theory", ["实践"]),
        _c("cg-udim",               "UDIM",                 "多Tile UV布局与大面积纹理管理", 3, 25, "theory", ["流程"]),
    ],

    # ── 9. 几何处理 (21 concepts) ──────────────────────────────
    "geometry-processing": [
        _c("cg-geo-intro",          "几何处理概述",         "几何表示方法与处理管线概览", 1, 20, "theory", ["基础"], True),
        _c("cg-mesh-representation","网格表示",             "三角网格、半边结构与邻接关系", 2, 25, "theory", ["核心"]),
        _c("cg-mesh-simplification","网格简化",             "QEM误差度量与边折叠简化算法", 3, 30, "theory", ["算法"], True),
        _c("cg-subdivision",        "细分曲面",             "Catmull-Clark与Loop细分的规则与极限面", 3, 30, "theory", ["算法"]),
        _c("cg-lod",                "LOD系统",              "离散LOD/连续LOD/HLOD的管线设计", 2, 25, "theory", ["核心"], True),
        _c("cg-nanite",             "Nanite架构",           "UE5 Nanite的虚拟几何体与软件光栅化", 4, 35, "theory", ["前沿"], True),
        _c("cg-mesh-boolean",       "网格布尔运算",         "CSG操作的实现与鲁棒性挑战", 3, 30, "theory", ["算法"]),
        _c("cg-parametric-surface", "参数曲面",             "Bezier/B-Spline/NURBS曲面基础", 3, 30, "theory", ["数学"]),
        _c("cg-point-cloud",        "点云处理",             "点云的采集、降噪与表面重建", 3, 30, "theory", ["技术"]),
        _c("cg-isosurface",         "等值面提取",           "Marching Cubes与Dual Contouring算法", 3, 30, "theory", ["算法"]),
        _c("cg-sdf-modeling",       "SDF建模",              "有符号距离场的构建、布尔运算与可视化", 3, 30, "theory", ["技术"]),
        _c("cg-mesh-repair",        "网格修复",             "非流形/法线翻转/自交的检测与修复", 2, 25, "theory", ["实践"]),
        _c("cg-mesh-deformation",   "网格变形",             "Free-Form Deformation与骨骼蒙皮绑定", 3, 30, "theory", ["技术"]),
        _c("cg-mesh-compression",   "网格压缩",             "量化/预测/熵编码的网格压缩方案", 3, 25, "theory", ["优化"]),
        _c("cg-instancing",         "实例化渲染",           "Hardware Instancing与Indirect Instancing", 2, 25, "theory", ["优化"], True),
        _c("cg-impostor",           "替身技术",             "Billboard/Impostor Atlas用于远景简化", 3, 25, "theory", ["优化"]),
        _c("cg-terrain-geometry",   "地形几何",             "高度图、Clipmap与自适应网格", 3, 30, "theory", ["实践"]),
        _c("cg-vegetation",         "植被渲染",             "植被的LOD策略、风动画与渲染优化", 3, 30, "theory", ["实践"]),
        _c("cg-procedural-mesh",    "程序化网格",           "运行时网格生成与修改的技术方案", 3, 30, "theory", ["技术"]),
        _c("cg-mesh-streaming",     "网格流式加载",         "大场景几何的流式加载与LOD过渡", 3, 25, "theory", ["实践"]),
        _c("cg-neural-geometry",    "神经网络几何",         "NeRF与Neural SDF在几何表示中的应用", 5, 35, "theory", ["前沿"]),
    ],

    # ── 10. 体积渲染 (21 concepts) ─────────────────────────────
    "volume-rendering": [
        _c("cg-vol-intro",          "体积渲染概述",         "体积数据表示与渲染方法分类", 1, 20, "theory", ["基础"], True),
        _c("cg-ray-marching",       "Ray Marching",         "步进式体积渲染的基本算法", 2, 25, "theory", ["核心"], True),
        _c("cg-beer-lambert",       "Beer-Lambert定律",     "体积介质的光衰减与光学深度", 2, 25, "theory", ["物理"]),
        _c("cg-participating-media","参与介质",             "吸收、散射与发射的体积渲染方程", 3, 30, "theory", ["核心"]),
        _c("cg-phase-function",     "相函数",               "Henyey-Greenstein等相函数与各向异性散射", 3, 25, "theory", ["物理"]),
        _c("cg-vol-shadow",         "体积阴影",             "Shadow Ray Marching与Transmittance估算", 3, 30, "theory", ["光照"]),
        _c("cg-vol-cloud",          "体积云实现",           "噪声驱动的云密度场与光照散射计算", 3, 35, "theory", ["实践"], True),
        _c("cg-vol-fog",            "体积雾",               "Volumetric Fog的Froxel体素化方案", 3, 30, "theory", ["实践"]),
        _c("cg-god-rays",           "体积光",               "光轴散射效果（God Rays）的屏幕空间实现", 2, 25, "theory", ["效果"]),
        _c("cg-vol-texture",        "3D纹理",               "体积纹理的生成、采样与压缩", 2, 25, "theory", ["技术"]),
        _c("cg-fluid-rendering",    "流体渲染",             "SPH/Grid粒子流体的表面提取与渲染", 4, 35, "theory", ["模拟"]),
        _c("cg-fire-explosion",     "火焰与爆炸",           "火焰体积渲染的温度-颜色映射与风场", 3, 30, "theory", ["效果"]),
        _c("cg-smoke-sim",          "烟雾模拟",             "Euler/Lagrange方法的烟雾模拟基础", 4, 35, "theory", ["模拟"]),
        _c("cg-heterogeneous",      "异构体积",             "非均匀介质的Delta Tracking采样", 4, 30, "theory", ["进阶"]),
        _c("cg-vol-gi",             "体积全局光照",         "体积散射中的多重散射近似方法", 4, 35, "theory", ["进阶"]),
        _c("cg-openvdb",            "OpenVDB",              "稀疏体积数据的VDB数据结构", 3, 30, "theory", ["工具"]),
        _c("cg-medical-vis",        "医学可视化",           "CT/MRI数据的传递函数与体绘制", 3, 30, "theory", ["应用"]),
        _c("cg-scientific-vis",     "科学可视化",           "矢量场/标量场的可视化技术", 3, 25, "theory", ["应用"]),
        _c("cg-vol-decal",          "体积贴花",             "3D空间投影的体积贴花系统", 3, 25, "theory", ["技术"]),
        _c("cg-atmosphere-scatter", "大气散射实现",         "单/多次散射的预计算查表方案", 4, 35, "theory", ["环境"]),
        _c("cg-neural-radiance",    "神经辐射场",           "NeRF的体积渲染公式与训练原理", 5, 35, "theory", ["前沿"], True),
    ],

    # ── 11. 抗锯齿 (20 concepts) ──────────────────────────────
    "anti-aliasing": [
        _c("cg-aa-intro",           "抗锯齿概述",           "锯齿产生的原因——采样定理与Nyquist频率", 1, 20, "theory", ["基础"], True),
        _c("cg-ssaa",               "SSAA",                 "超级采样抗锯齿的原理与性能开销", 2, 20, "theory", ["基础"]),
        _c("cg-msaa-detail",        "MSAA详解",             "多重采样的覆盖掩码与解析过程", 2, 25, "theory", ["核心"], True),
        _c("cg-fxaa",               "FXAA",                 "Fast Approximate AA的边缘检测与亚像素位移", 2, 25, "theory", ["核心"]),
        _c("cg-smaa",               "SMAA",                 "基于图案匹配的形态学抗锯齿", 3, 30, "theory", ["核心"], True),
        _c("cg-taa",                "TAA",                   "时间性抗锯齿的抖动采样与历史帧混合", 3, 35, "theory", ["核心"], True),
        _c("cg-taa-ghosting",       "TAA鬼影",              "Ghosting的成因——遮挡/去遮挡与对策", 3, 25, "theory", ["问题"]),
        _c("cg-taa-sharpness",      "TAA锐度",              "TAA模糊的成因与反向色调映射/锐化补偿", 3, 25, "theory", ["问题"]),
        _c("cg-velocity-buffer",    "速度缓冲",             "Per-Pixel Velocity的计算与TAA/Motion Blur共享", 2, 25, "theory", ["技术"]),
        _c("cg-jitter-pattern",     "抖动模式",             "Halton/R2序列在TAA子像素抖动中的应用", 3, 25, "theory", ["技术"]),
        _c("cg-dlss",               "DLSS",                 "深度学习超采样的架构与时序帧生成", 3, 30, "theory", ["AI"], True),
        _c("cg-fsr",                "FSR",                  "AMD FidelityFX Super Resolution的空间/时间升采样", 3, 25, "theory", ["技术"]),
        _c("cg-xess",               "XeSS",                 "Intel XeSS的XMX加速超分辨率", 3, 25, "theory", ["技术"]),
        _c("cg-upscaling",          "超分辨率技术",         "空间/时间超分辨率的统一框架与对比", 3, 30, "theory", ["核心"]),
        _c("cg-alpha-testing-aa",   "Alpha测试抗锯齿",     "Alpha To Coverage与MSAA配合处理植被锯齿", 3, 25, "theory", ["实践"]),
        _c("cg-specular-aa",        "高光抗锯齿",           "法线方差过滤与Roughness修正防闪烁", 3, 25, "theory", ["进阶"]),
        _c("cg-geometric-aa",       "几何抗锯齿",           "线框/细线条的几何级抗锯齿方案", 3, 25, "theory", ["实践"]),
        _c("cg-temporal-stability", "时间稳定性",           "渲染输出的帧间稳定性评估与优化", 3, 25, "theory", ["质量"]),
        _c("cg-aa-comparison",      "AA方案对比",           "各AA技术的质量/性能/兼容性综合评估", 2, 25, "theory", ["总结"]),
        _c("cg-frame-generation",   "帧生成",               "DLSS 3/FSR 3的光流帧插值技术", 4, 30, "theory", ["前沿"]),
    ],

    # ── 12. 渲染优化 (20 concepts) ─────────────────────────────
    "render-optimization": [
        _c("cg-optim-intro",        "渲染优化概述",         "渲染性能瓶颈分类与优化方法论", 1, 20, "theory", ["基础"], True),
        _c("cg-draw-call",          "Draw Call优化",        "批处理、Instancing与Indirect绘制的减少策略", 2, 25, "theory", ["核心"], True),
        _c("cg-frustum-culling",    "视锥剔除",             "AABB/OBB/Sphere的视锥体相交测试", 2, 25, "theory", ["核心"]),
        _c("cg-occlusion-culling",  "遮挡剔除",             "HZB/Software Rasterization遮挡查询", 3, 30, "theory", ["核心"], True),
        _c("cg-gpu-culling",        "GPU剔除",              "基于Compute Shader的GPU-side剔除管线", 3, 30, "theory", ["进阶"]),
        _c("cg-bandwidth-opt",      "带宽优化",             "VRAM带宽瓶颈诊断与压缩/格式选择", 3, 25, "theory", ["核心"]),
        _c("cg-overdraw",           "Overdraw分析",         "Overdraw的测量、原因与Front-to-Back排序", 2, 25, "theory", ["实践"]),
        _c("cg-state-sorting",      "状态排序",             "渲染对象的材质/深度排序减少状态切换", 2, 25, "theory", ["实践"]),
        _c("cg-atlas-batching",     "图集批处理",           "纹理Atlas与材质合批的实际应用", 2, 25, "theory", ["实践"]),
        _c("cg-shader-complexity",  "着色器复杂度",         "ALU/TEX/控制流对着色器性能的影响", 3, 25, "theory", ["分析"]),
        _c("cg-render-budget",      "渲染预算",             "帧时间预算分配与自适应质量缩放", 2, 25, "theory", ["管理"]),
        _c("cg-adaptive-quality",   "自适应质量",           "动态分辨率缩放与质量级联", 3, 25, "theory", ["技术"], True),
        _c("cg-streaming-opt",      "流式加载优化",         "纹理/网格/场景的流式加载策略与预加载", 3, 30, "theory", ["实践"]),
        _c("cg-render-graph",       "渲染图",               "Frame Graph/Render Graph的自动资源管理与Pass排序", 4, 35, "theory", ["架构"], True),
        _c("cg-cpu-gpu-sync",       "CPU-GPU同步",          "帧延迟、双/三缓冲与Fence管理", 3, 25, "theory", ["核心"]),
        _c("cg-multithreaded-cmd",  "多线程命令构建",       "并行命令缓冲录制与提交策略", 3, 30, "theory", ["进阶"]),
        _c("cg-mobile-opt",         "移动端优化",           "Tile-Based架构的特定优化策略", 3, 30, "theory", ["移动端"]),
        _c("cg-vr-opt",             "VR渲染优化",           "双眼渲染、Foveated Rendering与ASW", 3, 30, "theory", ["XR"]),
        _c("cg-perf-counter",       "性能计数器",           "GPU硬件性能计数器的含义与瓶颈定位", 3, 25, "theory", ["工具"]),
        _c("cg-profiling-workflow", "性能调优工作流",       "Measure→Identify→Fix→Verify的系统化调优方法", 2, 25, "theory", ["方法论"], True),
    ],
}

# ── Build edges ─────────────────────────────────────────────────────
EDGES = []

def _e(src, tgt, rel="prerequisite", strength=0.8):
    EDGES.append({"source_id": src, "target_id": tgt, "relation_type": rel, "strength": strength})

# -- Rasterization edges --
_e("cg-raster-intro", "cg-raster-pipeline")
_e("cg-raster-pipeline", "cg-vertex-transform")
_e("cg-raster-pipeline", "cg-clipping")
_e("cg-vertex-transform", "cg-projection")
_e("cg-projection", "cg-viewport-transform")
_e("cg-viewport-transform", "cg-triangle-setup")
_e("cg-triangle-setup", "cg-scanline")
_e("cg-triangle-setup", "cg-interpolation")
_e("cg-interpolation", "cg-depth-buffer")
_e("cg-depth-buffer", "cg-stencil-buffer")
_e("cg-depth-buffer", "cg-early-z")
_e("cg-interpolation", "cg-blending")
_e("cg-blending", "cg-msaa")
_e("cg-raster-pipeline", "cg-forward-rendering")
_e("cg-forward-rendering", "cg-deferred-rendering")
_e("cg-deferred-rendering", "cg-forward-plus")
_e("cg-deferred-rendering", "cg-tiled-rendering")
_e("cg-forward-plus", "cg-clustered-rendering")
_e("cg-deferred-rendering", "cg-visibility-buffer")
_e("cg-depth-buffer", "cg-indirect-draw")
_e("cg-indirect-draw", "cg-mesh-shader")

# -- Ray Tracing edges --
_e("cg-rt-intro", "cg-ray-generation")
_e("cg-ray-generation", "cg-ray-intersection")
_e("cg-ray-intersection", "cg-bvh")
_e("cg-ray-intersection", "cg-kd-tree")
_e("cg-ray-intersection", "cg-rt-shadows")
_e("cg-rt-shadows", "cg-rt-reflection")
_e("cg-rt-reflection", "cg-rt-refraction")
_e("cg-rt-intro", "cg-path-tracing")
_e("cg-path-tracing", "cg-importance-sampling")
_e("cg-importance-sampling", "cg-mis")
_e("cg-path-tracing", "cg-bidirectional-pt")
_e("cg-bidirectional-pt", "cg-mlt")
_e("cg-path-tracing", "cg-photon-mapping")
_e("cg-path-tracing", "cg-rt-denoising")
_e("cg-bvh", "cg-rtx-hardware")
_e("cg-raster-intro", "cg-hybrid-rendering", "related", 0.7)  # cross-subdomain
_e("cg-rtx-hardware", "cg-hybrid-rendering")
_e("cg-importance-sampling", "cg-restir")
_e("cg-ray-intersection", "cg-sdf-tracing")
_e("cg-path-tracing", "cg-rt-gi")
_e("cg-rt-refraction", "cg-spectral-rendering")

# -- PBR Materials edges --
_e("cg-pbr-intro", "cg-brdf")
_e("cg-brdf", "cg-cook-torrance")
_e("cg-cook-torrance", "cg-ndf")
_e("cg-cook-torrance", "cg-fresnel")
_e("cg-cook-torrance", "cg-geometry-term")
_e("cg-pbr-intro", "cg-metallic-workflow")
_e("cg-metallic-workflow", "cg-specular-workflow")
_e("cg-cook-torrance", "cg-subsurface")
_e("cg-cook-torrance", "cg-clear-coat")
_e("cg-cook-torrance", "cg-anisotropy")
_e("cg-brdf", "cg-cloth-shading")
_e("cg-brdf", "cg-hair-shading")
_e("cg-subsurface", "cg-eye-rendering")
_e("cg-subsurface", "cg-skin-rendering")
_e("cg-fresnel", "cg-iridescence")
_e("cg-cook-torrance", "cg-energy-conservation")
_e("cg-energy-conservation", "cg-material-layering")
_e("cg-brdf", "cg-disney-brdf")
_e("cg-brdf", "cg-btdf")

# -- Global Illumination edges --
_e("cg-gi-intro", "cg-rendering-equation")
_e("cg-rendering-equation", "cg-radiometry")
_e("cg-rendering-equation", "cg-radiosity")
_e("cg-gi-intro", "cg-ambient-occlusion")
_e("cg-gi-intro", "cg-irradiance-map")
_e("cg-irradiance-map", "cg-spherical-harmonics")
_e("cg-irradiance-map", "cg-light-probes")
_e("cg-gi-intro", "cg-reflection-probes")
_e("cg-ambient-occlusion", "cg-screen-space-gi")
_e("cg-gi-intro", "cg-lpv")
_e("cg-lpv", "cg-voxel-gi")
_e("cg-voxel-gi", "cg-lumen")
_e("cg-light-probes", "cg-ddgi")
_e("cg-gi-intro", "cg-lightmap-baking")
_e("cg-spherical-harmonics", "cg-irradiance-volume")
_e("cg-path-tracing", "cg-caustics", "related", 0.7)  # cross-subdomain
_e("cg-gi-intro", "cg-sky-atmosphere")
_e("cg-sky-atmosphere", "cg-cloud-rendering")
_e("cg-screen-space-gi", "cg-indirect-specular")
_e("cg-voxel-gi", "cg-gi-hybrid")

# -- Post Processing edges --
_e("cg-pp-intro", "cg-tone-mapping")
_e("cg-tone-mapping", "cg-color-grading")
_e("cg-pp-intro", "cg-bloom")
_e("cg-pp-intro", "cg-dof")
_e("cg-pp-intro", "cg-motion-blur")
_e("cg-pp-intro", "cg-lens-flare")
_e("cg-lens-flare", "cg-chromatic-aberration")
_e("cg-pp-intro", "cg-vignette")
_e("cg-pp-intro", "cg-film-grain")
_e("cg-pp-intro", "cg-sharpening")
_e("cg-tone-mapping", "cg-exposure")
_e("cg-pp-intro", "cg-fog-pp")
_e("cg-deferred-rendering", "cg-ssr", "related", 0.7)  # cross-subdomain
_e("cg-pp-intro", "cg-outline")
_e("cg-outline", "cg-cel-shading")
_e("cg-pp-intro", "cg-pixel-art-filter")
_e("cg-tone-mapping", "cg-hdr-pipeline")
_e("cg-pp-intro", "cg-pp-volume")
_e("cg-exposure", "cg-eye-adaptation")
_e("cg-pp-volume", "cg-pp-stack")

# -- GPU Architecture edges --
_e("cg-gpu-intro", "cg-gpu-pipeline")
_e("cg-gpu-pipeline", "cg-gpu-memory")
_e("cg-gpu-intro", "cg-warp-wavefront")
_e("cg-warp-wavefront", "cg-occupancy")
_e("cg-occupancy", "cg-gpu-scheduling")
_e("cg-gpu-pipeline", "cg-texture-unit")
_e("cg-gpu-pipeline", "cg-rop")
_e("cg-texture-unit", "cg-tmu-cache")
_e("cg-gpu-intro", "cg-compute-shader")
_e("cg-compute-shader", "cg-async-compute")
_e("cg-compute-shader", "cg-gpu-driven")
_e("cg-gpu-driven", "cg-bindless")
_e("cg-gpu-intro", "cg-dx12-vk")
_e("cg-dx12-vk", "cg-command-buffer")
_e("cg-dx12-vk", "cg-render-pass")
_e("cg-dx12-vk", "cg-descriptor-set")
_e("cg-command-buffer", "cg-pipeline-barrier")
_e("cg-gpu-intro", "cg-gpu-profiling")
_e("cg-gpu-intro", "cg-mobile-gpu")
_e("cg-bvh", "cg-ray-tracing-hw", "related", 0.7)  # cross-subdomain

# -- Shader Programming edges --
_e("cg-shader-intro", "cg-vertex-shader")
_e("cg-vertex-shader", "cg-fragment-shader")
_e("cg-fragment-shader", "cg-geometry-shader")
_e("cg-fragment-shader", "cg-tessellation")
_e("cg-shader-intro", "cg-hlsl")
_e("cg-shader-intro", "cg-glsl")
_e("cg-hlsl", "cg-spirv")
_e("cg-glsl", "cg-spirv")
_e("cg-shader-intro", "cg-shader-model")
_e("cg-fragment-shader", "cg-uber-shader")
_e("cg-uber-shader", "cg-shader-permutation")
_e("cg-fragment-shader", "cg-material-graph")
_e("cg-fragment-shader", "cg-surface-shader")
_e("cg-material-graph", "cg-material-function")
_e("cg-shader-intro", "cg-shader-debug")
_e("cg-fragment-shader", "cg-custom-lighting")
_e("cg-fragment-shader", "cg-procedural-shader")
_e("cg-uber-shader", "cg-shader-optimization")
_e("cg-warp-wavefront", "cg-wave-intrinsics", "related", 0.7)  # cross-subdomain
_e("cg-compute-shader", "cg-shader-interop", "related", 0.7)  # cross-subdomain
_e("cg-spirv", "cg-slang")

# -- Texture Techniques edges --
_e("cg-tex-intro", "cg-mipmap")
_e("cg-mipmap", "cg-aniso-filtering")
_e("cg-tex-intro", "cg-normal-mapping")
_e("cg-normal-mapping", "cg-parallax-mapping")
_e("cg-parallax-mapping", "cg-displacement-map")
_e("cg-tex-intro", "cg-cube-mapping")
_e("cg-tex-intro", "cg-texture-compression")
_e("cg-texture-compression", "cg-virtual-texture")
_e("cg-tex-intro", "cg-texture-atlas")
_e("cg-mipmap", "cg-texture-streaming")
_e("cg-tex-intro", "cg-procedural-texture")
_e("cg-tex-intro", "cg-detail-mapping")
_e("cg-tex-intro", "cg-texture-projection")
_e("cg-texture-projection", "cg-decal-system")
_e("cg-tex-intro", "cg-triplanar")
_e("cg-procedural-texture", "cg-texture-synthesis")
_e("cg-tex-intro", "cg-sdf-texture")
_e("cg-tex-intro", "cg-material-textures")
_e("cg-material-textures", "cg-texture-baking")
_e("cg-texture-atlas", "cg-udim")

# -- Geometry Processing edges --
_e("cg-geo-intro", "cg-mesh-representation")
_e("cg-mesh-representation", "cg-mesh-simplification")
_e("cg-mesh-representation", "cg-subdivision")
_e("cg-geo-intro", "cg-lod")
_e("cg-lod", "cg-nanite")
_e("cg-mesh-representation", "cg-mesh-boolean")
_e("cg-geo-intro", "cg-parametric-surface")
_e("cg-geo-intro", "cg-point-cloud")
_e("cg-point-cloud", "cg-isosurface")
_e("cg-isosurface", "cg-sdf-modeling")
_e("cg-mesh-representation", "cg-mesh-repair")
_e("cg-mesh-representation", "cg-mesh-deformation")
_e("cg-mesh-representation", "cg-mesh-compression")
_e("cg-geo-intro", "cg-instancing")
_e("cg-lod", "cg-impostor")
_e("cg-geo-intro", "cg-terrain-geometry")
_e("cg-terrain-geometry", "cg-vegetation")
_e("cg-geo-intro", "cg-procedural-mesh")
_e("cg-lod", "cg-mesh-streaming")
_e("cg-sdf-modeling", "cg-neural-geometry")

# -- Volume Rendering edges --
_e("cg-vol-intro", "cg-ray-marching")
_e("cg-ray-marching", "cg-beer-lambert")
_e("cg-beer-lambert", "cg-participating-media")
_e("cg-participating-media", "cg-phase-function")
_e("cg-participating-media", "cg-vol-shadow")
_e("cg-ray-marching", "cg-vol-cloud")
_e("cg-ray-marching", "cg-vol-fog")
_e("cg-ray-marching", "cg-god-rays")
_e("cg-vol-intro", "cg-vol-texture")
_e("cg-participating-media", "cg-fluid-rendering")
_e("cg-ray-marching", "cg-fire-explosion")
_e("cg-participating-media", "cg-smoke-sim")
_e("cg-participating-media", "cg-heterogeneous")
_e("cg-participating-media", "cg-vol-gi")
_e("cg-vol-intro", "cg-openvdb")
_e("cg-vol-intro", "cg-medical-vis")
_e("cg-vol-intro", "cg-scientific-vis")
_e("cg-vol-intro", "cg-vol-decal")
_e("cg-sky-atmosphere", "cg-atmosphere-scatter", "related", 0.7)  # cross-subdomain
_e("cg-ray-marching", "cg-neural-radiance")

# -- Anti-Aliasing edges --
_e("cg-aa-intro", "cg-ssaa")
_e("cg-ssaa", "cg-msaa-detail")
_e("cg-aa-intro", "cg-fxaa")
_e("cg-fxaa", "cg-smaa")
_e("cg-aa-intro", "cg-taa")
_e("cg-taa", "cg-taa-ghosting")
_e("cg-taa", "cg-taa-sharpness")
_e("cg-taa", "cg-velocity-buffer")
_e("cg-taa", "cg-jitter-pattern")
_e("cg-taa", "cg-dlss")
_e("cg-taa", "cg-fsr")
_e("cg-taa", "cg-xess")
_e("cg-dlss", "cg-upscaling")
_e("cg-fsr", "cg-upscaling")
_e("cg-msaa-detail", "cg-alpha-testing-aa")
_e("cg-taa", "cg-specular-aa")
_e("cg-aa-intro", "cg-geometric-aa")
_e("cg-taa", "cg-temporal-stability")
_e("cg-aa-intro", "cg-aa-comparison")
_e("cg-dlss", "cg-frame-generation")

# -- Render Optimization edges --
_e("cg-optim-intro", "cg-draw-call")
_e("cg-optim-intro", "cg-frustum-culling")
_e("cg-frustum-culling", "cg-occlusion-culling")
_e("cg-occlusion-culling", "cg-gpu-culling")
_e("cg-optim-intro", "cg-bandwidth-opt")
_e("cg-optim-intro", "cg-overdraw")
_e("cg-draw-call", "cg-state-sorting")
_e("cg-draw-call", "cg-atlas-batching")
_e("cg-optim-intro", "cg-shader-complexity")
_e("cg-optim-intro", "cg-render-budget")
_e("cg-render-budget", "cg-adaptive-quality")
_e("cg-optim-intro", "cg-streaming-opt")
_e("cg-optim-intro", "cg-render-graph")
_e("cg-optim-intro", "cg-cpu-gpu-sync")
_e("cg-cpu-gpu-sync", "cg-multithreaded-cmd")
_e("cg-optim-intro", "cg-mobile-opt")
_e("cg-optim-intro", "cg-vr-opt")
_e("cg-gpu-profiling", "cg-perf-counter", "related", 0.7)  # cross-subdomain
_e("cg-optim-intro", "cg-profiling-workflow")

# ── Assemble ────────────────────────────────────────────────────────
all_concepts = []
for sd_id, concepts in CONCEPTS_BY_SUBDOMAIN.items():
    for c in concepts:
        c["subdomain_id"] = sd_id
        all_concepts.append(c)

milestones = [c["id"] for c in all_concepts if c.get("is_milestone")]

seed_graph = {
    "domain": {
        "id": DOMAIN_ID,
        "name": "图形学",
        "description": "从光栅化到光线追踪的完整计算机图形学知识体系",
        "icon": "💡",
        "color": "#0284c7",
    },
    "subdomains": SUBDOMAINS,
    "concepts": all_concepts,
    "edges": EDGES,
    "metadata": {
        "domain_id": DOMAIN_ID,
        "version": "1.0.0",
        "generated_by": "generate_cg_seed.py",
        "total_concepts": len(all_concepts),
        "total_edges": len(EDGES),
        "subdomains": [{"id": s["id"], "name": s["name"], "order": s["order"]} for s in SUBDOMAINS],
        "milestones": milestones,
    },
}

# ── Validation ──────────────────────────────────────────────────────
ids = [c["id"] for c in all_concepts]
assert len(ids) == len(set(ids)), f"Duplicate IDs: {[x for x in ids if ids.count(x) > 1]}"

id_set = set(ids)
for e in EDGES:
    assert e["source_id"] in id_set, f"Edge source not found: {e['source_id']}"
    assert e["target_id"] in id_set, f"Edge target not found: {e['target_id']}"

# ── Write ───────────────────────────────────────────────────────────
out_dir = os.path.join(os.path.dirname(__file__), "..", "seed", DOMAIN_ID)
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "seed_graph.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(seed_graph, f, ensure_ascii=False, indent=2)

print(f"✅ Generated {out_path}")
print(f"   Concepts: {len(all_concepts)}")
print(f"   Edges:    {len(EDGES)}")
print(f"   Subdomains: {len(SUBDOMAINS)}")
print(f"   Milestones: {len(milestones)}")
