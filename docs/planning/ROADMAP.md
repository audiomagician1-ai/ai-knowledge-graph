# AI知识图谱 — 后续推进计划

> **版本**: v1.0
> **日期**: 2026-03-16
> **状态**: Phase 4 完成 (3轮审查65项修复) + Phase 5 进行中 (Supabase跨端同步代码已提交)
> **最新Commit**: `1a91280` — Supabase cross-device sync + auth flow improvements
> **最新EXE**: `akg-v0.1.0-c11ac37` (46.6MB, 含3轮审查修复)

---

## 一、项目现状盘点

### 1.1 已完成里程碑

| Phase | 周次 | 目标 | 状态 | 关键产出 |
|:---|:---|:---|:---|:---|
| **Phase 0** | W1-2 | 基础设施 + 种子图谱 | ✅ | Monorepo骨架, Neo4j/Redis/Supabase, CI/CD |
| **Phase 1** | W3-4 | 图谱展示 + 基础交互 | ✅ | 267节点334边, 3D球面力导向图, 里程碑高亮 |
| **Phase 2** | W5-7 | 对话引擎 (核心) | ✅ | V2引导式学习, SSE流式, RAG, 评估器 |
| **Phase 3** | W8-9 | 节点点亮 + 进度系统 | ✅ | 前置条件图, mastered绿光, Dashboard |
| **Phase 4** | W10-12 | 打磨 + 内测 | ✅ | 3轮审查65项修复, EXE打包, UI改版 |
| **Phase 5** | W13+ | 可选登录 + 跨端同步 | 🟡 | 代码完成(10/12步), 待配置+测试 |

### 1.2 技术栈现状

- **前端**: React 19 + TS 5.7 + Vite 6 + TailwindCSS 4 + Zustand 5 + Three.js + Framer Motion
- **后端**: FastAPI + Neo4j 5 + SQLite (EXE模式) + Redis 7
- **云服务**: Supabase (Auth+PostgreSQL+RLS) + Cloudflare Pages + D1 Worker
- **移动端**: Capacitor 8 (配置就绪, 未实际构建)
- **LLM**: 分层调度 via OpenRouter (DeepSeek/GPT-4o-mini/GPT-4o), 用户自带Key
- **分发**: PyInstaller EXE (Windows单文件) + Cloudflare Pages (Web)

### 1.3 Phase 5 未完成项

| 步骤 | 内容 | 状态 |
|:---|:---|:---|
| 1-10 | auth/sync/双写/UI/tsc+build | ✅ 代码已提交 |
| 11 | Supabase Cloud 配置 (OAuth providers + .env) | 🟡 待操作 |
| 12 | 端到端测试 (注册→学习→退出→新设备恢复) | 🟡 待执行 |

### 1.4 已知遗留问题

1. **EXE打包未包含Phase 5变更** — 最新EXE是c11ac37(Phase 4), 需含1a91280重新打包
2. **Cloudflare Worker (akg-api)** — D1 SQLite Worker已配置, 但与FastAPI后端的关系需明确
3. **CORS代理依赖** — Direct模式需要本地代理BAT, 用户体验有门槛
4. **Neo4j线上部署未确定** — 目前仅本地Docker, 线上需AuraDB或自托管
5. **测试覆盖不足** — 前端vitest存在但覆盖率不明, 后端pytest同
6. **移动端Capacitor** — 配置就绪但从未实际构建Android/iOS APK

---

## 二、后续推进计划 — 分阶段路线图

### Phase 5 收尾 (1-2天) — 🔴 最高优先

> **目标**: 完成跨端同步的最后配置和验证

| # | 任务 | 预估时间 | 产出 |
|:---|:---|:---|:---|
| 5.1 | **Supabase Cloud 项目创建** — 在 supabase.com 创建线上项目, 运行 migrations/00001 | 30min | 线上DB就绪 |
| 5.2 | **OAuth Provider 配置** — Google/GitHub OAuth 在 Supabase Dashboard 开启, 配置回调URL | 30min | OAuth可用 |
| 5.3 | **环境变量配置** — .env.production 写入 VITE_SUPABASE_URL + VITE_SUPABASE_ANON_KEY | 15min | 前端可连接 |
| 5.4 | **端到端测试** — 邮箱注册→学习3节点→退出→新浏览器登录→验证进度恢复 | 1h | 功能验证 |
| 5.5 | **OAuth 测试** — Google/GitHub 登录→同步→跨端恢复 | 30min | OAuth验证 |
| 5.6 | **EXE 重新打包** — 含 Phase 5 全部变更 (1a91280+), 版本号升至 v0.2.0 | 15min | 新版EXE |
| 5.7 | **CLAUDE.md + Release Note** — 更新项目状态, Phase 5 标记完成 | 15min | 文档同步 |

**验收标准**: 匿名用户仍可完整使用; 登录用户数据自动同步; 跨设备进度恢复正常

---

### Phase 6: 线上部署 + 公测准备 (1-2周) — 🟠 高优先

> **目标**: 将项目从本地EXE模式推进到线上可访问状态, 准备公测

#### 6.1 后端部署方案确定

| 方案 | 优点 | 缺点 | 推荐度 |
|:---|:---|:---|:---|
| **A: Cloudflare Worker + D1** | 免运维, 全球边缘, 已有wrangler配置 | 不支持Neo4j/Redis, 需重写后端逻辑 | ⭐⭐ |
| **B: Docker on Fly.io/Railway** | FastAPI原样部署, 支持Neo4j/Redis连接 | 月费$5-20, 冷启动 | ⭐⭐⭐⭐ |
| **C: 混合模式** — CF Worker做API网关+缓存, 后端Docker处理LLM/图谱 | 兼顾性能和灵活性 | 架构复杂 | ⭐⭐⭐ |
| **D: 纯前端 Direct 模式** — 去后端, 前端直调LLM+Supabase | 零后端成本 | 失去Neo4j图谱查询, 仅用种子JSON | ⭐⭐⭐ |

**推荐**: 短期 **方案D** (纯前端Direct模式优化) → 中期 **方案B** (后端Docker部署)

#### 6.2 短期: 纯前端Direct模式增强 (优先)

| # | 任务 | 预估 | 说明 |
|:---|:---|:---|:---|
| 6.2.1 | **去CORS代理依赖** — Direct模式直接调用OpenRouter (已有CORS), 去掉本地代理需求 | 2h | OpenRouter本身支持CORS |
| 6.2.2 | **图谱数据静态化** — 将seed JSON打包到前端assets, 无需后端图谱API | 1h | 已有JSON fallback机制 |
| 6.2.3 | **学习数据完全走Supabase** — 登录用户不再fire-and-forget SQLite | 2h | 简化数据流 |
| 6.2.4 | **Cloudflare Pages 部署** — 前端SPA部署, 自定义域名 | 1h | 已有deploy workflow |
| 6.2.5 | **EXE模式保留** — 作为离线/免登录备选, 不影响线上版 | 0h | 现有功能不动 |

#### 6.3 中期: 后端Docker部署 (可选)

| # | 任务 | 预估 | 说明 |
|:---|:---|:---|:---|
| 6.3.1 | **Neo4j AuraDB Free** — 创建云端图数据库, 导入种子数据 | 1h | 20万节点免费 |
| 6.3.2 | **Railway/Fly.io 部署** — Docker Compose → 单容器FastAPI | 2h | 含healthcheck |
| 6.3.3 | **Redis Cloud Free** — 创建缓存实例, 配置连接 | 30min | 30MB免费 |
| 6.3.4 | **API域名 + HTTPS** — api.xxx.com 指向后端 | 30min | CF DNS |
| 6.3.5 | **环境切换** — 前端根据环境自动选择 Direct/Backend 模式 | 1h | VITE_API_MODE |

#### 6.4 公测准备

| # | 任务 | 预估 | 说明 |
|:---|:---|:---|:---|
| 6.4.1 | **Landing Page** — 简洁介绍页 + "开始学习"入口 | 2h | Cloudflare Pages |
| 6.4.2 | **用户反馈通道** — GitHub Discussions 或 简单反馈表单 | 30min | 收集意见 |
| 6.4.3 | **错误监控** — Sentry 或 CF Analytics | 1h | 线上问题追踪 |
| 6.4.4 | **使用统计** — 简单的学习行为埋点 (匿名) | 1h | 验证核心假设 |
| 6.4.5 | **公测邀请** — 邀请10-20名目标用户 | 持续 | 收集反馈 |

---

### Phase 7: 内容扩展 + FSRS复习 (2-3周) — 🟡 中优先

> **目标**: 从单一编程领域扩展, 引入间隔复习机制

#### 7.1 多域知识图谱

| # | 任务 | 预估 | 说明 |
|:---|:---|:---|:---|
| 7.1.1 | **图谱扩展工具** — LLM批量生成 + 人工校验管线 | 4h | 复用seed生成脚本 |
| 7.1.2 | **数学领域图谱** — ~200节点 (初等→高等→线代→概率) | 3h | 第二个领域 |
| 7.1.3 | **AI/ML领域图谱深化** — 现有267节点扩展到500+ | 2h | 补充实践节点 |
| 7.1.4 | **图谱质量审核** — 人工检查依赖关系准确性 | 2h | 避免错误引导 |
| 7.1.5 | **域切换UI** — 图谱页顶部域选择器, 支持跨域关联可视化 | 3h | 多域体验 |

#### 7.2 FSRS 间隔复习

| # | 任务 | 预估 | 说明 |
|:---|:---|:---|:---|
| 7.2.1 | **FSRS算法集成** — py-fsrs / ts-fsrs, 每个mastered节点维护FSRS状态 | 4h | ADR-007已决策 |
| 7.2.2 | **复习提醒UI** — Dashboard "今日待复习" + 图谱节点复习标记 | 3h | 黄色渐变表示衰减 |
| 7.2.3 | **复习对话模式** — 简化版对话(快速回顾而非完整费曼) | 2h | 降低复习负担 |
| 7.2.4 | **复习数据持久化** — FSRS参数同步到Supabase (stability/difficulty/due_date) | 2h | 跨端复习 |
| 7.2.5 | **衰减可视化** — mastered节点随时间渐暗, 复习后重新亮起 | 2h | 视觉激励 |

---

### Phase 8: 移动端 + 体验优化 (2-3周) — 🟡 中优先

> **目标**: 移动端原生体验 + 核心交互优化

#### 8.1 移动端构建

| # | 任务 | 预估 | 说明 |
|:---|:---|:---|:---|
| 8.1.1 | **Capacitor Android 构建** — 实际生成APK, 解决native依赖 | 4h | 配置已就绪 |
| 8.1.2 | **移动端UI适配** — 图谱触控手势 (pinch zoom / drag), 对话键盘适配 | 4h | 需真机测试 |
| 8.1.3 | **PWA 支持** — Service Worker + manifest.json, 离线缓存图谱数据 | 3h | 无需安装 |
| 8.1.4 | **推送通知** — 复习提醒 (Capacitor Push Notifications) | 2h | 仅Android/iOS |
| 8.1.5 | **APK 分发** — GitHub Releases + MuseSea Landing 下载页 | 1h | 已有分发模板 |

#### 8.2 核心体验优化

| # | 任务 | 预估 | 说明 |
|:---|:---|:---|:---|
| 8.2.1 | **对话体验升级** — 更自然的苏格拉底追问, 避免重复问法 | 3h | Prompt工程迭代 |
| 8.2.2 | **图谱导航优化** — 学习路径推荐高亮, "下一步学什么"引导 | 3h | 降低选择困难 |
| 8.2.3 | **成就系统** — 首次对话/连续学习/域完成等成就 + 徽章 | 4h | 游戏化激励 |
| 8.2.4 | **键盘快捷键** — 图谱导航(方向键) + 对话(Enter发送) | 1h | 桌面效率 |
| 8.2.5 | **无障碍(a11y)** — 键盘导航 + aria标签 + 屏幕阅读器 | 2h | 基础无障碍 |

---

### Phase 9: 社交 + 高级功能 (3-4周) — 🟢 低优先

> **目标**: 构建社区特性和高级学习功能

#### 9.1 社交学习

| # | 任务 | 预估 | 说明 |
|:---|:---|:---|:---|
| 9.1.1 | **学习档案公开页** — 用户学习图谱可分享 (可选公开) | 4h | 社交传播 |
| 9.1.2 | **排行榜** — 周/月学习排行 (节点数/连续天数) | 3h | 竞争激励 |
| 9.1.3 | **学习小组** — 创建/加入小组, 组内进度对比 | 6h | 团队学习 |
| 9.1.4 | **评论/讨论** — 节点维度的学习讨论区 | 4h | UGC内容 |

#### 9.2 高级学习功能

| # | 任务 | 预估 | 说明 |
|:---|:---|:---|:---|
| 9.2.1 | **语音费曼模式** — Web Speech API / Whisper, 说出来而非打字 | 6h | 更接近真实费曼 |
| 9.2.2 | **多模态解释** — AI生成图解/代码示例/动画 | 8h | 多感官学习 |
| 9.2.3 | **自定义图谱** — 用户上传笔记/文档, AI自动构建私有知识图谱 | 10h | Obsidian导入 |
| 9.2.4 | **学习数据分析** — 详细的学习行为分析Dashboard (强弱项/时间分布) | 4h | 数据驱动 |
| 9.2.5 | **BKT知识追踪** — 贝叶斯知识追踪模型, 更精准的掌握度预测 | 6h | 算法升级 |

---

### Phase 10: 商业化 + 规模化 (长期) — 📋 规划中

| # | 方向 | 说明 |
|:---|:---|:---|
| 10.1 | **Freemium 模式** | 免费: 基础对话+图谱浏览; Pro: 无限对话+FSRS+高级LLM+导出 |
| 10.2 | **多语言支持** | i18n (中/英/日), 图谱内容多语言 |
| 10.3 | **全域图谱** | 数学/物理/化学/生物/历史/经济等 |
| 10.4 | **企业版** | 企业培训知识图谱 + 团队学习管理 |
| 10.5 | **API市场** | 开放图谱数据API + 对话引擎API |
| 10.6 | **社区共建** | 用户贡献图谱节点 + 审核机制 |

---

## 三、技术债与优化项

### 3.1 必须清理 (Phase 5-6期间)

| # | 类型 | 问题 | 优先级 | 预估 |
|:---|:---|:---|:---|:---|
| T-01 | 测试 | 前端测试覆盖率不明, 需补充核心store测试 | 🔴 | 4h |
| T-02 | 测试 | 后端pytest需补充dialogue/evaluator集成测试 | 🔴 | 4h |
| T-03 | 安全 | .env 敏感信息管理规范化 (dotenv + CI secrets) | 🔴 | 1h |
| T-04 | 性能 | 图谱>500节点时3D渲染性能需profiling | 🟡 | 2h |
| T-05 | 架构 | Worker(D1) vs FastAPI(SQLite) 数据层统一 | 🟡 | 4h |

### 3.2 应该优化 (Phase 7-8期间)

| # | 类型 | 问题 | 优先级 | 预估 |
|:---|:---|:---|:---|:---|
| T-06 | 前端 | Bundle分析优化 — Three.js treeshake, 减少主包体积 | 🟡 | 2h |
| T-07 | 前端 | React组件拆分 — GraphPage/LearnPage超200行 | 🟡 | 3h |
| T-08 | 后端 | 对话引擎Prompt模板外部化 (YAML/JSON配置) | 🟡 | 2h |
| T-09 | 后端 | API限流 (Redis rate limiter) | 🟡 | 2h |
| T-10 | 基础设施 | 日志规范化 (structured logging + 日志级别) | 🟢 | 2h |

---

## 四、风险与应对

| 风险 | 概率 | 影响 | 应对策略 |
|:---|:---|:---|:---|
| LLM API 成本失控 | 中 | 高 | 分层调度(已有) + 缓存 + 用户自带Key(已有) + 每日用量上限 |
| Neo4j AuraDB Free 限额不够 | 低 | 中 | 20万节点Free够用; 超限迁移到自托管Docker |
| OpenRouter 服务不稳定 | 中 | 中 | 多provider fallback(已有) + 本地缓存 |
| 移动端Capacitor兼容问题 | 中 | 中 | 先PWA降级, Capacitor作为增强 |
| Supabase免费额度不够 | 低 | 低 | Pro计划$25/月, 早期用户量可控 |
| 用户对"教AI"模式不适应 | 中 | 高 | A/B测试: 费曼模式 vs 传统问答模式, 数据驱动决策 |

---

## 五、核心指标定义

### 5.1 公测阶段KPI

| 指标 | 目标 | 衡量方式 |
|:---|:---|:---|
| **注册用户** | 100+ (公测1个月) | Supabase Auth统计 |
| **费曼对话完成率** | >60% | 开始对话→完成评估的比例 |
| **节点点亮数/用户** | ≥5 | 平均每用户mastered节点 |
| **7日留存** | >20% | D7活跃/D1注册 |
| **NPS** | >40 | 用户调查 |
| **对话满意度** | >3.5/5 | 对话后评分(待加) |

### 5.2 数据埋点需求

```
[必须] session_start / session_end (含duration)
[必须] conversation_start / conversation_complete (含concept_id, score)
[必须] node_mastered (含concept_id, attempt_count)
[建议] graph_interaction (zoom/pan/click/search)
[建议] feature_usage (settings/export/import/login/logout)
[建议] error_occurrence (type, message, stack_trace)
```

---

## 六、近期执行优先级排序

```
立即 (本周):
  1. Phase 5.1-5.7  → Supabase Cloud 配置 + 端到端测试 + EXE v0.2.0
  2. T-01, T-02     → 补充测试覆盖

短期 (1-2周):
  3. Phase 6.2      → 纯前端Direct模式增强, 去CORS代理依赖
  4. Phase 6.4      → 公测准备 (Landing + 反馈 + 监控)
  5. T-03           → 环境变量安全规范化

中期 (2-4周):
  6. Phase 7.2      → FSRS间隔复习 (核心差异化功能)
  7. Phase 7.1      → 多域图谱 (数学领域)
  8. Phase 8.1      → Capacitor Android APK

远期 (1-2月):
  9. Phase 8.2      → 核心体验优化
  10. Phase 9       → 社交功能 + 语音费曼
  11. Phase 10      → 商业化
```

---

## 七、版本规划

| 版本 | 对应Phase | 核心功能 | 预计时间 |
|:---|:---|:---|:---|
| **v0.2.0** | Phase 5 完成 | 可选登录 + Supabase跨端同步 | 本周 |
| **v0.3.0** | Phase 6 完成 | 线上部署 + 公测就绪 | +1-2周 |
| **v1.0.0** | Phase 7 完成 | FSRS复习 + 多域图谱 | +3-4周 |
| **v1.1.0** | Phase 8 完成 | 移动端APK + 体验优化 | +5-6周 |
| **v2.0.0** | Phase 9 完成 | 社交 + 语音 + 高级功能 | +8-10周 |

---

*本计划将随实际进展持续更新。每完成一个Phase后回顾并调整后续计划。*