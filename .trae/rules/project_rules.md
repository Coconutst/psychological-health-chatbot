你不需要加载向量数据库了，我已经执行了ingest.py这个脚本，加载成功了。后续过程你不需要再次加载向量数据库了。
PowerShell不支持&&语法。需要分两步执行命令。
记住mysql数据库名称：psy_chatbot_db
你不要修改代码后每次都要重启前端后端。不用重启。因为前端用的vue框架3，后端是fastapi
在使用 Vue 3 + FastAPI 开发时，其实完全可以做到 热更新 (hot reload)，避免每次修改代码都手动重启前端或后端。

✅ 前端 (Vue 3)
使用 npm run dev 自带的开发服务器。
Vite 会在保存文件后自动热更新，无需重启。
bash
复制代码
# 启动开发模式
npm run dev
修改 .vue 组件或 JS/TS 文件后，页面会自动刷新。
✅ 后端 (FastAPI)
使用 Uvicorn 的 --reload 参数，后端代码改动后自动重启。
bash
复制代码
uvicorn main:app --reload
这样每次保存 Python 文件时，服务会自动重启，无需手动操作。
