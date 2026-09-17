# 智能任务管理系统（Smart Task Manager）

一个带 **AI 智能辅助** 的任务管理系统，重点展示 AI/LLM 方向的能力：自然语言建任务、自动标签/优先级推荐、任务拆解、任务摘要。

## 岗位方向

AI/LLM 开发方向

## 技术栈

- **语言**：Python 3.11+
- **框架**：FastAPI + Uvicorn + SQLAlchemy 2.0（同步引擎）
- **数据库**：MySQL 8（utf8mb4）
- **AI/LLM 方案**：DeepSeek（OpenAI 兼容接口，通过 `openai` SDK 调用）
- **其他工具**：Pydantic v2（校验）、pydantic-settings（配置）、PyMySQL（驱动）、pytest（测试）

## 已实现的功能

基础能力：
- [x] 任务 CRUD（CREATE / READ / UPDATE / DELETE）
- [x] 任务列表筛选（status / priority / tag）、排序、分页

AI 智能功能：
- [x] 智能任务生成（自然语言 → 结构化任务草稿）
- [x] 自动标签推荐
- [x] 优先级推荐
- [x] 任务分类
- [x] 任务拆解（复杂任务 → 子任务列表）
- [x] 任务摘要（每日/每周，结构化统计 + 自然语言）

明确未实现（v1 范围）：
- [ ] 语义搜索 / 相似任务检测（需向量库 + embedding，DeepSeek 无官方 embedding 接口）

## 项目结构

```
project/
├── README.md
├── DEVELOPMENT_PLAN.md        # 开发规划文档
├── requirements.txt
├── .env.example               # 环境变量模板（不含真实 key）
├── src/
│   ├── main.py                # FastAPI 入口 + 全局异常处理 + 健康检查
│   ├── config.py              # 读取 .env
│   ├── db.py                  # engine / session / Base
│   ├── models/
│   │   ├── task.py            # SQLAlchemy Task 模型 + 枚举
│   │   └── schemas.py         # Pydantic 请求/响应模型
│   ├── routes/
│   │   ├── tasks.py           # /tasks CRUD
│   │   └── ai.py              # /ai/* 智能功能
│   ├── services/
│   │   └── task_service.py    # 业务逻辑（CRUD/筛选/排序/分页）
│   ├── ai/
│   │   ├── client.py          # DeepSeek 封装（重试/超时/JSON mode）
│   │   ├── prompts.py         # 所有 prompt 模板
│   │   ├── parsers.py         # LLM 输出解析 + 宽松校验
│   │   ├── fallback.py        # 降级规则引擎（关键词/时间）
│   │   ├── generate.py        # 自然语言 → 任务草稿
│   │   ├── recommend.py       # 标签/优先级/分类推荐
│   │   ├── breakdown.py       # 任务拆解
│   │   └── summarize.py       # 任务摘要
│   └── utils/
│       └── time.py            # 时间表达式解析（规则版）
└── tests/                     # 测试（见「测试」一节）
```

## 安装与运行

### 1. 前置条件

- Python 3.11+
- MySQL 8（本地或远程，已创建数据库）

### 2. 安装依赖

```bash
# 建议在虚拟环境里
python -m venv venv
# Windows: venv\Scripts\activate    Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
```

### 3. 配置

```bash
# 复制模板并填入真实值（.env 不要提交到 git）
cp .env.example .env
```

`.env` 关键项：

```env
# 数据库
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=task_management
DB_CHARSET=utf8mb4

# DeepSeek
DEEPSEEK_API_KEY=sk-xxxx
DEEPSEEK_MODEL=DeepSeek-V4.1-Flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

**API key 安全**：`.env` 已被 `.gitignore` 忽略，只提交 `.env.example`。若 key 泄露，在 DeepSeek 控制台吊销重建，仅更新本地 `.env` 即可。

### 4. 运行

```bash
uvicorn src.main:app --reload
```

- 交互式 API 文档（Swagger）：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/healthz

> 启动时会自动 `create_all` 建表。生产环境应改用 Alembic 迁移。

## API 文档

统一前缀 `/api/v1`。

### 任务 CRUD

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/tasks` | 创建任务 |
| GET | `/api/v1/tasks` | 列表（筛选/排序/分页） |
| GET | `/api/v1/tasks/{id}` | 按 ID 获取 |
| PATCH | `/api/v1/tasks/{id}` | 部分更新 |
| DELETE | `/api/v1/tasks/{id}` | 删除 |

**创建任务**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"买日用品","description":"牛奶、鸡蛋","priority":"high","tags":["购物"],"due_date":"2026-09-18T15:00:00"}'
```

响应（`201`）：

```json
{
  "id": 1,
  "title": "买日用品",
  "description": "牛奶、鸡蛋",
  "status": "pending",
  "priority": "high",
  "tags": ["购物"],
  "due_date": "2026-09-18T15:00:00",
  "created_at": "2026-09-17T12:00:00",
  "updated_at": "2026-09-17T12:00:00"
}
```

**列表**（筛选/排序/分页）

```
GET /api/v1/tasks?status=pending&priority=high&tag=购物&sort=due_date&order=asc&page=1&page_size=20
```

响应：

```json
{
  "items": [ { "...": "任务对象" } ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

### AI 智能功能

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/ai/generate` | 自然语言 → 任务草稿（不落库） |
| POST | `/api/v1/ai/recommend` | 标题+描述 → 标签/优先级/分类 |
| POST | `/api/v1/ai/tasks/{id}/breakdown` | 任务拆解 |
| POST | `/api/v1/ai/summarize?period=day\|week` | 每日/每周摘要 |

**智能任务生成**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"明天下午3点提醒我买日用品"}'
```

响应（`source` 标记结果来自 LLM 还是降级规则）：

```json
{
  "title": "买日用品",
  "description": null,
  "priority": "medium",
  "tags": ["购物"],
  "due_date": "2026-09-18T15:00:00",
  "source": "llm"
}
```

**推荐**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/recommend \
  -H "Content-Type: application/json" \
  -d '{"title":"写季度报告","description":"给老板汇报 Q3 业绩"}'
```

响应：

```json
{ "tags": ["工作"], "priority": "medium", "category": "工作", "source": "llm" }
```

**任务拆解**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/tasks/1/breakdown
```

响应：

```json
{
  "task_id": 1,
  "subtasks": [
    { "title": "预订蛋糕", "priority": "medium" },
    { "title": "发出邀请", "priority": "high" }
  ],
  "source": "llm"
}
```

**任务摘要**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ai/summarize?period=week"
```

响应：

```json
{
  "period": "week",
  "stats": { "total": 8, "high_priority": 3, "completed": 2, "overdue": 1 },
  "summary": "本周共有 8 个任务，其中 3 个高优先级待处理，1 个已逾期，建议优先处理。",
  "source": "llm"
}
```

> 说明：AI 相关接口均返回 `source` 字段（`llm` / `fallback`），便于前端/调用方判断结果来源。生成/推荐先返回「草稿/建议」，由用户确认后再调 `/tasks` 落库，实现业务逻辑与 AI 逻辑解耦。

## AI 功能设计决策

**1. 为什么用 DeepSeek + openai SDK？**
DeepSeek 提供 OpenAI 兼容接口并支持 JSON 输出模式（`response_format={"type":"json_object"}`），可直接复用 `openai` SDK 的超时、重试、流式等能力，少造轮子。相比本地模型，无需下载权重、部署快，适合 2-4 小时的挑战场景。

**2. 为什么 JSON mode + temperature=0？**
任务抽取/推荐/拆解需要结构化输出。JSON mode 强制模型只返回合法 JSON，temperature=0 让输出确定、稳定，减少随机性导致的解析失败。

**3. 为什么「先返回草稿、用户确认后落库」？**
把 AI 逻辑与业务逻辑解耦（挑战明确要求）。AI 层只负责「建议」，落库仍走普通 CRUD，用户可覆盖自动推荐结果。这样 AI 层可独立演进、测试、替换。

**4. 为什么摘要数字由代码统计、LLM 只润色？**
LLM 对精确计数（total/high_priority 等）容易幻觉。改为：代码先算准数字，LLM 只把统计结果转成自然语言，从根源上避免编数字。

**5. 为什么做规则降级引擎？**
LLM 是外部依赖，存在超时/限流/返回异常等不确定性。规则引擎（关键词→标签/优先级、时间正则解析）作为「最后一道保险」，保证任何 AI 功能在 LLM 失败时仍返回合理结果或明确标记（`source="fallback"`），且 CRUD 完全不受影响。

**6. 为什么用同步 `def` 端点而非 `async`？**
FastAPI 会把同步端点丢进线程池，LLM 的阻塞调用（最长 60s）不会卡住事件循环，同时代码保持同步的简单性。未来并发上量再迁移 SQLAlchemy async + httpx async。

**7. 为什么不做语义搜索 / 向量库？**
DeepSeek 无官方 embedding 接口，引入本地 embedding 模型 + 向量库会显著增加复杂度，超出 2-4 小时范围。故 v1 明确不做，写入「未来改进」。

## Prompt 设计与示例

所有 prompt 集中在 `src/ai/prompts.py`。核心思路：**系统消息定 schema + 要求只输出 JSON + 无法确定的字段填 null**。

**智能任务生成（示例）**

```
系统：你是一个任务信息抽取助手。从用户的中文自然语言中抽取任务信息，只输出一个 JSON 对象。
字段：title(字符串)、description(字符串或null)、due_date(ISO8601带时区或null)、
priority("low"|"medium"|"high")、tags(字符串数组)。无法确定的字段填 null，不要编造。

用户：明天下午3点提醒我买日用品
```

**任务摘要（示例）**

```
系统：根据给定的统计数据生成一句简洁、自然的中文任务摘要。只输出 JSON {"summary":"..."}。
必须使用给定数字，不要编造或省略关键信息。

用户：周期：本周\n任务总数：8\n高优先级待处理：3\n已完成：2\n已逾期：1
```

> 迭代记录：最初未强制 JSON mode，模型偶尔返回 ```` ```json ... ``` ```` 包裹或前后带解释文字，导致解析失败。改进后：开启 JSON mode + 客户端剥离可能的代码块 + 宽松校验（单字段非法取默认值而非整体失败），解析稳定性显著提升。

## 挑战与解决方案

| 挑战 | 解决方案 |
|------|----------|
| LLM 返回不稳定（非 JSON / 字段类型错） | JSON mode + 重试 1 次 + Pydantic 宽松校验（`field_validator` 逐字段兜底） |
| LLM 超时 / 限流 / 网络异常 | openai SDK `max_retries` + `timeout`；最终失败回退规则引擎 |
| 中文时间表达多样（明天/下周五/X 小时后） | LLM 主解析 + 规则时间解析器（`utils/time.py`）兜底 |
| 摘要数字幻觉 | 数字由代码统计，LLM 只润色 |
| 时区不一致 | 约定统一存本地朴素时间，LLM 返回的带时区时间统一去时区（MVP 简化） |
| 业务与 AI 耦合 | 分层：routes → services → ai，AI 只返回建议、落库走 CRUD |

## 已知限制

- **模型幻觉**：日期、优先级等仍可能不准确，靠 JSON mode + 校验 + 规则兜底缓解，无法 100% 消除。
- **时延**：LLM 调用最长 60s，接口为同步阻塞（已走线程池避免阻塞并发）。
- **依赖外部 API**：DeepSeek 不可用时 AI 功能降级为规则结果，但生成/拆解质量下降。
- **无语义搜索**：未引入 embedding/向量库，搜索仅靠标签/关键词。
- **tags 用 JSON 列**：MySQL 下按标签过滤用 `JSON_CONTAINS`，可读性一般、不易加索引，大数据量下建议规范化。
- **无用户认证 / 多租户 / 限流**：挑战范围外，未实现。
- **建表用 `create_all`**：无迁移管理，生产应改 Alembic。

## 未来改进

- 接入向量库（ChromaDB）+ 本地 embedding，实现**语义搜索**与**相似任务检测**。
- tags 拆成规范化关联表（`tags` + `task_tags`），支持高效标签聚合与索引。
- 持久化子任务（`subtasks` 自关联表）与任务依赖。
- 全异步化（SQLAlchemy async + httpx async），提升高并发吞吐。
- 用户认证 / 多租户 / 限流；结构化日志 + 请求 ID。
- 提示词系统化评估（记录不同 prompt 的稳定性/准确率对比）。

## 测试

- `tests/test_crud.py`：CRUD + 筛选/排序/分页
- `tests/test_time_parser.py`：时间表达式规则解析（今天/明天/下周五/X 小时后等）
- `tests/test_fallback.py`：关键词→标签/优先级映射
- `tests/test_ai.py`：mock LLM 客户端，验证生成/推荐/拆解/摘要的正常路径 + 解析失败降级路径

```bash
pytest -q
```

## 使用 AI 助手声明

本项目开发过程中使用了 AI 助手（Claude Code）辅助编码与方案设计。所有技术选型、架构决策、prompt 设计均由本人理解、确认并最终负责。

## 花费时间

约 3 小时（编码时间，不含环境搭建与调试；请按实际填写）
