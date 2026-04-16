# Frontend — Vite + React 19 SPA

## 目录结构
```
src/
├── main.tsx             # 入口，挂载 React
├── App.tsx              # 路由定义 + QueryClient + AntD ConfigProvider
├── App.css              # 全局样式
├── pages/               # 页面组件（一个路由对应一个页面）
│   ├── Home.tsx         # / — 首页搜索 + 推荐基金列表
│   ├── FundDetail.tsx   # /fund/:fundCode — 基金详情 + AI 分析 + 对话
│   ├── Compare.tsx      # /compare — 多基金对比
│   ├── DcaCalculator.tsx # /calculator — 定投计算器
│   └── Recommend.tsx    # /recommend — 智能推荐
├── components/          # 共享 UI 组件
│   ├── AppHeader.tsx    # 顶部导航栏
│   ├── FundSearch.tsx   # 搜索框组件
│   ├── FundCard.tsx     # 基金卡片
│   ├── ChatPanel.tsx    # 对话面板（含 SSE 流式接收）
│   ├── AnalysisReport.tsx    # AI 分析报告展示
│   ├── PerformanceChart.tsx  # 净值走势图（ECharts）
│   ├── CompareRadar.tsx      # 对比雷达图
│   ├── HoldingsTable.tsx     # 持仓明细表
│   ├── UserProfileForm.tsx   # 用户投资画像表单
│   ├── FundQuickListsPanel.tsx # 快速基金列表面板
│   └── SubtleHint.tsx        # 提示组件
├── hooks/               # 自定义 React Hooks
│   ├── useFund.ts       # 基金数据查询 hooks（TanStack Query）
│   ├── useChat.ts       # 对话状态管理
│   └── useLocalFundLists.ts  # 本地基金列表持久化
├── api/                 # API 调用层
│   └── client.ts        # Axios 实例 + 所有 API 封装（含流式 fetch）
├── types/               # TypeScript 类型定义
│   ├── fund.ts          # 基金相关类型
│   └── chat.ts          # 对话相关类型
└── utils/
    └── storage.ts       # LocalStorage 工具
```

## 路由表
| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | Home | 首页搜索 + 推荐 |
| `/fund/:fundCode` | FundDetail | 基金详情 |
| `/compare` | Compare | 多基对比 |
| `/calculator` | DcaCalculator | 定投计算器 |
| `/recommend` | Recommend | 智能推荐 |

## 本地开发
```bash
npm install
npm run dev    # → http://localhost:5173
```

Vite 开发代理将 `/api` 转发到 `http://localhost:8000`。

## 关键约定
- 所有 API 调用通过 `api/client.ts`，不要在组件中直接 fetch
- 数据查询使用 TanStack Query hooks（在 `hooks/` 中封装）
- UI 组件使用 Ant Design，遵循 antd6 API
- 类型定义放在 `types/` 目录，不在组件内定义接口
- 图表统一使用 ECharts（`echarts-for-react`）
