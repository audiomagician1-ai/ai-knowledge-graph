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
quality_tier: "pending-rescore"
quality_score: 41.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 编辑器测试

## 概述

编辑器测试（Editor Testing）是指在游戏引擎编辑器模式（Editor Mode）下运行的自动化测试，区别于游戏运行时（Play Mode）测试，它专门验证编辑器工具、Inspector面板、自定义窗口、菜单扩展等编辑器功能的正确性。由于编辑器代码运行在引擎进程而非游戏进程中，编辑器测试需要访问引擎的编辑器API（如Unity中的`UnityEditor`命名空间或Unreal的`EditorScriptingUtilities`），这使其与普通单元测试在执行环境上存在根本差异。

编辑器测试的概念随着游戏引擎工具化程度提升而兴起。Unity在2018年引入Test Framework 1.0时正式将编辑器测试（Edit Mode Test）与运行时测试（Play Mode Test）明确区分，提供了`[UnityEditor.TestTools]`标注体系。Unreal Engine则通过`FEditorAutomationTestBase`类支持编辑器层面的自动化验证。这一区分解决了早期开发者将编辑器逻辑混入运行时测试导致的环境污染问题。

在实际游戏开发管线中，美术工具、关卡编辑脚本、资产导入处理器（AssetPostprocessor）等编辑器扩展代码往往缺乏测试保障，一旦引擎版本升级或编辑器API变更，这些工具会静默损坏。编辑器测试能在CI/CD流程中提前捕获此类回归，避免美术或设计团队依赖损坏工具进行低效返工。

---

## 核心原理

### Edit Mode 与 Play Mode 的执行差异

Edit Mode测试在Unity中使用`[UnityTest]`或`[Test]`标注，并要求测试程序集放置在 `Editor` 文件夹下，或在 `.asmdef` 文件中将 `Include Platforms` 配置为仅 `Editor`。Edit Mode测试在不启动游戏循环（Game Loop）的情况下直接访问`AssetDatabase`、`EditorUtility`等API，因此每帧协程（`yield return null`）的含义是"等待编辑器的下一次更新"而非"等待游戏帧"，这导致Edit Mode测试的帧等待行为不同于Play Mode。Unreal中对应概念为 `EAutomationTestFlags::EditorContext` 标志位，只有携带此标志的测试才能访问`GEditor`全局指针。

### AssetDatabase 的事务性测试模式

编辑器测试中对资产操作的验证需要特别处理文件系统副作用。Unity提供 `AssetDatabase.StartAssetEditing()` 与 `AssetDatabase.StopAssetEditing()` 包裹批量操作，但在测试中更常见的模式是在 `[TearDown]` 阶段调用 `AssetDatabase.DeleteAsset(testAssetPath)` 清理测试产生的临时资产。若不执行清理，多次运行测试将在 `Assets/` 目录下累积垃圾资产，并触发不必要的重新导入（reimport）开销，每次导入纹理资产可能耗费数百毫秒，严重拖慢CI。

### SerializedObject 状态验证

编辑器测试的核心验证对象之一是`SerializedObject`和`SerializedProperty`。测试Custom Editor时，标准模式是：
1. 用`GameObject go = new GameObject()` 创建临时对象并挂载目标组件；
2. 用`SerializedObject so = new SerializedObject(component)` 获取序列化视图；
3. 调用编辑器逻辑后用`so.FindProperty("fieldName").intValue` 断言属性值；
4. 在`[TearDown]`中调用`Object.DestroyImmediate(go)` 防止测试对象泄漏到场景。

若跳过`DestroyImmediate`改用`Destroy`，对象会残留在编辑器场景中直到下一帧，导致后续测试读取到脏数据。

### 菜单与编辑器窗口的触发测试

验证`[MenuItem]`标注方法是否正常触发，可通过反射直接调用静态方法，而不必模拟UI点击。例如：
```csharp
typeof(MyEditorTool)
    .GetMethod("BuildLightingData", BindingFlags.Static | BindingFlags.NonPublic)
    .Invoke(null, null);
Assert.IsTrue(LightingDataAsset.ExistsAtPath("Assets/LightingData.asset"));
```
这种方式绕过菜单系统的权限检查，直接验证业务逻辑，执行时间比通过`EditorApplication.ExecuteMenuItem`快约40%。

---

## 实际应用

**自定义资产导入器的回归测试**：美术团队使用自定义`ScriptedImporter`处理`.vfx`特效文件时，编写编辑器测试将一个固定的`.vfx`测试文件复制到`Assets/TestArtifacts/`路径，触发`AssetDatabase.ImportAsset()`，然后断言导入后的`ScriptableObject`中`ParticleCount`属性等于预期的128。当Shader编译逻辑被修改时，该测试在CI第一步（Edit Mode Tests）即报错，而非等到QA运行游戏时才发现视觉异常。

**Inspector 自动布局验证**：针对复杂的Custom Editor，可验证`OnInspectorGUI`执行后不抛出`NullReferenceException`，做法是在测试中实例化Editor对象：`var editor = Editor.CreateEditor(component)`，然后在`using var scope = new EditorGUILayout.VerticalScope()` 保护下调用`editor.OnInspectorGUI()`，捕获任何异常作为测试失败依据。

**场景批处理工具的幂等性测试**：关卡工具（如自动摆放Probe的编辑器脚本）应满足幂等性，即运行两次与运行一次结果相同。编辑器测试可加载测试场景、运行工具两次，然后断言`LightProbeGroup`中探针数量在两次运行后保持一致，防止工具重复执行时指数级增加探针导致场景文件臃肿。

---

## 常见误区

**误区一：在编辑器测试中使用`Object.Destroy`而非`Object.DestroyImmediate`**。`Destroy`在编辑器Edit Mode下不会立即销毁对象，而是将其标记为待删除并在下一帧处理。这意味着`[TearDown]`完成后该对象仍然存在于场景中，下一个测试的`FindObjectOfType<T>()`调用将错误地找到该残留对象，产生测试间依赖（Test Interdependency）。编辑器测试中必须使用`DestroyImmediate`确保同步清理。

**误区二：认为编辑器测试可以不依赖 `[InitializeOnLoad]` 初始化完成**。部分编辑器扩展通过`[InitializeOnLoad]`在域重载（Domain Reload）时注册回调或初始化静态状态。测试运行器在执行Edit Mode测试前会触发域重载，若测试假设这些静态状态已初始化，而`[InitializeOnLoad]`类的执行顺序晚于测试构造函数，将导致测试访问未初始化的服务定位器（Service Locator）。正确做法是在`[OneTimeSetUp]`中显式调用初始化方法，而非依赖隐式的类加载顺序。

**误区三：用Play Mode测试替代Edit Mode测试来验证编辑器工具**。Play Mode测试启动游戏循环，`AssetDatabase`操作在Play Mode下有诸多限制（如无法删除正在使用的资产），且每次运行Play Mode测试需要额外约2-5秒的进入/退出Play Mode开销。对于纯编辑器功能的验证，错误地选择Play Mode会显著增加CI时间并引入不必要的运行时环境变量。

---

## 知识关联

从**编辑器扩展概述**中掌握的`CustomEditor`、`EditorWindow`、`MenuItem`等API是编辑器测试的直接被测对象；不了解这些API的作用域和生命周期，就无法编写有意义的断言。

从**引擎测试框架**中学到的测试生命周期（`[SetUp]`/`[TearDown]`/`[OneTimeSetUp]`）和断言方法（`Assert.AreEqual`、`Assert.Throws`）在编辑器测试中完全复用，但编辑器测试额外引入了`[UnitySetUp]`（返回`IEnumerator`以在编辑器帧之间执行异步设置）这一编辑器专用特性，这是标准NUnit框架中不存在的扩展点。掌握编辑器测试后，开发者具备为整个工具管线（Asset Pipeline → Editor Tools → Scene Processing）构建完整自动化回归套件的能力，是游戏引擎工具质量工程的终点实践。
