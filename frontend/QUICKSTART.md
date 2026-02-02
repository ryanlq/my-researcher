# 前端快速启动指南

## 1. 安装依赖

```bash
cd frontend

# 使用 npm
npm install

# 如果安装慢，可以使用国内镜像
npm install --registry=https://registry.npmmirror.com
```

## 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.local.example .env.local

# 编辑（确认后端地址正确）
cat .env.local
```

应该包含：
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## 3. 确保后端运行

在另一个终端窗口：

```bash
cd backend

# 启动后端服务器
uv run python scripts/dev.py
```

确认看到：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 4. 启动前端

```bash
cd frontend

# 开发模式
npm run dev
```

应该看到：
```
▲ Next.js 14.2.15
- Local:        http://localhost:3000

✓ Ready in 2.3s
```

## 5. 访问应用

打开浏览器访问: http://localhost:3000

## 6. 测试功能

### 创建研究任务

1. 在"研究问题"输入框输入问题
2. 选择研究模式（标准/深度/多智能体）
3. 选择语言（中文/English）
4. 点击"开始研究"

### 观察实时进度

- 进度条显示百分比
- 显示当前查询内容
- 显示已完成/总查询数
- 显示研究深度
- 显示实时花费

### 查看结果

- 研究完成后自动显示结果
- Markdown 格式渲染
- 参考来源列表
- 导出按钮（功能待实现）

## 故障排除

### 无法连接后端

**错误**: `Network Error` 或 `ERR_CONNECTION_REFUSED`

**解决**:
1. 确认后端运行: `curl http://127.0.0.1:8000/health`
2. 检查 `.env.local` 中的 API 地址
3. 检查后端 CORS 配置

### WebSocket 连接失败

**错误**: Console 中显示 `WebSocket connection failed`

**解决**:
1. 确认后端支持 WebSocket
2. 检查防火墙设置
3. 查看浏览器 Console 的详细错误信息

### 样式显示异常

**错误**: 组件样式不正确

**解决**:
```bash
rm -rf .next node_modules
npm install
npm run dev
```

### 依赖安装失败

**错误**: `npm install` 报错

**解决**:
```bash
# 清理缓存
npm cache clean --force

# 使用国内镜像
npm install --registry=https://registry.npmmirror.com
```

## 开发提示

### 热重载

修改代码后，前端会自动刷新。如果没有：
- 按 `Ctrl+C` 停止
- 重新运行 `npm run dev`

### 查看日志

- 浏览器 Console: 查看 JavaScript 错误和 WebSocket 消息
- 浏览器 Network: 查看 API 请求和响应
- 后端终端: 查看服务器日志

### 调试

在组件中添加 `console.log`:

```typescript
console.log("Debug:", { currentResearch, progress });
```

## 下一步

- [ ] 实现用户认证（登录/注册）
- [ ] 添加研究历史管理
- [ ] 实现知识库功能
- [ ] 添加配置页面
- [ ] 实现报告导出
- [ ] 添加暗色模式切换
