# Unity场景编辑器

## 概述

Unity场景编辑器（Scene Editor）是Unity引擎内置的3D/2D关卡构建环境，其核心交互界面由Scene视图、Hierarchy面板、Inspector面板和Project面板四个协同工作的窗口构成。与虚幻引擎（Unreal Engine）采用World Partition分块管理世界的方式不同，Unity将每个关卡存储为独立的`.unity`文件，该文件以YAML格式序列化保存场景中所有GameObject的层级关系、组件列表、组件属性数值以及对外部资产的引用GUID。一个典型的中型关卡场景文件体积通常在500KB到数MB之间，其中每个GameObject对应一段独立的YAML文档块。

Unity场景编辑器自Unity 1.0于2005年正式发布时即为引擎核心功能模块。在Unity 2018.3版本中，嵌套Prefab（Nested Prefab）系统被正式引入，彻底改变了大型关卡的模块化编辑方式。Unity 2019.3进一步引入了可寻址资产系统（Addressable Asset System），配合多场景加载机制（Multi-Scene Editing），使开放世界关卡的流式加载成为标准工作流。理解Unity场景编辑器的底层数据模型与操作规范，是所有Unity关卡设计师必须掌握的基础能力。

## 核心原理

### Scene视图与Hierarchy面板的数据绑定

Scene视图是一个实时渲染的3D/2D可视化工作空间，而Hierarchy面板是该场景内所有GameObject的树状结构索引。两者对同一份场景数据进行操作，任何一侧的修改都会立即反映在另一侧。在Hierarchy中选中任意GameObject后，按快捷键`F`（Frame Selected），Scene视图摄像机将自动聚焦并缩放至该对象的包围盒中心；双击对象则可进入子级查看模式。

场景中所有GameObject以父子层级（Parent-Child Hierarchy）方式组织，子对象的空间变换由父对象的变换矩阵决定。设父对象的世界变换矩阵为 $M_{parent}$，子对象的本地变换矩阵为 $M_{local}$，则子对象的世界变换矩阵为：

$$M_{world} = M_{parent} \times M_{local}$$

其中每个变换矩阵是一个4×4的仿射变换矩阵，编码了位置（Translation）、旋转（Rotation）和缩放（Scale）三种变换。这意味着将一组房间道具归属到同一个空父对象（Empty GameObject）下后，移动父对象会整体平移所有子对象，这是Unity关卡中组织场景元素的标准做法。

### 变换工具（Transform Gizmos）的精确操控

Unity场景编辑器提供五种基础变换工具，对应键盘快捷键依次为：`W`（Move，移动）、`E`（Rotate，旋转）、`R`（Scale，缩放）、`T`（Rect Tool，矩形变换，专用于2D元素和UI Canvas）、`Y`（Transform Tool，综合工具，同时显示移动/旋转/缩放控制柄）。

三轴颜色遵循统一规范：红色（X轴）、绿色（Y轴）、蓝色（Z轴），与Unity的右手坐标系一致——X轴向右，Y轴向上，Z轴朝向屏幕外。需注意Unity使用**左手Y轴朝上坐标系**（相较于OpenGL的右手系有所不同），这在与外部3D资产（如从Maya或Blender导出的FBX）的坐标对齐时经常引发旋转问题。

网格吸附（Grid Snapping）通过按住`Ctrl`键（macOS为`Command`键）激活，吸附单位默认为1个Unity单位。Unity定义1个单位等于现实中的1米，因此在构建人形角色场景时，门洞高度建议设为2单位（2米），符合现实人体工学比例。可通过菜单 **Edit → Grid and Snap Settings** 自定义吸附增量，例如将位移吸附设为0.25单位，以实现精细的模块化关卡拼接。

### Prefab系统：关卡元素的工厂化管理

Prefab（预制体）是Unity场景编辑器中实现关卡元素复用的核心机制。将Hierarchy中的任意GameObject拖拽到Project面板即可将其"打包"为独立的`.prefab`资产文件；之后可将该Prefab多次拖入场景，每次生成一个实例（Instance）。

Prefab的覆盖（Override）系统是其最精妙的设计：在场景中选中某个Prefab实例后，可以在Inspector中修改任意属性，被修改的属性会以**粗体加蓝色标记**高亮显示，表示这是相对于Prefab原始定义的"本地覆盖"。通过 **Prefab Overrides → Apply All** 可以将实例的改动推回原始Prefab，影响所有实例；而 **Revert All** 则丢弃本地覆盖，还原至Prefab定义。

Unity 2018.3引入的**嵌套Prefab（Nested Prefab）**系统允许Prefab内部包含其他Prefab作为子节点。例如，一个"房间"Prefab可以内嵌"桌椅"Prefab、"灯具"Prefab等，修改"桌椅"Prefab会同步到所有包含它的"房间"实例中，形成多层级的变更传播链。这一机制对于大型RPG或开放世界游戏的关卡制作尤为重要（Unity Technologies, 2019）。

### 多场景编辑（Multi-Scene Editing）

Unity 5.3版本引入的多场景编辑功能允许在同一Hierarchy面板中同时加载多个`.unity`场景文件。其典型应用场景是将**永久性游戏逻辑对象**（如GameManager、AudioManager）单独存放在一个"Master Scene"中，而关卡地形、道具、NPC则分布在各自的"Level Scene"中。通过 `SceneManager.LoadSceneAsync("LevelScene", LoadSceneMode.Additive)` API可在运行时异步叠加加载场景，实现开放世界的区块流式加载。

多场景工作流中，每个场景拥有独立的光照烘焙数据（Lightmaps）和光照探针（Light Probes），需要分别执行 **Window → Rendering → Lighting** 中的烘焙操作。场景间的对象引用（Cross-Scene Reference）在编辑器中被明确禁止序列化，必须通过运行时事件系统或单例模式解耦，这是多场景工作流中最常见的架构约束（Thorn & Ahearn, 2018）。

## 关键操作与公式

### Scene视图导航速查

| 操作 | 快捷键/鼠标操作 |
|------|----------------|
| 旋转视角（Orbit） | `Alt` + 鼠标左键拖拽 |
| 推拉缩放（Dolly） | 鼠标滚轮 或 `Alt` + 鼠标右键拖拽 |
| 平移视图（Pan） | 鼠标中键拖拽 |
| 飞行模式（Flythrough） | 鼠标右键按住 + `WASD` |
| 加速飞行 | 飞行模式中按住 `Shift`（速度×2） |
| 聚焦选中对象 | `F` 键 |
| 正交/透视切换 | Scene Gizmo中央点击 |

飞行模式的速度可通过Scene视图右上角的**Camera Speed滑块**在0.01到99单位/秒之间调节，这在编辑巨大开放世界场景（如地形尺寸为4096×4096单位）时尤其必要。

### Terrain地形工具的笔刷强度公式

Unity内置Terrain系统（通过 **GameObject → 3D Object → Terrain** 创建）使用高度图（Heightmap）存储地形数据，默认分辨率为513×513像素。地形笔刷的实际高度影响量遵循以下关系：

$$\Delta h = Strength \times BrushSize^2 \times \Delta t$$

其中 $Strength$ 为笔刷强度参数（0到1），$BrushSize$ 为笔刷半径（单位：Unity单位），$\Delta t$ 为单帧时间步长。理解此公式有助于设计师在不同帧率条件下保持雕刻操作的一致性，避免在高帧率下过度雕刻地形。

## 实际应用

**案例一：模块化地牢关卡的快速搭建**

以一个2D俯视角地牢关卡为例：首先创建"墙壁""地板""门"三类Prefab，在Sprite Atlas中打包贴图以减少Draw Call；然后在Scene视图中开启**2D模式**（Scene工具栏左端的"2D"按钮），配合网格吸附（吸附单位设为1.0）将地板Tile拼接为房间轮廓。通过将所有同类型Tile归属到命名为"Floor_Layer"的空父对象下，可以在Hierarchy中快速折叠/展开该层，整洁的层级结构能够显著提高多人协作时的编辑效率。

**案例二：ProBuilder插件实现灰盒（Greyboxing）关卡**

Unity Package Manager中的**ProBuilder**（原Procore公司开发，Unity 2018年收购后免费内置）允许在Scene视图内直接创建和编辑多边形网格，无需往返3ds Max或Blender。关卡设计师可通过ProBuilder的"New Shape"工具快速生成走廊、楼梯、斜坡等几何体，以此构建关卡的灰盒原型。ProBuilder面对象（Face）、顶点（Vertex）和边（Edge）的独立编辑模式，配合Unity场景编辑器的变换工具，可在10分钟内完成一个中等复杂度房间的白盒搭建。

例如，构建一条宽2单位、高3单位、长10单位的标准走廊：在ProBuilder中创建Box Shape并设置尺寸为(2, 3, 10)，然后选中顶面和底面将其法线翻转（Flip Normals），最终得到玩家可以行走其中的空心走廊——整个过程无需离开Unity编辑器。

**案例三：Light Probe与Reflection Probe的空间放置**

在烘焙光照（Baked Lighting）场景中，Light Probe（光照探针）的空间布局直接影响动态对象的光照质量。应在明暗交界处、颜色明显变化的过渡区域以及开放空间中心以密集/稀疏变化的方式放置探针——具体而言，门口两侧各放1个，走廊每2~3单位放1个，开阔庭院中心每5单位放1个，构成探针组（Light Probe Group）。Reflection Probe则需覆盖关键反射表面（金属器皿、光亮地板），在Inspector中设置Resolution为256或512（较高分辨率），并将Refresh Mode设为 **Via Scripting** 以避免实时刷新的性能开销。

## 常见误区

**误区一：将所有对象平铺在Hierarchy顶层**
许多初学者习惯将全部GameObject不加父子关系地平铺在Hierarchy根级，导致场景含有数百个顶层节点，搜索和选择极为低效。正确做法是按功能或空间区域（如"Zone_A_Props""Enemies""Lights"）建立空父对象分组，并启用Hierarchy面板的**搜索过滤**功能（支持按名称、按类型、按Layer过滤）。

**误区二：混淆Local Space与World Space的旋转操作**
在Scene视图顶部工具栏中，Toggle between **Local**（本地坐标）和 **Global**（世界坐标）模式的快捷键为`X`。对一个已旋转45°的父对象的子对象进行操作时，若误用Global模式，移动方向将沿世界轴而非父对象轴，导致对象偏移至非预期位置。规则是：对已有旋转的父子层级操作时，应切换至Local模式。

**误区三：Static标记对性能的影响被低估**
在Inspector顶部勾选**Static**复选框会将对象标记为静态，这影响多个子系统：勾选后该对象的Transform在运行时不可通过代码修改（否则产生性能警告），同时Unity的**Batching Static**系统会将所有静态网格合并为Combined Mesh以减少Draw Call。一个常见错误是将应当动态旋转的门或开关错误标记为Static，导致运行时动画失效。应仔细区分：地形和建筑标记Static，而所有可交互对象则不勾选。

**误区四：过度依赖Undo历史而不使用版本控制**
Unity编辑器的Undo栈（`Ctrl+Z`）默认保存最近100步