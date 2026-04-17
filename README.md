# 智能旅行助手

基于 HelloAgents 的多智能体旅行规划项目，采用 `Vue 3 + TypeScript + FastAPI` 的前后端分离结构，围绕“景点搜索、天气查询、酒店推荐、行程规划”四段式协作流程生成完整旅行方案。

这份仓库不是原始教程目录的镜像，我做了针对简历展示和独立仓库交付的整理：

- 把项目从教程章节目录中抽出来，调整成单项目根目录结构。
- 保留了原项目里一部分中文注释、四阶段多 Agent 规划流程和 MCP 接入痕迹。
- 补了后端共享 MCP 单例复用、预算/天气/餐饮兜底、健康检查等细节。
- 改了前端首页和结果页交互，增加草稿恢复、结果统计、地图中心点修正等实际使用细节。
- 删除了与旅行助手无关的教程章节、共创项目和文档目录，方便直接作为个人项目仓库展示。

## 功能概览

- 根据目的地、日期、交通方式、住宿偏好和旅行标签生成多日行程
- 使用高德地图 MCP Server 进行景点搜索、天气查询和地图可视化
- 支持酒店推荐、预算汇总、行程编辑和地图路线展示
- 支持结果页导出为图片或 PDF
- 支持使用 Unsplash 图片增强景点展示

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Ant Design Vue、AMap JS API
- 后端：FastAPI、HelloAgents、MCPTool、高德地图 MCP Server
- 外部能力：高德地图、Unsplash、兼容 OpenAI/DeepSeek 等 LLM 接口

## 目录结构

```text
.
├── backend
│   ├── app
│   │   ├── agents
│   │   ├── api
│   │   ├── models
│   │   └── services
│   ├── requirements.txt
│   └── run.py
├── frontend
│   ├── src
│   │   ├── services
│   │   ├── types
│   │   └── views
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 本次整理的关键修改

### 1. 共享 MCP 实例真正落地

原始版本里多 Agent 会单独创建 `MCPTool`，我把旅行规划 Agent 改成直接复用 `amap_service` 里的共享实例，和项目描述里的“共享 MCP 服务进程”保持一致。

### 2. 行程结果增加后处理兜底

LLM 返回 JSON 不稳定时，现在会自动：

- 补齐缺失日期、景点、酒店和三餐字段
- 对齐 `weather_info` 和旅行天数
- 根据门票、住宿、餐饮和交通方式补算预算

这样结果页不会因为模型漏字段而直接崩掉。

### 3. 前端更像真实做过一轮产品打磨

- 首页新增会话级草稿保存与恢复
- 结果页新增行程统计卡片
- 地图默认中心改为首个景点位置，不再固定北京
- 景点图片获取改成复用统一 API 封装，去掉硬编码地址

## 快速启动

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

### 前端

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

默认访问地址：

- 前端：`http://localhost:5173`
- 后端：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`

## 环境变量

### `backend/.env`

- `LLM_MODEL_ID`
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `AMAP_API_KEY`
- `UNSPLASH_ACCESS_KEY`
- `UNSPLASH_SECRET_KEY`

### `frontend/.env`

- `VITE_API_BASE_URL`
- `VITE_AMAP_WEB_JS_KEY`

## 说明

这个仓库基于 HelloAgents 教程中的旅行助手章节继续整理，保留了原有实现思路与部分注释，但目录、文档和部分交互逻辑已经按独立项目仓库重新收束，适合直接放在个人 GitHub 主页或简历项目列表中。
