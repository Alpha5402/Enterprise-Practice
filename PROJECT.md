Codex 总控 Prompt（建议直接保存为 PROJECT_SPEC.md）

# 项目名称
基于 Claude + LangChain 的竞品动态追踪与智能对标分析系统
---
# 项目目标
构建一个企业级 AI Agent 系统，用于：
- 自动抓取竞品公开信息
- 分析价格战 / 新品发布 / 负面舆情
- 基于 Claude 自动生成竞争态势分析报告
- 提供 REST API 与 Web 可视化界面
- 支持 Docker 部署
系统必须具备：
- 工程化
- 可扩展
- 模块解耦
- 支持后续多 Agent 演进
不要生成 Demo Toy Project。
要按照真实企业项目标准组织代码。
---
# 技术栈要求
## 后端
- Python 3.12
- FastAPI
- LangChain
- LangGraph（优先于传统 AgentExecutor）
- Anthropic Claude SDK
- Pydantic v2
- SQLAlchemy
- APScheduler
- Redis
- ChromaDB
## 前端
- React
- TypeScript
- Vite
- TailwindCSS
- shadcn/ui
- TanStack Query
- Zustand
- Recharts
## AI / RAG
- Claude Sonnet 作为主模型
- Claude Haiku 作为轻量分类模型
- Embedding 使用 OpenAI Embedding 或 Claude Embedding
- Chroma 作为本地向量数据库
## 工程化
- Docker Compose
- ESLint
- Prettier
- Ruff
- pytest
- Vitest
- GitHub Actions
---
# 核心功能
系统包含以下模块：
## 1. 竞品管理
支持：
- 新增竞品
- 编辑竞品
- 删除竞品
- 设置监控维度
- 设置监控关键词
数据模型：
Competitor:
- id
- name
- industry
- description
- keywords
- enabled
---
## 2. 数据采集模块
实现：
- RSS 抓取
- 新闻网页抓取
- 定时任务采集
- 文本清洗
要求：
- 模块化 crawler
- 支持后续扩展 Twitter / Reddit / Github Release
- 每个 crawler 独立目录
目录：
backend/app/crawlers/
---
## 3. RAG 知识库
实现：
- 文本切块
- Embedding
- 向量化存储
- Retrieval
要求：
- 封装统一 VectorStoreService
- 支持切换 Chroma / FAISS
目录：
backend/app/rag/
---
## 4. AI Agent 系统
使用 LangGraph。
不要使用传统单 Agent 结构。
必须实现：
### Agent 节点
- sentiment_agent
- price_agent
- product_agent
- summary_agent
### Workflow
新闻内容
→ 分类
→ 多 Agent 并行分析
→ 汇总
→ 输出结构化报告
输出必须是严格 JSON。
禁止输出自由文本。
---
# 输出 Schema
```json
{
  "competitor": "",
  "dimension": "",
  "risk_level": "",
  "summary": "",
  "opportunity_points": [],
  "threat_points": [],
  "confidence_score": 0.0
}

使用：

* Pydantic
* Structured Output
* OutputParser

强制约束。

⸻

5. Prompt Engineering

创建：

backend/app/prompts/

包含：

* sentiment_prompt.md
* price_prompt.md
* product_prompt.md
* summary_prompt.md

Prompt 必须：

* 可维护
* 模块化
* 支持 few-shot
* 禁止硬编码在 Python 中

⸻

6. API 服务

FastAPI 提供：

Competitor APIs

* GET /competitors
* POST /competitors
* DELETE /competitors/:id

Analysis APIs

* POST /analyze
* GET /reports
* GET /reports/:id

Streaming

支持：

* SSE 流式输出

⸻

7. 前端

实现：

页面

* Dashboard
* Competitor Management
* Report Detail
* System Settings

Dashboard 内容

* 风险等级统计
* 最新竞品动态
* 趋势图
* 雷达图
* Agent 推理结果

⸻

8. 数据库设计

使用 PostgreSQL。

生成：

* SQLAlchemy models
* Alembic migration

核心表：

* competitors
* news_articles
* analysis_reports
* embeddings_metadata

⸻

9. 调度系统

使用 APScheduler。

支持：

* 定时抓取
* 定时分析
* 自动生成日报

⸻

10. 部署

必须生成：

* Dockerfile
* docker-compose.yml
* .env.example

Compose 包含：

* backend
* frontend
* postgres
* redis
* chromadb

⸻

11. 工程要求

必须满足：

* 类型完整
* 所有函数有 docstring
* 不允许 God Object
* 不允许超过 500 行的大文件
* 每个 service 独立
* 遵守 clean architecture

⸻

目录结构要求

project-root/
├── backend/
├── frontend/
├── docker/
├── docs/
├── scripts/
├── .github/

⸻

Codex 执行要求

非常重要：

1. 先生成完整目录结构
2. 再生成数据模型
3. 再生成基础 API
4. 再实现 RAG
5. 最后实现 Agent Workflow

不要一次性生成所有代码。

必须分阶段提交。

每完成一个阶段：

* 输出当前完成内容
* 输出目录树
* 输出下一阶段计划

⸻

禁止事项

禁止：

* 生成伪代码
* TODO 占位
* mock implementation
* fake AI logic
* 单文件塞全部代码
* 把 Prompt 写死在 Python

⸻

代码质量要求

生成代码时：

* 优先可维护性
* 优先模块解耦
* 优先工程结构
* 优先类型安全

而不是“快速能跑”。

⸻

第一阶段目标

现在先完成：

1. 项目目录初始化
2. Docker Compose
3. FastAPI 基础框架
4. React 前端初始化
5. PostgreSQL + SQLAlchemy
6. Competitor CRUD API
7. 基础 Dashboard 页面

完成后停止。