---
id: "ta-lod-crowd"
concept: "人群LOD"
domain: "technical-art"
subdomain: "lod-strategy"
subdomain_name: "LOD策略"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 99.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 人群LOD

## 概述

人群LOD（Crowd Level of Detail）是专门针对游戏场景中数百至数千个NPC同时存在时的综合性渐进简化技术。与单个角色的LOD不同，人群LOD必须同时协调**骨骼层级数量、材质批次合并、动画系统切换**三个维度的降级策略——单独优化任何一个维度均无法解决成百上千个动态角色带来的性能瓶颈。

该技术在2005年前后随着《刺客信条》系列（Ubisoft，2007）与《全面战争：罗马》（Creative Assembly，2004）等需要展示大规模战场的游戏兴起而系统化。传统单角色LOD在100个以上NPC并存时会因DrawCall爆炸式增长（每个角色独立骨骼动画产生独立绘制调用）而失效。人群LOD通过引入GPU Instancing与骨骼动画纹理（Bone Animation Texture，BAT）将动画计算瓶颈从CPU侧彻底转移至GPU侧。

在现代开放世界游戏中，一个城市广场场景可能需要同时渲染300至500个NPC。若全部使用标准骨骼动画，仅动画Transform更新的CPU消耗在60Hz帧率下就会超出约4ms的帧预算（以8核CPU、每帧总预算16.7ms为参考）。人群LOD将这一问题拆解为可分级管理的子问题，使同屏NPC数量相较传统方案提升10倍以上成为可能。

参考资料：Kavan, L. et al.《Skinning with Dual Quaternions》ACM SIGGRAPH 2008；Ubisoft技术博客《Crowds in Assassin's Creed Unity》GDC 2015。

---

## 核心原理

### 骨骼简化策略：从全骨骼到伪骨骼

标准人形角色骨骼通常包含50至80根骨骼（含手指17根、面部约15根、武器辅助骨骼若干）。人群LOD将其划分为典型的三个等级：

- **LOD0（0–15米）**：完整骨骼，启用IK（Inverse Kinematics），约50–80根骨骼，动画状态机全功能运行
- **LOD1（15–40米）**：精简骨骼，移除手指、面部、武器辅助骨骼，保留约18–22根核心骨骼，禁用IK与布料模拟
- **LOD2（40米以上）**：极简骨骼，或直接切换为**骨骼动画纹理（BAT）**，仅保留根骨骼+髋、脊柱、左右肩、左右髋共7个关节

BAT技术的核心思路由Valve工程师在2009年发表的技术文档中提出：将每帧的骨骼变换矩阵预烘焙进一张RGBA32浮点纹理，纹理的Y轴方向每行存储一帧数据，X轴方向每列对应一根骨骼的变换四元数（共需4个通道存储一个旋转四元数，位移额外占1行）。运行时顶点着色器通过`tex2Dlod()`按播放时间戳采样该纹理重建蒙皮，完全绕过CPU侧的骨骼矩阵运算。

### 材质与DrawCall合并：GPU Instancing的限制突破

人群LOD中最关键的材质策略是将所有NPC的颜色变体打包进**颜色变化图集（Color Variation Atlas）**，并通过InstanceID索引不同的色调偏移向量（Hue Shift + Tint Multiply）。这使得同一材质的NPC可以被合并为单次GPU Instancing调用，将300个NPC的DrawCall从300次压缩至3–5次（按材质类型分组）。

Unity的Hybrid Renderer V2（现为URP/HDRP Entities Graphics）和Unreal Engine的Crowd Manager均实现了这一策略，但批次上限不同：

- **Unity GPU Instancing**：单批次上限1023个实例（DirectX 11限制），超出后自动分批
- **Unreal Crowd Manager**：默认分批大小512，可在`CrowdManager.ini`中调整`MaxAgents`参数

在设计NPC材质时，应将材质变体控制在8种以内（皮肤色调2–4种、服装色调2–4种通过纹理图集合并），以确保同屏300个NPC的DrawCall总量不超过40次。

### 动画系统的三级切换

动画系统的降级是延迟最敏感的部分，切换时需避免明显的动作跳变（Popping）：

1. **近距离（< 15米）**：完整AnimGraph，支持状态机、混合树（Blend Tree）、动态FootIK，每帧CPU更新所有骨骼Transform，动画系统独占约0.5–1.2ms/角色
2. **中距离（15–40米）**：切换为**AnimationBudgetAllocator**模式（Unreal 4.25+原生支持），将动画更新频率从60Hz降至15–20Hz，帧间以线性插值（Lerp）补偿视觉连续性，CPU消耗降至约0.08ms/角色
3. **远距离（> 40米）**：切换为预烘焙BAT动画，动画播放完全在GPU顶点着色器内完成，CPU端仅维护一个播放时间戳`float animTime`，内存开销从标准骨骼动画的约200 bytes/帧降至4 bytes/角色

---

## 关键公式与着色器实现

### BAT顶点着色器采样公式

设骨骼动画纹理分辨率为 $W \times H$，其中 $W$ = 骨骼数量，$H$ = 总帧数，则顶点着色器中采样第 $b$ 根骨骼在时间 $t$ 处的变换四元数为：

$$
uv = \left(\frac{b + 0.5}{W},\ \frac{\lfloor t \cdot fps \rfloor + 0.5}{H}\right)
$$

实际HLSL实现示例：

```hlsl
// BAT顶点着色器核心采样逻辑
sampler2D _BoneAnimTex;  // 预烘焙骨骼动画纹理
float _AnimTime;         // 当前播放时间（秒），由CPU传入
float _FPS;              // 烘焙帧率，通常为30fps
float _TotalFrames;      // 动画总帧数
float _BoneCount;        // 骨骼数量

float4 SampleBoneTransform(int boneIndex)
{
    float u = (boneIndex + 0.5) / _BoneCount;
    float frame = fmod(_AnimTime * _FPS, _TotalFrames);
    float v = (floor(frame) + 0.5) / _TotalFrames;
    return tex2Dlod(_BoneAnimTex, float4(u, v, 0, 0));
}

// 顶点蒙皮：将采样到的四元数还原为旋转矩阵后变换顶点
float3 SkinVertex(float3 pos, int boneIndex, float weight)
{
    float4 q = SampleBoneTransform(boneIndex);
    // 四元数旋转：q * pos * q^(-1)
    float3 rotated = pos + 2.0 * cross(q.xyz, cross(q.xyz, pos) + q.w * pos);
    return rotated * weight;
}
```

### LOD切换距离的计算

LOD切换距离并非固定值，而是应根据角色屏幕覆盖像素数动态调整。设角色高度为 $h$（米），垂直FOV为 $\theta$，屏幕垂直分辨率为 $R_{v}$，则角色在距离 $d$ 处的屏幕像素高度为：

$$
pixels = \frac{h \cdot R_v}{2d \cdot \tan(\theta / 2)}
$$

当 $pixels < 50$ 时切换至LOD1，$pixels < 15$ 时切换至LOD2——这一阈值来自《刺客信条：大革命》GDC 2015技术分享中对Paris人群渲染的实测数据。

---

## 实际应用

### 案例：《刺客信条：大革命》巴黎人群系统

《刺客信条：大革命》（2014）是人群LOD技术的标志性实现案例。该游戏同屏NPC数量峰值达到2000个，技术团队在GDC 2015上公开了其三层人群架构：

- **第一层（前景，0–20米）**：约30–50个完整骨骼NPC，使用标准Ubisoft ANM动画系统，支持碰撞响应与社会行为AI
- **第二层（中景，20–80米）**：约200–400个LOD1简化角色，动画更新频率10Hz，材质使用4种变体Atlas合并为单批次Instancing
- **第三层（背景，> 80米）**：约1500–2000个使用预烘焙Impostor（公告板图像）或极简BAT的"幽灵NPC"，每帧GPU消耗不超过0.3ms

最终整体人群系统在PS4（8核 Jaguar CPU + 1.84 TFLOPS GPU）上将帧时消耗控制在2.1ms以内。

### 案例：Unity DOTS Crowd Simulation

Unity 2022.3 LTS中，基于DOTS（Data-Oriented Technology Stack）的人群系统将NPC数据完全以SoA（Structure of Arrays）格式存储，动画更新使用Burst Compiler编译为SIMD指令。在Apple M1芯片的测试中，1000个LOD分级NPC的全系统更新耗时约0.9ms，较传统MonoBehaviour方案降低约87%。

---

## 常见误区

### 误区一：LOD切换距离对所有分辨率使用同一固定值

许多开发者直接使用固定的15米/40米切换阈值，而忽略了在4K分辨率下角色屏幕覆盖面积是1080P的4倍这一事实。在4K显示器上以固定15米切换LOD1，会导致仍占据屏幕约200像素高度的角色突然失去手指骨骼动画，产生明显的视觉退化（Popping）。正确做法是以屏幕像素覆盖面积（Screen Coverage）而非物理距离作为切换依据，Unreal Engine 5的Nanite与LOD系统已内置Screen Size阈值配置项（范围0–1，对应屏幕高度百分比）。

### 误区二：BAT与标准骨骼动画可以无缝混用同一套Rig

BAT烘焙纹理与标准骨骼动画系统使用不同的蒙皮路径：标准蒙皮由CPU计算矩阵调色板后上传GPU，而BAT完全在顶点着色器中采样纹理重建变换。两者切换时若不同步重置顶点缓冲区的蒙皮模式，会出现角色在切换瞬间T-Pose闪烁1帧的问题。Unreal的Crowd LOD插件通过在切换帧插入一帧混合过渡（权重从1.0到0.0的线性过渡，持续约3帧/0.05秒）规避了这一问题。

### 误区三：动画更新频率降低等同于动画播放变慢

AnimationBudgetAllocator将更新频率从60Hz降至15Hz，仅意味着骨骼Transform每4帧才重新计算一次，但动画播放时间戳依然以实际帧时间推进，并通过帧间线性插值（Pose Blending）使视觉上保持流畅。若误将动画的`DeltaTime`也同步除以4，则角色动画会以1/4速度慢动作播放，这是初接触该系统的工程师最常犯的错误之一。

---

## 知识关联

### 与LOD动画简化的关系

单角色LOD动画简化（前置知识）处理的是单一角色的骨骼层级削减与动画混合策略；人群LOD在此基础上增加了**批次合并维度**——仅靠减少单角色骨骼数量，在500个NPC同屏时仍会产生500次独立DrawCall，帧率依然不可接受。人群LOD的核心增量在于通过GPU Instancing与BAT将CPU侧O(N)复杂度的动画更新转化为GPU侧接近O(1)的并行计算。

### 与Impostor技术的关系

当NPC距离超过约100米时，BAT本身的几何体开销（即便是LOD2的低模网格，仍有约200–400个三角面）也变得浪费。此时人群LOD通常与**Impostor（公告板替换）**技术结合：使用预渲染的4–8方向角色图像替代3D网格，将三角面开销降至2个（一个四边形面片）。《地平线：零之曙光》的人群系统在150米以外完全切换为Impostor，相关技术细节见GDC 2017 "Horizon Zero Dawn: A Game Art Tricks"演讲。

###