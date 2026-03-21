#!/usr/bin/env python3
"""Generate game-qa knowledge sphere seed data."""
import json, os

DOMAIN = "game-qa"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "seed", "game-qa", "seed_graph.json")

subdomains = [
    {"id": "functional-testing", "name": "功能测试", "description": "游戏功能验证、测试用例设计、边界条件与异常路径测试", "order": 1},
    {"id": "automation-testing", "name": "自动化测试", "description": "测试自动化框架、脚本编写、CI集成与自动化策略", "order": 2},
    {"id": "performance-testing", "name": "性能测试(Profiling)", "description": "帧率分析、内存检测、CPU/GPU Profiling与性能优化验证", "order": 3},
    {"id": "compatibility-testing", "name": "兼容性测试", "description": "多平台/多设备/多分辨率/多系统版本的兼容性验证", "order": 4},
    {"id": "localization-testing", "name": "本地化测试", "description": "多语言翻译验证、文化适配、UI排版与地区合规测试", "order": 5},
    {"id": "regression-testing", "name": "回归测试", "description": "版本更新后的回归验证、影响分析与回归测试策略", "order": 6},
    {"id": "bug-lifecycle", "name": "Bug生命周期", "description": "Bug报告、分类、优先级、修复跟踪与关闭的全流程管理", "order": 7},
    {"id": "test-toolchain", "name": "测试工具链", "description": "测试管理工具、自动化平台、性能分析器与测试基础设施", "order": 8},
]

# 8 subdomains x 20 concepts = 160
concepts_data = {
    "functional-testing": [
        ("qa-ft-basics", "功能测试基础", "游戏功能测试的定义、目标与在开发流程中的角色", 1, 20, False),
        ("qa-ft-test-case-design", "测试用例设计", "测试用例的结构(前置条件/步骤/预期结果)与设计原则", 1, 25, False),
        ("qa-ft-equivalence-partition", "等价类划分", "将输入数据划分为有效/无效等价类以减少用例数量", 2, 30, True),
        ("qa-ft-boundary-value", "边界值分析", "针对输入范围边界的极值测试方法", 2, 25, False),
        ("qa-ft-state-transition", "状态转换测试", "基于游戏状态机的状态转换路径覆盖测试", 2, 30, False),
        ("qa-ft-combinatorial", "组合测试", "多参数组合(正交表/Pairwise)降低用例爆炸", 3, 35, False),
        ("qa-ft-gameplay-testing", "玩法测试", "核心玩法循环、数值平衡与游戏性验证", 2, 35, False),
        ("qa-ft-ui-testing", "UI功能测试", "菜单/HUD/弹窗/输入控件的功能与交互测试", 2, 30, False),
        ("qa-ft-multiplayer-testing", "多人游戏测试", "联机功能、同步一致性与网络异常场景测试", 3, 40, True),
        ("qa-ft-save-load-testing", "存档/加载测试", "存档完整性、跨版本兼容与损坏恢复测试", 2, 30, False),
        ("qa-ft-input-testing", "输入设备测试", "键鼠/手柄/触屏/体感等输入设备的兼容性验证", 2, 30, False),
        ("qa-ft-audio-testing", "音频功能测试", "音效触发/音量控制/空间音频/音频切换测试", 2, 25, False),
        ("qa-ft-achievement-testing", "成就/奖杯测试", "成就解锁条件、进度追踪与平台认证测试", 2, 30, False),
        ("qa-ft-economy-testing", "经济系统测试", "虚拟货币/交易/商城/付费流程的功能验证", 3, 35, False),
        ("qa-ft-tutorial-testing", "新手引导测试", "教程流程完整性、跳过机制与异常中断恢复", 2, 30, False),
        ("qa-ft-negative-testing", "负面测试", "异常输入/非法操作/极端条件下的系统健壮性验证", 3, 35, False),
        ("qa-ft-smoke-testing", "冒烟测试", "版本构建后的快速基本功能验证流程", 1, 20, False),
        ("qa-ft-exploratory-testing", "探索性测试", "基于经验与直觉的自由探索式测试方法", 2, 30, True),
        ("qa-ft-acceptance-testing", "验收测试", "基于需求文档的最终功能验收标准与流程", 2, 30, False),
        ("qa-ft-compliance-testing", "合规性测试", "平台TRC/Lotcheck/XR认证要求的合规验证", 3, 40, True),
    ],
    "automation-testing": [
        ("qa-at-automation-overview", "自动化测试概述", "游戏测试自动化的价值、挑战与适用场景", 1, 20, False),
        ("qa-at-test-pyramid", "测试金字塔", "单元测试/集成测试/E2E测试的分层策略与投入比例", 1, 25, False),
        ("qa-at-unit-testing", "单元测试", "游戏逻辑单元测试的框架选择与编写规范", 2, 30, True),
        ("qa-at-integration-testing", "集成测试", "模块间接口与数据流的集成验证方法", 2, 30, False),
        ("qa-at-e2e-testing", "端到端测试", "模拟真实用户操作的全流程自动化测试", 3, 35, False),
        ("qa-at-visual-testing", "视觉回归测试", "截图对比/像素差异检测的自动化视觉验证", 3, 40, False),
        ("qa-at-api-testing", "API测试", "后端接口/网络协议的自动化验证与Mock", 2, 30, False),
        ("qa-at-script-language", "脚本语言选择", "Python/Lua/C#等自动化脚本语言的优劣对比", 2, 25, False),
        ("qa-at-framework-design", "测试框架设计", "Page Object/关键字驱动/数据驱动等框架模式", 3, 35, True),
        ("qa-at-ci-integration", "CI/CD集成", "自动化测试与持续集成管线的集成策略", 2, 30, False),
        ("qa-at-test-data-mgmt", "测试数据管理", "测试数据的生成、维护、隔离与环境清理", 2, 30, False),
        ("qa-at-bot-testing", "Bot测试", "AI机器人模拟玩家行为的自动化压力/功能测试", 3, 40, False),
        ("qa-at-record-replay", "录制回放", "操作录制与回放技术在回归测试中的应用", 2, 30, False),
        ("qa-at-flaky-tests", "不稳定测试治理", "Flaky Test的检测、隔离、修复与预防策略", 3, 35, False),
        ("qa-at-parallel-execution", "并行执行", "测试用例的并行化策略与分布式执行架构", 3, 35, False),
        ("qa-at-test-reporting", "测试报告", "自动化测试结果的可视化报告与趋势分析", 2, 25, False),
        ("qa-at-mocking-stubbing", "Mock与Stub", "外部依赖模拟技术在游戏测试中的应用", 2, 30, False),
        ("qa-at-tdd-bdd", "TDD/BDD实践", "测试驱动/行为驱动开发在游戏项目中的适用性", 3, 35, False),
        ("qa-at-maintenance", "自动化维护", "测试脚本的版本管理、重构与维护成本控制", 3, 30, False),
        ("qa-at-roi-metrics", "自动化ROI", "自动化投入产出比的度量与决策模型", 3, 35, True),
    ],
    "performance-testing": [
        ("qa-pt-perf-overview", "性能测试概述", "游戏性能测试的目标、指标与测试类型分类", 1, 20, False),
        ("qa-pt-fps-analysis", "帧率分析", "FPS测量、帧时间分布、卡顿检测与性能基准", 1, 25, False),
        ("qa-pt-cpu-profiling", "CPU Profiling", "CPU热点分析、调用栈追踪与瓶颈定位方法", 2, 35, True),
        ("qa-pt-gpu-profiling", "GPU Profiling", "Draw Call分析、Shader性能、带宽瓶颈与GPU时间轴", 2, 35, True),
        ("qa-pt-memory-profiling", "内存检测", "内存占用追踪、泄漏检测、碎片化分析与预算管理", 2, 35, False),
        ("qa-pt-load-time", "加载时间测试", "场景加载/资源流送/初始化的耗时测量与优化验证", 2, 30, False),
        ("qa-pt-network-perf", "网络性能测试", "延迟/带宽/丢包/抖动对游戏体验的影响测试", 3, 35, False),
        ("qa-pt-stress-testing", "压力测试", "高并发/大规模场景/极端条件下的系统稳定性验证", 3, 40, False),
        ("qa-pt-soak-testing", "长时间运行测试", "长时间连续运行检测内存泄漏/性能衰退/崩溃", 3, 35, False),
        ("qa-pt-thermal-testing", "热量测试", "移动设备长时间游戏的发热/降频/续航测试", 2, 30, False),
        ("qa-pt-disk-io", "磁盘IO测试", "资源读写速度、流式加载与存储空间占用测试", 2, 30, False),
        ("qa-pt-render-pipeline", "渲染管线分析", "渲染各阶段(几何/光照/后处理)的性能拆解", 3, 40, False),
        ("qa-pt-scalability", "可扩展性测试", "不同画质/LOD/视距设置下的性能缩放验证", 3, 35, True),
        ("qa-pt-benchmark-design", "基准测试设计", "可复现的性能基准场景设计与自动化采集", 3, 35, False),
        ("qa-pt-perf-budget", "性能预算", "帧时间/内存/Draw Call等性能预算的制定与监控", 2, 30, False),
        ("qa-pt-profiling-tools", "Profiling工具", "引擎内置/第三方性能分析工具的使用方法", 2, 30, False),
        ("qa-pt-regression-perf", "性能回归检测", "版本间性能指标自动对比与退化告警", 3, 35, True),
        ("qa-pt-mobile-perf", "移动端性能", "移动GPU特性/纹理压缩/DrawCall优化的验证", 3, 35, False),
        ("qa-pt-server-perf", "服务器性能", "游戏服务器TPS/QPS/响应时间/承载量测试", 3, 40, False),
        ("qa-pt-perf-report", "性能报告", "性能测试结果的可视化报告与优化建议撰写", 2, 30, False),
    ],
    "compatibility-testing": [
        ("qa-ct-compat-overview", "兼容性测试概述", "多平台多设备游戏兼容性测试的范围与策略", 1, 20, False),
        ("qa-ct-device-matrix", "设备矩阵", "目标设备列表的制定、优先级排序与覆盖策略", 1, 25, False),
        ("qa-ct-os-version", "操作系统版本", "不同OS版本(Windows/macOS/Android/iOS)的兼容验证", 2, 30, True),
        ("qa-ct-gpu-driver", "GPU驱动兼容", "不同显卡厂商/驱动版本的渲染兼容性测试", 2, 35, False),
        ("qa-ct-resolution-aspect", "分辨率与宽高比", "多分辨率/宽高比/DPI缩放的UI适配验证", 2, 30, True),
        ("qa-ct-controller-compat", "控制器兼容", "不同品牌手柄/触控方案/键鼠布局的兼容验证", 2, 30, False),
        ("qa-ct-cloud-gaming", "云游戏兼容", "云游戏平台(GeForce Now/Xbox Cloud)的适配测试", 3, 35, False),
        ("qa-ct-cross-platform", "跨平台一致性", "PC/主机/移动端间的功能与体验一致性验证", 3, 35, False),
        ("qa-ct-network-conditions", "网络环境模拟", "弱网/断网/切换网络等异常网络条件的兼容测试", 2, 30, False),
        ("qa-ct-storage-space", "存储空间兼容", "低存储空间/SD卡/外部存储的安装与运行测试", 2, 25, False),
        ("qa-ct-peripheral", "外设兼容", "耳机/VR头显/方向盘/飞行摇杆等外设兼容测试", 2, 30, False),
        ("qa-ct-accessibility-hw", "辅助功能硬件", "无障碍硬件(语音控制/开关控制)的兼容验证", 3, 35, False),
        ("qa-ct-minimum-spec", "最低配置验证", "官方最低/推荐配置设备上的性能与稳定性验证", 2, 30, True),
        ("qa-ct-console-cert", "主机认证兼容", "PlayStation/Xbox/Switch平台认证要求的兼容验证", 3, 40, False),
        ("qa-ct-web-browser", "浏览器兼容", "Web游戏在不同浏览器/版本的功能与性能验证", 2, 30, False),
        ("qa-ct-locale-compat", "区域设置兼容", "不同系统语言/时区/日期格式的兼容验证", 2, 25, False),
        ("qa-ct-update-compat", "更新兼容", "新旧版本共存/增量更新/存档迁移的兼容验证", 3, 35, True),
        ("qa-ct-emulator-testing", "模拟器测试", "使用模拟器/虚拟机扩展设备覆盖的方法与局限", 2, 30, False),
        ("qa-ct-hardware-debug", "硬件调试方法", "设备特定问题的远程调试与日志采集技术", 3, 35, False),
        ("qa-ct-compat-report", "兼容性报告", "兼容性测试结果的设备覆盖矩阵报告", 2, 25, False),
    ],
    "localization-testing": [
        ("qa-lt-loc-overview", "本地化测试概述", "游戏本地化测试的范围、流程与最佳实践", 1, 20, False),
        ("qa-lt-linguistic-qa", "语言质量测试", "翻译准确性、术语一致性与语境适切性验证", 1, 25, False),
        ("qa-lt-ui-overflow", "UI文本溢出", "长文本截断/换行/控件溢出的多语言排版验证", 2, 30, True),
        ("qa-lt-font-rendering", "字体渲染", "多语言字体(CJK/阿拉伯/泰文)的渲染与排版测试", 2, 30, False),
        ("qa-lt-rtl-support", "RTL语言支持", "阿拉伯语/希伯来语等从右到左语言的界面镜像测试", 3, 35, True),
        ("qa-lt-cultural-adapt", "文化适配", "色彩/图标/手势/符号在不同文化中的适当性验证", 2, 30, False),
        ("qa-lt-date-number-format", "日期/数字格式", "不同地区日期、时间、数字、货币格式的正确性", 2, 25, False),
        ("qa-lt-audio-loc", "音频本地化", "配音/字幕同步/音频切换/语言选择的功能验证", 2, 30, False),
        ("qa-lt-image-loc", "图片本地化", "含文字图片/纹理/Logo的多语言替换验证", 2, 25, False),
        ("qa-lt-pseudoloc", "伪本地化", "Pseudo-localization技术快速发现本地化潜在问题", 2, 30, False),
        ("qa-lt-string-extraction", "字符串提取验证", "确认所有UI文本已外部化、无硬编码字符串", 2, 30, False),
        ("qa-lt-context-testing", "上下文测试", "翻译在实际游戏场景中的语境正确性验证", 2, 30, False),
        ("qa-lt-legal-compliance", "法律合规", "各地区法律法规(GDPR/年龄分级/敏感内容)的合规验证", 3, 35, False),
        ("qa-lt-input-method", "输入法兼容", "CJK输入法/虚拟键盘在游戏内的兼容性测试", 2, 30, False),
        ("qa-lt-plurals-gender", "复数/性别变化", "不同语言复数规则/语法性别的正确处理验证", 3, 35, True),
        ("qa-lt-loc-automation", "本地化自动化", "自动化截图对比/文本长度检测等本地化测试工具", 3, 35, False),
        ("qa-lt-vendor-mgmt", "外包翻译管理", "本地化供应商质量管控、反馈流程与术语表管理", 2, 30, False),
        ("qa-lt-hot-text-update", "热更新文本", "运营期间文本热更新的验证与回滚测试", 2, 25, False),
        ("qa-lt-loc-regression", "本地化回归", "版本更新后新增/修改文本的本地化回归验证", 2, 30, False),
        ("qa-lt-loc-metrics", "本地化质量指标", "翻译错误率/覆盖率/玩家反馈等质量度量", 2, 30, True),
    ],
    "regression-testing": [
        ("qa-rt-regression-overview", "回归测试概述", "回归测试的定义、价值与在敏捷开发中的角色", 1, 20, False),
        ("qa-rt-impact-analysis", "影响分析", "代码变更的影响范围评估与测试范围确定", 2, 30, False),
        ("qa-rt-test-selection", "测试选择策略", "全量/选择性/风险驱动回归测试策略的选择", 2, 30, True),
        ("qa-rt-smoke-regression", "冒烟回归", "每日构建后的快速核心路径回归验证", 1, 20, False),
        ("qa-rt-full-regression", "全量回归", "版本发布前的完整功能回归测试计划", 2, 35, False),
        ("qa-rt-auto-regression", "自动化回归", "利用自动化测试套件执行高频回归验证", 2, 30, True),
        ("qa-rt-visual-regression", "视觉回归", "UI/场景截图对比检测视觉变化与退化", 3, 35, False),
        ("qa-rt-data-regression", "数据回归", "游戏配置/数值表/存档格式变更的回归验证", 2, 30, False),
        ("qa-rt-priority-ranking", "用例优先级排序", "基于风险/频率/影响的回归用例优先级排序方法", 2, 30, True),
        ("qa-rt-test-suite-mgmt", "测试套件管理", "回归测试套件的版本化、分类与定期维护", 2, 25, False),
        ("qa-rt-change-log-review", "变更日志审查", "通过代码提交记录定向确定回归测试重点", 2, 25, False),
        ("qa-rt-hotfix-regression", "热修复回归", "紧急修复后的快速定向回归验证流程", 2, 30, False),
        ("qa-rt-platform-regression", "多平台回归", "跨平台构建的同步回归测试策略", 3, 35, True),
        ("qa-rt-schedule-planning", "回归排期", "回归测试在迭代/冲刺中的时间规划与执行窗口", 2, 25, False),
        ("qa-rt-build-verification", "构建验证测试", "新版本构建的自动化验证(BVT)流程与标准", 2, 30, False),
        ("qa-rt-feature-toggle-reg", "功能开关回归", "Feature Flag启/禁组合的回归测试覆盖", 3, 35, False),
        ("qa-rt-dlc-regression", "DLC/更新回归", "DLC/赛季更新对主游戏功能的回归影响验证", 3, 35, False),
        ("qa-rt-perf-regression", "性能回归", "版本间性能指标对比与性能退化检测", 3, 35, True),
        ("qa-rt-flaky-mgmt", "不稳定用例管理", "回归测试中不稳定用例的标记、隔离与修复", 2, 25, False),
        ("qa-rt-regression-report", "回归报告", "回归测试通过率/覆盖率/趋势的报告模板", 2, 25, False),
    ],
    "bug-lifecycle": [
        ("qa-bl-bug-report-basics", "Bug报告基础", "一份合格Bug报告的要素:标题/步骤/预期/实际/环境/证据", 1, 20, False),
        ("qa-bl-severity-priority", "严重性与优先级", "Bug严重性(Blocker→Trivial)与优先级(P0-P4)的定义与区别", 1, 25, False),
        ("qa-bl-classification", "Bug分类体系", "功能/视觉/性能/崩溃/安全/本地化等Bug分类标准", 2, 25, False),
        ("qa-bl-lifecycle-states", "生命周期状态", "New→Open→Fixed→Verified→Closed/Reopened的状态流转", 1, 25, False),
        ("qa-bl-reproduction", "复现方法", "从概率性Bug到必现路径的复现技巧与策略", 2, 30, True),
        ("qa-bl-root-cause", "根因分析", "Bug根本原因的分析方法(5-Why/鱼骨图/代码审查)", 3, 35, False),
        ("qa-bl-triage-process", "Bug评审会", "定期Bug评审的流程、参与者与决策标准", 2, 30, False),
        ("qa-bl-wont-fix", "Won't Fix决策", "判断Bug不修复的标准:成本/风险/影响/临近发布", 2, 25, False),
        ("qa-bl-duplicate-mgmt", "重复Bug管理", "重复Bug的检测、合并与追踪策略", 2, 25, False),
        ("qa-bl-crash-reporting", "崩溃报告系统", "崩溃日志自动采集、分组、符号化与优先排序", 2, 30, True),
        ("qa-bl-issue-tracker", "Issue Tracker选型", "JIRA/Azure DevOps/Mantis/GitHub Issues等工具对比", 2, 25, False),
        ("qa-bl-automation-filing", "自动化Bug提报", "自动化测试失败自动创建Bug报告的工作流", 3, 35, False),
        ("qa-bl-screenshot-video", "截图/录屏证据", "Bug报告中截图、录屏与日志附件的规范", 1, 20, False),
        ("qa-bl-environment-info", "环境信息", "Bug报告中设备/系统/版本/网络环境信息的记录规范", 1, 20, False),
        ("qa-bl-regression-bug", "回归Bug", "已修复Bug再次出现的检测与预防策略", 2, 30, True),
        ("qa-bl-statistics", "Bug统计分析", "Bug趋势图/修复率/密度/平均修复时间等质量指标", 2, 30, False),
        ("qa-bl-release-criteria", "发布质量标准", "基于Bug数量/严重性的版本发布Go/No-Go决策标准", 3, 35, True),
        ("qa-bl-communication", "Bug沟通技巧", "与开发/策划团队有效沟通Bug的方法与技巧", 2, 25, False),
        ("qa-bl-known-issues", "已知问题列表", "版本已知问题的管理、公示与玩家沟通", 2, 25, False),
        ("qa-bl-post-release-bugs", "上线后Bug处理", "线上Bug的快速响应、热修复决策与玩家安抚", 3, 35, False),
    ],
    "test-toolchain": [
        ("qa-tc-tool-overview", "测试工具概述", "游戏QA测试工具生态与工具链搭建策略", 1, 20, False),
        ("qa-tc-test-mgmt-tools", "测试管理工具", "TestRail/qTest/Zephyr等测试用例与执行管理平台", 1, 25, False),
        ("qa-tc-engine-profiler", "引擎Profiler", "UE Insights/Unity Profiler/内置调试工具的使用", 2, 30, True),
        ("qa-tc-gpu-tools", "GPU调试工具", "RenderDoc/PIX/Nsight/AGI等GPU分析器的使用方法", 2, 35, False),
        ("qa-tc-crash-analytics", "崩溃分析平台", "Crashlytics/Sentry/BugSplat等崩溃分析服务", 2, 30, True),
        ("qa-tc-device-farm", "云设备农场", "AWS Device Farm/Firebase Test Lab/Sauce Labs使用", 3, 35, False),
        ("qa-tc-network-simulator", "网络模拟器", "Charles/Fiddler/Network Link Conditioner等网络调试工具", 2, 30, False),
        ("qa-tc-screenshot-comparison", "截图对比工具", "Applitools/Percy/BackstopJS等视觉回归工具", 3, 35, False),
        ("qa-tc-log-analysis", "日志分析工具", "ELK Stack/Splunk/Datadog在游戏日志分析中的应用", 2, 30, False),
        ("qa-tc-ci-tools", "CI/CD工具", "Jenkins/GitHub Actions/GitLab CI在游戏测试中的配置", 2, 30, False),
        ("qa-tc-game-test-framework", "游戏测试框架", "Gauntlet/Airtest/Poco等游戏专用自动化框架", 3, 35, True),
        ("qa-tc-performance-monitor", "性能监控工具", "PerfDog/GameBench/FrameView等实时性能监控", 2, 30, False),
        ("qa-tc-code-coverage", "代码覆盖率", "代码覆盖率工具的集成与覆盖率指标的正确解读", 2, 30, False),
        ("qa-tc-static-analysis", "静态分析", "代码静态分析工具(SonarQube/PVS-Studio)在游戏中的应用", 2, 30, False),
        ("qa-tc-remote-debugging", "远程调试", "移动设备/主机的远程调试连接与实时日志查看", 2, 30, False),
        ("qa-tc-version-control", "版本控制协作", "Perforce/Git在测试资产与用例管理中的最佳实践", 2, 25, False),
        ("qa-tc-test-env-mgmt", "测试环境管理", "开发/测试/预发布/生产环境的配置与数据管理", 2, 30, True),
        ("qa-tc-custom-tooling", "定制工具开发", "根据项目需求开发QA辅助工具(作弊码/跳关/数据注入)", 3, 35, False),
        ("qa-tc-metrics-dashboard", "质量仪表板", "测试覆盖率/Bug趋势/通过率的实时监控看板", 2, 30, False),
        ("qa-tc-toolchain-evolution", "工具链演进", "随项目阶段演进的工具链选型与技术债务管理", 3, 35, False),
    ],
}

concepts = []
edges = []
milestones = []

for sub_id, items in concepts_data.items():
    prev_id = None
    for (cid, name, desc, diff, minutes, is_ms) in items:
        concepts.append({
            "id": cid,
            "name": name,
            "description": desc,
            "domain_id": DOMAIN,
            "subdomain_id": sub_id,
            "difficulty": diff,
            "estimated_minutes": minutes,
            "content_type": "conceptual",
            "tags": [],
            "is_milestone": is_ms
        })
        if is_ms:
            milestones.append(cid)
        if prev_id:
            edges.append({
                "source_id": prev_id,
                "target_id": cid,
                "relation_type": "prerequisite",
                "strength": 0.8
            })
        prev_id = cid

# Cross-subdomain edges (related)
cross_edges = [
    ("qa-ft-smoke-testing", "qa-rt-smoke-regression", "related", 0.9),
    ("qa-ft-exploratory-testing", "qa-bl-reproduction", "related", 0.7),
    ("qa-ft-compliance-testing", "qa-ct-console-cert", "related", 0.8),
    ("qa-ft-multiplayer-testing", "qa-pt-network-perf", "related", 0.8),
    ("qa-ft-economy-testing", "qa-bl-severity-priority", "related", 0.6),
    ("qa-at-unit-testing", "qa-rt-auto-regression", "related", 0.8),
    ("qa-at-ci-integration", "qa-tc-ci-tools", "related", 0.9),
    ("qa-at-visual-testing", "qa-rt-visual-regression", "related", 0.9),
    ("qa-at-visual-testing", "qa-tc-screenshot-comparison", "related", 0.8),
    ("qa-at-bot-testing", "qa-pt-stress-testing", "related", 0.7),
    ("qa-at-flaky-tests", "qa-rt-flaky-mgmt", "related", 0.9),
    ("qa-pt-regression-perf", "qa-rt-perf-regression", "related", 0.9),
    ("qa-pt-profiling-tools", "qa-tc-engine-profiler", "related", 0.9),
    ("qa-pt-gpu-profiling", "qa-tc-gpu-tools", "related", 0.9),
    ("qa-ct-os-version", "qa-ct-locale-compat", "related", 0.6),
    ("qa-lt-ui-overflow", "qa-ct-resolution-aspect", "related", 0.7),
    ("qa-lt-loc-automation", "qa-at-automation-overview", "related", 0.6),
    ("qa-bl-crash-reporting", "qa-tc-crash-analytics", "related", 0.9),
    ("qa-bl-statistics", "qa-tc-metrics-dashboard", "related", 0.8),
    ("qa-bl-issue-tracker", "qa-tc-test-mgmt-tools", "related", 0.7),
    ("qa-rt-build-verification", "qa-at-ci-integration", "related", 0.8),
    ("qa-rt-platform-regression", "qa-ct-cross-platform", "related", 0.8),
    ("qa-bl-release-criteria", "qa-rt-regression-report", "related", 0.8),
    ("qa-tc-device-farm", "qa-ct-device-matrix", "related", 0.8),
    ("qa-tc-network-simulator", "qa-ct-network-conditions", "related", 0.9),
]

for src, tgt, rtype, strength in cross_edges:
    edges.append({"source_id": src, "target_id": tgt, "relation_type": rtype, "strength": strength})

data = {
    "domain": DOMAIN,
    "subdomains": subdomains,
    "concepts": concepts,
    "edges": edges,
    "milestones": milestones
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Generated: {len(concepts)} concepts, {len(edges)} edges, {len(milestones)} milestones, {len(subdomains)} subdomains")
