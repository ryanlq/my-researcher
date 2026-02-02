# GPT-Researcher Frontend

基于 Next.js 14 和 shadcn/ui 的现代化前端应用。

## 技术栈

- **框架**: Next.js 14 (App Router)
- **UI 组件**: shadcn/ui + Radix UI
- **样式**: TailwindCSS
- **动画**: Framer Motion
- **状态管理**: Zustand
- **HTTP 客户端**: Axios
- **实时通信**: WebSocket
- **Markdown**: React Markdown + remark-gfm

## 项目结构

```
frontend/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── layout.tsx    # 根布局
│   │   ├── page.tsx      # 主页（研究工作台）
│   │   └── globals.css   # 全局样式
│   ├── components/       # React 组件
│   │   ├── ui/           # shadcn/ui 基础组件
│   │   ├── ResearchProgress.tsx  # 进度显示
│   │   └── ResearchResults.tsx   # 结果展示
│   ├── lib/              # 工具函数
│   │   ├── api.ts        # API 客户端 + WebSocket
│   │   └── utils.ts      # 通用工具
│   ├── stores/           # Zustand 状态管理
│   │   └── research.ts   # 研究状态
│   └── types/            # TypeScript 类型
│       └── research.ts   # 研究相关类型
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 快速开始

### 1. 安装依赖

```bash
cd frontend

# 使用 npm
npm install

# 或使用 yarn
yarn install

# 或使用 pnpm
pnpm install
```

### 2. 配置环境变量

```bash
cp .env.local.example .env.local
```

编辑 `.env.local`:

```bash
# 后端 API 地址
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:3000

### 4. 构建生产版本

```bash
npm run build
npm start
```

## 功能特性

### ✅ 已实现

- **研究工作台**: 输入查询、选择研究模式、创建研究任务
- **实时进度**: WebSocket 连接、实时显示研究进度
- **结果展示**: Markdown 渲染、来源列表、导出功能（UI）
- **响应式设计**: 支持桌面和移动设备
- **暗色模式**: 支持亮色/暗色主题切换

### 🚧 待实现

- 用户认证（登录/注册）
- 研究历史管理
- 知识库管理（文档上传、向量化）
- 配置页面（LLM、搜索引擎配置）
- 成本统计和使用分析
- 报告导出功能（PDF、DOCX）

## 组件说明

### ResearchProgress

实时显示研究进度，包括：
- 进度百分比
- 当前查询内容
- 已完成/总查询数
- 研究深度
- 实时花费

使用 WebSocket 连接后端，自动重连。

### ResearchResults

展示研究结果，包括：
- 研究问题
- 参考来源列表
- Markdown 格式报告
- 导出按钮（Markdown/PDF）

## API 集成

### HTTP API

```typescript
import { api } from '@/lib/api';

// 创建研究
const response = await api.post('/research', {
  query: '...',
  report_type: 'deep',
  language: 'chinese',
});

// 获取研究详情
const research = await api.get(`/research/${id}`);

// 列出研究
const researches = await api.get('/research');
```

### WebSocket

```typescript
import { WebSocketClient } from '@/lib/api';

const ws = new WebSocketClient(researchId);

ws.connect(
  (data) => console.log('Message:', data),
  (error) => console.error('Error:', error),
  () => console.log('Closed')
);
```

## 状态管理

使用 Zustand 管理全局状态：

```typescript
import { useResearchStore } from '@/stores/research';

const {
  researches,
  currentResearch,
  progress,
  addResearch,
  updateResearch,
} = useResearchStore();
```

## 样式定制

### 颜色主题

在 `src/app/globals.css` 中修改 CSS 变量：

```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96.1%;
  /* ... */
}
```

### Tailwind 配置

编辑 `tailwind.config.ts` 自定义主题。

## 开发建议

### 添加新的 UI 组件

```bash
# 使用 shadcn/ui CLI（需要先安装）
npx shadcn-ui@latest add [component-name]
```

### 调试 WebSocket

打开浏览器开发者工具 → Console，查看 WebSocket 日志。

### 查看网络请求

开发者工具 → Network 标签，过滤 XHR 和 WS。

## 故障排除

### CORS 错误

确保后端 `CORS_ORIGINS` 包含前端地址：

```bash
# backend/.env
CORS_ORIGINS=["http://localhost:3000"]
```

### WebSocket 连接失败

1. 检查后端是否运行
2. 检查防火墙设置
3. 确认 WebSocket URL 正确

### 构建失败

删除 `.next` 和 `node_modules`，重新安装：

```bash
rm -rf .next node_modules
npm install
npm run build
```

## 性能优化

- 使用 React.memo 避免不必要的重渲染
- 图片使用 next/image 优化
- 路由使用动态导入减少初始加载
- 启用 SWC 压缩（Next.js 默认）

## 许可证

MIT
