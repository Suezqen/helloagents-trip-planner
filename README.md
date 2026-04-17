# HelloAgents 智能旅行助手

一个基于 HelloAgents 构建的多智能体旅行规划系统，采用 `Vue 3 + TypeScript + FastAPI` 前后端分离架构，围绕景点搜索、天气查询、酒店推荐与行程规划四类任务组织协作流程，生成可编辑、可导出的完整旅行方案。

## 项目概述

系统接收用户输入的目的地、出行日期、交通方式、住宿偏好和兴趣标签，通过多智能体协作生成多日行程。项目集成高德地图 MCP Server，以标准化方式接入地图搜索、天气查询和路线相关能力，并在前端完成预算展示、地图可视化、结果编辑与 PDF/图片导出。

本项目适合作为一个完整的多智能体应用示例，覆盖了从请求建模、Agent 编排、外部工具接入，到前端展示与结果导出的完整链路。

## 核心能力

- 基于多智能体协作生成多日旅行计划
- 支持景点搜索、天气查询、酒店推荐与行程整合
- 通过共享 MCP 实例复用高德地图能力，降低资源占用
- 提供地图展示、景点标注与日内路线连线
- 支持预算汇总、行程编辑与结果导出
- 支持接入 Unsplash 图片服务增强结果展示

## 系统架构

### 后端

- `FastAPI` 提供 API 服务与数据模型校验
- `HelloAgents` 负责多智能体协作与工具调用
- `MCPTool` 连接高德地图 MCP Server
- 共享 MCP 单例机制用于复用地图能力
- 对 LLM 输出结果进行后处理与字段兜底，保证前端可稳定消费

### 前端

- `Vue 3 + TypeScript + Vite` 构建单页应用
- `Ant Design Vue` 负责界面组件与交互布局
- `AMap JS API` 负责地图可视化
- 支持表单草稿恢复、行程编辑、图片/PDF 导出

## 多智能体流程

系统默认包含以下四个角色：

1. 景点搜索 Agent  
   负责调用地图搜索工具，根据用户偏好筛选目的地景点。

2. 天气查询 Agent  
   负责获取目的地天气信息，为行程安排提供参考。

3. 酒店推荐 Agent  
   负责结合城市与住宿偏好搜索候选住宿信息。

4. 行程规划 Agent  
   综合景点、天气和住宿信息，输出结构化旅行计划。

## 技术栈

- Frontend: Vue 3, TypeScript, Vite, Ant Design Vue, AMap JS API
- Backend: FastAPI, Pydantic, HelloAgents
- Tool Integration: MCPTool, AMap MCP Server
- External Services: AMap, Unsplash
- LLM Provider: Compatible with OpenAI-style or other configured model endpoints

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

## 主要实现点

### 共享 MCP 实例

后端将高德地图 MCP 工具封装为共享实例，多个 Agent 复用同一个服务进程，避免重复启动与不必要的资源消耗，也更便于统一控制外部 API 调用频率。

### 结构化结果兜底

考虑到大模型输出可能存在字段缺失或格式不稳定的情况，后端在解析行程结果时会进行统一后处理，包括：

- 补齐每日日期、景点、酒店与三餐字段
- 对齐天气信息与旅行天数
- 在预算缺失时按门票、住宿、餐饮与交通方式进行汇总估算

### 前端结果页能力

结果页支持：

- 行程概览与预算展示
- 景点地图标注与路线连线
- 行程内容编辑与本地保存
- 图片与 PDF 导出

## 快速开始

### 1. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

### 2. 启动前端

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 3. 默认访问地址

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 环境变量

### `backend/.env`

- `LLM_MODEL_ID`
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_TIMEOUT`
- `AMAP_API_KEY`
- `UNSPLASH_ACCESS_KEY`
- `UNSPLASH_SECRET_KEY`
- `HOST`
- `PORT`
- `CORS_ORIGINS`

### `frontend/.env`

- `VITE_API_BASE_URL`
- `VITE_AMAP_WEB_JS_KEY`

## API 概览

主要接口包括：

- `POST /api/trip/plan` 生成旅行计划
- `GET /api/trip/health` 检查旅行规划服务状态
- `GET /api/map/poi` 搜索景点信息
- `GET /api/map/weather` 查询天气信息
- `POST /api/map/route` 获取路线规划结果
- `GET /api/poi/photo` 获取景点展示图片

## 适用场景

- 多智能体应用开发示例
- MCP 工具集成与共享实例设计示例
- 前后端分离的智能体产品原型
- 旅行规划与地图服务集成类项目展示

## License

See [LICENSE.txt](LICENSE.txt).
