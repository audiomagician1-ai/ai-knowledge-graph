---
id: "vfx-vfxgraph-property"
concept: "Exposed Property"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# 暴露属性（Exposed Property）

## 概述

暴露属性（Exposed Property）是 VFX Graph 中一种将图内部参数开放给外部系统访问的机制。当你在 VFX Graph 的 Blackboard 面板中勾选某个属性的"Exposed"复选框时，该属性就会出现在 VisualEffect 组件的 Inspector 中，并可通过 C# 脚本在运行时动态读写。这个机制让粒子系统与游戏逻辑之间建立了清晰的数据通道。

暴露属性功能随 Unity VFX Graph 包的正式发布（Unity 2019.3，VFX Graph 7.0）一同提供稳定支持。在此之前，修改粒子行为需要重建资产或依赖间接方案。暴露属性的设计参考了 Shader Graph 中同名机制，两套系统使用统一的属性命名和哈希查找逻辑。

该功能的核心意义在于：VFX Graph 本身是一个封闭的节点图，外部无法直接触碰节点参数；而暴露属性打开了一个受控的接口，允许角色死亡触发颜色渐变、技能冷却驱动发射速率等具体游戏需求，同时不破坏 Graph 内部的数据流结构。

## 核心原理

### 属性注册与哈希 ID

每个暴露属性在首次设置时，VFX Graph 会为其名称计算一个 `int` 类型的哈希 ID，通过静态方法 `Shader.PropertyToID("属性名")` 获取。在 C# 脚本中推荐提前缓存此 ID：

```csharp
private static readonly int k_SpawnRate = Shader.PropertyToID("SpawnRate");
```

直接传字符串名称的调用方式也受支持，但每次调用都会重新计算哈希，在高频更新（如每帧修改粒子颜色）场景下会产生可测量的性能损耗。使用哈希 ID 的版本比字符串版本调用约快 3 倍（Unity 官方性能测试数据）。

### 支持的属性类型与对应 API

暴露属性支持以下具体类型，每种类型对应不同的 API 方法对：

| 属性类型 | Set 方法 | Get 方法 |
|----------|----------|----------|
| `float` | `SetFloat` | `GetFloat` |
| `int` | `SetInt` | `GetInt` |
| `bool` | `SetBool` | `GetBool` |
| `Vector3` | `SetVector3` | `GetVector3` |
| `Color` | `GetVector4` 配合转换 | 同左 |
| `Texture2D` | `SetTexture` | `GetTexture` |
| `Mesh` | `SetMesh` | `GetMesh` |
| `AnimationCurve` | `SetAnimationCurve` | — |

`Color` 类型在 VFX Graph 内部以 `Vector4` HDR 存储，因此需要使用 `SetVector4` 传入 `(Color)` 的隐式转换结果，而不是专用的 `SetColor`（该方法不存在于 `VisualEffect` API）。

### 运行时读写流程

`VisualEffect` 组件是所有属性操作的入口，完整的运行时写入流程如下：

```csharp
using UnityEngine;
using UnityEngine.VFX;

public class VFXController : MonoBehaviour
{
    [SerializeField] private VisualEffect vfx;
    private static readonly int k_SpawnRate = Shader.PropertyToID("SpawnRate");

    public void SetSpawnRate(float rate)
    {
        // 建议先检查属性是否存在，避免运行时报错
        if (vfx.HasFloat(k_SpawnRate))
            vfx.SetFloat(k_SpawnRate, rate);
    }
}
```

`HasFloat`、`HasInt` 等检查方法可验证属性名是否在当前 VFX Asset 中存在且类型匹配。在资产更新或热重载后，未及时更新脚本侧的属性名会导致静默失败（无异常但属性不更新），`Has*` 检查是防御这类问题的推荐做法。

### Inspector 覆盖与脚本控制的优先级

在 VisualEffect 组件 Inspector 中手动设置的属性值会作为"覆盖值"存储在组件上。当脚本调用 `SetFloat` 时，等同于在运行时写入同一覆盖值，两者互不区分。调用 `ResetOverride(propertyID)` 可以将单个属性恢复为 VFX Asset 中 Blackboard 定义的默认值；调用 `vfx.initialEventName` 相关 API 可控制整体初始化行为。

## 实际应用

**技能命中粒子强度控制**：在技能命中特效的 VFX Graph 中暴露一个名为 `HitForce` 的 `float` 属性，连接到 Turbulence 节点的强度输入。伤害计算系统在命中时调用 `vfx.SetFloat("HitForce", damage * 0.1f)`，不同伤害值产生不同剧烈程度的粒子扰动，无需为每种伤害档位创建独立的 VFX Asset。

**Timeline 控制发射颜色**：配合 Timeline 集成（前置概念），在 VisualEffectControlTrack 的 Clip 内无法直接写属性，但可以在 Timeline 的 Signal 信号触发时，由绑定的 SignalReceiver 调用脚本方法，再通过暴露属性修改颜色。这条路径比 Activation Track 开关整个特效拥有更细粒度的控制。

**角色状态驱动粒子密度**：暴露 `SpawnRateMultiplier`（float）并在角色的 Update 中将其绑定到血量百分比：`vfx.SetFloat(k_Multiplier, health / maxHealth)`。由于该操作每帧执行，必须使用预缓存的哈希 ID 而非字符串，否则在 60fps 下每秒产生 60 次额外哈希计算。

## 常见误区

**误区一：认为暴露属性与 VFX Graph 中的节点参数是同一回事**。Blackboard 中未勾选 Exposed 的属性可以在图内被多个节点引用，但外部完全不可见；勾选后外部可访问，但图内的引用关系完全不变。两者是同一数据的"可见性开关"，不是两种不同的数据存储。

**误区二：以为 `SetFloat` 调用会立即影响当前帧的粒子**。VFX Graph 在 GPU 上以异步方式更新，属性修改在下一个 VFX Graph 更新步骤（通常是下一帧的 Early Update 阶段）才生效。若需要同帧精确同步，需调用 `vfx.SendEvent` 配合暴露属性共同使用，或检查 `VFXManager.fixedTimeStep` 设置。

**误区三：混淆 `VisualEffect.SetFloat` 与 `MaterialPropertyBlock.SetFloat`**。Material Property Block 作用于渲染器的材质，而 `VisualEffect.SetFloat` 写入的是 VFX Graph Simulation 的逻辑参数。两套 API 互不相通，即使 VFX Graph 内部某节点最终影响的是渲染输出，也必须通过 `VisualEffect` 组件的接口修改，不能绕道 MaterialPropertyBlock。

## 知识关联

**前置：Timeline 集成**。Timeline 集成中使用的 VisualEffectControlTrack 本质上在幕后调用的也是 `SetFloat`/`SendEvent` 等同一套 API。理解暴露属性的哈希机制有助于诊断 Timeline Clip 属性绑定失效的问题，因为两者的失效原因高度一致（属性名拼写错误或类型不匹配）。

**后续：VFX Graph 性能**。暴露属性的调用频率直接影响 VFX Graph 的 CPU 开销。在性能优化阶段需要了解：每次 `Set*` 调用会标脏对应的 GPU 缓冲区，高频属性（如逐帧位置更新）与低频属性（如游戏开始时设置一次颜色）应在设计时区分，后者可通过 `vfx.pause` 配合批量设置再恢复来减少无效的缓冲区更新。