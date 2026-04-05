---
id: "editor-test"
concept: "编辑器测试"
domain: "game-engine"
subdomain: "editor-extension"
subdomain_name: "编辑器扩展"
difficulty: 3
is_milestone: false
tags: ["测试"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 编辑器测试

## 概述

编辑器测试（Editor Testing）是指在游戏引擎编辑器模式（Editor Mode）下运行的自动化测试，专门验证编辑器扩展功能、自定义工具窗口、Inspector 面板、菜单项以及资产处理流程的正确性。与运行时测试不同，编辑器测试在引擎的 `EditMode` 上下文中执行，不需要启动 Play Mode，因此测试速度更快，且可直接操作 Scene 层级结构、Asset Database 和 Serialization 系统。

以 Unity 为例，编辑器测试体系于 Unity 5.3 版本随 Test Runner 窗口正式引入，使用 NUnit 3.x 框架作为底层测试库，并通过 `[UnityTest]` 和 `[Test]` 特性区分协程测试与普通同步测试。编辑器测试必须放置在名为 `Editor` 的特殊文件夹下或在 Assembly Definition 文件中明确标注 `Editor` 平台，否则代码无法被 Test Runner 识别。

编辑器测试的核心价值在于保护工具链的稳定性。当团队成员修改了自定义 Inspector 的序列化逻辑或更改了资产导入管线的处理步骤时，编辑器测试能在进入 Play Mode 之前就捕获到回归问题，将问题发现时间从"运行游戏时"缩短到"保存脚本后数秒内"。

## 核心原理

### EditMode 测试的执行环境

Unity Test Runner 的 EditMode 测试在主线程上同步执行，直接运行于 `UnityEditor` 命名空间可用的环境中。测试代码可以调用 `AssetDatabase.CreateAsset()`、`EditorUtility.SetDirty()` 等仅在编辑器中存在的 API。每个测试方法运行前后，Test Runner 不会自动还原 Scene 状态，因此测试编写者必须在 `[TearDown]` 方法中手动清理通过 `new GameObject()` 或 `AssetDatabase` 操作创建的对象，否则会造成测试间的状态污染。

### 测试类的组织结构

编辑器测试类使用标准 NUnit 特性进行声明，但有两处编辑器特有约定：第一，使用 `[UnityTest]` 返回 `IEnumerator` 可以等待编辑器帧（通过 `yield return null` 跳过一帧），用于测试需要延迟刷新的 Inspector 重绘或 AssetDatabase 导入回调；第二，`[SetUp]` 中可以通过 `EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single)` 为每个测试创建干净的 Scene 环境。典型测试类声明如下：

```csharp
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

[TestFixture]
public class CustomInspectorTests
{
    private GameObject _testObject;

    [SetUp]
    public void Setup()
    {
        _testObject = new GameObject("TestTarget");
    }

    [TearDown]
    public void Teardown()
    {
        Object.DestroyImmediate(_testObject);
    }

    [Test]
    public void CustomComponent_SerializesFieldCorrectly()
    {
        var comp = _testObject.AddComponent<MyCustomComponent>();
        comp.Value = 42;
        EditorUtility.SetDirty(comp);
        Assert.AreEqual(42, comp.Value);
    }
}
```

### AssetDatabase 操作的测试模式

测试涉及资产创建和修改时，需要在 `Assets/` 目录下的临时路径（通常约定为 `Assets/Tests/Temp/`）创建测试资产，并在 `[TearDown]` 或 `[OneTimeTearDown]` 中调用 `AssetDatabase.DeleteAsset()` 清除它们。`AssetDatabase.Refresh()` 调用会触发完整的导入流程，耗时可能超过 500ms，应尽量用 `AssetDatabase.StartAssetEditing()` 和 `AssetDatabase.StopAssetEditing()` 批量包裹多个资产操作，将多次导入合并为一次，显著降低测试套件的总执行时间。

### 使用 MenuItem 和 EditorWindow 的测试策略

测试 `EditorWindow` 子类时，应通过 `EditorWindow.GetWindow<T>()` 实例化窗口，然后直接调用窗口的公开方法或内部逻辑方法，而不是模拟 GUI 点击事件。`OnGUI` 方法依赖 `Event.current` 上下文，在测试环境中无法可靠触发，因此正确做法是将业务逻辑从 `OnGUI` 中分离到独立的可测试方法中。

## 实际应用

**自定义资产处理器验证**：团队为游戏编写了一个 `ScriptedImporter`，将 `.dialogue` 扩展名的文本文件解析为 `DialogueAsset` ScriptableObject。编辑器测试将一个测试用 `.dialogue` 文件放入 `Assets/Tests/Temp/` 并触发导入，然后断言生成的 `DialogueAsset` 包含正确数量的对话节点（例如断言 `asset.Lines.Count == 5`）。每次修改解析器逻辑后，CI 管线中的编辑器测试套件会在 2 分钟内给出通过或失败的反馈。

**Inspector 序列化回归测试**：某个自定义组件使用 `[SerializeField]` 存储嵌套数据结构。测试通过 `EditorJsonUtility.ToJson()` 序列化组件状态，修改字段后再反序列化，验证 `Undo.RecordObject` 是否正确记录了变更，确保 Undo 栈在 Inspector 操作后保持完整。

**编辑器菜单功能测试**：为 `Tools/Generate Level Data` 菜单项编写测试时，直接调用该菜单背后的静态方法 `LevelDataGenerator.GenerateAll()`，验证其在 `Assets/Generated/` 路径下创建了预期数量的 ScriptableObject 文件，并通过 `AssetDatabase.LoadAssetAtPath<LevelData>()` 加载后断言字段值的正确性。

## 常见误区

**误区一：在编辑器测试中使用 PlayMode 专用 API**
`Physics.Raycast()`、`Application.isPlaying` 检测、`Coroutine` 的 `StartCoroutine()` 在 EditMode 测试中行为异常或直接无效。`Physics.Raycast()` 在 EditMode 下不会模拟物理步骤，总是返回 `false`。如果需要测试涉及物理的编辑器工具，应将物理计算逻辑抽象为纯函数，单独对其输入输出进行断言。

**误区二：测试结束后不清理 Scene 对象导致测试相互干扰**
多个测试共享同一个 Scene 时，前一个测试遗留的 `GameObject` 会被下一个测试的 `FindObjectOfType()` 意外发现，造成假阳性通过或假阴性失败。正确做法是每个 `[TearDown]` 调用 `Object.DestroyImmediate()` 清理所有在 `[SetUp]` 中创建的对象，或在 `[SetUp]` 中调用 `EditorSceneManager.NewScene()` 强制重置 Scene。

**误区三：将 `AssetDatabase.Refresh()` 视为同步操作**
在调用 `AssetDatabase.Refresh()` 后立即断言资产属性，有时会因导入尚未完成而读到旧数据。正确的处理方式是使用 `[UnityTest]` 结合 `yield return new WaitForDomainReload()` 或检查 `AssetDatabase.IsMainAsset()` 返回值，确认资产已被正确注册后再执行断言。

## 知识关联

编辑器测试建立在**编辑器扩展概述**所描述的 `Editor` 文件夹结构和 `CustomEditor`/`EditorWindow` 扩展点之上——只有理解这些扩展点的生命周期，才能知道在 `[SetUp]` 中应该初始化哪些对象。同时，编辑器测试直接依赖**引擎测试框架**中 NUnit 的 `Assert` 体系、`[TestFixture]` 组织方式和 Test Runner 的执行模型；`[UnityTest]` 特性对 NUnit `[Test]` 的协程扩展是 Unity 在标准 NUnit 之上做出的专有增强，两者并存于同一个测试类中时需要清楚区分其适用场景。掌握编辑器测试后，开发者可以将其纳入 CI/CD 流程（例如通过命令行参数 `-runTests -testPlatform editmode` 启动无头测试），使整个编辑器工具链获得与运行时代码同等级别的自动化质量保障。