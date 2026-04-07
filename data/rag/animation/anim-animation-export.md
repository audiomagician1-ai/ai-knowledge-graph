---
id: "anim-animation-export"
concept: "动画导出"
domain: "animation"
subdomain: "keyframe-animation"
subdomain_name: "关键帧动画"
difficulty: 2
is_milestone: false
tags: ["流程"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 动画导出

## 概述

动画导出是将三维软件内部制作完成的关键帧动画数据，以标准化格式输出为可供游戏引擎、渲染软件或其他工具读取的文件的操作流程。最常用的导出格式包括 **FBX**（Autodesk Filmbox）和 **glTF**（GL Transmission Format 2.0），两者在骨骼绑定、变换矩阵、动画曲线的存储方式上存在根本性差异。

FBX 格式由 Autodesk 于1996年收购 FilmBox 软件时随之推广，目前仍是游戏工业管线（如 Unity 和 Unreal Engine）中传递骨骼动画的事实标准；glTF 2.0 由 Khronos Group 于2017年正式发布，专为 WebGL 和实时渲染设计，JSON 元数据与二进制缓冲分离存储，体积通常比同内容的 FBX 文件小 40%–70%。

选择正确的导出参数直接决定动画在目标平台的播放精度。帧率不匹配会造成时间轴拉伸，采样精度不足会丢失高频曲线细节，骨骼命名冲突会导致蒙皮权重错乱，单位错误则会让角色在引擎中缩放为原来的 100 倍或 1/100 倍——这四类问题几乎涵盖了动画导出失败的绝大多数案例。

---

## 核心原理

### 帧率（Frame Rate）设置

导出时的帧率必须与**制作时的时间轴帧率**和**目标引擎的项目帧率**三者保持一致。Blender 默认 24 fps，Unity 默认 30 fps，Unreal Engine 默认也是 30 fps。若在 24 fps 的 Blender 场景中制作了一段 48 帧的动画（原始时长 2 秒），以 FBX 格式导出并导入 Unity 30 fps 项目后，Unity 会将其解析为 `48 ÷ 30 = 1.6 秒`，动作整体加速约 25%。

FBX 文件内部以 `FBXHeaderExtension.Creator` 字段记录时间协议（`Time::Mode`），支持的枚举值包括 `eFrames24`、`eFrames30`、`eFrames60` 等；导出时若不显式指定，软件可能回退为默认值，造成隐性帧率漂移。

### 采样（Bake / Sample）精度

三维软件内的动画曲线是由贝塞尔或 Hermite 样条描述的连续函数，而 FBX 和 glTF 均以**离散关键帧**存储动画数据。"烘焙采样"（Bake Animation）操作将曲线在每个整数帧处求值，生成密集的线性关键帧序列。

- **Blender FBX 导出**提供 `Simplify` 参数（0.0–1.0），数值越高表示允许越大的误差容忍度，减少输出关键帧数量；设为 `0` 则强制输出每帧一个关键帧，文件体积最大但曲线保真度最高。
- **Maya FBX 导出**提供 `Bake Animation` 选项，并可设定 `Step`（采样间隔），`Step = 1` 表示逐帧采样，`Step = 2` 则每隔一帧采样一次。
- glTF 格式的动画通道（`animation.samplers`）只支持线性（`LINEAR`）、步进（`STEP`）和三次样条（`CUBICSPLINE`）三种插值方式，不支持 Bezier 切线权重，因此从 Bezier 曲线转换为 glTF 时必须适当提高采样密度，否则弧形轨迹会退化为折线。

### 骨骼（Skeleton / Armature）导出规则

FBX 中骨骼以 `FbxSkeleton` 节点存储，glTF 中骨骼以 `skin.joints` 数组存储，两者均要求骨骼层级在导出前已经**Apply 所有静态变换**（即根骨骼的位移、旋转、缩放归零或单位化）。

Blender 中必须在导出前对 Armature 对象执行 `Object → Apply → All Transforms`，否则骨骼的 Rest Pose 矩阵会携带额外偏移，导致引擎中蒙皮网格出现撕裂或扭曲。此外，骨骼名称不得含有空格或特殊字符（部分 FBX SDK 版本会将空格替换为 `_`，造成目标端找不到同名骨骼而蒙皮失效）。

### 单位（Units）换算

FBX 文件在 `GlobalSettings` 节点中以 `UnitScaleFactor` 字段记录场景单位。Blender 默认单位为**米（1 BU = 1 m）**，导出 FBX 时 `UnitScaleFactor = 1.0`；3ds Max 默认单位为**厘米**，其 FBX 导出的 `UnitScaleFactor = 0.01`（相对于引擎标准米单位的缩放比）。Unity 读取 FBX 时会自动应用此系数，但 Unreal Engine 5 默认场景单位为厘米，导入时若不勾选 `Convert Scene Unit`，一个 Blender 中 1.8 m 高的角色在 UE5 中会被渲染为 1.8 cm 高。

glTF 规范明确规定所有线性单位均为**米**，无需额外缩放字段；但部分工具链导出时仍可能在根节点附加一个 `scale: [0.01, 0.01, 0.01]` 的变换节点来"模拟厘米"，接收端需注意消除这一冗余缩放。

---

## 实际应用

**游戏角色导出到 Unity 的完整参数配置示例（Blender FBX）：**

1. `Sampling Rate`：设为 `1`（逐帧烘焙），确保 IK 链和约束驱动的骨骼运动完整记录。
2. `Scale`：设为 `0.01`，将 Blender 米单位换算为 Unity 厘米惯例（或在 Unity 导入设置中将 `Scale Factor` 改为 `100`，效果等价）。
3. `Armature → Add Leaf Bones`：取消勾选，否则每根骨骼末端会额外生成虚拟叶骨，导致 Unity 动画重定向时骨骼数量不匹配。
4. `Bake Animation → NLA Strips`：勾选，以便将 NLA 编辑器中堆叠的动画片段全部展开导出。

**glTF 导出到 Three.js Web 场景：**
使用 Blender 的 `glTF 2.0 (.glb/.gltf)` 导出器，选择 `.glb`（二进制单文件），勾选 `Include → Animations → Active Actions Only`，确保只导出当前激活动作而非场景中所有 Object 的动作。导出后用 `gltf-validator`（Khronos 官方工具）检查 `animation.samplers` 的插值类型是否符合预期。

---

## 常见误区

**误区一：认为"导出成功"等于"动画正确"**
FBX/glTF 导出不报错，仅说明文件格式合法，不代表动画数据语义正确。最典型的陷阱是骨骼旋转轴顺序（Euler Order）：Blender 默认 `XYZ`，Maya 默认 `XYZ` 但部分节点使用 `ZXY`，FBX 中 `EulerXYZ` 与 `EulerZXY` 是不同枚举值，混淆后角色肢体会出现异常翻转，而文件本身完全有效。

**误区二：把"采样率"和"帧率"混为一谈**
采样率（Sample Rate）是导出时对动画曲线求值的频率，可以独立于场景帧率设置。例如在 30 fps 场景中以 `Step = 2` 导出，实际只在第 0、2、4… 帧处采样，等效于 15 fps 的关键帧密度，但时间轴总长度仍然按 30 fps 计算——这会造成高速动作（如手指快速弯曲）的曲线失真，而不影响慢速动作。

**误区三：glTF 和 FBX 可以随意互换**
glTF 不支持 Blend Shape（Shape Key）动画的骨骼权重叠加混合（MorphTarget 和 Skin 是分离通道），FBX 则支持将变形目标绑定在骨骼层级下。对于同时包含骨骼动画和表情 Blend Shape 的角色，FBX 能在一个文件内完整表达，而 glTF 需要在引擎层通过 `AnimationMixer` 同时驱动两个独立通道，配置更复杂。

---

## 知识关联

**前置概念——动画片段管理：** 动画导出依赖片段管理中定义的**片段起止帧范围**和**命名规则**。导出器通过读取片段的 `Start Frame` 和 `End Frame` 决定输出哪段时间范围；若片段管理阶段未正确分割动作（如 Idle、Walk、Run 混存于同一时间轴），导出时需要手动指定帧范围，极易出现帧偏移错误。

**格式选择对后续工作流的影响：** FBX 导出后通常进入 DCC 软件（Unity、UE）的导入管线，可在引擎内对动画压缩格式（如 U