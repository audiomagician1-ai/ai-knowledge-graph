# 共享后端方案 — Multi-Project Supabase Consolidation

> Created: 2026-04-06 | Status: DRAFT
> 目标: 将多个轻量项目合并到一个 Supabase 实例，节约成本、统一用户系统

---

## 1. 现状审计

### 1.1 各项目后端资源盘点

| 项目 | Supabase | D1 | Workers | KV | 后端重度 |
|------|----------|----|---------|----|---------|
| **MuseSea** | `wgzjlnuiqzjkmeqqhqbn` · 177迁移 · 16 Edge Fn | — | — | — | **🔴 重** |
| **AI知识图谱** | `oepkmybgwptxnkpgrglv` · 2迁移 · 0用户 | akg-db (1MB) | akg-api | — | 🟢 轻 |
| **BrainForge** | 仅本地 · 未部署远程 | — | — | — | 🟢 轻 |
| **NewCRPG** | 无 | countdown99-world-hub | llm-proxy, world-hub | — | 🟢 轻 |
| **Timentropy** | 无 | — | analytics | analytics KV | 🟢 极轻 |

### 1.2 Supabase Free Tier 限制

| 资源 | Free 额度 | Pro ($25/月) |
|------|----------|-------------|
| 项目数 | **2 个活跃** (7天不活跃自动暂停) | 无限 |
| 数据库 | 500 MB | 8 GB |
| Auth MAU | 50,000 | 100,000 |
| Edge Functions | 500K 调用/月 | 2M |
| Storage | 1 GB | 100 GB |
| 带宽 | 5 GB | 250 GB |

### 1.3 合并策略决策

| 项目 | 决策 | 理由 |
|------|------|------|
| **MuseSea** | ❌ **不合并，保持独立** | 177迁移+16 Edge Fn+真实用户+复杂度极高，合并风险远大于收益 |
| **AI知识图谱** | ✅ **作为共享实例的宿主** | 当前0用户、2迁移、数据库空，改造成本最低 |
| **BrainForge** | ✅ **合入共享实例** | 尚未部署远程 DB，直接在共享实例创建 schema |
| **NewCRPG** | ✅ **合入共享实例 (按需)** | 单机游戏，仅社区功能需要用户系统时接入 |
| **Timentropy** | ✅ **合入共享实例 (按需)** | 评论/互动功能需要时接入，KV 分析继续用 CF |

### 1.4 合并后资源占用预估

| 资源 | 预估用量 | Free 额度 | 是否够 |
|------|---------|----------|--------|
| 项目数 | 2 (MuseSea + Shared) | 2 | ✅ 刚好 |
| 数据库 | <50 MB (4项目合计) | 500 MB | ✅ 充裕 |
| Auth MAU | <100 | 50,000 | ✅ 充裕 |
| Edge Functions | <10K/月 | 500K | ✅ 充裕 |

---

## 2. 架构设计

### 2.1 总体架构

```
┌──────────────────────────────────────────────────────────────────┐
│  Supabase Shared Instance (oepkmybgwptxnkpgrglv.supabase.co)    │
│                                                                    │
│  auth.users ────── 统一用户体系 (一次注册，所有项目通用)           │
│       │                                                            │
│       ├── schema: akg          (AI知识图谱)                       │
│       │     ├── profiles                                           │
│       │     ├── user_settings                                      │
│       │     ├── user_concept_status                                │
│       │     ├── conversations                                      │
│       │     └── learning_events                                    │
│       │                                                            │
│       ├── schema: brainforge   (BrainForge 认知训练)              │
│       │     ├── user_profiles                                      │
│       │     ├── training_sessions                                  │
│       │     ├── trial_results                                      │
│       │     ├── assessments                                        │
│       │     ├── daily_checkins                                     │
│       │     └── norm_data                                          │
│       │                                                            │
│       ├── schema: newcrpg      (末日倒数99天 — 按需)              │
│       │     ├── world_seeds    (社区世界分享)                      │
│       │     └── leaderboard                                        │
│       │                                                            │
│       ├── schema: timentropy   (时熵 — 按需)                      │
│       │     ├── comments                                           │
│       │     └── reactions                                          │
│       │                                                            │
│       └── schema: shared       (跨项目共享表)                     │
│             ├── user_projects   (用户↔项目关联)                    │
│             └── feedback        (通用反馈收集)                     │
│                                                                    │
│  Edge Functions:                                                    │
│       ├── akg--health          (AKG 健康检查)                      │
│       ├── akg--llm-proxy       (AKG LLM代理)                      │
│       ├── bf--generate-report  (BrainForge 报告生成)               │
│       ├── bf--norm-compare     (BrainForge 常模对比)               │
│       └── _shared/             (公共工具库)                        │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
          │                    │                    │
     akg-web.pages.dev   brainforge.pages.dev  countdown99.pages.dev
          │                    │                    │
     (+ CF Workers)      (+ Flutter App)     (+ CF Workers D1)
```

### 2.2 数据流

```
[前端/客户端]
     │
     │  supabase.schema('akg').from('profiles')...
     │  supabase.schema('brainforge').from('training_sessions')...
     │
     ▼
[Supabase PostgREST]  ──→  PostgreSQL (schema隔离)
     │                           │
     │                      [RLS 策略]
     │                      auth.uid() = user_id
     │
[Supabase Auth]  ←── 统一登录 (Email/OAuth/Magic Link)
     │
     └──→ auth.users (所有项目共享)
              │
              └──→ trigger: handle_new_user()
                     ├── INSERT shared.user_projects
                     └── (各 schema 的 profile 在首次访问时懒创建)
```

---

## 3. 实施方案

### 3.1 Phase 1 — Schema 基础设施 (Day 1)

#### 3.1.1 创建 Schema + 授权

```sql
-- 文件: supabase/migrations/00003_shared_backend_foundation.sql

-- ─── 创建项目 Schema ───
CREATE SCHEMA IF NOT EXISTS akg;
CREATE SCHEMA IF NOT EXISTS brainforge;
CREATE SCHEMA IF NOT EXISTS newcrpg;
CREATE SCHEMA IF NOT EXISTS timentropy;
CREATE SCHEMA IF NOT EXISTS shared;

-- ─── PostgREST 角色授权 ───
-- anon: 未登录用户 | authenticated: 已登录用户 | service_role: 后端管理
GRANT USAGE ON SCHEMA akg TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA brainforge TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA newcrpg TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA timentropy TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA shared TO anon, authenticated, service_role;

-- ─── 默认权限 (新建表自动继承) ───
ALTER DEFAULT PRIVILEGES IN SCHEMA akg
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA akg
  GRANT ALL ON TABLES TO service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA brainforge
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA brainforge
  GRANT ALL ON TABLES TO service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA newcrpg
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA newcrpg
  GRANT ALL ON TABLES TO service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA timentropy
  GRANT SELECT ON TABLES TO anon;  -- 评论可公开读
ALTER DEFAULT PRIVILEGES IN SCHEMA timentropy
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA timentropy
  GRANT ALL ON TABLES TO service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA shared
  GRANT SELECT ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA shared
  GRANT ALL ON TABLES TO service_role;
```

#### 3.1.2 共享表

```sql
-- 文件: supabase/migrations/00004_shared_tables.sql

-- ─── 用户↔项目关联 ───
CREATE TABLE shared.user_projects (
  user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  project     TEXT NOT NULL CHECK (project IN ('akg', 'brainforge', 'newcrpg', 'timentropy')),
  first_seen  TIMESTAMPTZ DEFAULT NOW(),
  last_active TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, project)
);

ALTER TABLE shared.user_projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_projects"
  ON shared.user_projects FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- ─── 通用反馈 ───
CREATE TABLE shared.feedback (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  project     TEXT NOT NULL,
  category    TEXT DEFAULT 'general',
  content     TEXT NOT NULL,
  metadata    JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE shared.feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_insert_feedback"
  ON shared.feedback FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "users_read_own_feedback"
  ON shared.feedback FOR SELECT
  USING (auth.uid() = user_id);
```

### 3.2 Phase 2 — AKG 迁移到 akg schema (Day 1-2)

```sql
-- 文件: supabase/migrations/00005_migrate_akg_to_schema.sql

-- ─── 将 public 表移动到 akg schema ───
-- 注意: public 中原来的表全部是空的 (0注册用户)，直接搬迁无风险

ALTER TABLE public.profiles SET SCHEMA akg;
ALTER TABLE public.user_settings SET SCHEMA akg;
ALTER TABLE public.user_concept_status SET SCHEMA akg;
ALTER TABLE public.conversations SET SCHEMA akg;
ALTER TABLE public.learning_events SET SCHEMA akg;

-- ─── 修复索引引用 (ALTER TABLE SET SCHEMA 会自动迁移索引) ───
-- ─── 修复触发器 ───

-- 删除旧触发器 (它引用 public.profiles)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS handle_new_user();

-- 新触发器: 只注册到 shared.user_projects，各 schema 的 profile 懒创建
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  -- 不再自动创建任何项目的 profile
  -- profile 在用户首次访问各项目时由客户端/Edge Function 按需创建
  -- 这里只记录用户的存在
  RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- ─── AKG Profile 懒创建函数 ───
CREATE OR REPLACE FUNCTION akg.ensure_profile()
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = akg
AS $$
DECLARE
  _uid UUID := auth.uid();
  _email TEXT;
BEGIN
  -- 已存在则直接返回
  IF EXISTS (SELECT 1 FROM akg.profiles WHERE id = _uid) THEN
    RETURN _uid;
  END IF;

  -- 从 auth.users 获取 email
  SELECT email INTO _email FROM auth.users WHERE id = _uid;

  -- 创建 profile + settings
  INSERT INTO akg.profiles (id, email, display_name)
  VALUES (_uid, _email, split_part(_email, '@', 1));

  INSERT INTO akg.user_settings (user_id) VALUES (_uid);

  -- 注册到共享项目表
  INSERT INTO shared.user_projects (user_id, project)
  VALUES (_uid, 'akg')
  ON CONFLICT DO NOTHING;

  RETURN _uid;
END;
$$;
```

### 3.3 Phase 3 — BrainForge Schema (Day 2-3)

```sql
-- 文件: supabase/migrations/00006_brainforge_schema.sql

-- ─── BrainForge 用户资料 ───
CREATE TABLE brainforge.user_profiles (
  user_id         UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name    TEXT,
  birth_year      SMALLINT CHECK (birth_year BETWEEN 1940 AND 2010),
  education_level TEXT CHECK (education_level IN (
    'high_school', 'some_college', 'bachelors', 'masters', 'doctorate', 'other'
  )),
  timezone        TEXT DEFAULT 'UTC',
  subscription    TEXT NOT NULL DEFAULT 'free' CHECK (subscription IN ('free', 'premium')),
  onboarding_done BOOLEAN NOT NULL DEFAULT false,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE brainforge.user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own_profile" ON brainforge.user_profiles
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ─── 训练记录 ───
CREATE TABLE brainforge.training_sessions (
  session_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  task_type        TEXT NOT NULL,
  started_at       TIMESTAMPTZ NOT NULL,
  completed_at     TIMESTAMPTZ,
  duration_seconds INTEGER GENERATED ALWAYS AS (
    EXTRACT(EPOCH FROM (completed_at - started_at))::INTEGER
  ) STORED,
  final_level      SMALLINT NOT NULL DEFAULT 1 CHECK (final_level >= 1),
  overall_accuracy REAL CHECK (overall_accuracy BETWEEN 0 AND 1),
  client_session_id TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bf_sessions_user_task
  ON brainforge.training_sessions (user_id, task_type, started_at DESC);

ALTER TABLE brainforge.training_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own_sessions" ON brainforge.training_sessions
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ─── Trial 结果 ───
CREATE TABLE brainforge.trial_results (
  id               BIGSERIAL PRIMARY KEY,
  session_id       UUID NOT NULL REFERENCES brainforge.training_sessions(session_id) ON DELETE CASCADE,
  user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  task_type        TEXT NOT NULL,
  block_index      SMALLINT NOT NULL,
  trial_index      SMALLINT NOT NULL,
  difficulty       SMALLINT NOT NULL CHECK (difficulty >= 1),
  is_correct       BOOLEAN NOT NULL,
  reaction_time_ms INTEGER NOT NULL,
  metadata         JSONB DEFAULT '{}'::jsonb,
  recorded_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bf_trials_session
  ON brainforge.trial_results (session_id, block_index, trial_index);

ALTER TABLE brainforge.trial_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own_trials" ON brainforge.trial_results
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ─── 每日打卡 ───
CREATE TABLE brainforge.daily_checkins (
  user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  checkin_date DATE NOT NULL,
  sessions_count SMALLINT NOT NULL DEFAULT 0,
  total_time_sec INTEGER NOT NULL DEFAULT 0,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, checkin_date)
);

ALTER TABLE brainforge.daily_checkins ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own_checkins" ON brainforge.daily_checkins
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ─── 懒创建函数 ───
CREATE OR REPLACE FUNCTION brainforge.ensure_profile()
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = brainforge
AS $$
DECLARE
  _uid UUID := auth.uid();
BEGIN
  IF EXISTS (SELECT 1 FROM brainforge.user_profiles WHERE user_id = _uid) THEN
    RETURN _uid;
  END IF;

  INSERT INTO brainforge.user_profiles (user_id) VALUES (_uid);

  INSERT INTO shared.user_projects (user_id, project)
  VALUES (_uid, 'brainforge')
  ON CONFLICT DO NOTHING;

  RETURN _uid;
END;
$$;
```

### 3.4 Phase 4 — NewCRPG / Timentropy 预留 Schema (Day 3)

```sql
-- 文件: supabase/migrations/00007_newcrpg_timentropy_stubs.sql

-- ─── NewCRPG: 社区世界分享 (D1 仍处理单机数据，Supabase 仅处理社区) ───
CREATE TABLE newcrpg.shared_worlds (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  creator_id  UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  world_seed  JSONB NOT NULL,
  title       TEXT NOT NULL,
  description TEXT,
  plays       INTEGER DEFAULT 0,
  likes       INTEGER DEFAULT 0,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE newcrpg.shared_worlds ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anyone_read_worlds" ON newcrpg.shared_worlds
  FOR SELECT USING (true);

CREATE POLICY "creator_manage_worlds" ON newcrpg.shared_worlds
  FOR ALL USING (auth.uid() = creator_id)
  WITH CHECK (auth.uid() = creator_id);

-- ─── Timentropy: 文章互动 ───
CREATE TABLE timentropy.comments (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  article_id  TEXT NOT NULL,
  content     TEXT NOT NULL CHECK (length(content) <= 2000),
  parent_id   UUID REFERENCES timentropy.comments(id) ON DELETE CASCADE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tim_comments_article ON timentropy.comments(article_id, created_at);

ALTER TABLE timentropy.comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anyone_read_comments" ON timentropy.comments
  FOR SELECT USING (true);

CREATE POLICY "users_create_comments" ON timentropy.comments
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "users_delete_own" ON timentropy.comments
  FOR DELETE USING (auth.uid() = user_id);

CREATE TABLE timentropy.reactions (
  user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  article_id  TEXT NOT NULL,
  type        TEXT NOT NULL CHECK (type IN ('like', 'bookmark', 'insightful')),
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, article_id, type)
);

ALTER TABLE timentropy.reactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anyone_read_reactions" ON timentropy.reactions
  FOR SELECT USING (true);

CREATE POLICY "users_manage_own" ON timentropy.reactions
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
```

---

## 4. 前端接入指南

### 4.1 Supabase 客户端配置

所有项目共享同一个 Supabase URL 和 Anon Key：

```typescript
// 所有项目的 .env
VITE_SUPABASE_URL=https://oepkmybgwptxnkpgrglv.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJI...（同一个 anon key）
```

### 4.2 各项目的 Supabase 客户端封装

```typescript
// ─── AI知识图谱 ─────────────────────────────
// packages/web/src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

// 查询 akg schema 的表
export const akgDb = supabase.schema('akg')

// 用法
const { data } = await akgDb.from('profiles').select('*')
const { data } = await akgDb.from('user_concept_status').select('*')

// Auth 不变 — auth.users 是全局的
const { data } = await supabase.auth.signUp({ email, password })
```

```typescript
// ─── BrainForge ─────────────────────────────
// lib/core/supabase/client.dart (Flutter)
import 'package:supabase_flutter/supabase_flutter.dart';

final supabase = Supabase.instance.client;

// Flutter SDK 也支持 schema 切换
final brainforgeDb = supabase.schema('brainforge');

// 查询训练记录
final data = await brainforgeDb
    .from('training_sessions')
    .select()
    .eq('user_id', supabase.auth.currentUser!.id)
    .order('started_at', ascending: false);
```

```typescript
// ─── NewCRPG (可选，社区功能时接入) ─────────
// src/lib/supabase.ts
const newcrpgDb = supabase.schema('newcrpg')

// 浏览社区世界
const { data } = await newcrpgDb
  .from('shared_worlds')
  .select('*')
  .order('likes', { ascending: false })
  .limit(20)
```

### 4.3 Profile 懒创建模式

```typescript
// 通用模式: 首次访问时确保 profile 存在
async function ensureProfile(project: 'akg' | 'brainforge' | 'newcrpg' | 'timentropy') {
  const { data, error } = await supabase.rpc(`${project === 'akg' ? 'akg' : project}.ensure_profile`)
  // 或通过 Edge Function
  if (error) {
    await supabase.functions.invoke('ensure-profile', {
      body: { project }
    })
  }
}
```

---

## 5. Supabase 配置变更

### 5.1 config.toml

```toml
[api]
port = 54321
schemas = ["public", "akg", "brainforge", "newcrpg", "timentropy", "shared"]
extra_search_path = ["public", "extensions"]
max_rows = 1000

[db]
port = 54322
major_version = 15

[auth]
site_url = "https://akg-web.pages.dev"
additional_redirect_urls = [
  "https://akg-web.pages.dev",
  "https://brainforge-web.pages.dev",
  "https://countdown99.pages.dev",
  "https://timentropy.com",
  "http://localhost:3000",
  "http://localhost:5173"
]
jwt_expiry = 3600
enable_signup = true

[auth.email]
enable_signup = true
double_confirm_changes = true
enable_confirmations = false
```

### 5.2 Dashboard 配置

在 Supabase Dashboard → Settings → API 中：
1. 添加 `akg, brainforge, newcrpg, timentropy, shared` 到 `Exposed schemas`
2. 在 Auth → URL Configuration 中添加所有项目域名到 Redirect URLs

---

## 6. Edge Functions 命名约定

```
supabase/functions/
  ├── _shared/              # 公共工具库 (所有项目共享)
  │   ├── cors.ts
  │   ├── auth.ts
  │   └── response.ts
  │
  ├── akg--health/          # AKG: 健康检查
  ├── akg--llm-proxy/       # AKG: LLM 代理
  │
  ├── bf--generate-report/  # BrainForge: 报告生成
  ├── bf--norm-compare/     # BrainForge: 常模对比
  │
  ├── ensure-profile/       # 通用: 懒创建 profile
  └── user-stats/           # 通用: 跨项目统计
```

调用方式:
```typescript
// AKG 调用
await supabase.functions.invoke('akg--llm-proxy', { body: { ... } })

// BrainForge 调用
await supabase.functions.invoke('bf--generate-report', { body: { ... } })
```

---

## 7. 与 Cloudflare 服务的分工

合并到 Supabase 后，各项目的 Cloudflare 服务继续保留，分工如下：

| 服务 | 用途 | 项目 |
|------|------|------|
| **CF Pages** | 前端托管 | 所有项目 (免费) |
| **CF Workers** | LLM 代理、API 网关 | AKG (akg-api)、NewCRPG (world-hub, llm-proxy) |
| **CF D1** | 匿名/离线本地数据 | AKG (匿名学习进度)、NewCRPG (单机存档) |
| **CF KV** | 分析数据 | Timentropy (analytics) |
| **Supabase Auth** | 用户注册登录 | 所有需要账号的项目 |
| **Supabase DB** | 用户数据持久化 | 登录用户的长期数据 |
| **Supabase Edge Fn** | 轻量服务端逻辑 | 报告生成、常模计算等 |

**关键原则**: D1/KV 处理匿名+高频+本地数据，Supabase 处理用户+低频+云端数据。

---

## 8. 迁移检查清单

### Phase 1: 基础设施 (Day 1)
- [ ] 在 Supabase Dashboard 中开启多 schema 支持
- [ ] 执行 `00003_shared_backend_foundation.sql`
- [ ] 执行 `00004_shared_tables.sql`
- [ ] 更新 `supabase/config.toml` 的 schemas 列表
- [ ] 验证: 通过 Dashboard SQL Editor 确认 schema 创建成功

### Phase 2: AKG 迁移 (Day 1-2)
- [ ] 执行 `00005_migrate_akg_to_schema.sql`
- [ ] 更新 AKG 前端 supabase 客户端: 添加 `.schema('akg')`
- [ ] 更新 AKG Workers 中的 Supabase 调用
- [ ] 更新 AKG Edge Functions
- [ ] 验证: 注册新用户 → 确认 akg.profiles 创建成功

### Phase 3: BrainForge 接入 (Day 2-3)
- [ ] 执行 `00006_brainforge_schema.sql`
- [ ] BrainForge Flutter 配置 Supabase URL + Anon Key
- [ ] BrainForge Web 配置 `.schema('brainforge')`
- [ ] 部署 bf--generate-report, bf--norm-compare Edge Functions
- [ ] 验证: 训练数据 sync 到 brainforge schema

### Phase 4: 预留 Schema (Day 3)
- [ ] 执行 `00007_newcrpg_timentropy_stubs.sql`
- [ ] 验证: schema 创建成功，RLS 策略生效

### Phase 5: Auth 域名配置 (Day 3)
- [ ] Supabase Dashboard → Auth → URL Configuration 添加所有域名
- [ ] 各项目测试注册/登录流程
- [ ] 验证: 同一账号在不同项目间可正常登录

---

## 9. 安全要点

1. **Schema 不等于安全边界** — RLS 是真正的数据隔离机制，每张表必须有 RLS
2. **service_role key 绝不暴露给前端** — 只在 Edge Functions 和后端使用
3. **anon key 可以共享** — 它被 RLS 限制，本身无特权
4. **跨 schema 查询**: 普通用户无法跨 schema 查询，除非 RLS 明确放行
5. **auth.users 共享**: 一个用户的 JWT 在所有 schema 中有效，但每个 schema 的 RLS 独立控制可见数据

---

## 10. 成本对比

| 场景 | Supabase 项目数 | 月费 |
|------|:---:|:---:|
| **现状** (每项目独立) | 4-5 个 → 需 Pro $25×3 | **$75/月** |
| **合并后** (MuseSea + Shared) | 2 个 | **$0/月** (Free Tier) |
| 未来增长 (Free 不够时) | 2 个 Pro | **$50/月** |

**年节省**: $75×12 = **$900/年** → 合并后 $0/年 (Free Tier 足够阶段)
