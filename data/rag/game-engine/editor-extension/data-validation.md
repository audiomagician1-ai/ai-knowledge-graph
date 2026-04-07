# 数据校验工具

## 概述

数据校验工具（Data Validation Tool）是游戏编辑器扩展中用于自动检测资产是否符合项目工程规范的功能模块。它在资产导入、保存或构建打包前，对纹理命名格式、网格引用完整性、材质参数范围、音频采样率规格、蓝图/脚本引用链等数十类规则执行断言检查，将原本依赖人工代码评审和资产审查会议的质量管控流程系统化、自动化。

从引擎支持层面看，Unity 编辑器自 2017.1 起可通过 `AssetPostprocessor.OnPreprocessAsset()` 回调在资产导入管线中注入校验逻辑；Unreal Engine 自 4.23 版本起内置 `DataValidation` 插件，提供 `UEditorValidatorBase` 基类，开发者重写其 `ValidateLoadedAsset()` 虚函数即可注册自定义校验器。两种方案的共同点是：**校验逻辑与资产数据分离**，规则以独立配置资产（ScriptableObject 或 DataAsset）存储，使美术主管可在不修改 C++ 或 C# 代码的前提下调整规则参数。

数据校验工具的工程价值源于"错误修复成本随发现阶段呈指数增长"这一软件工程规律。Boehm（1981）在 *Software Engineering Economics* 中通过对多个大型软件项目的测量指出，缺陷在集成阶段发现的修复成本约为编码阶段的 6 倍，在系统测试阶段则高达 15 倍以上。游戏资产管线中同样如此：一个纹理命名错误若在导入时被拦截，美术平均修复耗时约 3 分钟；若待到构建打包失败时才发现，需排查资产依赖图、重新烘焙 Lightmap、重跑 CI 流水线，平均耗时超过 90 分钟。

当游戏项目团队规模扩大到 20 人以上、资产总量超过 5000 个时，口头约定和 Wiki 文档维护的规范合规率会随迭代频率快速下滑。数据校验工具将规范转化为可版本控制的代码规则，保证每一次 `git commit` 或资产保存操作都触发确定性检查。

---

## 核心原理

### 规则定义层：将规范转化为断言函数

校验工具的底层逻辑是**规则库（Rule Registry）**，每条规则本质上是一个签名为 `ValidationResult Validate(UnityEngine.Object asset)` 或 `EDataValidationResult ValidateLoadedAsset(UObject* InAsset, TArray<FText>& ValidationErrors)` 的断言函数。

以纹理命名规范为例，一条典型规则的正则表达式为：

$$
\text{Pattern} = \texttt{\^{}T\\_[A-Z][a-zA-Z0-9]+\_(Diffuse|Normal|Roughness|Emissive)\\_[0-9]\{4\}\$}
$$

该模式要求纹理文件名以 `T_` 为前缀，后跟帕斯卡命名的资产标识符，再跟贴图语义类型枚举（Diffuse / Normal / Roughness / Emissive），最后跟四位分辨率数字，例如 `T_HeroWarrior_Normal_2048`。对不符合格式的资产，规则函数返回 `FAIL` 并附带人类可读的错误消息，指明期望格式与实际文件名的差异。

规则库采用复合校验模型：规则按**严重等级**分为 Error（阻断构建）、Warning（记录日志但不阻断）、Info（仅统计）三级，这与 ESLint 的 `error/warn/off` 三级配置模型同构（Zakas, 2013, *The Principles of Object-Oriented JavaScript*）。Error 级规则失败时，Unity 的 `AssetPostprocessor` 会调用 `context.LogImportError()` 使导入操作回滚；Unreal 的校验插件则在 `CookCommandlet` 执行期间返回非零退出码，中断 CI 流水线。

### 资产遍历层：AssetDatabase 扫描机制

校验执行时，工具通过**资产数据库接口**枚举目标资产并逐一送入规则库。Unity 中的标准调用链为：

```csharp
string[] guids = AssetDatabase.FindAssets("t:Texture2D", new[] { "Assets/Characters" });
foreach (string guid in guids)
{
    string path = AssetDatabase.GUIDToAssetPath(guid);
    Texture2D tex = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
    RunAllRules(tex, path);
}
```

`FindAssets` 的类型过滤器 `t:Texture2D` 利用 Unity 内部的资产类型索引，避免对整个 `Assets` 目录进行文件系统遍历，在含 10 万资产的项目中查询耗时通常低于 200ms。Unreal 的等价操作是 `IAssetRegistry::GetAssets(FARFilter)` 方法，`FARFilter` 支持按 `ClassNames`、`PackagePaths`、`ObjectPaths` 以及任意 `TagsAndValues` 元数据过滤。

遍历层需区分**增量扫描**与**全量扫描**两种模式。增量扫描仅处理自上次校验后时间戳发生变化的资产（通过对比 `.meta` 文件的 `timeCreated` 字段或版本控制系统的 diff 输出），可将每次保存触发的在线校验耗时控制在 50ms 以内，不影响编辑器响应速度；全量扫描在 CI 构建流水线中作为独立步骤执行，对整个资产目录做完整遍历，通常运行于无界面的批处理模式（Unity `-batchmode -executeMethod ValidationRunner.RunAll`）。

### 引用校验层：依赖图完整性检测

引用校验是数据校验工具中技术复杂度最高的部分，其核心是构建**资产依赖图（Asset Dependency Graph）**。设项目资产集合为 $V$，资产间引用关系为有向边集合 $E$，则依赖图 $G = (V, E)$ 是一个有向无环图（DAG，Directed Acyclic Graph）——若出现环形引用则属于规范违规。

对每个资产节点 $a \in V$，工具通过 `AssetDatabase.GetDependencies(path, recursive: false)` 获取其直接引用集合 $\text{Deps}(a)$，再递归向下扩展获取传递依赖。引用校验的关键检查项包括：

1. **空引用检测**：`Deps(a)` 中存在 GUID 有记录但对应路径文件已被删除的条目，即"幽灵引用（Ghost Reference）"。
2. **跨域引用检测**：角色资产引用了场景专属的光照贴图，或 UI 资产引用了游戏世界的网格体，违反资产边界划分约定。
3. **循环引用检测**：对依赖图执行 DFS 拓扑排序，若 DFS 过程中发现后向边（Back Edge）则判定为循环依赖，报告构成环的资产路径链。

Unreal 的 `AssetRegistry` 提供 `GetReferencers` 和 `GetDependencies` 两个接口，分别对应反向引用查询（谁引用了我）与正向依赖查询（我引用了谁），可在不加载资产到内存的情况下完成依赖图构建，避免大规模校验时的内存峰值问题。

---

## 关键方法与公式

### 校验覆盖率度量

设项目中需要校验的资产总数为 $N$，已通过所有 Error 级规则的资产数为 $P$，则**校验合规率** $R$ 定义为：

$$
R = \frac{P}{N} \times 100\%
$$

对于包含 Warning 级规则，引入加权合规率：

$$
R_w = \frac{P + 0.5 \cdot W}{N} \times 100\%
$$

其中 $W$ 为仅触发 Warning 而未触发 Error 的资产数量。该指标可集成到 CI Dashboard，以折线图形式展示每次提交后合规率的趋势，当 $R$ 连续两次构建下降超过 5 个百分点时触发告警通知。

### 规则优先级调度算法

当多条规则同时适用于一个资产时，为最小化总校验时间，应将**执行耗时短但错误率高的规则优先调度**。设规则 $i$ 的单次执行时间为 $t_i$，历史错误检出率为 $p_i$，则规则的优先级得分为：

$$
\text{Score}(i) = \frac{p_i}{t_i}
$$

按 $\text{Score}(i)$ 降序排列规则执行顺序，并在首条规则返回 Error 时短路（short-circuit）跳过后续规则，可显著减少增量扫描的平均耗时。这一思路与测试套件优化中的"失败优先排序（Fail-First Ordering）"策略同源（Rothermel et al., 2001, *Prioritizing Test Cases for Regression Testing*, IEEE Transactions on Software Engineering）。

---

## 实际应用

### 案例一：Unity 项目中的纹理规格校验

某 RPG 手游项目在资产管线中接入了纹理规格校验器，规则涵盖以下约束：

- 角色漫反射贴图分辨率必须为 2 的幂次且不超过 2048×2048（移动端 GPU 的 NPOT 纹理会触发额外内存拷贝）
- 法线贴图必须启用 `textureImporter.textureType = TextureImporterType.NormalMap`，否则 Unity 不会在导入时执行 DXT5nm 压缩
- UI Atlas 中单个精灵的尺寸不得超过其 Atlas 总面积的 30%，避免 Draw Call 合批失败

校验器通过 `AssetPostprocessor.OnPostprocessTexture(Texture2D tex)` 回调实现，在资产导入完成后立即执行，错误以 `Debug.LogError` 形式输出到 Console 并阻止资产写入 `.meta` 文件的 `guid` 字段，强制要求美术人员修正后重新导入。项目上线后三个月内，因纹理格式错误导致的构建失败次数从月均 12 次降至 0 次。

### 案例二：Unreal Engine 中的蓝图引用完整性校验

基于 `UEditorValidatorBase` 实现的蓝图校验器，针对以下常见问题编写了专项规则：

```cpp
EDataValidationResult UBlueprintReferenceValidator::ValidateLoadedAsset(
    UObject* InAsset, TArray<FText>& ValidationErrors)
{
    UBlueprint* BP = Cast<UBlueprint>(InAsset);
    if (!BP) return EDataValidationResult::NotValidated;

    // 检查所有 SoftObjectPtr 是否指向有效资产
    for (FObjectProperty* Prop : TFieldRange<FObjectProperty>(BP->GeneratedClass))
    {
        UObject* RefObj = Prop->GetObjectPropertyValue(
            Prop->ContainerPtrToValuePtr<void>(BP->GeneratedClass->GetDefaultObject()));
        if (RefObj == nullptr && !Prop->HasMetaData("AllowNull"))
        {
            ValidationErrors.Add(FText::Format(
                LOCTEXT("NullRef", "属性 {0} 包含空引用，需显式设置 AllowNull 元数据或赋值"),
                FText::FromName(Prop->GetFName())));
            return EDataValidationResult::Invalid;
        }
    }
    return EDataValidationResult::Valid;
}
```

该校验器在 `Editor Preferences → Data Validation` 中启用后，会自动集成到 UE 编辑器的 `File → Validate Assets` 菜单和 `RunUAT BuildCookRun` 的 Cook 前置步骤中。

### 案例三：CI 流水线中的全量资产校验

大型 AAA 项目通常将全量资产校验作为 CI 流水线的独立 Stage，位于编译阶段之后、打包阶段之前。以 Jenkins Pipeline 为例：

```groovy
stage('Asset Validation') {
    steps {
        sh '''Unity -batchmode -projectPath $WORKSPACE \
              -executeMethod ValidationRunner.RunAll \
              -logFile validation_report.log \
              -quit'''
        archiveArtifacts 'validation_report.log'
        script {
            def report = readFile('validation_report.log')
            if (report.contains('[ERROR]')) {
                error("资产校验失败，请查看 validation_report.log")
            }
        }
    }
}
```

流水线将校验报告作为构建产物归档，方便追溯历史违规趋势，同时通过 Slack Webhook 向责任人发送包含违规资产路径和规则说明的通知消息。

---

## 常见误区

**误区一：将所有规则设置为 Error