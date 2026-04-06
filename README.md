# 🌌 AI知识图谱 (AI Knowledge Graph)

> 通过"教AI"来学会知识 — 费曼对话 × 苏格拉底式教学 × 知识图谱技能树点亮

**线上体验**: [akg-web.pages.dev](https://akg-web.pages.dev)

## 核心特性

- 🧠 **费曼对话引擎** — AI主动提问/反问，检验你是否真正理解
- 🌐 **36域知识图谱** — 6,300+概念 × 7,167条边 × 633条跨域链接，3D可视化技能树
- 💡 **苏格拉底追问** — 不直接给答案，引导自主发现
- 📚 **间隔复习 (FSRS-5)** — 科学的遗忘曲线管理，超越SM-2
- 🎯 **BKT知识追踪** — 贝叶斯模型实时评估掌握概率
- 🏆 **成就系统** — 多维度成就解锁 + 学习连续天数
- 📊 **学习仪表盘** — 30天热力图 + 掌握度分布 + 域进度卡片
- 📱 **移动端适配** — PWA可安装 + Capacitor原生Shell
- 🔐 **免登录可用** — 匿名即可体验全部功能，登录后云端同步

## 技术栈

| 层 | 技术 |
|---|---|
| **前端** | React 19 + TypeScript 5.7 + Vite 6 + TailwindCSS 4 + Zustand 5 |
| **3D可视化** | Three.js + 3d-force-graph (知识宇宙) |
| **后端** | FastAPI (Python 3.11+) + Redis 7 (LLM缓存) |
| **图数据库** | Neo4j 5 (知识图谱) |
| **BaaS** | Supabase (Auth + PostgreSQL 15 + Edge Functions) |
| **移动端** | Capacitor 8 (Android / iOS) |
| **AI** | OpenRouter 统一入口 (stepfun/step-3.5-flash:free 默认 + 自带Key升级) |
| **边缘计算** | Cloudflare Workers (LLM代理 + API缓存) |
| **部署** | Cloudflare Pages (前端) + Docker (后端) |
| **CI/CD** | GitHub Actions |

## 数据规模

| 指标 | 数值 |
|------|------|
| 知识域 | 36 个 (AI工程、算法、数学、物理、游戏引擎等) |
| 知识概念 | 6,300+ |
| 知识边 | 7,167 |
| 跨域链接 | 633 |
| RAG文档 | 6,300 篇 (100%覆盖, 均分79.5+) |
| 测试 | 1,275+ (981 BE + 278 FE + 16 E2E) |
| 月成本 | **$0** (全免费栈) |

## 快速开始

```bash
# 安装依赖
pnpm install

# 启动基础设施 (Neo4j + Redis)
docker compose up -d

# 启动前端 (port 3000)
pnpm dev

# 启动后端 (port 8000)
pnpm api:dev

# 运行测试
cd packages/web && npx vitest run    # 前端测试
cd apps/api && python -m pytest      # 后端测试

# 生产构建
pnpm build
```

## 项目结构

```
packages/web/      → 前端 (Vite + React 19, 路由级代码分割)
packages/shared/   → 共享类型/常量
packages/mobile/   → 移动端 (Capacitor 8)
apps/api/          → 后端 (FastAPI: 图谱+对话+学习引擎)
workers/           → Cloudflare Workers (LLM代理+API)
supabase/          → Auth + PostgreSQL + Edge Functions
data/seed/         → 36域种子图谱数据
data/rag/          → 6,300篇 RAG知识文档
e2e/               → Playwright E2E测试
docs/              → 项目文档 (架构决策/审计报告/扩展计划)
```

## 架构决策 (ADR)

关键决策记录在 [CLAUDE.md](./CLAUDE.md) 和 [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md)：

- **ADR-004**: Vite+React (非 Next.js) — Capacitor兼容 + 零成本部署
- **ADR-007**: FSRS-5 (非 SM-2) — 97.4%准确率，Anki已默认采用
- **ADR-010**: 默认免费LLM — stepfun/step-3.5-flash:free, $0运行成本
- **ADR-014**: 文件RAG (非向量数据库) — 精确匹配覆盖97.7%
- **ADR-015**: 路由级代码分割 + PWA — 初始bundle减60%

## License

MIT
