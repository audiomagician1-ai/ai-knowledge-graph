#!/usr/bin/env python3
"""Generate seed_graph.json for software-engineering knowledge sphere (Phase 21).

Run:  python data/scripts/generate_se_seed.py
Output: data/seed/software-engineering/seed_graph.json
"""

import json, pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "seed" / "software-engineering" / "seed_graph.json"

DOMAIN = {
    "id": "software-engineering",
    "name": "软件工程",
    "description": "从架构模式到构建系统的完整软件工程知识体系",
    "icon": "⚙️",
    "color": "#4f46e5",
}

SUBDOMAINS = [
    {"id": "architecture-patterns",     "name": "架构模式",        "order": 1},
    {"id": "design-patterns",           "name": "设计模式",        "order": 2},
    {"id": "version-control",           "name": "版本控制",        "order": 3},
    {"id": "ci-cd",                     "name": "CI/CD",           "order": 4},
    {"id": "code-review",              "name": "代码审查",        "order": 5},
    {"id": "tdd",                       "name": "测试驱动开发",    "order": 6},
    {"id": "performance-analysis",      "name": "性能分析",        "order": 7},
    {"id": "refactoring",              "name": "重构",            "order": 8},
    {"id": "game-programming-patterns", "name": "游戏编程模式",    "order": 9},
    {"id": "ecs-architecture",          "name": "ECS架构",         "order": 10},
    {"id": "memory-management",         "name": "内存管理",        "order": 11},
    {"id": "multithreading",            "name": "多线程",          "order": 12},
    {"id": "build-systems",             "name": "构建系统",        "order": 13},
    {"id": "package-management",        "name": "包管理",          "order": 14},
]

# ---------------------------------------------------------------------------
# Concepts: 280 total, 20 per subdomain
# ---------------------------------------------------------------------------

def c(id_, name, desc, sub, diff, mins, ctype="theory", tags=None, ms=False):
    return {
        "id": id_,
        "name": name,
        "description": desc,
        "subdomain_id": sub,
        "domain_id": "software-engineering",
        "difficulty": diff,
        "estimated_minutes": mins,
        "content_type": ctype,
        "tags": tags or [],
        "is_milestone": ms,
    }

concepts = [
    # --- architecture-patterns (20) ---
    c("se-arch-intro",          "软件架构概述",             "软件架构的定义、目标与评估维度",             "architecture-patterns", 1, 20, tags=["基础"], ms=True),
    c("se-layered-arch",        "分层架构",                 "三层/N层架构的职责划分与依赖规则",           "architecture-patterns", 2, 25, tags=["经典"]),
    c("se-mvc-mvvm",            "MVC/MVVM模式",             "Model-View-Controller与MVVM变体",            "architecture-patterns", 2, 25, tags=["UI架构"]),
    c("se-microservices",       "微服务架构",               "服务拆分、通信协议与分布式挑战",             "architecture-patterns", 3, 35, tags=["分布式"], ms=True),
    c("se-event-driven",        "事件驱动架构",             "事件溯源、CQRS与消息队列模式",               "architecture-patterns", 3, 30, tags=["异步"]),
    c("se-hexagonal",           "六边形架构",               "端口与适配器模式实现依赖反转",               "architecture-patterns", 3, 30, tags=["DDD"]),
    c("se-clean-arch",          "Clean Architecture",       "Robert Martin的洋葱架构与依赖规则",          "architecture-patterns", 3, 30, tags=["原则"]),
    c("se-ddd",                 "领域驱动设计",             "限界上下文、聚合根与通用语言",               "architecture-patterns", 3, 35, tags=["DDD"], ms=True),
    c("se-pipe-filter",         "管道-过滤器架构",          "数据流导向的处理链模式",                     "architecture-patterns", 2, 25, tags=["数据流"]),
    c("se-plugin-arch",         "插件架构",                 "宿主/插件解耦与动态加载机制",                "architecture-patterns", 2, 25, tags=["扩展"]),
    c("se-serverless",          "Serverless架构",           "FaaS/BaaS模型与冷启动优化",                  "architecture-patterns", 3, 30, tags=["云原生"]),
    c("se-monorepo",            "Monorepo策略",             "单仓库管理、代码共享与构建优化",             "architecture-patterns", 2, 25, tags=["工程化"]),
    c("se-modular-arch",        "模块化架构",               "高内聚低耦合的模块划分原则",                 "architecture-patterns", 2, 25, tags=["原则"]),
    c("se-solid",               "SOLID原则",                "五大面向对象设计原则详解",                   "architecture-patterns", 2, 30, tags=["原则"]),
    c("se-api-design",          "API设计原则",              "RESTful/GraphQL/gRPC接口设计规范",            "architecture-patterns", 2, 30, tags=["接口"]),
    c("se-caching-arch",        "缓存架构",                 "多级缓存策略与一致性保证",                   "architecture-patterns", 3, 25, tags=["性能"]),
    c("se-database-arch",       "数据库架构",               "SQL/NoSQL选型与分库分表策略",                "architecture-patterns", 3, 30, tags=["数据"]),
    c("se-arch-decision",       "架构决策记录",             "ADR文档与技术选型评估框架",                  "architecture-patterns", 2, 25, "practice", tags=["文档"]),
    c("se-service-mesh",        "Service Mesh",             "Istio/Envoy/Sidecar代理模式",                "architecture-patterns", 3, 30, tags=["微服务"]),
    c("se-arch-evolution",      "架构演进策略",             "增量重构、Strangler Fig模式与渐进式迁移",    "architecture-patterns", 3, 30, tags=["演进"]),

    # --- design-patterns (20) ---
    c("se-dp-intro",            "设计模式概述",             "设计模式的分类、适用场景与反模式",           "design-patterns", 1, 20, tags=["基础"], ms=True),
    c("se-dp-singleton",        "单例模式",                 "全局唯一实例的线程安全实现",                 "design-patterns", 2, 20, tags=["创建型"]),
    c("se-dp-factory",          "工厂模式",                 "Simple/Method/Abstract Factory对比",         "design-patterns", 2, 25, tags=["创建型"], ms=True),
    c("se-dp-builder",          "建造者模式",               "复杂对象的分步构建与Director角色",           "design-patterns", 2, 25, tags=["创建型"]),
    c("se-dp-prototype",        "原型模式",                 "深拷贝/浅拷贝与对象克隆注册表",             "design-patterns", 2, 20, tags=["创建型"]),
    c("se-dp-adapter",          "适配器模式",               "接口转换与遗留系统集成",                     "design-patterns", 2, 20, tags=["结构型"]),
    c("se-dp-decorator",        "装饰器模式",               "动态职责附加与组合优于继承",                 "design-patterns", 2, 25, tags=["结构型"]),
    c("se-dp-proxy",            "代理模式",                 "远程/虚拟/保护代理与懒加载",                 "design-patterns", 2, 25, tags=["结构型"]),
    c("se-dp-facade",           "外观模式",                 "子系统简化接口与解耦策略",                   "design-patterns", 2, 20, tags=["结构型"]),
    c("se-dp-composite",        "组合模式",                 "树形结构的统一处理接口",                     "design-patterns", 2, 25, tags=["结构型"]),
    c("se-dp-observer",         "观察者模式",               "发布-订阅与事件驱动解耦",                   "design-patterns", 2, 25, tags=["行为型"], ms=True),
    c("se-dp-strategy",         "策略模式",                 "算法族封装与运行时切换",                     "design-patterns", 2, 20, tags=["行为型"]),
    c("se-dp-command",          "命令模式",                 "请求封装、撤销/重做与宏命令",               "design-patterns", 2, 25, tags=["行为型"]),
    c("se-dp-state",            "状态模式",                 "有限状态机的面向对象实现",                   "design-patterns", 2, 25, tags=["行为型"]),
    c("se-dp-template",         "模板方法模式",             "算法骨架与可覆写步骤",                       "design-patterns", 2, 20, tags=["行为型"]),
    c("se-dp-iterator",         "迭代器模式",               "聚合对象的顺序访问接口",                     "design-patterns", 2, 20, tags=["行为型"]),
    c("se-dp-mediator",         "中介者模式",               "组件间通信集中化与松耦合",                   "design-patterns", 2, 25, tags=["行为型"]),
    c("se-dp-visitor",          "访问者模式",               "双分派与操作扩展不修改数据结构",             "design-patterns", 3, 25, tags=["行为型"]),
    c("se-dp-flyweight",        "享元模式",                 "共享细粒度对象降低内存开销",                 "design-patterns", 2, 25, tags=["结构型"]),
    c("se-dp-chain",            "责任链模式",               "请求沿链传递与中间件管道",                   "design-patterns", 2, 25, tags=["行为型"]),

    # --- version-control (20) ---
    c("se-vc-intro",            "版本控制概述",             "版本控制系统的演进与核心概念",               "version-control", 1, 20, tags=["基础"], ms=True),
    c("se-git-basics",          "Git基础",                  "仓库初始化、暂存区与提交工作流",             "version-control", 1, 25, tags=["Git"]),
    c("se-git-branching",       "Git分支策略",              "Git Flow/GitHub Flow/Trunk-Based对比",       "version-control", 2, 30, tags=["分支"], ms=True),
    c("se-git-merge-rebase",    "Merge与Rebase",            "合并策略选择与冲突解决技巧",                 "version-control", 2, 25, tags=["Git"]),
    c("se-git-hooks",           "Git Hooks",                "客户端/服务端钩子与自动化",                  "version-control", 2, 25, tags=["自动化"]),
    c("se-git-submodule",       "Git子模块与子树",          "Submodule/Subtree/Subrepo对比",              "version-control", 3, 25, tags=["依赖"]),
    c("se-conventional-commit", "约定式提交",               "Conventional Commits规范与自动化变更日志",   "version-control", 2, 20, tags=["规范"]),
    c("se-git-lfs",             "Git LFS",                  "大文件存储与二进制资产管理",                 "version-control", 2, 25, tags=["大文件"]),
    c("se-pr-workflow",         "Pull Request工作流",       "PR创建、Review循环与合并策略",               "version-control", 2, 25, tags=["协作"], ms=True),
    c("se-monorepo-tools",      "Monorepo工具",             "Nx/Turborepo/Lerna/Rush工具对比",            "version-control", 2, 25, tags=["工具"]),
    c("se-perforce",            "Perforce基础",             "P4V/Workspace/Stream Depot游戏行业实践",     "version-control", 2, 25, tags=["游戏"]),
    c("se-vc-binary",           "二进制版本控制",           "游戏资产/美术文件的版本管理策略",            "version-control", 2, 25, tags=["游戏"]),
    c("se-semantic-versioning",  "语义化版本",              "SemVer规范与API兼容性承诺",                  "version-control", 2, 20, tags=["规范"]),
    c("se-changelog",           "变更日志管理",             "CHANGELOG.md自动化与发布说明",               "version-control", 2, 20, "practice", tags=["文档"]),
    c("se-gitignore",           "忽略规则",                 ".gitignore模式与全局配置",                   "version-control", 1, 15, tags=["配置"]),
    c("se-cherry-pick",         "Cherry-pick与补丁",        "精选提交与热修复回港策略",                   "version-control", 2, 25, tags=["Git"]),
    c("se-bisect",              "Git Bisect调试",           "二分查找引入Bug的提交",                      "version-control", 2, 20, "practice", tags=["调试"]),
    c("se-worktree",            "Git Worktree",             "多工作目录并行开发",                         "version-control", 2, 20, tags=["效率"]),
    c("se-git-internals",       "Git内部原理",              "对象模型(blob/tree/commit/tag)与引用",       "version-control", 3, 30, tags=["原理"]),
    c("se-vc-migration",        "版本控制迁移",             "SVN→Git/P4→Git迁移策略与历史保留",           "version-control", 3, 25, tags=["迁移"]),

    # --- ci-cd (20) ---
    c("se-cicd-intro",          "CI/CD概述",                "持续集成/交付/部署的概念与价值",             "ci-cd", 1, 20, tags=["基础"], ms=True),
    c("se-pipeline-design",     "流水线设计",               "Stage/Job/Step分层与并行策略",               "ci-cd", 2, 25, tags=["设计"]),
    c("se-github-actions",      "GitHub Actions",           "Workflow/Action/Runner配置与编写",           "ci-cd", 2, 30, tags=["平台"], ms=True),
    c("se-jenkins",             "Jenkins",                  "Jenkinsfile/Pipeline语法与插件生态",         "ci-cd", 2, 30, tags=["平台"]),
    c("se-gitlab-ci",           "GitLab CI",                ".gitlab-ci.yml配置与Runner管理",             "ci-cd", 2, 25, tags=["平台"]),
    c("se-docker-ci",           "Docker在CI中的应用",       "容器化构建、镜像缓存与多阶段构建",          "ci-cd", 2, 30, tags=["容器"]),
    c("se-artifact-mgmt",       "制品管理",                 "Docker Registry/NPM/Maven制品存储",          "ci-cd", 2, 25, tags=["制品"]),
    c("se-deploy-strategies",   "部署策略",                 "蓝绿/金丝雀/滚动/A-B部署对比",              "ci-cd", 3, 30, tags=["部署"], ms=True),
    c("se-infra-as-code",       "基础设施即代码",           "Terraform/Pulumi/CloudFormation",             "ci-cd", 3, 30, tags=["IaC"]),
    c("se-env-management",      "环境管理",                 "Dev/Staging/Prod环境隔离与配置管理",         "ci-cd", 2, 25, tags=["环境"]),
    c("se-feature-flags",       "Feature Flags",            "功能开关实现与渐进式发布",                   "ci-cd", 2, 25, tags=["发布"]),
    c("se-monitoring-ci",       "监控与告警",               "CI指标采集、构建失败告警与仪表盘",          "ci-cd", 2, 25, tags=["监控"]),
    c("se-secrets-mgmt",        "密钥管理",                 "Vault/环境变量/OIDC安全凭证管理",            "ci-cd", 2, 25, tags=["安全"]),
    c("se-ci-testing",          "CI中的测试策略",           "测试金字塔与CI阶段测试编排",                "ci-cd", 2, 25, tags=["测试"]),
    c("se-rollback",            "回滚策略",                 "自动回滚/手动回滚与版本锁定",               "ci-cd", 2, 25, tags=["安全"]),
    c("se-ci-cache",            "构建缓存优化",             "依赖缓存/增量构建/远程缓存",                "ci-cd", 2, 25, tags=["性能"]),
    c("se-ci-security",         "CI安全扫描",               "SAST/DAST/SCA安全检查集成",                  "ci-cd", 3, 25, tags=["安全"]),
    c("se-gitops",              "GitOps",                   "Flux/ArgoCD声明式持续交付",                  "ci-cd", 3, 30, tags=["GitOps"]),
    c("se-game-ci",             "游戏CI/CD",                "UE5/Unity自动化构建与打包",                  "ci-cd", 3, 30, tags=["游戏"], ms=True),
    c("se-release-mgmt",        "发布管理",                 "Release Branch/Tag/自动化Release Notes",     "ci-cd", 2, 25, tags=["发布"]),

    # --- code-review (20) ---
    c("se-cr-intro",            "代码审查概述",             "代码审查的目标、价值与最佳实践",             "code-review", 1, 20, tags=["基础"], ms=True),
    c("se-cr-checklist",        "审查清单",                 "功能/安全/性能/可读性检查维度",              "code-review", 2, 25, "practice", tags=["方法"]),
    c("se-cr-tooling",          "审查工具",                 "GitHub PR Review/Gerrit/Crucible对比",       "code-review", 2, 25, tags=["工具"]),
    c("se-cr-feedback",         "建设性反馈",               "审查评论的措辞、优先级标记与建议格式",       "code-review", 2, 20, tags=["沟通"], ms=True),
    c("se-cr-automation",       "自动化审查",               "Lint/Format/StaticAnalysis集成",              "code-review", 2, 25, tags=["自动化"]),
    c("se-cr-pair-programming", "结对编程",                 "Driver/Navigator模式与远程结对",             "code-review", 2, 25, tags=["协作"]),
    c("se-cr-metrics",          "审查指标",                 "Review Time/Comment Density/Defect Escape",  "code-review", 2, 25, tags=["度量"]),
    c("se-code-quality",        "代码质量标准",             "圈复杂度/认知复杂度/重复率",                "code-review", 2, 25, tags=["质量"]),
    c("se-static-analysis",     "静态分析",                 "SonarQube/ESLint/Pylint/Clang-Tidy",         "code-review", 2, 30, tags=["工具"], ms=True),
    c("se-tech-debt",           "技术债务管理",             "技术债识别、分类与偿还策略",                 "code-review", 2, 25, tags=["管理"]),
    c("se-code-convention",     "编码规范",                 "命名/格式/注释/文件组织约定",               "code-review", 1, 20, tags=["规范"]),
    c("se-documentation",       "文档实践",                 "API文档/README/Architecture Decision Record", "code-review", 2, 25, "practice", tags=["文档"]),
    c("se-security-review",     "安全审查",                 "OWASP/注入/XSS/CSRF安全检查",                "code-review", 3, 30, tags=["安全"]),
    c("se-perf-review",         "性能审查",                 "N+1查询/内存泄漏/算法复杂度检查",           "code-review", 3, 25, tags=["性能"]),
    c("se-accessibility-review","可访问性审查",             "WCAG/ARIA/键盘导航/屏幕阅读器检查",         "code-review", 2, 25, tags=["可访问"]),
    c("se-cr-culture",          "审查文化建设",             "心理安全/知识共享/导师制度",                 "code-review", 2, 25, tags=["文化"]),
    c("se-mob-programming",     "群体编程",                 "Mob Programming与实时协作方法",              "code-review", 2, 25, tags=["协作"]),
    c("se-dependency-review",   "依赖审查",                 "第三方库安全/许可证/维护状态评估",           "code-review", 2, 25, tags=["供应链"]),
    c("se-cr-large-diff",       "大型变更审查",             "拆分策略/Stacked PR/增量审查",               "code-review", 2, 25, tags=["技巧"]),
    c("se-cr-game-specific",    "游戏项目审查重点",         "资源引用/内存预算/帧率影响检查",             "code-review", 3, 25, tags=["游戏"]),

    # --- tdd (20) ---
    c("se-tdd-intro",           "TDD概述",                  "测试驱动开发的红-绿-重构循环",               "tdd", 1, 20, tags=["基础"], ms=True),
    c("se-test-pyramid",        "测试金字塔",               "单元/集成/端到端测试比例策略",               "tdd", 2, 25, tags=["策略"]),
    c("se-unit-test",           "单元测试",                 "隔离测试、断言与测试命名规范",               "tdd", 2, 25, tags=["单元"], ms=True),
    c("se-integration-test",    "集成测试",                 "组件间协作验证与测试容器",                   "tdd", 2, 25, tags=["集成"]),
    c("se-e2e-test",            "端到端测试",               "Playwright/Cypress/Selenium UI自动化",       "tdd", 3, 30, tags=["E2E"]),
    c("se-test-doubles",        "测试替身",                 "Mock/Stub/Spy/Fake与隔离策略",               "tdd", 2, 25, tags=["技巧"], ms=True),
    c("se-test-coverage",       "测试覆盖率",               "行/分支/路径覆盖与覆盖率陷阱",              "tdd", 2, 25, tags=["度量"]),
    c("se-bdd",                 "行为驱动开发",             "BDD/Gherkin/Given-When-Then规范",            "tdd", 2, 25, tags=["BDD"]),
    c("se-property-test",       "属性测试",                 "QuickCheck/Hypothesis随机化测试",            "tdd", 3, 25, tags=["高级"]),
    c("se-mutation-test",       "变异测试",                 "代码变异检测测试套件有效性",                 "tdd", 3, 25, tags=["高级"]),
    c("se-snapshot-test",       "快照测试",                 "UI/API响应快照与差异对比",                   "tdd", 2, 20, tags=["UI"]),
    c("se-test-fixture",        "测试夹具",                 "SetUp/TearDown/数据工厂与共享状态",          "tdd", 2, 20, tags=["基础"]),
    c("se-test-patterns",       "测试模式",                 "AAA模式/Builder Pattern/Object Mother",      "tdd", 2, 25, tags=["模式"]),
    c("se-contract-test",       "契约测试",                 "Pact/消费者驱动契约与API兼容验证",           "tdd", 3, 25, tags=["微服务"]),
    c("se-perf-test",           "性能测试",                 "LoadRunner/JMeter/k6负载/压力/基准测试",     "tdd", 3, 30, tags=["性能"]),
    c("se-chaos-engineering",   "混沌工程",                 "故障注入/Chaos Monkey/韧性测试",             "tdd", 3, 30, tags=["韧性"]),
    c("se-test-game",           "游戏测试策略",             "自动化游戏测试/Bot测试/回放系统",            "tdd", 3, 30, tags=["游戏"], ms=True),
    c("se-test-refactoring",    "测试与重构",               "安全重构的测试保障策略",                     "tdd", 2, 25, tags=["重构"]),
    c("se-flaky-tests",         "不稳定测试",               "Flaky Test诊断与修复策略",                   "tdd", 2, 25, tags=["维护"]),
    c("se-test-data",           "测试数据管理",             "数据生成/清理/隔离与种子策略",               "tdd", 2, 25, tags=["数据"]),

    # --- performance-analysis (20) ---
    c("se-perf-intro",          "性能分析概述",             "性能指标定义与分析方法论",                   "performance-analysis", 1, 20, tags=["基础"], ms=True),
    c("se-profiling-tools",     "剖析工具",                 "Sampling/Instrumentation Profiler对比",      "performance-analysis", 2, 25, tags=["工具"]),
    c("se-cpu-profiling",       "CPU性能分析",              "热点函数/调用图/火焰图解读",                "performance-analysis", 2, 30, tags=["CPU"], ms=True),
    c("se-memory-profiling",    "内存性能分析",             "分配跟踪/泄漏检测/堆快照",                  "performance-analysis", 2, 30, tags=["内存"]),
    c("se-gpu-profiling",       "GPU性能分析",              "RenderDoc/Nsight/PIX图形调试",               "performance-analysis", 3, 30, tags=["GPU"]),
    c("se-benchmark",           "基准测试",                 "Microbenchmark/Macro/回归基准方法",          "performance-analysis", 2, 25, tags=["测试"]),
    c("se-algo-complexity",     "算法复杂度分析",           "时间/空间复杂度与实际性能关系",              "performance-analysis", 2, 25, tags=["算法"]),
    c("se-cache-perf",          "缓存性能",                 "CPU缓存层级/缓存行/数据局部性",              "performance-analysis", 3, 30, tags=["硬件"], ms=True),
    c("se-io-perf",             "I/O性能分析",              "磁盘/网络I/O瓶颈与异步优化",                "performance-analysis", 2, 25, tags=["I/O"]),
    c("se-concurrency-perf",    "并发性能分析",             "锁竞争/上下文切换/False Sharing",            "performance-analysis", 3, 30, tags=["并发"]),
    c("se-frame-analysis",      "帧分析",                   "游戏帧时间分解与瓶颈定位",                  "performance-analysis", 3, 30, tags=["游戏"]),
    c("se-load-testing",        "负载测试",                 "并发用户模拟与服务器性能评估",               "performance-analysis", 2, 25, tags=["服务器"]),
    c("se-apm",                 "APM监控",                  "Application Performance Monitoring工具",     "performance-analysis", 2, 25, tags=["监控"]),
    c("se-optimization-pattern","优化模式",                 "空间换时间/预计算/批处理/池化",              "performance-analysis", 2, 25, tags=["模式"]),
    c("se-compile-time-perf",   "编译时性能",               "编译耗时分析与优化策略",                    "performance-analysis", 2, 25, tags=["编译"]),
    c("se-startup-perf",        "启动性能优化",             "冷启动/热启动/懒加载策略",                  "performance-analysis", 2, 25, tags=["启动"]),
    c("se-network-perf",        "网络性能分析",             "延迟/带宽/吞吐量/协议优化",                 "performance-analysis", 2, 25, tags=["网络"]),
    c("se-database-perf",       "数据库性能",               "查询优化/索引/执行计划分析",                 "performance-analysis", 3, 30, tags=["数据库"]),
    c("se-perf-regression",     "性能回归检测",             "CI集成性能基准与告警阈值",                   "performance-analysis", 3, 25, "practice", tags=["CI"]),
    c("se-perf-budget",         "性能预算",                 "性能指标预算分配与监控策略",                 "performance-analysis", 2, 25, "practice", tags=["规划"]),

    # --- refactoring (20) ---
    c("se-refactor-intro",      "重构概述",                 "重构的定义、时机与安全保障",                 "refactoring", 1, 20, tags=["基础"], ms=True),
    c("se-code-smells",         "代码异味",                 "22种常见代码异味识别与分类",                 "refactoring", 2, 25, tags=["识别"]),
    c("se-extract-method",      "提取方法",                 "长方法拆分与职责单一化",                     "refactoring", 2, 20, tags=["方法"], ms=True),
    c("se-rename-refactor",     "重命名重构",               "变量/方法/类的语义化命名",                   "refactoring", 1, 15, tags=["基础"]),
    c("se-extract-class",       "提取类",                   "God Class拆分与职责分配",                    "refactoring", 2, 25, tags=["类"]),
    c("se-move-method",         "移动方法/字段",            "Feature Envy修复与职责归位",                 "refactoring", 2, 20, tags=["方法"]),
    c("se-inline-refactor",     "内联重构",                 "过度抽象的简化与消除间接层",                 "refactoring", 2, 20, tags=["简化"]),
    c("se-replace-conditional", "替换条件逻辑",             "多态替换switch/if-else链",                   "refactoring", 2, 25, tags=["控制流"]),
    c("se-introduce-parameter", "引入参数对象",             "参数列表简化与数据聚合",                     "refactoring", 2, 20, tags=["参数"]),
    c("se-null-object",         "Null对象模式",             "消除null检查的策略模式",                     "refactoring", 2, 20, tags=["模式"]),
    c("se-legacy-refactor",     "遗留代码重构",             "Michael Feathers的遗留代码改善策略",         "refactoring", 3, 30, tags=["遗留"], ms=True),
    c("se-strangler-fig",       "绞杀者模式",               "渐进式系统替换而非大爆炸重写",               "refactoring", 3, 25, tags=["迁移"]),
    c("se-refactor-patterns",   "重构模式",                 "Kerievsky《重构到模式》关键手法",            "refactoring", 3, 25, tags=["高级"]),
    c("se-test-before-refactor","重构前加测试",             "Characterization Test与安全网构建",          "refactoring", 2, 25, "practice", tags=["测试"]),
    c("se-micro-refactor",      "微重构",                   "5分钟内完成的小步安全重构",                  "refactoring", 1, 20, "practice", tags=["实践"]),
    c("se-api-refactor",        "API重构",                  "向后兼容的接口重构与废弃策略",               "refactoring", 3, 30, tags=["接口"]),
    c("se-database-refactor",   "数据库重构",               "Schema迁移/零停机变更/演化式设计",           "refactoring", 3, 30, tags=["数据库"]),
    c("se-arch-refactor",       "架构级重构",               "模块解耦/微服务拆分/代码分层调整",           "refactoring", 3, 35, tags=["架构"]),
    c("se-continuous-refactor", "持续重构",                 "童子军原则与日常重构习惯",                   "refactoring", 2, 20, "practice", tags=["文化"]),
    c("se-refactor-game",       "游戏代码重构",             "热路径性能保护/ECS迁移/脚本重组",            "refactoring", 3, 30, tags=["游戏"]),

    # --- game-programming-patterns (20) ---
    c("se-gpp-intro",           "游戏编程模式概述",         "Robert Nystrom《游戏编程模式》核心思想",     "game-programming-patterns", 1, 20, tags=["基础"], ms=True),
    c("se-game-loop",           "游戏循环",                 "Fixed/Variable/Semi-Fixed Timestep",         "game-programming-patterns", 2, 25, tags=["核心"], ms=True),
    c("se-update-method",       "更新方法",                 "统一更新接口与帧驱动逻辑",                  "game-programming-patterns", 2, 20, tags=["核心"]),
    c("se-component-pattern",   "组件模式",                 "组合优于继承的游戏对象设计",                 "game-programming-patterns", 2, 25, tags=["架构"]),
    c("se-event-queue",         "事件队列",                 "异步消息分发与帧间通信",                     "game-programming-patterns", 2, 25, tags=["通信"]),
    c("se-service-locator",     "服务定位器",               "全局服务访问点与Mock替换",                   "game-programming-patterns", 2, 20, tags=["依赖"]),
    c("se-object-pool",         "对象池",                   "预分配对象复用降低GC压力",                   "game-programming-patterns", 2, 25, tags=["内存"], ms=True),
    c("se-spatial-partition",   "空间分区",                 "Grid/Quadtree/Octree/BSP/BVH",              "game-programming-patterns", 3, 30, tags=["空间"]),
    c("se-double-buffer",       "双缓冲",                   "帧缓冲/状态缓冲与无撕裂更新",               "game-programming-patterns", 2, 25, tags=["渲染"]),
    c("se-dirty-flag",          "脏标记",                   "变化追踪与按需更新优化",                     "game-programming-patterns", 2, 20, tags=["优化"]),
    c("se-bytecode",            "字节码模式",               "用户定义行为的安全沙箱执行",                 "game-programming-patterns", 3, 30, tags=["脚本"]),
    c("se-type-object",         "类型对象",                 "数据驱动的类型定义系统",                     "game-programming-patterns", 2, 25, tags=["数据驱动"]),
    c("se-data-locality",       "数据局部性",               "缓存友好的数据布局与SoA模式",                "game-programming-patterns", 3, 25, tags=["性能"]),
    c("se-flyweight-game",      "享元模式(游戏)",           "共享资源实例化与实例数据分离",               "game-programming-patterns", 2, 25, tags=["内存"]),
    c("se-prototype-game",      "原型模式(游戏)",           "运行时对象克隆与Prefab系统",                 "game-programming-patterns", 2, 25, tags=["创建"]),
    c("se-state-pattern-game",  "状态模式(游戏)",           "角色/AI有限状态机实现",                      "game-programming-patterns", 2, 25, tags=["AI"]),
    c("se-command-pattern-game","命令模式(游戏)",           "输入映射/撤销/回放/网络同步",                "game-programming-patterns", 2, 25, tags=["输入"]),
    c("se-observer-game",       "观察者模式(游戏)",         "成就/事件系统/UI绑定",                       "game-programming-patterns", 2, 25, tags=["事件"]),
    c("se-sandbox-pattern",     "沙箱模式",                 "安全隔离的自定义行为运行环境",               "game-programming-patterns", 3, 25, tags=["安全"]),
    c("se-subclass-sandbox",    "子类沙箱",                 "模板方法+受限API的行为定义模式",             "game-programming-patterns", 2, 25, tags=["继承"]),

    # --- ecs-architecture (20) ---
    c("se-ecs-intro",           "ECS架构概述",              "Entity-Component-System的核心理念",          "ecs-architecture", 1, 20, tags=["基础"], ms=True),
    c("se-entity",              "Entity实体",               "轻量ID与组件容器设计",                       "ecs-architecture", 2, 25, tags=["核心"]),
    c("se-component-ecs",       "Component组件",            "纯数据结构与组合式对象定义",                 "ecs-architecture", 2, 25, tags=["核心"]),
    c("se-system-ecs",          "System系统",               "逻辑处理单元与查询遍历",                    "ecs-architecture", 2, 25, tags=["核心"], ms=True),
    c("se-archetype",           "Archetype存储",            "组件组合分类与连续内存布局",                 "ecs-architecture", 3, 30, tags=["存储"]),
    c("se-sparse-set",          "Sparse Set",               "O(1)查找/添加/删除的组件存储",               "ecs-architecture", 3, 25, tags=["存储"]),
    c("se-ecs-query",           "ECS查询系统",              "Component Query/Filter/排除条件",             "ecs-architecture", 2, 25, tags=["查询"]),
    c("se-ecs-scheduling",      "System调度",               "依赖图/并行执行/阶段分组",                   "ecs-architecture", 3, 30, tags=["调度"]),
    c("se-ecs-events",          "ECS事件系统",              "Command Buffer/Event Queue/延迟操作",        "ecs-architecture", 3, 25, tags=["事件"]),
    c("se-soa-layout",          "SoA数据布局",              "Structure of Arrays与SIMD友好设计",          "ecs-architecture", 3, 25, tags=["数据布局"], ms=True),
    c("se-entt",                "EnTT框架",                 "C++ ECS库的设计与使用",                      "ecs-architecture", 3, 25, tags=["框架"]),
    c("se-flecs",               "Flecs框架",                "高性能ECS框架与关系型查询",                  "ecs-architecture", 3, 25, tags=["框架"]),
    c("se-unity-dots-ecs",      "Unity DOTS ECS",           "Unity官方ECS实现与Burst集成",                "ecs-architecture", 3, 30, tags=["Unity"]),
    c("se-ue5-mass",            "UE5 Mass Entity",          "UE5 ECS变体与Gameplay集成",                  "ecs-architecture", 3, 30, tags=["UE5"]),
    c("se-ecs-networking",      "ECS网络同步",              "组件快照/差量同步/状态复制",                 "ecs-architecture", 3, 30, tags=["网络"]),
    c("se-ecs-serialization",   "ECS序列化",                "World快照/Save-Load/Scene导入导出",          "ecs-architecture", 3, 25, tags=["持久化"]),
    c("se-ecs-hierarchy",       "ECS层级关系",              "Parent-Child关系与变换传播",                 "ecs-architecture", 2, 25, tags=["关系"]),
    c("se-ecs-prefab",          "ECS Prefab",               "实体模板与批量实例化",                       "ecs-architecture", 2, 25, tags=["工具"]),
    c("se-ecs-migration",       "OOP到ECS迁移",             "从面向对象到数据导向的渐进式重构",           "ecs-architecture", 3, 30, tags=["迁移"]),
    c("se-ecs-testing",         "ECS测试策略",              "System单元测试与集成测试方法",               "ecs-architecture", 2, 25, "practice", tags=["测试"]),

    # --- memory-management (20) ---
    c("se-mem-intro",           "内存管理概述",             "堆/栈/静态内存与生命周期管理",               "memory-management", 1, 20, tags=["基础"], ms=True),
    c("se-stack-heap",          "栈与堆",                   "分配策略对比与性能影响",                     "memory-management", 2, 25, tags=["基础"]),
    c("se-smart-pointers",      "智能指针",                 "unique_ptr/shared_ptr/weak_ptr语义",         "memory-management", 2, 25, tags=["C++"], ms=True),
    c("se-raii",                "RAII",                     "资源获取即初始化与异常安全",                 "memory-management", 2, 25, tags=["C++"]),
    c("se-memory-allocator",    "内存分配器",               "Custom Allocator/Arena/Slab分配策略",        "memory-management", 3, 30, tags=["高级"]),
    c("se-pool-allocator",      "池分配器",                 "固定大小对象的O(1)分配回收",                 "memory-management", 3, 25, tags=["池化"], ms=True),
    c("se-gc",                  "垃圾回收",                 "Mark-Sweep/Generational/Incremental GC",    "memory-management", 3, 30, tags=["GC"]),
    c("se-gc-optimization",     "GC优化",                   "减少分配/对象池/值类型/结构体",              "memory-management", 3, 25, tags=["优化"]),
    c("se-memory-leak",         "内存泄漏检测",             "Valgrind/AddressSanitizer/HeapTrack",        "memory-management", 2, 25, "practice", tags=["调试"]),
    c("se-memory-fragmentation","内存碎片化",               "碎片类型/紧凑化/分配策略",                   "memory-management", 3, 25, tags=["问题"]),
    c("se-virtual-memory",      "虚拟内存",                 "页表/TLB/内存映射文件",                      "memory-management", 3, 30, tags=["OS"]),
    c("se-cache-friendly",      "缓存友好编程",             "数据布局/预取/避免Cache Miss",               "memory-management", 3, 25, tags=["性能"]),
    c("se-memory-budget",       "内存预算管理",             "游戏平台内存限制与分配策略",                 "memory-management", 2, 25, tags=["游戏"]),
    c("se-texture-memory",      "纹理内存管理",             "流式加载/Mipmap/压缩格式选择",               "memory-management", 3, 25, tags=["图形"]),
    c("se-string-interning",    "字符串池化",               "字符串去重与哈希查找优化",                   "memory-management", 2, 20, tags=["优化"]),
    c("se-alignment",           "内存对齐",                 "结构体填充/SIMD对齐/平台差异",               "memory-management", 2, 25, tags=["底层"]),
    c("se-move-semantics",      "移动语义",                 "C++11 Move/右值引用/完美转发",               "memory-management", 3, 25, tags=["C++"]),
    c("se-ownership",           "所有权模型",               "Rust所有权/借用检查对C++的启示",             "memory-management", 3, 30, tags=["安全"]),
    c("se-arena-allocator",     "Arena分配器",              "Frame Allocator/Scope Allocator实现",        "memory-management", 3, 25, tags=["游戏"]),
    c("se-mem-debug",           "内存调试技巧",             "内存哨兵/Canary/填充模式/检测工具",          "memory-management", 2, 25, "practice", tags=["调试"]),

    # --- multithreading (20) ---
    c("se-mt-intro",            "多线程概述",               "并发/并行概念与线程模型",                    "multithreading", 1, 20, tags=["基础"], ms=True),
    c("se-thread-basics",       "线程基础",                 "创建/同步/生命周期管理",                     "multithreading", 2, 25, tags=["基础"]),
    c("se-mutex-lock",          "互斥锁",                   "Mutex/Lock Guard/Deadlock预防",              "multithreading", 2, 25, tags=["同步"], ms=True),
    c("se-condition-var",       "条件变量",                 "Wait/Notify/虚假唤醒与生产消费者",           "multithreading", 2, 25, tags=["同步"]),
    c("se-atomic",              "原子操作",                 "Atomic类型/CAS/内存序",                      "multithreading", 3, 30, tags=["底层"]),
    c("se-lock-free",           "无锁编程",                 "无锁队列/栈与ABA问题",                       "multithreading", 3, 35, tags=["高级"], ms=True),
    c("se-thread-pool",         "线程池",                   "工作窃取/任务调度/线程复用",                 "multithreading", 2, 25, tags=["模式"]),
    c("se-task-system",         "任务系统",                 "Task Graph/依赖/优先级调度",                 "multithreading", 3, 30, tags=["架构"]),
    c("se-future-promise",      "Future/Promise",           "异步结果与链式操作",                         "multithreading", 2, 25, tags=["异步"]),
    c("se-coroutine",           "协程",                     "C++20 Coroutine/Python async-await/Fiber",  "multithreading", 3, 30, tags=["异步"]),
    c("se-rwlock",              "读写锁",                   "Shared/Exclusive Lock与读多写少优化",        "multithreading", 2, 25, tags=["同步"]),
    c("se-memory-model",        "内存模型",                 "C++/Java内存模型与Happens-Before",           "multithreading", 3, 30, tags=["底层"]),
    c("se-data-race",           "数据竞争检测",             "ThreadSanitizer/Helgrind检测工具",           "multithreading", 2, 25, "practice", tags=["调试"]),
    c("se-mt-patterns",         "多线程模式",               "Producer-Consumer/Pipeline/MapReduce",       "multithreading", 2, 25, tags=["模式"]),
    c("se-game-threading",      "游戏多线程架构",           "主线程/渲染线程/Worker模型",                 "multithreading", 3, 30, tags=["游戏"], ms=True),
    c("se-simd",                "SIMD编程",                 "SSE/AVX/NEON向量化与intrinsics",             "multithreading", 3, 30, tags=["向量化"]),
    c("se-gpu-compute",         "GPU计算",                  "Compute Shader/CUDA/OpenCL基础",             "multithreading", 3, 30, tags=["GPU"]),
    c("se-false-sharing",       "False Sharing",            "缓存行争用与Padding对策",                    "multithreading", 3, 25, tags=["性能"]),
    c("se-concurrent-ds",       "并发数据结构",             "ConcurrentHashMap/Queue/SkipList",           "multithreading", 3, 30, tags=["数据结构"]),
    c("se-mt-debug",            "多线程调试",               "调试策略/日志/确定性重放",                   "multithreading", 2, 25, "practice", tags=["调试"]),

    # --- build-systems (20) ---
    c("se-build-intro",         "构建系统概述",             "构建系统的职责与核心概念",                   "build-systems", 1, 20, tags=["基础"], ms=True),
    c("se-cmake",               "CMake",                    "CMakeLists.txt/Target/Generator",            "build-systems", 2, 30, tags=["C++"], ms=True),
    c("se-make",                "Make/Makefile",            "经典构建工具的规则与模式",                   "build-systems", 2, 25, tags=["经典"]),
    c("se-msbuild",             "MSBuild",                  "Visual Studio构建系统与.vcxproj",            "build-systems", 2, 25, tags=["Windows"]),
    c("se-ninja",               "Ninja",                    "低层级高速构建执行器",                       "build-systems", 2, 20, tags=["工具"]),
    c("se-bazel",               "Bazel",                    "Google的可复现/可缓存构建系统",              "build-systems", 3, 30, tags=["大规模"]),
    c("se-gradle",              "Gradle",                   "JVM生态构建工具与Groovy/Kotlin DSL",         "build-systems", 2, 25, tags=["JVM"]),
    c("se-webpack-vite",        "Webpack/Vite",             "前端打包工具与模块联邦",                     "build-systems", 2, 25, tags=["前端"]),
    c("se-ubt",                 "Unreal Build Tool",        "UE5的UBT/UHT/模块编译",                     "build-systems", 3, 30, tags=["UE5"], ms=True),
    c("se-incremental-build",   "增量构建",                 "文件时间戳/内容哈希/依赖追踪",               "build-systems", 2, 25, tags=["优化"]),
    c("se-cross-compile",       "交叉编译",                 "多平台目标编译与工具链配置",                 "build-systems", 3, 25, tags=["平台"]),
    c("se-precompiled-header",  "预编译头",                 "PCH/Unity Build/模块接口单元",               "build-systems", 2, 25, tags=["C++"]),
    c("se-link-time",           "链接优化",                 "LTO/Linker脚本/符号可见性",                  "build-systems", 3, 25, tags=["优化"]),
    c("se-build-variant",       "构建变体",                 "Debug/Release/Profile配置管理",              "build-systems", 2, 20, tags=["配置"]),
    c("se-code-generation",     "代码生成",                 "Proto/Thrift/UHT反射代码自动生成",           "build-systems", 3, 25, tags=["生成"]),
    c("se-remote-build",        "远程构建",                 "分布式编译/IncrediBuild/distcc",             "build-systems", 3, 25, tags=["分布式"]),
    c("se-build-reproducibility","可复现构建",              "确定性构建与供应链安全",                     "build-systems", 3, 25, tags=["安全"]),
    c("se-shader-build",        "Shader编译管线",           "Shader变体/Permutation/异步编译",            "build-systems", 3, 25, tags=["渲染"]),
    c("se-asset-pipeline",      "资产处理管线",             "Cook/Compress/Platform-specific导出",        "build-systems", 3, 30, tags=["游戏"], ms=True),
    c("se-build-automation",    "构建自动化脚本",           "Python/PowerShell/Bash构建脚本",             "build-systems", 2, 25, "practice", tags=["自动化"]),

    # --- package-management (20) ---
    c("se-pkg-intro",           "包管理概述",               "依赖管理的核心问题与解决方案",               "package-management", 1, 20, tags=["基础"], ms=True),
    c("se-npm",                 "npm/Yarn/pnpm",            "Node.js包管理器与lock文件",                  "package-management", 2, 25, tags=["前端"]),
    c("se-pip",                 "pip/Poetry/conda",         "Python依赖管理与虚拟环境",                   "package-management", 2, 25, tags=["Python"]),
    c("se-nuget",               "NuGet",                    ".NET包管理器与C#项目集成",                   "package-management", 2, 25, tags=["C#"]),
    c("se-conan-vcpkg",         "Conan/vcpkg",              "C++包管理器与构建集成",                      "package-management", 2, 25, tags=["C++"], ms=True),
    c("se-cargo",               "Cargo",                    "Rust包管理器与crates.io生态",                "package-management", 2, 25, tags=["Rust"]),
    c("se-maven",               "Maven/Gradle依赖",        "JVM依赖解析/仓库/传递依赖",                  "package-management", 2, 25, tags=["JVM"]),
    c("se-dep-resolution",      "依赖解析算法",             "版本约束求解/SAT/回溯策略",                  "package-management", 3, 30, tags=["原理"]),
    c("se-lockfile",            "Lock文件",                 "确定性安装与协作一致性",                     "package-management", 2, 20, tags=["基础"]),
    c("se-private-registry",    "私有注册表",               "Verdaccio/Artifactory/自建仓库",             "package-management", 2, 25, tags=["企业"]),
    c("se-monorepo-deps",       "Monorepo依赖管理",        "Workspace Protocol/Hoist/Phantom依赖",       "package-management", 3, 25, tags=["Monorepo"]),
    c("se-dep-security",        "依赖安全",                 "npm audit/Snyk/Dependabot漏洞扫描",         "package-management", 2, 25, tags=["安全"], ms=True),
    c("se-dep-license",         "许可证合规",               "MIT/Apache/GPL兼容性与合规检查",             "package-management", 2, 25, tags=["法务"]),
    c("se-dep-upgrade",         "依赖升级策略",             "Renovate/Dependabot自动化更新",              "package-management", 2, 25, tags=["维护"]),
    c("se-vendoring",           "Vendoring",                "依赖内嵌与离线构建保障",                     "package-management", 2, 20, tags=["策略"]),
    c("se-game-dep",            "游戏项目依赖管理",         "引擎插件/第三方库/中间件版本控制",           "package-management", 3, 25, tags=["游戏"]),
    c("se-container-deps",      "容器化依赖",               "Dockerfile依赖管理与多阶段镜像",             "package-management", 2, 25, tags=["容器"]),
    c("se-workspace",           "Workspace管理",            "npm/pnpm/Yarn workspace协议",                "package-management", 2, 25, tags=["Monorepo"]),
    c("se-publish-flow",        "包发布流程",               "Publish/Unpublish/Deprecate生命周期",        "package-management", 2, 25, "practice", tags=["流程"], ms=True),
    c("se-dep-analysis",        "依赖分析",                 "依赖树可视化/循环检测/Tree Shaking",         "package-management", 2, 25, tags=["工具"]),
]

# ---------------------------------------------------------------------------
# Edges
# ---------------------------------------------------------------------------

edges = [
    # architecture-patterns internal
    {"source": "se-arch-intro",     "target": "se-layered-arch",     "type": "prerequisite"},
    {"source": "se-arch-intro",     "target": "se-mvc-mvvm",         "type": "prerequisite"},
    {"source": "se-arch-intro",     "target": "se-modular-arch",     "type": "prerequisite"},
    {"source": "se-modular-arch",   "target": "se-microservices",    "type": "prerequisite"},
    {"source": "se-layered-arch",   "target": "se-hexagonal",        "type": "prerequisite"},
    {"source": "se-layered-arch",   "target": "se-clean-arch",       "type": "prerequisite"},
    {"source": "se-solid",          "target": "se-clean-arch",       "type": "prerequisite"},
    {"source": "se-solid",          "target": "se-hexagonal",        "type": "prerequisite"},
    {"source": "se-microservices",  "target": "se-event-driven",     "type": "prerequisite"},
    {"source": "se-microservices",  "target": "se-service-mesh",     "type": "prerequisite"},
    {"source": "se-hexagonal",      "target": "se-ddd",              "type": "prerequisite"},
    {"source": "se-api-design",     "target": "se-microservices",    "type": "related"},
    {"source": "se-arch-intro",     "target": "se-arch-decision",    "type": "related"},
    {"source": "se-arch-intro",     "target": "se-arch-evolution",   "type": "related"},

    # design-patterns internal
    {"source": "se-dp-intro",       "target": "se-dp-singleton",     "type": "prerequisite"},
    {"source": "se-dp-intro",       "target": "se-dp-factory",       "type": "prerequisite"},
    {"source": "se-dp-intro",       "target": "se-dp-observer",      "type": "prerequisite"},
    {"source": "se-dp-factory",     "target": "se-dp-builder",       "type": "related"},
    {"source": "se-dp-factory",     "target": "se-dp-prototype",     "type": "related"},
    {"source": "se-dp-adapter",     "target": "se-dp-facade",        "type": "related"},
    {"source": "se-dp-decorator",   "target": "se-dp-proxy",         "type": "related"},
    {"source": "se-dp-observer",    "target": "se-dp-mediator",      "type": "related"},
    {"source": "se-dp-strategy",    "target": "se-dp-state",         "type": "related"},
    {"source": "se-dp-strategy",    "target": "se-dp-template",      "type": "related"},
    {"source": "se-dp-command",     "target": "se-dp-chain",         "type": "related"},
    {"source": "se-dp-composite",   "target": "se-dp-iterator",      "type": "related"},

    # version-control internal
    {"source": "se-vc-intro",       "target": "se-git-basics",       "type": "prerequisite"},
    {"source": "se-git-basics",     "target": "se-git-branching",    "type": "prerequisite"},
    {"source": "se-git-basics",     "target": "se-gitignore",        "type": "prerequisite"},
    {"source": "se-git-branching",  "target": "se-git-merge-rebase", "type": "prerequisite"},
    {"source": "se-git-branching",  "target": "se-pr-workflow",      "type": "prerequisite"},
    {"source": "se-git-basics",     "target": "se-git-hooks",        "type": "related"},
    {"source": "se-git-basics",     "target": "se-cherry-pick",      "type": "related"},
    {"source": "se-git-basics",     "target": "se-git-internals",    "type": "related"},
    {"source": "se-git-lfs",        "target": "se-vc-binary",        "type": "related"},
    {"source": "se-monorepo-tools", "target": "se-monorepo",         "type": "related"},
    {"source": "se-pr-workflow",    "target": "se-conventional-commit","type": "related"},

    # ci-cd internal
    {"source": "se-cicd-intro",     "target": "se-pipeline-design",  "type": "prerequisite"},
    {"source": "se-pipeline-design","target": "se-github-actions",   "type": "prerequisite"},
    {"source": "se-pipeline-design","target": "se-jenkins",          "type": "prerequisite"},
    {"source": "se-pipeline-design","target": "se-gitlab-ci",        "type": "prerequisite"},
    {"source": "se-github-actions", "target": "se-docker-ci",        "type": "related"},
    {"source": "se-pipeline-design","target": "se-ci-testing",       "type": "prerequisite"},
    {"source": "se-deploy-strategies","target": "se-rollback",       "type": "related"},
    {"source": "se-deploy-strategies","target": "se-feature-flags",  "type": "related"},
    {"source": "se-infra-as-code",  "target": "se-gitops",           "type": "prerequisite"},
    {"source": "se-cicd-intro",     "target": "se-game-ci",          "type": "related"},

    # code-review internal
    {"source": "se-cr-intro",       "target": "se-cr-checklist",     "type": "prerequisite"},
    {"source": "se-cr-intro",       "target": "se-cr-tooling",       "type": "prerequisite"},
    {"source": "se-cr-intro",       "target": "se-cr-feedback",      "type": "prerequisite"},
    {"source": "se-cr-checklist",   "target": "se-security-review",  "type": "related"},
    {"source": "se-cr-checklist",   "target": "se-perf-review",      "type": "related"},
    {"source": "se-cr-automation",  "target": "se-static-analysis",  "type": "prerequisite"},
    {"source": "se-cr-intro",       "target": "se-cr-culture",       "type": "related"},
    {"source": "se-code-quality",   "target": "se-tech-debt",        "type": "related"},

    # tdd internal
    {"source": "se-tdd-intro",      "target": "se-unit-test",        "type": "prerequisite"},
    {"source": "se-tdd-intro",      "target": "se-test-pyramid",     "type": "prerequisite"},
    {"source": "se-unit-test",      "target": "se-test-doubles",     "type": "prerequisite"},
    {"source": "se-unit-test",      "target": "se-integration-test", "type": "prerequisite"},
    {"source": "se-integration-test","target": "se-e2e-test",        "type": "prerequisite"},
    {"source": "se-test-doubles",   "target": "se-test-patterns",    "type": "related"},
    {"source": "se-unit-test",      "target": "se-test-coverage",    "type": "related"},
    {"source": "se-tdd-intro",      "target": "se-bdd",              "type": "related"},
    {"source": "se-unit-test",      "target": "se-property-test",    "type": "related"},
    {"source": "se-test-coverage",  "target": "se-mutation-test",    "type": "related"},

    # performance-analysis internal
    {"source": "se-perf-intro",     "target": "se-profiling-tools",  "type": "prerequisite"},
    {"source": "se-profiling-tools","target": "se-cpu-profiling",    "type": "prerequisite"},
    {"source": "se-profiling-tools","target": "se-memory-profiling", "type": "prerequisite"},
    {"source": "se-profiling-tools","target": "se-gpu-profiling",    "type": "prerequisite"},
    {"source": "se-perf-intro",     "target": "se-algo-complexity",  "type": "prerequisite"},
    {"source": "se-cpu-profiling",  "target": "se-cache-perf",       "type": "related"},
    {"source": "se-perf-intro",     "target": "se-benchmark",        "type": "related"},
    {"source": "se-benchmark",      "target": "se-perf-regression",  "type": "related"},
    {"source": "se-perf-intro",     "target": "se-frame-analysis",   "type": "related"},

    # refactoring internal
    {"source": "se-refactor-intro", "target": "se-code-smells",      "type": "prerequisite"},
    {"source": "se-code-smells",    "target": "se-extract-method",   "type": "prerequisite"},
    {"source": "se-code-smells",    "target": "se-rename-refactor",  "type": "prerequisite"},
    {"source": "se-code-smells",    "target": "se-extract-class",    "type": "prerequisite"},
    {"source": "se-extract-method", "target": "se-move-method",      "type": "related"},
    {"source": "se-extract-method", "target": "se-inline-refactor",  "type": "related"},
    {"source": "se-refactor-intro", "target": "se-test-before-refactor","type": "prerequisite"},
    {"source": "se-legacy-refactor","target": "se-strangler-fig",    "type": "related"},
    {"source": "se-refactor-patterns","target": "se-arch-refactor",  "type": "related"},

    # game-programming-patterns internal
    {"source": "se-gpp-intro",      "target": "se-game-loop",        "type": "prerequisite"},
    {"source": "se-gpp-intro",      "target": "se-component-pattern","type": "prerequisite"},
    {"source": "se-game-loop",      "target": "se-update-method",    "type": "prerequisite"},
    {"source": "se-component-pattern","target": "se-event-queue",    "type": "related"},
    {"source": "se-gpp-intro",      "target": "se-object-pool",      "type": "prerequisite"},
    {"source": "se-gpp-intro",      "target": "se-state-pattern-game","type": "prerequisite"},
    {"source": "se-object-pool",    "target": "se-spatial-partition", "type": "related"},
    {"source": "se-data-locality",  "target": "se-flyweight-game",   "type": "related"},
    {"source": "se-command-pattern-game","target": "se-event-queue", "type": "related"},

    # ecs-architecture internal
    {"source": "se-ecs-intro",      "target": "se-entity",           "type": "prerequisite"},
    {"source": "se-ecs-intro",      "target": "se-component-ecs",    "type": "prerequisite"},
    {"source": "se-ecs-intro",      "target": "se-system-ecs",       "type": "prerequisite"},
    {"source": "se-component-ecs",  "target": "se-archetype",        "type": "prerequisite"},
    {"source": "se-component-ecs",  "target": "se-sparse-set",       "type": "prerequisite"},
    {"source": "se-system-ecs",     "target": "se-ecs-query",        "type": "prerequisite"},
    {"source": "se-system-ecs",     "target": "se-ecs-scheduling",   "type": "prerequisite"},
    {"source": "se-archetype",      "target": "se-soa-layout",       "type": "related"},
    {"source": "se-ecs-intro",      "target": "se-ecs-migration",    "type": "related"},
    {"source": "se-ecs-intro",      "target": "se-unity-dots-ecs",   "type": "related"},
    {"source": "se-ecs-intro",      "target": "se-ue5-mass",         "type": "related"},

    # memory-management internal
    {"source": "se-mem-intro",      "target": "se-stack-heap",       "type": "prerequisite"},
    {"source": "se-stack-heap",     "target": "se-smart-pointers",   "type": "prerequisite"},
    {"source": "se-stack-heap",     "target": "se-raii",             "type": "prerequisite"},
    {"source": "se-stack-heap",     "target": "se-memory-allocator", "type": "prerequisite"},
    {"source": "se-memory-allocator","target": "se-pool-allocator",  "type": "prerequisite"},
    {"source": "se-memory-allocator","target": "se-arena-allocator", "type": "related"},
    {"source": "se-mem-intro",      "target": "se-gc",               "type": "prerequisite"},
    {"source": "se-gc",             "target": "se-gc-optimization",  "type": "prerequisite"},
    {"source": "se-mem-intro",      "target": "se-memory-leak",      "type": "related"},
    {"source": "se-memory-allocator","target": "se-memory-fragmentation","type": "related"},
    {"source": "se-cache-friendly", "target": "se-alignment",        "type": "related"},
    {"source": "se-smart-pointers", "target": "se-move-semantics",   "type": "related"},

    # multithreading internal
    {"source": "se-mt-intro",       "target": "se-thread-basics",    "type": "prerequisite"},
    {"source": "se-thread-basics",  "target": "se-mutex-lock",       "type": "prerequisite"},
    {"source": "se-thread-basics",  "target": "se-condition-var",    "type": "prerequisite"},
    {"source": "se-mutex-lock",     "target": "se-atomic",           "type": "prerequisite"},
    {"source": "se-atomic",         "target": "se-lock-free",        "type": "prerequisite"},
    {"source": "se-thread-basics",  "target": "se-thread-pool",      "type": "prerequisite"},
    {"source": "se-thread-pool",    "target": "se-task-system",      "type": "prerequisite"},
    {"source": "se-thread-basics",  "target": "se-future-promise",   "type": "related"},
    {"source": "se-future-promise", "target": "se-coroutine",        "type": "related"},
    {"source": "se-mutex-lock",     "target": "se-rwlock",           "type": "related"},
    {"source": "se-atomic",         "target": "se-memory-model",     "type": "related"},
    {"source": "se-mt-intro",       "target": "se-game-threading",   "type": "related"},
    {"source": "se-mt-intro",       "target": "se-simd",             "type": "related"},

    # build-systems internal
    {"source": "se-build-intro",    "target": "se-cmake",            "type": "prerequisite"},
    {"source": "se-build-intro",    "target": "se-make",             "type": "prerequisite"},
    {"source": "se-build-intro",    "target": "se-msbuild",          "type": "prerequisite"},
    {"source": "se-cmake",          "target": "se-ninja",            "type": "related"},
    {"source": "se-build-intro",    "target": "se-bazel",            "type": "related"},
    {"source": "se-build-intro",    "target": "se-incremental-build","type": "prerequisite"},
    {"source": "se-cmake",          "target": "se-cross-compile",    "type": "related"},
    {"source": "se-cmake",          "target": "se-precompiled-header","type": "related"},
    {"source": "se-build-intro",    "target": "se-ubt",              "type": "related"},
    {"source": "se-build-intro",    "target": "se-asset-pipeline",   "type": "related"},

    # package-management internal
    {"source": "se-pkg-intro",      "target": "se-npm",              "type": "prerequisite"},
    {"source": "se-pkg-intro",      "target": "se-pip",              "type": "prerequisite"},
    {"source": "se-pkg-intro",      "target": "se-conan-vcpkg",      "type": "prerequisite"},
    {"source": "se-npm",            "target": "se-lockfile",         "type": "prerequisite"},
    {"source": "se-pkg-intro",      "target": "se-dep-resolution",   "type": "related"},
    {"source": "se-npm",            "target": "se-workspace",        "type": "related"},
    {"source": "se-workspace",      "target": "se-monorepo-deps",    "type": "related"},
    {"source": "se-pkg-intro",      "target": "se-dep-security",     "type": "related"},
    {"source": "se-dep-security",   "target": "se-dep-license",      "type": "related"},
    {"source": "se-pkg-intro",      "target": "se-publish-flow",     "type": "related"},

    # === Cross-subdomain edges ===
    {"source": "se-solid",          "target": "se-dp-intro",         "type": "prerequisite"},
    {"source": "se-dp-observer",    "target": "se-observer-game",    "type": "related"},
    {"source": "se-dp-command",     "target": "se-command-pattern-game","type": "related"},
    {"source": "se-dp-state",       "target": "se-state-pattern-game","type": "related"},
    {"source": "se-dp-strategy",    "target": "se-object-pool",      "type": "related"},
    {"source": "se-dp-flyweight",   "target": "se-flyweight-game",   "type": "related"},
    {"source": "se-dp-prototype",   "target": "se-prototype-game",   "type": "related"},
    {"source": "se-component-pattern","target": "se-ecs-intro",      "type": "prerequisite"},
    {"source": "se-data-locality",  "target": "se-soa-layout",       "type": "related"},
    {"source": "se-data-locality",  "target": "se-cache-friendly",   "type": "related"},
    {"source": "se-object-pool",    "target": "se-pool-allocator",   "type": "related"},
    {"source": "se-pr-workflow",    "target": "se-cr-intro",         "type": "related"},
    {"source": "se-git-hooks",      "target": "se-cr-automation",    "type": "related"},
    {"source": "se-tdd-intro",      "target": "se-test-before-refactor","type": "related"},
    {"source": "se-test-refactoring","target": "se-refactor-intro",  "type": "related"},
    {"source": "se-ci-testing",     "target": "se-test-pyramid",     "type": "related"},
    {"source": "se-github-actions", "target": "se-game-ci",          "type": "related"},
    {"source": "se-ubt",            "target": "se-cmake",            "type": "related"},
    {"source": "se-conan-vcpkg",    "target": "se-cmake",            "type": "related"},
    {"source": "se-game-threading", "target": "se-task-system",      "type": "related"},
    {"source": "se-memory-allocator","target": "se-perf-intro",      "type": "related"},
    {"source": "se-algo-complexity","target": "se-code-quality",     "type": "related"},
    {"source": "se-static-analysis","target": "se-ci-security",      "type": "related"},
    {"source": "se-ecs-migration",  "target": "se-refactor-game",    "type": "related"},
    {"source": "se-gc-optimization","target": "se-object-pool",      "type": "related"},
    {"source": "se-memory-budget",  "target": "se-texture-memory",   "type": "related"},
    {"source": "se-lock-free",      "target": "se-concurrent-ds",    "type": "prerequisite"},
    {"source": "se-game-loop",      "target": "se-game-threading",   "type": "related"},
    {"source": "se-asset-pipeline", "target": "se-game-ci",          "type": "related"},
    {"source": "se-dep-security",   "target": "se-ci-security",      "type": "related"},
]

# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------

milestones = [
    {"concept_id": c_["id"], "name": c_["name"], "order": i+1}
    for i, c_ in enumerate([cx for cx in concepts if cx["is_milestone"]])
]

# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def main():
    data = {
        "domain": DOMAIN,
        "subdomains": SUBDOMAINS,
        "concepts": concepts,
        "edges": edges,
        "milestones": milestones,
    }

    # Validate
    ids = {c_["id"] for c_ in concepts}
    assert len(ids) == len(concepts), f"Duplicate IDs! {len(ids)} unique vs {len(concepts)} total"
    assert len(concepts) == 280, f"Expected 280 concepts, got {len(concepts)}"
    assert len(SUBDOMAINS) == 14, f"Expected 14 subdomains, got {len(SUBDOMAINS)}"

    for e in edges:
        assert e["source"] in ids, f"Edge source '{e['source']}' not found"
        assert e["target"] in ids, f"Edge target '{e['target']}' not found"

    # Per-subdomain count
    from collections import Counter
    sub_counts = Counter(c_["subdomain_id"] for c_ in concepts)
    for s in SUBDOMAINS:
        assert sub_counts[s["id"]] == 20, f"{s['id']} has {sub_counts[s['id']]} concepts (expected 20)"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Wrote {OUT}")
    print(f"   {len(concepts)} concepts, {len(edges)} edges, {len(SUBDOMAINS)} subdomains, {len(milestones)} milestones")

if __name__ == "__main__":
    main()
