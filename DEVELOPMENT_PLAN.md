# 智能任务管理系统 — 开发规划文档

> 方向 D（AI/LLM 开发方向）· 实习生编程挑战
> 本文档为项目开发蓝图，落地实现前请通读，并以此为准对齐范围与设计。

---

## 1. 项目定位与目标

构建一个带 **AI 智能辅助** 的任务管理系统，核心能力：

1. 完整的 **任务 CRUD** RESTful API（基础能力）
2. **自然语言创建任务**（智能任务生成）
3. **自动标签 + 优先级推荐**（智能任务组织）
4. **任务拆解 / 任务摘要**（AI 助手功能，共 2 个）

**范围边界（明确不做）**：语义搜索 / 相似任务检测（不引入向量库与 embedding，见 §8 决策记录）。

**验收口径**：优先保证「干净代码 + 合理 AI 设计 + 清晰思路」，功能数量次之（对应挑战第五部分评估权重：代码 30% / 问题解决 30% / 系统设计 25% / 文档 15%）。

---

## 2. 技术选型（已定）

| 维度 | 选型 | 理由 |
|------|------|------|
| 语言 | Python 3.11+ | AI 生态最完善，挑战官方推荐 |
| 后端框架 | **FastAPI** + Uvicorn | 异步 + 自动 OpenAPI 文档 + Pydantic 校验，天然契合 LLM 的耗时调用场景 |
| ORM | **SQLAlchemy 2.0**（同步引擎） | `.env` 已按 SQLAlchemy 连接池参数配好（pool_size/recycle/pre_ping 等） |
| 数据库驱动 | PyMySQL | 纯 Python，跨平台，配 `utf8mb4` 避免中文/emoji 乱码 |
| 数据库 | **MySQL**（utf8mb4） | 已在 `.env.example` 定好 |
| LLM | **DeepSeek**（OpenAI 兼容接口） | 已在 `.env` 配好 key + base_url + 超时/重试 |
| LLM 客户端 | `openai` SDK 指向 `base_url=https://api.deepseek.com` | 复用官方重试/超时/JSON mode 能力，少造轮子 |
| 校验 | Pydantic v2（FastAPI 自带） | 请求/响应 + LLM 输出双重校验 |
| 测试 | pytest + pytest-cov | 单元测试 + AI 逻辑用 mock LLM |

**异步策略（关键决策）**：FastAPI 端点用 **同步 `def`** 写法。FastAPI 会把同步端点丢进线程池，这样 LLM 的阻塞调用（最长 60s）不会卡住事件循环，同时代码保持同步的简单性。SQLAlchemy 也用同步引擎，与线程池模型一致。→ 未来若并发上量，再迁移 SQLAlchemy async + httpx async。

---

## 3. 功能范围（MVP 清单）

### 3.1 基础能力
- [x] 任务 CRUD（CREATE / READ / UPDATE / DELETE）
- [x] 任务列表：按 status / priority / tags 筛选，按 created_at / due_date / priority 排序，分页

### 3.2 AI 功能（DeepSeek 驱动）
- [x] **智能任务生成**：自然语言 → 结构化任务草稿（title / description / due_date / priority / tags）
- [x] **自动标签推荐**：标题 + 描述 → 标签集合
- [x] **优先级推荐**：内容 + 截止时间 → priority
- [x] **任务分类**：归入预定义类别（与标签/优先级合并为一次 LLM 调用）
- [x] **任务拆解**：复杂任务 → 子任务列表
- [x] **任务摘要**：每日/每周任务摘要（结构化统计 + 自然语言描述）

### 3.3 明确不做（v1）
- [ ] 语义搜索 / 向量库 / embedding（DeepSeek 无官方 embedding 接口，避免引入本地模型复杂度）
- [ ] 相似任务检测（依赖语义匹配，一并去掉）
- [ ] 前端 UI（本方向核心为后端 API，README 里用 curl / Swagger 演示）
- [ ] 用户认证 / 多租户

---

## 4. 系统架构

分层设计，核心原则：**业务逻辑与 AI 逻辑解耦**（挑战明确要求）。

```
        ┌─────────────────────────────────────────────┐
        │                API 层 (routes/)              │
        │   FastAPI Router · Pydantic 请求/响应校验      │
        └───────────────┬─────────────────────────────┘
                        │ 依赖注入
        ┌───────────────▼─────────────────────────────┐
        │            业务层 (services/)                 │
        │   TaskService：CRUD / 筛选 / 排序 / 分页        │
        └───────────────┬─────────────────────────────┘
                        │ 仅通过接口调用
        ┌───────────────▼─────────────────────────────┐
        │              AI 层 (ai/)                      │
        │  NL 提取 · 标签/优先级推荐 · 拆解 · 摘要         │
        │  + 降级规则引擎（LLM 失败时回退）                │
        └───────────────┬─────────────────────────────┘
                        │
        ┌───────────────▼─────────────┬───────────────┐
        │  数据层 (models/ + db.py)     │  DeepSeek      │
        │  SQLAlchemy ORM + MySQL      │  (openai SDK)  │
        └─────────────────────────────┴───────────────┘
```

**解耦方式**：`services/task_service.py` 不直接 import LLM 客户端，而是依赖 `ai/` 层暴露的接口（如 `generate_task_draft()`、`recommend_metadata()`）。AI 层内部决定「走 LLM 还是走规则降级」，业务层无感知。

---

## 5. 目录结构

```
project/
├── README.md
├── DEVELOPMENT_PLAN.md          # 本文档
├── requirements.txt
├── .gitignore
├── .env.example                 # 模板（真实 key 不提交）
├── src/
│   ├── main.py                  # FastAPI 入口 + 路由注册
│   ├── config.py                # 读取 .env → pydantic-settings
│   ├── db.py                    # engine / SessionLocal / get_db 依赖
│   ├── models/
│   │   ├── task.py              # SQLAlchemy Task 模型
│   │   └── schemas.py           # Pydantic 请求/响应模型
│   ├── routes/
│   │   ├── tasks.py             # /tasks CRUD
│   │   └── ai.py                # /ai/* 智能功能
│   ├── services/
│   │   └── task_service.py      # CRUD / 筛选 / 排序 / 分页业务逻辑
│   ├── ai/
│   │   ├── client.py            # DeepSeek 封装（重试/超时/JSON mode）
│   │   ├── prompts.py           # 所有 prompt 模板（集中管理，便于测试）
│   │   ├── parsers.py           # LLM 输出解析 + Pydantic 校验
│   │   ├── fallback.py          # 降级规则引擎（时间解析/关键词映射）
│   │   ├── generate.py          # 自然语言 → 任务草稿
│   │   ├── recommend.py         # 标签/优先级/分类推荐
│   │   ├── breakdown.py         # 任务拆解
│   │   └── summarize.py         # 任务摘要
│   └── utils/
│       └── time.py              # 时间表达式解析（规则版）
└── tests/
    ├── test_crud.py
    ├── test_fallback.py         # 规则引擎单测（不依赖网络）
    ├── test_time_parser.py
    └── test_ai.py               # mock LLM 测试 AI 层
```

---

## 6. 数据库设计

### 6.1 `tasks` 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BIGINT | PK, AUTO_INCREMENT | 唯一标识 |
| `title` | VARCHAR(255) | NOT NULL | 必填 |
| `description` | TEXT | NULL | 可选 |
| `status` | ENUM | NOT NULL, DEFAULT `pending` | `pending` / `in_progress` / `completed` |
| `priority` | ENUM | NOT NULL, DEFAULT `medium` | `low` / `medium` / `high` |
| `tags` | JSON | NULL | 字符串数组（MySQL JSON 类型） |
| `due_date` | DATETIME | NULL | 截止时间 |
| `created_at` | DATETIME | NOT NULL | 创建时间 |
| `updated_at` | DATETIME | NOT NULL | 更新时间（更新时自动刷新） |

**索引**：`status`、`priority`、`due_date` 建普通索引（支撑筛选/排序）。`updated_at` 由 ORM 的 `onupdate` 自动维护。

**关于 tags 的权衡**：v1 用 JSON 列，简单、与挑战字段定义（`tags` 字符串数组）天然对齐；代价是 MySQL 里按标签过滤要用 `JSON_CONTAINS`，可读性一般。→ 未来若标签成为核心查询维度，再拆成 `tags` + `task_tags` 关联表（记录在「未来改进」）。

**关于子任务的权衡**：`任务拆解` 的产出在 v1 **不持久化**为单独表，而是作为「建议子任务」返回，用户确认后走普通 `POST /tasks` 落库。→ 避免引入 `subtasks` 自关联表的复杂度。

---

## 7. API 设计

统一前缀 `/api/v1`，错误统一返回 `{ "detail": "..." }`（FastAPI 默认）。LLM 相关接口均为**同步阻塞**（见 §2 异步策略）。

### 7.1 任务 CRUD

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/tasks` | 创建任务 |
| GET | `/api/v1/tasks` | 列表（`?status=&priority=&tag=&sort=&order=&page=&page_size=`） |
| GET | `/api/v1/tasks/{id}` | 按 ID 获取 |
| PATCH | `/api/v1/tasks/{id}` | 部分更新 |
| DELETE | `/api/v1/tasks/{id}` | 删除 |

**创建任务请求示例**：
```json
{
  "title": "买日用品",
  "description": "牛奶、鸡蛋、洗衣液",
  "priority": "high",
  "tags": ["购物"],
  "due_date": "2026-09-18T15:00:00+08:00"
}
```

### 7.2 AI 智能功能（与业务解耦，先返回「草稿/建议」，由用户确认后落库）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/ai/generate` | 自然语言 → 任务草稿（**不落库**） |
| POST | `/api/v1/ai/recommend` | 标题+描述 → 标签/优先级/分类建议 |
| POST | `/api/v1/ai/tasks/{id}/breakdown` | 任务拆解 → 子任务列表 |
| POST | `/api/v1/ai/summarize` | 每日/每周任务摘要（`?period=day\|week`） |

**`/ai/generate` 请求/响应示例**：
```jsonc
// 请求
{ "text": "明天下午3点提醒我买日用品" }

// 响应（草稿，前端可让用户确认后再 POST /tasks）
{
  "title": "买日用品",
  "description": null,
  "priority": "medium",
  "tags": ["购物"],
  "due_date": "2026-09-18T15:00:00+08:00",
  "source": "llm"          // "llm" | "fallback"（降级时标记）
}
```

**`/ai/summarize` 响应示例**（结构化统计 + 自然语言）：
```json
{
  "period": "week",
  "stats": { "total": 8, "high_priority": 3, "completed": 2, "overdue": 1 },
  "summary": "本周共有 8 个任务，其中 3 个高优先级待处理，1 个已逾期，建议优先处理。"
}
```

> 设计要点：摘要里的数字（total/high_priority 等）**由代码统计**，LLM 只负责把统计结果转成自然语言，避免模型幻觉编数字。

---

## 8. AI 功能设计

### 8.1 统一 LLM 调用规范（`ai/client.py`）

- 用 `openai.OpenAI(api_key=..., base_url=..., timeout=60, max_retries=3)`（参数全部来自 `.env`）
- 所有结构化输出开启 **JSON mode**：`response_format={"type":"json_object"}`，`temperature=0`
- 输出解析流程：`LLM 返回 → 尝试 json.loads → Pydantic 校验 → 失败重试 1 次 → 仍失败走降级规则`

### 8.2 智能任务生成（`ai/generate.py`）

**Prompt 设计**（`prompts.py` 集中维护）：

```
系统：你是一个任务信息抽取助手。从用户的中文自然语言中抽取任务信息，
只输出 JSON，不要输出任何解释。字段：title(字符串)、description(字符串或null)、
due_date(ISO8601 带时区或null)、priority("low"|"medium"|"high")、
tags(字符串数组)。无法确定的字段填 null。

用户：明天下午3点提醒我买日用品
```

**输出 Schema 校验**：Pydantic 模型约束 `priority ∈ {low,medium,high}`、`due_date` 合法 ISO 时间、`tags` 为字符串数组且去重。

**时间表达处理**：常见表达（今天/明天/后天/下周五/X 小时后/X 分钟后/周X）优先由 LLM 解析；**降级规则引擎**（`utils/time.py` + `ai/fallback.py`）用正则 + 相对时间计算兜底，确保 LLM 失败时仍能给出合理默认值。

**验收映射**：能处理多种时间表达 ✓；无法识别时给默认值（priority 默认 medium，无时间则 due_date 为 null）✓。

### 8.3 标签 + 优先级 + 分类推荐（`ai/recommend.py`）

**一次 LLM 调用合并三项**（降低 token 与延迟）：

```
系统：你是任务分类助手。根据任务标题和描述输出 JSON：
tags(字符串数组，2-4个，如"购物/工作/学习/健康/生活/财务")、
priority("low"|"medium"|"high")、category(从给定类别表选一个)。
类别表：工作、学习、生活、健康、财务、社交。

用户：{title} | {description}
```

**降级规则引擎**（`fallback.py`）：
- 关键词 → 标签：`买菜/超市/购物`→购物，`报告/开会/项目`→工作，`背单词/复习/课程`→学习，`健身/跑步/体检`→健康 …
- 关键词 → 优先级：`紧急/立刻/马上/尽快/重要/截止`→high，`有空/不急/随便`→low，其余 medium
- 时间 → 优先级：`due_date` 距今 < 24h → high；< 3 天 → medium

**验收映射**：创建后可自动获得标签与优先级建议 ✓；用户可覆盖（建议先返回建议、再由前端/调用方决定是否采纳）✓。

### 8.4 任务拆解（`ai/breakdown.py`）

```
系统：你是任务拆解助手。把一个复杂任务拆成 3-7 个可执行子任务。
输出 JSON：{"subtasks":[{"title":"...", "priority":"..."}, ...]}。
子任务要具体、可独立完成。

用户：筹备生日聚会
```

输出 → `[{title:"预订蛋糕",priority:"medium"}, {title:"发出邀请",priority:"high"}, ...]`。返回给前端，用户确认后走普通创建接口。

### 8.5 任务摘要（`ai/summarize.py`）

两步走：
1. **代码统计**：按 `period=day|week` 查出任务，算出 `total / high_priority / completed / overdue` 等精确数字。
2. **LLM 润色**：把统计数字作为结构化输入喂给 LLM，只生成自然语言 `summary`（`temperature=0`，禁止编造数字）。

---

## 9. 配置与密钥管理

- 用 `pydantic-settings` 读取 `.env`（`config.py`），类型校验（`DB_PORT` 是 int 等）。
- `.env` 已被 `.gitignore` 忽略（`.env` + `.env.*`，仅放行 `.env.example`），提交前用 `git ls-files | grep env` 确认未误提交。
- `.env.example` 作为模板已存在，含真实 key 的 `.env` 永不提交。
- **密钥轮换说明**（README 加分项）：若 key 泄露，在 DeepSeek 控制台吊销重建，仅更新本地 `.env`，不影响仓库。

> ⚠️ 待办：确认 `DEEPSEEK_MODEL=DeepSeek-V4.1-Flash` 是否为你账号实际可调用的模型 ID（DeepSeek 官方历史名称为 `deepseek-chat` / `deepseek-reasoner`）。

---

## 10. 错误处理与降级策略（全局）

这是本方案的核心加分点，对应挑战 FAQ「LLM 返回不稳定 / 超时 / 解析失败如何处理」。

| 场景 | 策略 |
|------|------|
| LLM 超时 | `.env` `LLM_TIMEOUT=60` + `LLM_MAX_RETRIES=3`（openai SDK 自动重试） |
| LLM 返回非 JSON | `json.loads` 失败 → 重试 1 次 → 走降级规则引擎 |
| LLM 输出字段非法 | Pydantic 校验失败 → 丢弃非法字段 / 取默认值 |
| LLM 整体不可用（网络/限流） | AI 接口返回 `503` + `source:"fallback"` 的规则结果；**CRUD 永不因此失败** |
| 请求参数非法 | FastAPI + Pydantic 自动 `422`，业务层再兜底校验 |
| 任务不存在 | `404` |
| 数据库连接异常 | 统一异常处理器 → `500` + 日志 |

**降级原则**：规则引擎是「最后一道保险」，保证任何情况下 AI 功能都返回**合理结果或明确错误**，而不是抛异常。

---

## 11. 测试策略

- `test_crud.py`：CRUD + 筛选/排序/分页（用临时 SQLite 或 mock DB，避免依赖本机 MySQL；集成测试另跑 MySQL）。
- `test_time_parser.py`：时间表达式解析的规则版单测（今天/明天/后天/下周五/X小时后 等）。
- `test_fallback.py`：关键词→标签/优先级映射单测。
- `test_ai.py`：**mock LLM 客户端**（monkeypatch `openai` 响应），验证 generate/recommend/breakdown/summarize 的正常路径 + JSON 解析失败降级路径。

---

## 12. 分阶段实现计划

| 阶段 | 内容 | 产出 | 预计 |
|------|------|------|------|
| P0 脚手架 | git init、`requirements.txt`、`config.py`、`db.py`、目录骨架、`.env.example` 校对 | 可启动的空 FastAPI | ~20min |
| P1 基础 CRUD | `Task` 模型 + schema + `task_service` + `/tasks` 路由 | CRUD + 列表筛选分页 | ~40min |
| P2 LLM 客户端 + 生成 | `client.py`、`prompts.py`、`parsers.py`、`generate.py` | 自然语言→任务草稿 | ~40min |
| P3 推荐 | `recommend.py` + 降级规则引擎 | 标签/优先级/分类建议 | ~30min |
| P4 拆解 + 摘要 | `breakdown.py`、`summarize.py` | 两个 AI 助手功能 | ~40min |
| P5 降级 + 测试 + 文档 | 全局降级、pytest、README、提交历史整理 | 可交付仓库 | ~40min |

> 时间仅作参考，按「质量优先、功能次之」取舍；若时间不够，优先保证 P0–P2 干净完整，P3–P4 至少完成其一。

---

## 13. Git 提交计划

- 从 P0 起就 `git init`，每个阶段至少一个**有意义的提交**（如 `feat: task CRUD 接口`、`feat: 自然语言任务生成 + 降级规则`）。
- 提交信息用英文或中文统一，动词开头，说明「做了什么」。
- 确保 `.gitignore` 覆盖 `.env`、`venv/`、`__pycache__/`、`*.log`、`.vscode/`、`.idea/`。

---

## 14. 风险与已知限制

| 风险 | 影响 | 缓解 |
|------|------|------|
| DeepSeek 模型幻觉（日期/数字） | 生成不准确 | 温度=0 + JSON mode + Pydantic 校验 + 统计数字由代码算 |
| LLM 时延（最长 60s） | 接口慢 | 同步线程池不阻塞并发 + 超时/重试 + 降级 |
| 依赖外部 API 可用性 | 功能不可用 | 规则引擎兜底，CRUD 不受影响 |
| 无 embedding/向量库 | 无法做语义搜索 | 明确降级为「未来改进」，v1 不承诺 |
| 模型 ID 不确定 | 调用失败 | 上线前用最小请求验证 `DEEPSEEK_MODEL` |

---

## 15. 加分项（可选，按投入产出排序）

1. **API key 安全管理**：`.env.example` 模板 + 密钥轮换说明（已纳入 §9，README 里补一段）。
2. **提示词优化与测试**：在 README 记录 prompt 迭代过程与最终版本对比（如「JSON mode 前 vs 后」的稳定性差异）。
3. **结构化日志**：Python `logging` + 请求 ID，便于排查 LLM 调用失败。
4. **健康检查端点**：`GET /healthz`（DB + LLM 连通性探测）。
5. **RAG / 多智能体 / 领域微调**：v1 不做，写入「未来改进」。

---

## 16. 验收对照（映射挑战要求）

| 挑战要求 | 本方案落点 |
|----------|-----------|
| 任务 CRUD | §7.1 |
| 任务属性（9 字段） | §6.1 `tasks` 表全字段覆盖 |
| 数据持久化（推荐 MySQL） | §2 / §6 |
| 代码质量 | §5 分层 + §10 错误处理 + §11 测试 |
| 智能任务生成（自然语言） | §8.2 |
| 自动标签 / 优先级推荐 / 分类 | §8.3 |
| AI 助手功能 ≥2 | 任务拆解 §8.4 + 任务摘要 §8.5 |
| 实现选项（LLM API） | DeepSeek OpenAI 兼容接口 |
| 业务逻辑与 AI 逻辑解耦 | §4 分层 + §7.2 草稿/建议模式 |
| 边界情况（LLM 异常/超时/解析失败） | §10 降级策略 |
| 文档（设计决策/prompt/限制/改进） | 落地时写入 README |
| 提交要求（git/.gitignore/不提交密钥） | §9 + §13 |

---

## 17. 未来改进（README「未来改进」章节素材）

- 接入向量库（ChromaDB）+ 本地 embedding，实现**语义搜索**与**相似任务检测**。
- tags 拆成规范化关联表，支持更高效的标签聚合查询。
- 持久化子任务（`subtasks` 自关联表）与任务依赖。
- SQLAlchemy async + httpx async 全异步化，提升高并发下的吞吐。
- 用户认证 / 多租户 / 限流。
