---
id: "cg-ray-generation"
concept: "光线生成"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 光线生成

## 概述

光线生成（Ray Generation）是光线追踪渲染管线的第一步，负责从虚拟相机向场景中发射主光线（Primary Ray）。其核心任务是将屏幕上每个像素映射到三维空间中的一条唯一射线，该射线的起点与方向完全由相机模型的参数决定。Turner Whitted 在 1980 年发表的论文《An Improved Illumination Model for Shaded Display》（*Communications of the ACM*, 23(6):343–349）中，将针孔相机模型正式引入递归光线追踪框架，标志着现代光线追踪相机模型的确立。

针孔相机（Pinhole Camera）假设所有主光线从单一焦点（Focal Point）出发穿过虚拟图像平面，该假设将光线方向计算简化为纯粹的向量减法与归一化运算。在分辨率为 1920×1080 的场景中，每帧仅主光线就需生成 2,073,600 条，若启用 4×超采样（MSAA 或随机超采样），每帧主光线数量上升至 8,294,400 条——因此光线生成的计算效率对整体渲染性能有直接影响。

现代渲染器（如 NVIDIA OptiX 7.x、Mitsuba 3）在针孔模型基础上扩展出薄透镜模型（Thin Lens Model）、等距鱼眼相机（Equidistant Fisheye）和全景球形相机（Spherical Camera）等，但针孔相机仍是离线渲染与实时光线追踪的默认基准模型。

---

## 核心原理

### 针孔相机的坐标系构建

针孔相机由三个输入参数唯一确定：相机位置 $\mathbf{E}$（Eye Point）、观察目标点 $\mathbf{C}$（Look-At Point）和世界上方向 $\mathbf{U}$（Up Vector，通常取 $(0,1,0)$）。从这三个参数出发，按以下顺序构建相机本地正交基底：

$$
\mathbf{w} = \frac{\mathbf{E} - \mathbf{C}}{|\mathbf{E} - \mathbf{C}|}, \quad
\mathbf{u} = \frac{\mathbf{U} \times \mathbf{w}}{|\mathbf{U} \times \mathbf{w}|}, \quad
\mathbf{v} = \mathbf{w} \times \mathbf{u}
$$

其中 $\mathbf{w}$ 指向相机后方（与观察方向相反），$\mathbf{u}$ 指向相机右方，$\mathbf{v}$ 指向相机真实上方。注意 $\mathbf{v}$ 不等于原始 $\mathbf{U}$，除非相机完全水平放置——这一区别是初学实现时坐标系错误的主要来源之一。三向量满足 $\mathbf{u} \cdot \mathbf{v} = \mathbf{v} \cdot \mathbf{w} = \mathbf{w} \cdot \mathbf{u} = 0$，构成右手系正交基。

### 图像平面参数化与像素坐标映射

图像平面（Image Plane）距相机 $d$ 处（通常取 $d=1$，不影响方向计算），其半宽和半高由水平视场角 $\theta_h$ 和宽高比 $r = W/H$ 决定：

$$
\text{half\_width} = d \cdot \tan\!\left(\frac{\theta_h}{2}\right), \qquad
\text{half\_height} = \frac{\text{half\_width}}{r}
$$

对于分辨率 $W \times H$ 的图像，第 $(i,\, j)$ 号像素（$i$ 为列，$j$ 为行，原点取左下角）的图像平面采样坐标为：

$$
s = \text{half\_width} \cdot \left(\frac{2i + 1}{W} - 1\right), \qquad
t = \text{half\_height} \cdot \left(\frac{2j + 1}{H} - 1\right)
$$

分子中的 $2i+1$ 将采样点定位在像素格的正中央，而非左下角顶点，消除了边缘像素的系统性半像素偏移。例如，在 $W=800$ 的图像中，第 0 列像素中心的 $s$ 坐标为 $\text{half\_width} \cdot (1/800 - 1)$，而非 $-\text{half\_width}$。

### 主光线的参数化表示

每条主光线以参数形式表示：

$$
\mathbf{P}(t) = \mathbf{O} + t\,\mathbf{d}, \quad t > 0
$$

其中 $\mathbf{O}$ 为光线起点（针孔模型中 $\mathbf{O} = \mathbf{E}$），$\mathbf{d}$ 为归一化方向向量：

$$
\mathbf{d} = \frac{s\,\mathbf{u} + t\,\mathbf{v} - d\,\mathbf{w}}{|s\,\mathbf{u} + t\,\mathbf{v} - d\,\mathbf{w}|}
$$

约束 $t > 0$ 保证光线只向相机前方延伸。$\mathbf{d}$ **必须归一化**：后续光线-球体求交公式 $t = -\mathbf{d} \cdot (\mathbf{O}-\mathbf{C}) \pm \sqrt{\Delta}$ 中，判别式 $\Delta$ 的量纲假定 $|\mathbf{d}|=1$；若 $|\mathbf{d}| \neq 1$，求得的 $t$ 值不再表示世界空间距离，导致近远平面裁剪和折射角计算全部出错。

---

## 关键算法与代码实现

以下为针孔相机光线生成的 C++ 核心实现，使用 GLM 数学库（glm 0.9.9+）：

```cpp
#include <glm/glm.hpp>
#include <glm/gtc/normalize.hpp>

struct Ray {
    glm::vec3 origin;    // 光线起点
    glm::vec3 direction; // 归一化方向向量
};

struct PinholeCamera {
    glm::vec3 eye;       // 相机位置 E
    glm::vec3 lookAt;    // 观察目标 C
    glm::vec3 up;        // 世界上方向 U（通常 (0,1,0)）
    float     fovH;      // 水平视场角（弧度）
    int       width;     // 图像宽度（像素）
    int       height;    // 图像高度（像素）
};

Ray generateRay(const PinholeCamera& cam, int pixelX, int pixelY) {
    // 1. 构建相机正交基
    glm::vec3 w = glm::normalize(cam.eye - cam.lookAt); // 后向
    glm::vec3 u = glm::normalize(glm::cross(cam.up, w)); // 右向
    glm::vec3 v = glm::cross(w, u);                      // 真实上向

    // 2. 计算图像平面半尺寸（焦距 d=1）
    float halfW = std::tan(cam.fovH / 2.0f);
    float halfH = halfW / (float(cam.width) / float(cam.height));

    // 3. 像素中心的图像平面坐标
    float s = halfW * (2.0f * pixelX + 1.0f) / cam.width  - halfW;
    float t = halfH * (2.0f * pixelY + 1.0f) / cam.height - halfH;

    // 4. 计算归一化光线方向
    glm::vec3 dir = glm::normalize(s * u + t * v - w); // -w = 前向

    return Ray{ cam.eye, dir };
}
```

**关键细节**：`glm::cross(cam.up, w)` 的顺序决定 $\mathbf{u}$ 朝右还是朝左，顺序错误将产生左右镜像的渲染结果，且该错误无法通过调整其他参数补救。

---

## 薄透镜模型与景深效果

真实相机镜头具有有限孔径（Aperture），焦平面（Focal Plane）之外的物体会产生弥散圆（Circle of Confusion），形成景深（Depth of Field, DoF）效果。薄透镜模型（详见《Physically Based Rendering: From Theory to Implementation》Pharr, Jakob & Humphreys, 第三版，2018，Morgan Kaufmann，第6.2节）在针孔模型基础上引入两个额外参数：

- **焦距** $f$（Focal Length）：焦平面到透镜的距离
- **光圈半径** $r$（Lens Radius）：$r = f / (2 \cdot F\text{-number})$，F/1.4 镜头的 $r$ 约为 $f/2.8$

生成带景深的光线时，步骤如下：

1. 计算针孔模型下光线与焦平面的交点 $\mathbf{F}$（焦点，所有样本共享）
2. 在透镜圆盘上均匀随机采样一个偏移量 $(\Delta u, \Delta v)$，满足 $\Delta u^2 + \Delta v^2 \leq r^2$
3. 新光线起点：$\mathbf{O}' = \mathbf{E} + \Delta u \cdot \mathbf{u} + \Delta v \cdot \mathbf{v}$
4. 新光线方向：$\mathbf{d}' = \text{normalize}(\mathbf{F} - \mathbf{O}')$

焦平面上的物体被多个样本光线汇聚到同一点，保持锐利；焦平面外的物体被离散的多条光线打到不同位置，形成模糊，模糊半径正比于 $r$ 与物体离焦距离的乘积。典型电影渲染中 F/1.4 镜头配合 50mm 焦距，焦平面前后各 10cm 内的物体保持锐利，背景模糊半径可达数十像素。

---

## 实际应用案例

**案例一：NVIDIA RTX 硬件光线追踪中的光线生成**

在 DirectX Raytracing (DXR) 和 Vulkan Ray Tracing 管线中，光线生成由专用着色器阶段 Ray Generation Shader 完成。每个线程对应一个像素，通过内置函数 `DispatchRaysIndex()` 获取像素坐标 $(i,j)$，执行上述针孔相机计算后调用 `TraceRay()` 将光线送入硬件 BVH 遍历单元（RT Core）。RTX 3090 的 RT Core 每秒可处理约 58 亿条光线求交，光线生成阶段若不能以足够快的速度向 RT Core 喂送光线，将成为渲染瓶颈——因此实际项目中光线生成着色器需尽量避免分支和内存随机访问。

**案例二：Mitsuba 3 中的透视相机实现**

Mitsuba 3（Jakob et al., 2022，《Dr.Jit: A Just-In-Time Compiler for Differentiable Rendering》）中 `PerspectiveCamera` 类预计算 $\tan(\theta_h/2)$ 并以 `sample_ray()` 方法接受 $[0,1)^2$ 范围内的像素样本坐标，支持自动微分（Automatic Differentiation）以便对相机参数（包括焦距和位置）求导，用于逆渲染（Inverse Rendering）中的相机标定任务。

**案例三：抗锯齿中的超采样光线**

在每像素 $N$ 条随机采样光线的路径追踪中（如 $N=64$），每条样本光线的图像平面坐标在像素格内随机偏移：

$$
s_k = \text{half\_width} \cdot \left(\frac{2(i + \xi_k^x)}{W} - 1\right), \quad \xi_k^x \sim \mathcal{U}(0,1)
$$

最终像素颜色取 $N$ 条光线的辐射度平均值，随着 $N$ 增大，锯齿（Aliasing）以 $O(1/\sqrt{N})$ 速度收敛消除。

---

## 常见误区

**误区 1：混淆视场角的水平与垂直定义**

OpenGL `gluPerspective` 使用**垂直** FoV，而许多游戏引擎（Unreal Engine、Unity）默认使用**垂直** FoV，但部分教程代码直接将 FoV 当作水平角代入 `half_width = tan(fov/2)` 计算，导致在非 1:1 宽高比下图像横向被压缩或拉伸。正确做法：明确区分水平 FoV（$\theta_h$）与垂直 FoV（$\theta_v$），二者满足 $\tan(\theta_h/2) = r \cdot \tan(\theta_v/2)$，其中 $r=W/H$。