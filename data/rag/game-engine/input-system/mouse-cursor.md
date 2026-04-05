---
id: "mouse-cursor"
concept: "鼠标光标处理"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 2
is_milestone: false
tags: ["鼠标"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 鼠标光标处理

## 概述

鼠标光标处理是游戏引擎输入系统中专门管理鼠标指针**可见性**、**位置约束**和**渲染方式**的子系统。它直接决定玩家在游戏窗口内的鼠标体验——无论是点击式UI界面中跟随鼠标移动的自定义手型指针，还是第一人称射击游戏中光标被完全隐藏并每帧强制归位到屏幕中心。

光标处理的需求随早期图形操作系统的普及而成形。1984年Apple Macintosh System 1.0首次将鼠标光标作为核心交互元素引入消费市场；1990年Windows 3.0开始以32×32像素单色位图作为系统光标的标准格式（`.cur` 文件）。早期DOS游戏无需处理光标，因为它们独占显存，不存在"桌面光标滑出窗口"的问题。当游戏迁移到Windows窗口化环境后，引擎开发者才意识到必须主动管理光标，才能在游戏内交互与桌面环境之间正确切换。

现代主流引擎均提供封装好的跨平台光标API：Unity 2017.1 起通过 `UnityEngine.Cursor` 静态类统一管理光标；Unreal Engine 4/5 通过 `UPlayerController` 的 `bShowMouseCursor` 属性和 `EMouseCursor` 枚举类型控制光标形状，底层屏蔽了 Win32 `ShowCursor()`、X11 `XDefineCursor()`、macOS `NSCursor` 等平台差异。

正确处理光标对游戏体验至关重要：在RTS或RPG游戏中，错误隐藏光标会导致玩家无法点击UI；在FPS游戏中，未锁定的光标滑出窗口边界则会导致每帧鼠标增量数据被操作系统截断，角色视角旋转因此卡死或中断。

---

## 核心原理

### 显示与隐藏（Visibility）

引擎通过调用平台层API切换光标的可见状态。Unity的接口为 `Cursor.visible = true/false`；Unreal为 `PlayerController->bShowMouseCursor = true/false`。

Windows底层原理是维护一个**全局光标可见计数器**：`ShowCursor(TRUE)` 将计数器加1，`ShowCursor(FALSE)` 将计数器减1，**只有计数器值 ≥ 0 时光标才可见**。若某段代码错误调用了3次 `ShowCursor(FALSE)` 而只调用了1次 `ShowCursor(TRUE)`，计数器停留在 -2，光标不会恢复可见——这是引起光标"永久消失"bug的常见根源，必须成对调用。Unity的 `Cursor.visible` 封装屏蔽了此计数器逻辑，每次赋值 `true` 时会将计数器归零而非仅加1，避免了直接调用Win32 API带来的配对问题。

### 锁定模式（Lock Mode）

锁定分为三种语义，Unity的 `CursorLockMode` 枚举精确对应：

- **`CursorLockMode.None`**：光标自由移动，不受窗口约束，可滑出游戏窗口至桌面。适用于菜单界面。
- **`CursorLockMode.Confined`**：光标可自由移动，但被约束在游戏窗口客户区矩形内。Windows底层调用 `ClipCursor(RECT*)` 传入窗口客户区坐标。适用于策略游戏，防止鼠标滑至第二屏幕。
- **`CursorLockMode.Locked`**：每帧将光标强制归位到窗口中心坐标 `(Screen.width/2, Screen.height/2)`，同时操作系统通过 Raw Input 或 Pointer Lock API 持续报告**增量位移**而非绝对坐标。Web平台等价实现为W3C标准的 Pointer Lock API（`canvas.requestPointerLock()`，2016年成为正式推荐标准）。

**关键行为差异**：锁定状态下 `Input.mousePosition` 始终返回屏幕中心坐标（无意义），必须改用 `Input.GetAxis("Mouse X")` 和 `Input.GetAxis("Mouse Y")` 读取帧间增量，两者不可混用。

### 软件光标与硬件光标

硬件光标（Hardware Cursor）由操作系统或GPU驱动直接合成到最终显示帧，完全独立于游戏的渲染循环；软件光标（Software Cursor）是引擎在游戏渲染管线末尾绘制的一个普通精灵（Sprite），随游戏帧率刷新。

| 特性 | 硬件光标 | 软件光标 |
|---|---|---|
| 渲染者 | OS / GPU驱动叠加层 | 引擎游戏循环（CPU/GPU） |
| 帧率依赖 | 独立，移动延迟 < 1ms | 与游戏帧率同步，存在 1 帧延迟 |
| 尺寸上限 | Windows：32×32 或 64×64（DPI缩放后） | 无限制 |
| 动画能力 | 有限（`.ani` 多帧格式，Windows专有） | 完整精灵动画，可叠加Shader效果 |
| 跨平台一致性 | 各OS外观不一致 | 完全一致 |

硬件光标加载（Windows平台）：
```csharp
// Unity 硬件光标：将 Texture2D 转换为系统光标
// hotspot 为光标纹理中的"热点"像素坐标（即实际点击点）
Texture2D cursorTex = Resources.Load<Texture2D>("Cursors/Crosshair");
Vector2 hotspot = new Vector2(16, 16); // 64×64 纹理的中心点
Cursor.SetCursor(cursorTex, hotspot, CursorMode.Auto);
// CursorMode.Auto: 优先尝试硬件光标，失败则自动降级为软件光标
// CursorMode.ForceSoftware: 强制软件光标（用于需要Shader特效的场景）
```

软件光标实现的核心在于将光标精灵绘制在UI Canvas的最高层级（`sortingOrder` 设为最大值），并在 `LateUpdate()` 中同步光标纹理位置到 `Input.mousePosition`，同时调用 `Cursor.visible = false` 隐藏系统光标，防止双重光标叠加显示。

---

## 关键公式与参数计算

### 热点坐标（Hotspot）

热点是光标纹理中代表"实际点击位置"的像素坐标，以纹理左上角为原点 `(0, 0)`。例如箭头光标的热点通常在 `(0, 0)`（箭头尖端），而十字准星光标的热点在纹理中心：

$$\text{hotspot} = \left(\frac{W_{texture}}{2},\ \frac{H_{texture}}{2}\right)$$

若将64×64像素的准星纹理的热点错误设为 `(0, 0)`，玩家单击时实际命中区域会在视觉准星左上角偏移32像素，造成点击偏差。

### 鼠标增量与相机旋转灵敏度

在 `CursorLockMode.Locked` 模式下，相机旋转角度由鼠标增量和灵敏度系数共同决定：

$$\Delta\theta_{yaw} = \Delta x_{mouse} \times S_{sensitivity} \times \Delta t$$
$$\Delta\theta_{pitch} = \Delta y_{mouse} \times S_{sensitivity} \times \Delta t$$

其中 $\Delta x_{mouse}$ 和 $\Delta y_{mouse}$ 为 `Input.GetAxis("Mouse X/Y")` 的返回值（已由 Unity 内部乘以 `Time.deltaTime` 归一化），$S_{sensitivity}$ 为用户可调灵敏度系数，典型取值范围为 `[0.5, 5.0]`。注意：Unity 的 `GetAxis` 返回值已经过平滑处理（平滑系数由 Input Manager 的 `Sensitivity` 和 `Gravity` 字段控制），若需原始像素级增量应改用 `Input.GetAxisRaw`。

---

## 实际应用

### FPS游戏的光标管理流程

第一人称射击游戏的光标状态切换是最典型的应用场景：

```csharp
public class FPSCursorManager : MonoBehaviour
{
    void Start()
    {
        // 游戏开始时锁定并隐藏光标
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    void Update()
    {
        // 按 Escape 暂停时释放光标，允许点击暂停菜单
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            bool isPaused = GameManager.Instance.IsPaused;
            Cursor.lockState = isPaused ? CursorLockMode.None : CursorLockMode.Locked;
            Cursor.visible = isPaused;
        }
    }

    void OnApplicationFocus(bool hasFocus)
    {
        // 窗口失去焦点时自动释放光标，恢复焦点时重新锁定
        // 防止 Alt+Tab 后光标仍被锁定导致无法操作桌面
        if (!hasFocus)
        {
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }
        else if (!GameManager.Instance.IsPaused)
        {
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
        }
    }
}
```

`OnApplicationFocus` 回调是新手最容易遗漏的处理点：若不在失焦时释放光标，玩家 Alt+Tab 切换到其他程序后，光标仍处于锁定状态，导致无法正常使用桌面。

### RTS游戏的多状态光标

即时战略游戏（如《星际争霸2》）通常根据鼠标悬停目标动态切换光标形状：悬停可攻击单位时显示攻击光标，悬停友军时显示选择光标，悬停地形时显示移动光标。实现方式是在 `Update()` 中执行射线检测（Raycast），根据命中对象的 Tag 或 Layer 调用不同参数的 `Cursor.SetCursor()`，每次切换硬件光标的开销约为一次系统调用，频率控制在每帧最多一次即可。

---

## 常见误区

**误区1：在锁定模式下读取 `Input.mousePosition`**

`CursorLockMode.Locked` 激活时，`Input.mousePosition` 始终返回 `(Screen.width/2, Screen.height/2)`，即屏幕中心的固定坐标，对旋转计算毫无意义。正确做法是读取 `Input.GetAxis("Mouse X")` 和 `"Mouse Y"` 的增量值。

**误区2：软件光标未在 `LateUpdate` 中更新位置**

若在 `Update()` 中更新软件光标位置，而场景中存在改变 `Input.mousePosition` 的脚本（极少见，但模拟鼠标输入时存在），两者执行顺序不可靠，应统一在 `LateUpdate()` 中同步光标精灵位置，确保在当帧所有逻辑处理完毕后再刷新显示位置。

**误区3：混用硬件光标和软件光标而不隐藏系统光标**

切换为软件光标模式时，若忘记调用 `Cursor.visible = false`，玩家会同时看到游戏内的精灵光标和系统原生光标两个指针叠加在一起。

**误区4：在WebGL平台未处理 Pointer Lock 的异步授权**

浏览器的 Pointer Lock API 需要用户手势触发（如点击事件），且返回的是异步 Promise。在 WebGL 构建的 Unity 游戏中，`Cursor.lockState = CursorLockMode.Locked` 必须在用户点击事件回调中调用，若在 `Start()` 中直接调用会因缺少用户手势而被浏览器静默拒绝，光标锁定不生效。

---

## 知识关联

**前置概念——输入设备抽象**：鼠标光标处理建立在输入设备抽象层之上。`Input.GetAxis("Mouse X")` 的增量数据来源于底层 Raw Input（Windows）或 evdev（Linux）的鼠标移动事件，经过引擎的设备抽象层统一封装后才暴露为光标增量。理解设备抽象层有助于解释为何在 `CursorLockMode.Locked` 下仍能持续收到鼠标移动数据——增量来自硬件报告，不依赖光标的屏幕坐标。

**后续概念——摄像机输入控制**：摄像机的旋转控制直接消费鼠标光标处理的输出——`Mouse X/Y` 增量。