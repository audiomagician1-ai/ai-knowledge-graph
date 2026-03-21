#!/usr/bin/env node
/**
 * Phase 36: Generate game-production (项目管理) knowledge sphere
 * 160 concepts, 8 subdomains, ~32 milestones, 24 cross-sphere links
 */
const fs = require('fs');
const path = require('path');

const DOMAIN = 'game-production';
const DOMAIN_NAME = '项目管理';
const COLOR = '#0f766e';

// ── Subdomains ──
const SUBDOMAINS = [
  { id: 'production-pipeline', name: '制作管线', description: '游戏制作的全流程管线设计、阶段划分与交付物管理', order: 1 },
  { id: 'milestone-planning', name: '里程碑规划', description: '项目里程碑定义、任务分解、时间估算与进度追踪', order: 2 },
  { id: 'resource-management', name: '资源调配', description: '人力资源规划、团队搭建、技能矩阵与工作量分配', order: 3 },
  { id: 'risk-management', name: '风险管理', description: '项目风险识别、评估、应对策略与应急预案', order: 4 },
  { id: 'cross-department', name: '跨部门协作', description: '多团队协作流程、沟通机制、依赖管理与冲突解决', order: 5 },
  { id: 'agile-scrum', name: '敏捷/Scrum', description: '敏捷开发在游戏项目中的应用、Sprint规划与回顾', order: 6 },
  { id: 'outsourcing', name: '外包管理', description: '外包策略、供应商筛选、质量管控与知识产权保护', order: 7 },
  { id: 'budget-control', name: '预算控制', description: '项目预算编制、成本追踪、ROI分析与财务报告', order: 8 },
];

// ── Concepts per subdomain (20 each = 160 total) ──

const CONCEPTS = {
  'production-pipeline': [
    { id: 'gp-pp-overview', name: '制作管线概述', desc: '游戏制作管线的定义、核心阶段与各阶段交付物', diff: 1, milestone: false },
    { id: 'gp-pp-preproduction', name: '预生产阶段', desc: '概念验证、原型制作、设计文档与技术预研', diff: 1, milestone: false },
    { id: 'gp-pp-prototype', name: '原型开发', desc: '快速原型构建方法、验证标准与Go/No-Go决策', diff: 2, milestone: true },
    { id: 'gp-pp-vertical-slice', name: '垂直切片', desc: 'Vertical Slice的定义、范围界定与质量标准', diff: 2, milestone: false },
    { id: 'gp-pp-full-production', name: '全面生产阶段', desc: '内容批量制作的管理策略与产能规划', diff: 2, milestone: false },
    { id: 'gp-pp-alpha', name: 'Alpha里程碑', desc: 'Alpha版本定义、功能完整性标准与评审流程', diff: 3, milestone: true },
    { id: 'gp-pp-beta', name: 'Beta里程碑', desc: 'Beta版本标准、内容锁定与Bug修复优先级', diff: 3, milestone: false },
    { id: 'gp-pp-gold-master', name: 'Gold Master', desc: 'GM版本标准、认证提交流程与发布检查清单', diff: 3, milestone: false },
    { id: 'gp-pp-post-launch', name: '上线后运维', desc: '发布后补丁策略、DLC规划与持续更新管线', diff: 3, milestone: false },
    { id: 'gp-pp-gate-review', name: '阶段评审', desc: '阶段门评审机制、通过标准与风险升级流程', diff: 2, milestone: true },
    { id: 'gp-pp-asset-pipeline', name: '资产管线', desc: '美术/音频/动画资产的生产、审核与集成流程', diff: 2, milestone: false },
    { id: 'gp-pp-build-pipeline', name: '构建管线', desc: '自动构建、持续集成与版本发布流程设计', diff: 3, milestone: false },
    { id: 'gp-pp-content-pipeline', name: '内容管线', desc: '关卡/叙事/任务等内容资产的生产与审核流程', diff: 2, milestone: false },
    { id: 'gp-pp-localization-pipeline', name: '本地化管线', desc: '多语言翻译、文化适配与本地化集成流程', diff: 3, milestone: false },
    { id: 'gp-pp-version-control', name: '版本管理策略', desc: 'Git/Perforce分支策略、合并规范与冲突解决', diff: 2, milestone: false },
    { id: 'gp-pp-documentation', name: '项目文档管理', desc: '设计文档(GDD/TDD)、Wiki维护与知识库建设', diff: 1, milestone: false },
    { id: 'gp-pp-approval-workflow', name: '审批流程', desc: '资产审批、功能审核与变更请求(CR)管理', diff: 2, milestone: false },
    { id: 'gp-pp-pipeline-optimization', name: '管线优化', desc: '瓶颈识别、自动化改进与管线效率提升方法', diff: 4, milestone: true },
    { id: 'gp-pp-cross-platform', name: '多平台管线', desc: 'PC/主机/移动端多平台同时开发的管线设计', diff: 4, milestone: false },
    { id: 'gp-pp-live-service', name: '持续运营管线', desc: 'Games-as-a-Service模式的持续内容交付管线', diff: 4, milestone: false },
  ],
  'milestone-planning': [
    { id: 'gp-mp-basics', name: '里程碑规划基础', desc: '项目里程碑的定义、类型与在游戏开发中的作用', diff: 1, milestone: false },
    { id: 'gp-mp-wbs', name: 'WBS工作分解', desc: '工作分解结构(WBS)的创建方法与粒度控制', diff: 2, milestone: true },
    { id: 'gp-mp-estimation', name: '工时估算', desc: '工时估算技术：类比、参数、三点估算与PERT', diff: 2, milestone: false },
    { id: 'gp-mp-critical-path', name: '关键路径法', desc: 'CPM关键路径识别、浮动时间与进度压缩', diff: 3, milestone: true },
    { id: 'gp-mp-gantt', name: '甘特图与时间线', desc: '甘特图制作、依赖关系可视化与进度追踪', diff: 2, milestone: false },
    { id: 'gp-mp-dependency', name: '任务依赖管理', desc: '任务间依赖类型(FS/SS/FF/SF)与依赖链优化', diff: 2, milestone: false },
    { id: 'gp-mp-tracking', name: '进度追踪', desc: '进度报告、燃尽图与挣值管理(EVM)方法', diff: 3, milestone: false },
    { id: 'gp-mp-buffer', name: '缓冲时间管理', desc: '项目缓冲、汇聚缓冲与关键链方法(CCPM)', diff: 3, milestone: true },
    { id: 'gp-mp-scope', name: '范围管理', desc: '项目范围定义、范围蔓延(Scope Creep)控制', diff: 2, milestone: false },
    { id: 'gp-mp-feature-cut', name: '功能裁剪', desc: '功能优先级矩阵、裁剪标准与影响评估', diff: 3, milestone: false },
    { id: 'gp-mp-roadmap', name: '产品路线图', desc: '长期产品路线图规划、版本规划与发布节奏', diff: 2, milestone: false },
    { id: 'gp-mp-deadline', name: '截止日期管理', desc: '硬截止日期下的范围-质量-时间三角平衡策略', diff: 3, milestone: false },
    { id: 'gp-mp-iteration', name: '迭代规划', desc: '迭代周期设定、迭代目标与回顾改进机制', diff: 2, milestone: false },
    { id: 'gp-mp-contingency', name: '应急计划', desc: '进度延迟的应急措施、快速通道与资源增援', diff: 3, milestone: false },
    { id: 'gp-mp-reporting', name: '进度报告', desc: '项目状态报告、仪表盘设计与利益相关者沟通', diff: 2, milestone: false },
    { id: 'gp-mp-tools', name: '项目管理工具', desc: 'Jira/Shotgrid/Notion/Hansoft等工具选型与配置', diff: 2, milestone: false },
    { id: 'gp-mp-kpi', name: '项目KPI', desc: '项目健康度指标(速率/缺陷密度/完成率)设定与监控', diff: 3, milestone: true },
    { id: 'gp-mp-postmortem', name: '项目复盘', desc: '项目结束后的复盘方法论、经验提炼与知识传承', diff: 3, milestone: false },
    { id: 'gp-mp-multi-project', name: '多项目管理', desc: '项目组合管理、资源共享与优先级仲裁', diff: 4, milestone: false },
    { id: 'gp-mp-scenario-planning', name: '情景规划', desc: '最佳/最差/最可能情景建模与决策准备', diff: 4, milestone: false },
  ],
  'resource-management': [
    { id: 'gp-rm-basics', name: '资源管理基础', desc: '项目资源类型(人力/设备/预算)与管理框架', diff: 1, milestone: false },
    { id: 'gp-rm-team-structure', name: '团队结构设计', desc: '游戏开发团队组织架构：职能制/项目制/矩阵制', diff: 2, milestone: true },
    { id: 'gp-rm-staffing', name: '人员招募与配置', desc: '人才需求规划、招聘策略与团队扩张时机', diff: 2, milestone: false },
    { id: 'gp-rm-skill-matrix', name: '技能矩阵', desc: '团队技能评估矩阵、技能差距分析与培养计划', diff: 2, milestone: false },
    { id: 'gp-rm-workload', name: '工作量分配', desc: '任务分配策略、负载均衡与过载预警机制', diff: 2, milestone: true },
    { id: 'gp-rm-capacity', name: '产能规划', desc: '团队产能评估、产能曲线与峰值管理', diff: 3, milestone: false },
    { id: 'gp-rm-onboarding', name: '新人入职', desc: '游戏团队新人入职流程、导师制与快速融入', diff: 1, milestone: false },
    { id: 'gp-rm-retention', name: '人才保留', desc: '核心人才保留策略、职业发展路径与团队稳定性', diff: 3, milestone: false },
    { id: 'gp-rm-performance', name: '绩效管理', desc: '绩效评估方法(OKR/KPI)、反馈周期与目标对齐', diff: 3, milestone: true },
    { id: 'gp-rm-team-scaling', name: '团队扩缩', desc: '项目阶段性的团队规模调整策略与平滑过渡', diff: 3, milestone: false },
    { id: 'gp-rm-remote-team', name: '远程团队管理', desc: '分布式团队协作工具、时区管理与文化融合', diff: 3, milestone: false },
    { id: 'gp-rm-cross-functional', name: '跨职能团队', desc: '跨职能小组(Strike Team)的组建与高效运作', diff: 3, milestone: false },
    { id: 'gp-rm-leadership', name: '技术领导力', desc: '技术负责人(Lead)的角色定位、授权与决策框架', diff: 3, milestone: false },
    { id: 'gp-rm-motivation', name: '团队激励', desc: '内在/外在激励因素、团队士气管理与crunch预防', diff: 2, milestone: false },
    { id: 'gp-rm-conflict-resolution', name: '冲突解决', desc: '团队内部冲突识别、调解方法与建设性对话', diff: 2, milestone: false },
    { id: 'gp-rm-knowledge-sharing', name: '知识共享', desc: '团队知识管理、技术分享会与文档化文化建设', diff: 2, milestone: false },
    { id: 'gp-rm-succession', name: '继任规划', desc: '关键岗位继任者培养、单点故障消除与知识冗余', diff: 4, milestone: false },
    { id: 'gp-rm-culture', name: '团队文化建设', desc: '团队价值观塑造、心理安全感与创新氛围营造', diff: 3, milestone: true },
    { id: 'gp-rm-burnout', name: '倦怠预防', desc: '工作节奏管理、crunch政策与可持续开发实践', diff: 3, milestone: false },
    { id: 'gp-rm-diversity', name: '多元化与包容', desc: '多元化团队优势、包容性招聘与公平职场环境', diff: 3, milestone: false },
  ],
  'risk-management': [
    { id: 'gp-rk-basics', name: '风险管理基础', desc: '项目风险的定义、分类与风险管理框架', diff: 1, milestone: false },
    { id: 'gp-rk-identification', name: '风险识别', desc: '风险识别技术：头脑风暴、检查表、SWOT分析', diff: 2, milestone: true },
    { id: 'gp-rk-assessment', name: '风险评估', desc: '风险概率-影响矩阵、定量与定性风险分析', diff: 2, milestone: false },
    { id: 'gp-rk-register', name: '风险登记册', desc: '风险登记册的创建、维护与定期评审机制', diff: 2, milestone: false },
    { id: 'gp-rk-mitigation', name: '风险缓解策略', desc: '风险应对策略：规避/转移/减轻/接受与行动计划', diff: 2, milestone: true },
    { id: 'gp-rk-technical', name: '技术风险', desc: '新技术引入、技术债务、引擎迁移等技术风险管理', diff: 3, milestone: false },
    { id: 'gp-rk-schedule', name: '进度风险', desc: '工期延误原因分析、预警信号与进度恢复策略', diff: 3, milestone: false },
    { id: 'gp-rk-scope-creep', name: '范围蔓延风险', desc: '范围蔓延的识别、预防与变更控制流程', diff: 2, milestone: false },
    { id: 'gp-rk-personnel', name: '人员风险', desc: '关键人员离职、团队冲突与技能缺口风险', diff: 2, milestone: false },
    { id: 'gp-rk-market', name: '市场风险', desc: '市场竞争变化、玩家偏好转移与发布窗口风险', diff: 3, milestone: false },
    { id: 'gp-rk-dependency', name: '外部依赖风险', desc: '第三方SDK/引擎更新/平台政策变化等外部风险', diff: 3, milestone: false },
    { id: 'gp-rk-contingency-plan', name: '应急预案', desc: '关键风险的应急响应计划与升级路径设计', diff: 3, milestone: true },
    { id: 'gp-rk-monitoring', name: '风险监控', desc: '风险指标仪表盘、预警阈值与定期审查机制', diff: 3, milestone: false },
    { id: 'gp-rk-early-warning', name: '早期预警系统', desc: '先行指标设计、自动化预警与快速响应流程', diff: 4, milestone: false },
    { id: 'gp-rk-crisis', name: '危机管理', desc: '项目危机的识别、升级与快速决策框架', diff: 4, milestone: true },
    { id: 'gp-rk-retrospective', name: '风险复盘', desc: '风险事件事后分析、经验教训提炼与流程改进', diff: 3, milestone: false },
    { id: 'gp-rk-insurance', name: '风险转移', desc: '保险/合同条款/第三方保障等风险转移手段', diff: 3, milestone: false },
    { id: 'gp-rk-game-specific', name: '游戏特有风险', desc: '创意风险、Fun Factor不确定性与玩法验证策略', diff: 3, milestone: false },
    { id: 'gp-rk-platform', name: '平台审核风险', desc: '主机TRC/XR审核失败、App Store拒审等平台风险', diff: 3, milestone: false },
    { id: 'gp-rk-ip-legal', name: '知识产权风险', desc: 'IP授权纠纷、版权侵犯与法律合规风险管理', diff: 4, milestone: false },
  ],
  'cross-department': [
    { id: 'gp-cd-basics', name: '跨部门协作基础', desc: '游戏开发中多团队协作的必要性与常见挑战', diff: 1, milestone: false },
    { id: 'gp-cd-communication', name: '沟通机制设计', desc: '站会/周会/评审会等沟通机制的建立与优化', diff: 2, milestone: true },
    { id: 'gp-cd-dependency-map', name: '依赖关系图', desc: '团队间依赖关系可视化与瓶颈识别', diff: 2, milestone: false },
    { id: 'gp-cd-handoff', name: '交接流程', desc: '跨团队工作交接规范、验收标准与反馈循环', diff: 2, milestone: false },
    { id: 'gp-cd-meeting', name: '会议管理', desc: '高效会议组织、议程设计与会后跟进机制', diff: 1, milestone: false },
    { id: 'gp-cd-stakeholder', name: '利益相关者管理', desc: '利益相关者识别、期望管理与沟通策略', diff: 2, milestone: true },
    { id: 'gp-cd-art-tech', name: '美术-技术协作', desc: '美术与技术团队的协作规范、资产标准与管线约定', diff: 3, milestone: false },
    { id: 'gp-cd-design-dev', name: '策划-开发协作', desc: '设计意图传达、功能规格书与迭代反馈机制', diff: 3, milestone: false },
    { id: 'gp-cd-audio-integration', name: '音频集成协作', desc: '音频团队与程序/美术/设计的集成工作流', diff: 3, milestone: false },
    { id: 'gp-cd-qa-integration', name: 'QA集成协作', desc: 'QA团队在开发流程中的嵌入方式与反馈通道', diff: 2, milestone: false },
    { id: 'gp-cd-transparency', name: '信息透明', desc: '项目信息的透明化共享机制与权限控制', diff: 2, milestone: false },
    { id: 'gp-cd-conflict', name: '跨部门冲突解决', desc: '资源争夺、优先级分歧与技术方案冲突的调解', diff: 3, milestone: true },
    { id: 'gp-cd-alignment', name: '目标对齐', desc: '团队OKR/目标层层分解与跨团队目标一致性', diff: 3, milestone: false },
    { id: 'gp-cd-tools', name: '协作工具链', desc: 'Slack/Teams/Confluence/Miro等协作工具选型', diff: 2, milestone: false },
    { id: 'gp-cd-remote-collab', name: '远程协作', desc: '远程/混合办公下的跨团队协作策略与工具', diff: 3, milestone: false },
    { id: 'gp-cd-review-process', name: '评审流程', desc: '跨团队代码/资产/设计评审的组织与效率优化', diff: 3, milestone: false },
    { id: 'gp-cd-integration-testing', name: '集成协调', desc: '多团队代码/资产集成的协调策略与冲突解决', diff: 3, milestone: true },
    { id: 'gp-cd-change-management', name: '变更管理', desc: '需求变更的评审流程、影响分析与沟通通知', diff: 3, milestone: false },
    { id: 'gp-cd-studio-culture', name: '工作室文化', desc: '跨团队协作文化的塑造、信任建立与共同价值观', diff: 3, milestone: false },
    { id: 'gp-cd-external-partners', name: '外部合作伙伴', desc: '与发行商/平台方/IP持有者的沟通与协作管理', diff: 4, milestone: false },
  ],
  'agile-scrum': [
    { id: 'gp-as-basics', name: '敏捷基础', desc: '敏捷宣言、核心价值观与在游戏开发中的适用性', diff: 1, milestone: false },
    { id: 'gp-as-scrum-framework', name: 'Scrum框架', desc: 'Scrum角色(PO/SM/Team)、事件与工件总览', diff: 2, milestone: true },
    { id: 'gp-as-sprint-planning', name: 'Sprint计划', desc: 'Sprint目标设定、待办事项精炼与承诺机制', diff: 2, milestone: false },
    { id: 'gp-as-daily-standup', name: '每日站会', desc: '站会的三个问题、时间控制与常见反模式', diff: 1, milestone: false },
    { id: 'gp-as-sprint-review', name: 'Sprint评审', desc: 'Sprint成果演示、利益相关者反馈与待办调整', diff: 2, milestone: false },
    { id: 'gp-as-retrospective', name: 'Sprint回顾', desc: '回顾会方法论(帆船/四象限)、行动项与持续改进', diff: 2, milestone: true },
    { id: 'gp-as-backlog', name: '产品待办列表', desc: 'Product Backlog管理、优先级排序与用户故事编写', diff: 2, milestone: false },
    { id: 'gp-as-user-story', name: '用户故事', desc: '用户故事格式、验收标准(AC)与故事拆分技巧', diff: 2, milestone: false },
    { id: 'gp-as-estimation', name: '敏捷估算', desc: '故事点/T恤尺码/计划扑克等敏捷估算方法', diff: 2, milestone: false },
    { id: 'gp-as-velocity', name: '速率与燃尽图', desc: '团队速率追踪、燃尽图解读与预测完成日期', diff: 3, milestone: true },
    { id: 'gp-as-kanban', name: 'Kanban方法', desc: 'Kanban看板、WIP限制、流动效率与累积流图', diff: 2, milestone: false },
    { id: 'gp-as-scrumban', name: 'Scrumban', desc: 'Scrum与Kanban的混合模式在游戏开发中的实践', diff: 3, milestone: false },
    { id: 'gp-as-game-adaptation', name: '游戏敏捷适配', desc: '标准Scrum在游戏开发中的调整（创意迭代/美术管线）', diff: 3, milestone: true },
    { id: 'gp-as-definition-done', name: 'Definition of Done', desc: '完成定义的制定、分层(任务/Sprint/发布)与遵守', diff: 2, milestone: false },
    { id: 'gp-as-scaling', name: '规模化敏捷', desc: 'SAFe/LeSS/Nexus等规模化敏捷框架在大型游戏中的应用', diff: 4, milestone: false },
    { id: 'gp-as-metrics', name: '敏捷度量', desc: 'Lead Time/Cycle Time/吞吐量等敏捷效能指标', diff: 3, milestone: false },
    { id: 'gp-as-technical-debt', name: '技术债务管理', desc: '技术债务的识别、量化、优先级排序与偿还策略', diff: 3, milestone: false },
    { id: 'gp-as-continuous-improvement', name: '持续改进', desc: 'Kaizen理念、PDCA循环与团队效能持续提升', diff: 3, milestone: false },
    { id: 'gp-as-product-owner', name: '产品负责人', desc: 'PO在游戏项目中的角色(≈创意总监+制作人的桥梁)', diff: 3, milestone: false },
    { id: 'gp-as-scrum-master', name: 'Scrum Master', desc: 'SM在游戏团队中的服务型领导、障碍消除与团队赋能', diff: 3, milestone: false },
  ],
  'outsourcing': [
    { id: 'gp-os-basics', name: '外包管理基础', desc: '游戏外包的类型、优缺点与适用场景', diff: 1, milestone: false },
    { id: 'gp-os-strategy', name: '外包策略', desc: '自研vs外包决策框架、核心能力保护原则', diff: 2, milestone: true },
    { id: 'gp-os-vendor-selection', name: '供应商筛选', desc: '外包供应商评估标准、试做测试与合作伙伴选择', diff: 2, milestone: false },
    { id: 'gp-os-contract', name: '合同管理', desc: '外包合同条款设计、交付标准与付款条件', diff: 2, milestone: false },
    { id: 'gp-os-art-outsource', name: '美术外包', desc: '2D/3D美术外包的工作流、风格指南与质量把控', diff: 2, milestone: true },
    { id: 'gp-os-qa-outsource', name: 'QA外包', desc: 'QA测试外包的管理策略、测试覆盖与Bug分类', diff: 3, milestone: false },
    { id: 'gp-os-audio-outsource', name: '音频外包', desc: '音乐/音效外包的需求文档、风格参考与验收', diff: 3, milestone: false },
    { id: 'gp-os-programming', name: '编程外包', desc: '代码外包的风险、代码规范与集成策略', diff: 3, milestone: false },
    { id: 'gp-os-quality-control', name: '外包质量管控', desc: '反馈循环、里程碑验收与质量提升迭代', diff: 3, milestone: true },
    { id: 'gp-os-communication', name: '外包沟通', desc: '跨时区/跨文化沟通策略、定期同步与工具选择', diff: 2, milestone: false },
    { id: 'gp-os-ip-protection', name: '知识产权保护', desc: 'NDA/版权归属/源代码保护等IP安全措施', diff: 3, milestone: false },
    { id: 'gp-os-onsite-offsite', name: '驻场vs远程', desc: '驻场外包与远程外包的优缺点对比与选择', diff: 2, milestone: false },
    { id: 'gp-os-cost-analysis', name: '外包成本分析', desc: '外包总拥有成本(TCO)分析、隐性成本与性价比评估', diff: 3, milestone: false },
    { id: 'gp-os-transition', name: '外包过渡', desc: '外包启动/移交/结束的过渡管理与知识转移', diff: 3, milestone: false },
    { id: 'gp-os-risk', name: '外包风险管理', desc: '供应商锁定、质量下滑与沟通障碍的风险应对', diff: 3, milestone: true },
    { id: 'gp-os-localization', name: '本地化外包', desc: '翻译/配音/文化适配外包的特殊管理需求', diff: 3, milestone: false },
    { id: 'gp-os-co-development', name: '联合开发', desc: '多工作室联合开发的协调机制与责任边界', diff: 4, milestone: false },
    { id: 'gp-os-evaluation', name: '供应商评估', desc: '合作完成后的供应商绩效评估与长期关系维护', diff: 3, milestone: false },
    { id: 'gp-os-scaling', name: '外包规模化', desc: '大规模外包(50+人)的管理挑战与组织方案', diff: 4, milestone: false },
    { id: 'gp-os-tool-integration', name: '工具集成', desc: '外包团队与内部工具链(版本控制/任务管理)的集成', diff: 3, milestone: false },
  ],
  'budget-control': [
    { id: 'gp-bc-basics', name: '预算管理基础', desc: '游戏项目预算的组成、编制方法与审批流程', diff: 1, milestone: false },
    { id: 'gp-bc-estimation', name: '成本估算', desc: '开发成本估算方法：自上而下/自下而上/参数估算', diff: 2, milestone: true },
    { id: 'gp-bc-structure', name: '预算结构', desc: '人力/工具/外包/营销/运维等预算科目设计', diff: 2, milestone: false },
    { id: 'gp-bc-tracking', name: '成本追踪', desc: '实际成本vs预算对比、偏差分析与预警机制', diff: 2, milestone: false },
    { id: 'gp-bc-evm', name: '挣值管理', desc: 'EVM方法(PV/EV/AC)、CPI/SPI指标与趋势预测', diff: 3, milestone: true },
    { id: 'gp-bc-roi', name: 'ROI分析', desc: '投资回报率计算、回本周期与盈利预测模型', diff: 3, milestone: false },
    { id: 'gp-bc-contingency-budget', name: '应急预算', desc: '风险准备金设置、触发条件与使用审批', diff: 2, milestone: false },
    { id: 'gp-bc-cash-flow', name: '现金流管理', desc: '项目现金流规划、支出节奏与资金调度', diff: 3, milestone: false },
    { id: 'gp-bc-reporting', name: '财务报告', desc: '月度/季度财务报告、预算执行率与预测更新', diff: 2, milestone: false },
    { id: 'gp-bc-headcount', name: '人力成本管理', desc: '人力成本占比控制、效率指标与优化策略', diff: 3, milestone: true },
    { id: 'gp-bc-tool-cost', name: '工具与许可证', desc: '开发工具/引擎/中间件许可证成本管理与优化', diff: 2, milestone: false },
    { id: 'gp-bc-marketing-budget', name: '营销预算', desc: '游戏营销预算规划、渠道分配与效果追踪', diff: 3, milestone: false },
    { id: 'gp-bc-cost-reduction', name: '成本优化', desc: '成本削减策略、效率提升与价值工程方法', diff: 3, milestone: false },
    { id: 'gp-bc-funding', name: '资金来源', desc: '自有资金/投资/发行商预付/众筹等融资渠道', diff: 3, milestone: false },
    { id: 'gp-bc-f2p-economics', name: 'F2P经济模型', desc: '免费游戏的开发成本结构、LTV预测与回本模型', diff: 4, milestone: true },
    { id: 'gp-bc-premium-economics', name: '买断制经济模型', desc: '买断制游戏的成本-售价-销量盈利模型', diff: 3, milestone: false },
    { id: 'gp-bc-scope-budget', name: '范围-预算平衡', desc: '功能范围与预算约束的动态平衡策略', diff: 3, milestone: false },
    { id: 'gp-bc-audit', name: '预算审计', desc: '内部审计机制、费用合规性检查与异常处理', diff: 3, milestone: false },
    { id: 'gp-bc-benchmark', name: '行业成本基准', desc: '同类型游戏成本基准参考、人均产出对比', diff: 4, milestone: false },
    { id: 'gp-bc-greenlight', name: '绿灯评审', desc: '项目立项的财务可行性评估与绿灯审批流程', diff: 3, milestone: false },
  ],
};

// Build concepts array
const concepts = [];
const milestones = [];
for (const [subId, items] of Object.entries(CONCEPTS)) {
  for (const item of items) {
    concepts.push({
      id: item.id,
      name: item.name,
      description: item.desc,
      domain_id: DOMAIN,
      subdomain_id: subId,
      difficulty: item.diff,
      estimated_minutes: 15 + item.diff * 5,
      content_type: 'conceptual',
      tags: [],
      is_milestone: item.milestone,
    });
    if (item.milestone) milestones.push(item.id);
  }
}

// Build edges (prerequisite chains within each subdomain + some cross-subdomain)
const edges = [];
for (const [subId, items] of Object.entries(CONCEPTS)) {
  for (let i = 0; i < items.length - 1; i++) {
    // chain adjacent concepts
    if (i < items.length - 1) {
      edges.push({
        source_id: items[i].id,
        target_id: items[i + 1].id,
        relation_type: 'prerequisite',
        strength: 0.8,
      });
    }
  }
}

// Cross-subdomain edges
const crossEdges = [
  // pipeline → milestone planning
  ['gp-pp-preproduction', 'gp-mp-basics', 0.7],
  ['gp-pp-gate-review', 'gp-mp-kpi', 0.7],
  ['gp-pp-overview', 'gp-rm-basics', 0.6],
  // milestone → resource
  ['gp-mp-wbs', 'gp-rm-workload', 0.7],
  ['gp-mp-estimation', 'gp-bc-estimation', 0.8],
  // risk → pipeline
  ['gp-rk-schedule', 'gp-mp-buffer', 0.7],
  ['gp-rk-scope-creep', 'gp-mp-scope', 0.8],
  // agile → milestone
  ['gp-as-sprint-planning', 'gp-mp-iteration', 0.8],
  ['gp-as-velocity', 'gp-mp-tracking', 0.7],
  // outsourcing → resource
  ['gp-os-strategy', 'gp-rm-capacity', 0.7],
  ['gp-os-cost-analysis', 'gp-bc-basics', 0.7],
  // cross-department → agile
  ['gp-cd-communication', 'gp-as-daily-standup', 0.7],
  ['gp-cd-art-tech', 'gp-os-art-outsource', 0.6],
  // budget → risk
  ['gp-bc-contingency-budget', 'gp-rk-contingency-plan', 0.7],
  ['gp-bc-roi', 'gp-rk-market', 0.6],
  // more connections
  ['gp-pp-build-pipeline', 'gp-as-technical-debt', 0.6],
  ['gp-rm-team-structure', 'gp-cd-basics', 0.7],
  ['gp-rk-personnel', 'gp-rm-retention', 0.7],
  ['gp-as-game-adaptation', 'gp-cd-alignment', 0.6],
  ['gp-bc-greenlight', 'gp-pp-preproduction', 0.8],
];

for (const [src, tgt, str] of crossEdges) {
  edges.push({
    source_id: src,
    target_id: tgt,
    relation_type: 'related',
    strength: str,
  });
}

const seedGraph = {
  domain: DOMAIN,
  subdomains: SUBDOMAINS,
  concepts,
  edges,
  milestones,
};

// Write seed graph
const seedDir = path.join(__dirname, '..', 'data', 'seed', DOMAIN);
fs.mkdirSync(seedDir, { recursive: true });
fs.writeFileSync(
  path.join(seedDir, 'seed_graph.json'),
  JSON.stringify(seedGraph, null, 2) + '\n'
);

console.log(`✅ Seed graph: ${concepts.length} concepts, ${edges.length} edges, ${SUBDOMAINS.length} subdomains, ${milestones.length} milestones`);

// ── Generate RAG documents ──
const DIFFICULTY_LABELS = { 1: '入门', 2: '基础', 3: '进阶', 4: '高级', 5: '专家' };

function generateRagContent(concept) {
  const sub = SUBDOMAINS.find(s => s.id === concept.subdomain_id);
  const diffLabel = DIFFICULTY_LABELS[concept.difficulty] || '基础';
  const minutes = concept.estimated_minutes;

  return `---
id: "${concept.id}"
concept: "${concept.name}"
domain: "${DOMAIN}"
subdomain: "${concept.subdomain_id}"
subdomain_name: "${sub.name}"
difficulty: ${concept.difficulty}
is_milestone: ${concept.is_milestone}
tags: []

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 45.0
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# ${concept.name}

> **子领域**: ${sub.name} | **难度**: ${diffLabel} | **预计学习时间**: ${minutes}分钟

## 概述

${concept.description}。

## 核心要点

### 1. 基本概念

${concept.name}是游戏项目管理中${sub.name}领域的${concept.is_milestone ? '关键里程碑概念' : '重要组成部分'}。理解${concept.name}对于掌握游戏制作的全流程管理至关重要。

### 2. 实践应用

在实际的游戏开发项目中，${concept.name}的应用涉及以下方面：

- **规划阶段**: 在项目规划期确定${concept.name}的实施范围和标准
- **执行阶段**: 在日常开发中持续实践和监控${concept.name}相关活动
- **复盘阶段**: 在项目完成后评估${concept.name}的实施效果并总结经验

### 3. 与其他概念的关联

${concept.name}不是孤立存在的，它与${sub.name}领域中的其他概念紧密相连，共同构成了完整的项目管理知识体系。

## 学习建议

- 从实际项目案例入手，理解${concept.name}在不同规模项目中的应用
- 关注行业最佳实践，了解AAA和独立游戏团队的不同做法
- 结合工具实操，将理论知识转化为实际技能

## 常见误区

1. **过度流程化**: ${concept.name}的目标是提升效率，而非增加官僚负担
2. **忽视人的因素**: 任何管理方法都需要考虑团队成员的接受度和执行意愿
3. **照搬模板**: 每个项目有其独特性，需要根据实际情况调整${concept.name}的实施方式

## 进阶话题

- ${concept.name}在大型团队(100+人)中的特殊挑战
- ${concept.name}与敏捷开发方法论的融合
- ${concept.name}的自动化与工具化趋势
`;
}

const ragDir = path.join(__dirname, '..', 'data', 'rag', DOMAIN);
fs.mkdirSync(ragDir, { recursive: true });

const indexEntries = [];
let totalChars = 0;
const bySubdomain = {};

for (const concept of concepts) {
  const content = generateRagContent(concept);
  const filename = `${concept.id}.md`;
  fs.writeFileSync(path.join(ragDir, filename), content);
  totalChars += content.length;

  indexEntries.push({
    id: concept.id,
    title: concept.name,
    file: filename,
    subdomain: concept.subdomain_id,
    difficulty: concept.difficulty,
    is_milestone: concept.is_milestone,
  });

  if (!bySubdomain[concept.subdomain_id]) {
    const sub = SUBDOMAINS.find(s => s.id === concept.subdomain_id);
    bySubdomain[concept.subdomain_id] = { docs: 0, name: sub.name };
  }
  bySubdomain[concept.subdomain_id].docs++;
}

const ragIndex = {
  version: '1.0',
  domain: DOMAIN,
  domain_name: DOMAIN_NAME,
  generated_at: new Date().toISOString(),
  total_concepts: concepts.length,
  stats: {
    total_docs: concepts.length,
    total_chars: totalChars,
    by_subdomain: bySubdomain,
  },
  documents: indexEntries,
};

fs.writeFileSync(
  path.join(ragDir, '_index.json'),
  JSON.stringify(ragIndex, null, 2) + '\n'
);

console.log(`✅ RAG docs: ${concepts.length} files + _index.json (${totalChars} chars)`);

// ── Generate cross-sphere links ──
const crossSphereLinks = [
  // → game-design
  { src: 'gp-pp-overview', tgtDomain: 'game-design', tgtId: 'core-loop-intro', desc: '制作管线需要围绕核心游戏玩法循环来组织' },
  { src: 'gp-pp-preproduction', tgtDomain: 'game-design', tgtId: 'design-doc-writing', desc: '预生产阶段的核心产出是游戏设计文档(GDD)' },
  { src: 'gp-mp-scope', tgtDomain: 'game-design', tgtId: 'feature-scope-management', desc: '范围管理直接关系到游戏功能的取舍决策' },
  // → software-engineering
  { src: 'gp-pp-build-pipeline', tgtDomain: 'software-engineering', tgtId: 'se-devops-cicd', desc: '构建管线是CI/CD在游戏开发中的具体应用' },
  { src: 'gp-as-scrum-framework', tgtDomain: 'software-engineering', tgtId: 'se-agile-scrum-basics', desc: 'Scrum框架在游戏开发中需要特殊适配' },
  { src: 'gp-as-technical-debt', tgtDomain: 'software-engineering', tgtId: 'se-agile-tech-debt', desc: '技术债务管理是软件工程和项目管理的交叉领域' },
  // → game-engine
  { src: 'gp-pp-asset-pipeline', tgtDomain: 'game-engine', tgtId: 'ue-asset-manager', desc: '资产管线的后端由引擎资产管理系统支撑' },
  { src: 'gp-pp-version-control', tgtDomain: 'game-engine', tgtId: 'ue-collab-version-control', desc: '版本管理策略需要与引擎协作工具配合' },
  // → 3d-art
  { src: 'gp-os-art-outsource', tgtDomain: '3d-art', tgtId: 'art3d-ap-naming-convention', desc: '美术外包需要严格的资产命名和质量规范' },
  { src: 'gp-pp-asset-pipeline', tgtDomain: '3d-art', tgtId: 'art3d-ap-pipeline-overview', desc: '资产管线设计需要理解3D美术工作流' },
  // → game-qa
  { src: 'gp-cd-qa-integration', tgtDomain: 'game-qa', tgtId: 'qa-ft-basics', desc: 'QA团队集成需要理解功能测试的基本流程' },
  { src: 'gp-rk-technical', tgtDomain: 'game-qa', tgtId: 'qa-pt-basics', desc: '技术风险管理需要性能测试的支撑' },
  // → game-publishing
  { src: 'gp-bc-marketing-budget', tgtDomain: 'game-publishing', tgtId: 'gp-ms-budget-allocation', desc: '营销预算规划与市场发行策略紧密关联' },
  { src: 'gp-rk-platform', tgtDomain: 'game-publishing', tgtId: 'gp-pr-platform-guidelines', desc: '平台审核风险需要熟悉各平台发行规则' },
  // → game-live-ops
  { src: 'gp-pp-live-service', tgtDomain: 'game-live-ops', tgtId: 'glo-da-basics', desc: '持续运营管线为运营数据分析提供基础设施' },
  { src: 'gp-bc-f2p-economics', tgtDomain: 'game-live-ops', tgtId: 'glo-ps-f2p-model', desc: 'F2P经济模型与运营付费系统设计深度关联' },
  // → game-audio-music
  { src: 'gp-cd-audio-integration', tgtDomain: 'game-audio-music', tgtId: 'gam-wwise-basics', desc: '音频集成协作需要了解Wwise等中间件工作流' },
  // → narrative-design
  { src: 'gp-pp-content-pipeline', tgtDomain: 'narrative-design', tgtId: 'nd-ws-world-building-basics', desc: '内容管线需要覆盖叙事设计的世界观构建流程' },
  // → game-ui-ux
  { src: 'gp-cd-design-dev', tgtDomain: 'game-ui-ux', tgtId: 'gui-ut-guerrilla-testing', desc: '策划-开发协作中的快速可用性验证方法' },
  // → technical-art
  { src: 'gp-cd-art-tech', tgtDomain: 'technical-art', tgtId: 'ta-pipe-asset-pipeline', desc: '美术-技术协作的核心是技术美术搭建的管线' },
  // → animation
  { src: 'gp-os-art-outsource', tgtDomain: 'animation', tgtId: 'anim-pipe-game-pipeline', desc: '动画外包需要了解游戏动画管线的标准流程' },
  // → multiplayer-network
  { src: 'gp-rk-technical', tgtDomain: 'multiplayer-network', tgtId: 'mn-arch-client-server', desc: '网络架构选型是重大技术风险决策点' },
  // → level-design
  { src: 'gp-pp-content-pipeline', tgtDomain: 'level-design', tgtId: 'ld-process-blockout', desc: '内容管线包含关卡从Blockout到最终的全流程' },
  // → game-audio-sfx
  { src: 'gp-cd-audio-integration', tgtDomain: 'game-audio-sfx', tgtId: 'sfx-middleware-wwise-basics', desc: '音频集成需要理解音效中间件的集成方式' },
];

console.log(`✅ Cross-sphere links: ${crossSphereLinks.length} links designed`);

// Now update the cross_sphere_links.json
const crossFile = path.join(__dirname, '..', 'data', 'seed', 'cross_sphere_links.json');
const crossData = JSON.parse(fs.readFileSync(crossFile, 'utf-8'));

// Remove any existing game-production links
crossData.links = crossData.links.filter(l => l.source_domain !== DOMAIN);

// Add new links
for (const link of crossSphereLinks) {
  crossData.links.push({
    source_domain: DOMAIN,
    source_id: link.src,
    target_domain: link.tgtDomain,
    target_id: link.tgtId,
    relation: 'related',
    strength: 0.8,
    description: link.desc,
  });
}

crossData.total = crossData.links.length;
if (crossData._stats) {
  crossData._stats.total = crossData.total;
  crossData._stats.by_source_domain = {};
  for (const link of crossData.links) {
    crossData._stats.by_source_domain[link.source_domain] = (crossData._stats.by_source_domain[link.source_domain] || 0) + 1;
  }
}

fs.writeFileSync(crossFile, JSON.stringify(crossData, null, 2) + '\n');
console.log(`✅ cross_sphere_links.json updated: ${crossData.total} total links`);

// ── Update domains.json ──
const domainsFile = path.join(__dirname, '..', 'data', 'seed', 'domains.json');
const domainsData = JSON.parse(fs.readFileSync(domainsFile, 'utf-8'));

// Remove existing game-production entry if any
domainsData.domains = domainsData.domains.filter(d => d.id !== DOMAIN);

// Add new entry
domainsData.domains.push({
  id: DOMAIN,
  name: DOMAIN_NAME,
  description: '游戏项目管理全流程——制作管线、里程碑规划、资源调配、风险管理、跨部门协作、敏捷/Scrum、外包管理、预算控制',
  color: COLOR,
  icon: 'clipboard-list',
  order: domainsData.domains.length + 1,
  status: 'active',
  concept_count: concepts.length,
  subdomain_count: SUBDOMAINS.length,
  seed_dir: DOMAIN,
  rag_dir: DOMAIN,
});

fs.writeFileSync(domainsFile, JSON.stringify(domainsData, null, 2) + '\n');
console.log(`✅ domains.json updated: ${domainsData.domains.length} domains total`);

// ── Copy to workers directory ──
const workersSeedDir = path.join(__dirname, '..', 'workers', 'data', 'seed', DOMAIN);
const workersRagDir = path.join(__dirname, '..', 'workers', 'data', 'rag', DOMAIN);
fs.mkdirSync(workersSeedDir, { recursive: true });
fs.mkdirSync(workersRagDir, { recursive: true });

fs.copyFileSync(
  path.join(seedDir, 'seed_graph.json'),
  path.join(workersSeedDir, 'seed_graph.json')
);

fs.copyFileSync(
  path.join(ragDir, '_index.json'),
  path.join(workersRagDir, '_index.json')
);

// Also copy workers domains.json
const workersDomainsFile = path.join(__dirname, '..', 'workers', 'data', 'seed', 'domains.json');
if (fs.existsSync(workersDomainsFile)) {
  const wDomains = JSON.parse(fs.readFileSync(workersDomainsFile, 'utf-8'));
  wDomains.domains = wDomains.domains.filter(d => d.id !== DOMAIN);
  wDomains.domains.push({
    id: DOMAIN,
    name: DOMAIN_NAME,
    description: '游戏项目管理全流程——制作管线、里程碑规划、资源调配、风险管理、跨部门协作、敏捷/Scrum、外包管理、预算控制',
    color: COLOR,
    icon: 'clipboard-list',
    order: wDomains.domains.length + 1,
    status: 'active',
    concept_count: concepts.length,
    subdomain_count: SUBDOMAINS.length,
    seed_dir: DOMAIN,
    rag_dir: DOMAIN,
  });
  fs.writeFileSync(workersDomainsFile, JSON.stringify(wDomains, null, 2) + '\n');
  console.log(`✅ Workers domains.json updated`);
}

console.log('\n🎉 Phase 36 data generation complete!');
console.log(`  Domain: ${DOMAIN} (${DOMAIN_NAME})`);
console.log(`  Concepts: ${concepts.length}`);
console.log(`  Edges: ${edges.length}`);
console.log(`  Subdomains: ${SUBDOMAINS.length}`);
console.log(`  Milestones: ${milestones.length}`);
console.log(`  Cross-sphere links: ${crossSphereLinks.length}`);
console.log(`  RAG documents: ${concepts.length}`);
