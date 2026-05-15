# 企业竞争情报系统

基于 DeepSeek、LangChain、LangGraph、FastAPI 和 React 的企业级竞争动态跟踪与标杆分析系统。项目提供从竞品管理、数据采集、RAG 索引到 AI 分析报告生成的端到端工作流，并配套简体中文运营仪表盘。

## 当前能力

- Docker Compose 一键启动后端、前端、PostgreSQL、Redis 和 ChromaDB。
- 后端启动前自动执行 Alembic 迁移，新数据库卷可直接初始化表结构。
- FastAPI 分版本 API，提供竞品、采集、文章、索引、分析、报告与自动化接口。
- SQLAlchemy 数据模型覆盖竞品、新闻文章、分析报告、嵌入元数据和采集源。
- RSS 与网页采集器会统一清洗文本，并可保存为可复用采集源。
- RAG 索引使用 LangChain 兼容文本切分与 Chroma 向量存储。
- AI 分析使用 DeepSeek Chat Model，并通过 LangGraph 编排舆情、价格、产品和汇总分析节点。
- 前端使用 React、TypeScript、Vite、TailwindCSS 与 shadcn/ui 风格组件。
- 中文运营仪表盘支持竞品维护、采集、索引、分析、SSE 实时进度、报告查看和基础可视化。

## 快速开始

```bash
cp .env.example .env
```

编辑 `.env`，至少填写：

```bash
DEEPSEEK_API_KEY=你的 DeepSeek API Key
```

启动服务：

```bash
docker compose up --build
```

访问地址：

- 前端仪表盘：http://localhost:5173
- 后端 API 文档：http://localhost:8000/docs

## 使用流程

1. 在仪表盘中新建竞品。
2. 选择一个竞品作为当前工作对象。
3. 输入 RSS 或网页地址并执行采集，也可以保存为长期采集源。
4. 对已采集文章执行 RAG 索引。
5. 运行 DeepSeek + LangGraph 分析流程。
6. 在报告区查看风险等级、摘要、机会、风险与证据来源。

## 主要接口

- `GET /api/v1/competitors`：获取竞品列表。
- `POST /api/v1/competitors`：创建竞品。
- `DELETE /api/v1/competitors/{id}`：删除竞品。
- `POST /api/v1/collect`：按 URL 采集 RSS 或网页内容。
- `GET /api/v1/articles`：查询采集文章。
- `POST /api/v1/competitors/{id}/index`：为竞品文章建立 RAG 索引。
- `POST /api/v1/analyze`：运行分析并生成报告。
- `GET /api/v1/reports`：查询分析报告。
- `POST /api/v1/automation/daily-run`：对已保存采集源执行一次采集、索引和分析。

## 本地检查

```bash
scripts/check.sh
```

该脚本会执行后端 pytest、前端 ESLint 和前端生产构建。

## 注意事项

- DeepSeek 调用依赖 `.env` 中的 `DEEPSEEK_API_KEY`。
- RAG 索引默认使用 Chroma 的本地嵌入函数；首次索引时，运行环境可能需要缓存或下载对应嵌入模型。
- 前端生产构建若出现 Vite chunk size 提示，属于当前依赖体积的构建提醒，不影响系统运行。
