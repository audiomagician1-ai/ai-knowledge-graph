# 🌌 AI知识图谱 (AI Knowledge Graph)

> 通过"教AI"来学会知识 — 费曼对话 × 苏格拉底式教学 × 知识图谱技能树点亮

## 核心特性

- **费曼对话引擎** — AI主动提问/反问，检验你是否真正理解
- **全域知识图谱** — 可视化知识依赖网络，点亮技能树
- **苏格拉底追问** — 不直接给答案，引导自主发现
- **间隔复习 (FSRS)** — 科学的遗忘曲线管理
- **游戏化学习** — 战争迷雾、成就系统、连续天数

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 19 + TypeScript 5.7 + Vite 6 + TailwindCSS 4 |
| 后端 | FastAPI + Neo4j 5 + Redis 7 |
| BaaS | Supabase (Auth + PostgreSQL + Edge Functions) |
| 移动端 | Capacitor 8 (Android / iOS) |
| AI | OpenRouter (GPT-4o / DeepSeek) 分层调度 |
| 可视化 | Cytoscape.js |

## 快速开始

```bash
# 安装依赖
pnpm install

# 启动基础设施 (Neo4j + Redis)
docker compose up -d

# 启动前端
pnpm dev

# 启动后端
pnpm api:dev
```

## 项目结构

```
packages/web/      → 前端 (Vite + React)
packages/shared/   → 共享类型/常量
packages/mobile/   → 移动端 (Capacitor)
apps/api/          → 后端 (FastAPI)
supabase/          → Auth + DB + Edge Functions
data/seed/         → 种子图谱数据
```

## License

MIT
