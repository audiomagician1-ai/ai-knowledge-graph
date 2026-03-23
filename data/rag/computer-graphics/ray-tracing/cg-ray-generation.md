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
quality_tier: "pending-rescore"
quality_score: 40.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 光线生成

## 概述

光线生成（Ray Generation）是光线追踪渲染管线的第一个阶段，负责从虚拟相机出发，为屏幕上每一个像素构造出一条或多条初始射线（称为主光线，Primary Ray）。这些主光线的方向和起点完全由相机参数决定，直接影响场景在图像平面上的投影关系。

该算法最早在1980年 Turner Whitted 提出递归光线追踪的论文《An Improved Illumination Model for Shaded Display》中得到系统性描述。Whitted 的模型将相机视为一个针孔，从图像平面的每个采样点向场景发射射线，完整奠定了沿用至今的主光线生成框架。

光线生成之所以关键，在于它直接决定了最终图像的几何正确性：相机的视野角（Field of View，FOV）、宽高比（Aspect Ratio）、近裁剪面距离，以及光线在三维空间中的方向向量计算稍有偏差，就会导致透视形变错误或画面边缘失真，这些问题无法在后续的着色阶段弥补。

---

## 核心原理

### 针孔相机模型与坐标系构建

标准光线追踪采用**针孔相机模型**（Pinhole Camera Model）。该模型将相机定义为三个关键向量：
- **位置** `eye`：相机在世界空间中的坐标
- **观察目标** `lookat`：相机指向的目标点
- **上方向** `up`：用于确定相机的滚转角度

由这三个参数可以推导出右手正交坐标系（Camera Space）：

```
forward = normalize(lookat - eye)
right   = normalize(cross(forward, up))
up_true = cross(right, forward)
```

其中 `up_true` 是经过正交化的真实上方向，用于消除输入 `up` 向量不严格垂直时产生的误差。

### 图像平面的构造与像素坐标映射

设垂直视野角为 `fovY`（单位：度），图像分辨率为 `W × H`，相机到图像平面的距离（焦距）通常归一化为 1.0。图像平面的半高 `h` 和半宽 `w` 分别为：

```
h = tan(fovY / 2)
w = h × (W / H)          # 乘以宽高比
```

对于屏幕坐标 `(i, j)`（整数像素索引，从 0 开始），需要将其转换为图像平面上的连续坐标。常用的居中采样公式为：

```
u = (i + 0.5) / W × 2 - 1     # 范围 [-1, 1]
v = 1 - (j + 0.5) / H × 2     # 注意 Y 轴翻转：屏幕坐标 j 向下增大
```

其中 `0.5` 的偏移确保光线穿过像素中心，而非像素角点。最终图像平面上的采样点为：

```
P = eye + forward + u × w × right + v × h × up_true
```

主光线方向即为：

```
ray_direction = normalize(P - eye)
ray_origin    = eye
```

### 正交投影与透视投影的差异

除针孔透视相机外，光线生成也支持**正交投影**（Orthographic Projection）。正交模式下，所有主光线方向相同，均等于 `forward`，而光线起点随像素位置在图像平面上平移：

```
ray_origin    = eye + u × w × right + v × h × up_true
ray_direction = forward    # 固定方向，无收敛至单点
```

透视模式的光线从单点（eye）发出向外发散，产生近大远小的透视效果；正交模式的光线互相平行，常用于 CAD 和等距视图渲染。

### 多重采样与超采样

对于抗锯齿（Anti-Aliasing），每个像素需要生成多条主光线。以 4× MSAA（多重采样抗锯齿）为例，在像素内以 2×2 的规则网格偏移采样点，偏移量为 `±0.25` 个像素单位：

```
offsets = [(-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0.25, 0.25)]
```

随机采样（Stochastic Sampling）则在像素内以均匀随机分布生成 N 条光线，适用于路径追踪（Path Tracing）中同时处理景深（Depth of Field）和运动模糊（Motion Blur）。

---

## 实际应用

**景深效果（Depth of Field）** 是对针孔模型的延伸。真实镜头有有限孔径，表现为光线不从单点发出，而是在**镜头光圈盘**（Lens Disk，半径为 `aperture`）上随机采样起点，所有光线仍聚焦于焦平面（Focal Plane，距离为 `focusDistance`）上的同一点：

```
lens_point = eye + random_in_disk() × aperture × right
                 + random_in_disk() × aperture × up_true
focus_point = eye + focusDistance × ray_direction_original
ray_origin    = lens_point
ray_direction = normalize(focus_point - lens_point)
```

这一技术在 Peter Shirley 的《Ray Tracing in One Weekend》（2016年）中有详细实现示例，渲染出模拟单反相机虚化背景（Bokeh）的效果。

**等距柱状投影（Equirectangular Projection）** 用于生成360°全景图像。光线方向由球面坐标计算：

```
theta = π × (j + 0.5) / H          # 仰角，范围 [0, π]
phi   = 2π × (i + 0.5) / W         # 方位角，范围 [0, 2π]
ray_direction = (sin(theta)×cos(phi), cos(theta), sin(theta)×sin(phi))
```

---

## 常见误区

**误区一：忽略像素中心偏移（0.5 offset）**
初学者常将像素 `(i, j)` 直接映射为 `i/W × 2 - 1`，光线穿过像素左上角而非中心。在低分辨率（如 64×64）下，这会导致整张图像出现约半个像素的系统性偏移，在包含细直线的场景中产生明显锯齿错位。

**误区二：混淆 fovY 与 fovX**
常见错误是将水平视野角与垂直视野角互换，导致宽屏图像（如 1920×1080）出现纵向压缩或横向拉伸。正确做法是始终以 `fovY` 计算半高 `h`，再通过宽高比导出半宽 `w`，不应对 `w` 独立设置角度。

**误区三：正交化 up 向量**
当 `up` 向量与 `forward` 向量几乎平行时（如相机俯视场景），`cross(forward, up)` 的结果接近零向量，归一化后会产生数值错误（NaN）。必须在相机参数输入阶段验证两向量夹角不接近 0° 或 180°，或改用四元数描述相机朝向。

---

## 知识关联

光线生成以**光线追踪概述**中建立的射线数据结构（由原点 `origin` 和方向 `direction` 组成的参数化直线 `P(t) = origin + t × direction`）为输入规范，生成的主光线直接传递给下一阶段。

生成主光线后，立即进入**光线求交**阶段：将每条主光线与场景中的几何体（球体、三角形网格等）逐一检测相交，求解参数 `t` 的最小正值。光线生成阶段的计算量（每帧 O(W×H×N) 条光线）也决定了加速结构（如 BVH、KD-tree）在求交阶段必要性——分辨率为 1920×1080、每像素 8 条光线时，单帧仅主光线就超过 1600 万条。
