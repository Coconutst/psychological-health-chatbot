# 心理咨询聊天机器人 - 前端

基于 Vue 3 + Vite 构建的简洁前端应用。

## 功能特性

- 用户注册和登录
- 实时聊天对话
- 登录状态持久化
- 响应式设计
- 简洁的用户界面

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 快速的前端构建工具
- **Axios** - HTTP 客户端
- **原生 CSS** - 简洁的样式设计

## 项目结构

```
fronted/
├── src/
│   ├── api/
│   │   └── index.js          # API 接口封装
│   ├── utils/
│   │   └── cookie.js         # Cookie 工具函数
│   ├── App.vue               # 主应用组件
│   ├── main.js               # 应用入口
│   └── style.css             # 全局样式
├── index.html                # HTML 模板
├── package.json              # 项目配置
├── vite.config.js            # Vite 配置
└── README.md                 # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
cd fronted
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 3. 构建生产版本

```bash
npm run build
```

## 配置说明

### API 代理配置

在 `vite.config.js` 中配置了 API 代理，将 `/api` 请求代理到后端服务器：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### 环境要求

- Node.js >= 16
- npm >= 7

## 使用说明

1. **注册账户**：首次使用需要注册新账户
2. **登录系统**：使用邮箱和密码登录
3. **开始聊天**：登录后即可与心理健康助手对话
4. **自动保存**：登录状态会自动保存，刷新页面不会丢失

## 开发说明

- 所有 API 请求都通过 `src/api/index.js` 统一管理
- 用户认证使用 JWT Token，存储在 Cookie 中
- 组件采用 Vue 3 Composition API 编写
- 样式使用原生 CSS，保持简洁

## 注意事项

- 确保后端 API 服务器在 http://localhost:8000 运行
- 开发时前端服务器默认运行在 http://localhost:3000
- 生产环境需要配置正确的 API 地址