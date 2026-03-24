---
id: "3da-pipe-batch-processing"
concept: "批量处理"
domain: "3d-art"
subdomain: "asset-pipeline"
subdomain_name: "资产管线"
difficulty: 3
is_milestone: true
tags: ["效率"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 41.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 批量处理

## 概述

批量处理（Batch Processing）是指通过脚本或工具对大量3D资产文件执行统一操作的技术方案，核心目标是用一条命令或一次运行替代手动逐文件操作。在资产管线中，批量处理通常涵盖模型格式转换（如`.fbx`批量转`.glb`）、贴图压缩（如将512张原始PNG批量生成DXT1/BC1格式）、LOD生成以及元数据写入等任务。

批量处理概念在游戏工业中随着项目规模膨胀而普及。早在1990年代，id Software开发Quake引擎时已使用批处理脚本生成关卡资产；现代AAA项目中，单个项目的资产数量可达数万个文件，手动逐一导出的时间成本完全不可接受。一套成熟的批量处理方案能将数百小时的人工操作压缩到数分钟的脚本运行时间。

批量处理在资产管线中的价值体现在一致性和可重复性上：脚本不会遗漏步骤、不会因为操作疲劳产生差异，每次运行结果在相同输入下完全一致。这对需要多次迭代重新导出的项目（如引擎升级、平台移植）至关重要。

## 核心原理

### 文件遍历与过滤机制

批量处理脚本的第一步是构建目标文件列表。Python脚本通常使用`os.walk()`或`pathlib.Path.rglob("*.fbx")`递归扫描目录树，配合正则表达式过滤出符合命名规范的文件。例如，仅处理名称符合`CH_[角色名]_[LOD级别]_v[版本号].fbx`格式的文件，非规范命名的文件会被记录到错误日志而非静默跳过。这正是批量处理与命名规范强依赖关系的体现——命名不规范会导致批量脚本错误分类或跳过文件。

### 操作封装与参数化

批量处理的核心设计是将单次操作封装为可参数化的函数。以Blender Python API（bpy）为例，导出单个模型的函数签名通常为：

```python
def export_model(source_path, target_dir, export_scale=0.01, apply_modifiers=True):
    bpy.ops.import_scene.fbx(filepath=str(source_path))
    bpy.ops.export_scene.gltf(filepath=str(target_dir / source_path.stem) + ".glb",
                               export_apply=apply_modifiers,
                               export_global_scale=export_scale)
```

将`export_scale=0.01`这类参数集中写入配置文件（JSON或YAML），可以在不修改脚本代码的情况下调整输出规格，满足不同平台（如PC端与移动端）使用不同压缩质量的需求。

### 错误处理与日志记录

健壮的批量处理脚本必须对每个文件独立捕获异常，使用`try/except`包裹单文件处理逻辑，确保一个损坏的FBX文件不会中断整个批次的处理。日志文件需要记录四项关键信息：处理时间戳、文件路径、操作结果（成功/失败/跳过）、以及失败时的具体错误信息（如"顶点数超过65535限制"）。完成后输出汇总报告，例如"共处理342个文件，325成功，17失败，详见`batch_log_20240315.txt`"，方便美术人员定向修复问题文件。

### 增量处理与哈希校验

对于需要频繁重新运行的管线，全量批处理每次都处理所有文件会浪费大量时间。增量处理方案使用文件的MD5哈希值或修改时间戳与上次运行的记录作对比，仅重新处理发生变化的文件。实现上维护一个JSON格式的缓存文件，键为文件路径，值为上次处理时的哈希值，脚本启动时加载此缓存，跳过哈希未变化的文件，处理结束后更新缓存。

## 实际应用

**贴图批量压缩**：在Unity项目中，使用`Unity Editor`的`AssetPostprocessor`脚本对导入`Assets/Textures/Environment/`目录下的所有PNG文件自动应用DXT5压缩（含Alpha通道）或DXT1压缩（不含Alpha），并将最大分辨率限制为2048×2048。这个脚本在美术人员拖入贴图的瞬间自动触发，无需手动设置导入参数。

**多格式批量导出**：手机游戏项目同时维护iOS（Metal，使用ASTC压缩）和Android（Vulkan，使用ETC2压缩）两套资产。批量处理脚本读取同一批原始FBX，分别使用不同参数导出到`Build/iOS/`和`Build/Android/`两个目录，每次构建前自动完成，美术人员只需维护一套源文件。

**LOD批量生成**：使用命令行工具`meshoptimizer`或Unreal Engine的Python脚本接口，对场景内所有静态网格体自动生成LOD0至LOD3，简化比例分别设置为100%、50%、25%、12.5%，并将结果写回原始资产。

## 常见误区

**误区一：批量脚本可以兼容任何命名方式**
许多初学者认为只要脚本"搜索所有FBX文件"就能处理全部资产，而忽视了脚本内部逻辑依赖文件名解析出角色类型、LOD层级等语义信息。例如，从文件名`CH_Knight_LOD0_v3.fbx`中解析出`LOD0`用于决定导出精度，若文件命名为`knight_final_REAL.fbx`，脚本将无法提取LOD信息并报错或使用错误默认值。批量处理与命名规范是强耦合关系，脚本应在文档中明确声明支持的命名格式。

**误区二：批量处理速度越快越好，应尽量用多线程**
对于调用DCC软件（如Maya、Blender）的批量操作，多进程并行处理并非总是可行的。许多DCC软件的命令行模式不支持多实例同时写入同一资产库，或者会产生许可证（License）冲突（浮动授权服务器同时只允许N个实例）。正确做法是先评估工具链的并发支持能力，对于支持无头（headless）运行的工具（如`meshoptimizer`命令行），才安全地使用Python的`multiprocessing.Pool`进行并行化。

**误区三：批量处理结果只要文件生成就算成功**
脚本报告"0个错误"不代表输出文件质量合格。批量导出后必须加入自动化验证步骤：检查输出文件体积是否在合理范围（如单个角色网格不超过2MB）、顶点数是否满足目标平台限制、必要的贴图通道是否存在。没有验证步骤的批量处理只是把问题从"手动操作错误"变成了"脚本系统性错误"。

## 知识关联

**前置依赖：命名规范**
批量处理脚本的文件过滤、分类、参数提取逻辑全部建立在可预测的命名规范之上。没有统一命名规范，批量脚本要么需要为每种命名变体编写特判逻辑（导致脚本难以维护），要么对文件误分类。命名规范是批量处理正确运作的前提条件。

**后续发展：管线自动化**
批量处理是手动触发的脚本执行，而管线自动化在此基础上引入事件驱动机制：当源文件提交到版本控制系统（如Git LFS或Perforce）时，CI/CD系统（如Jenkins、TeamCity）自动触发相应的批量处理任务，美术人员无需手动运行任何脚本。批量处理脚本是管线自动化的执行单元，自动化系统负责调度和触发这些脚本。
