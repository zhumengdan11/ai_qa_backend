# AI 问答后台管理系统

基于 Python-Django 实现的校内 Qwen3-AI 问答后台管理系统。

## 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 后端 | Python 3 + Django 6.0 | Django 一体化框架 |
| 前端 | HTML + CSS + JavaScript | Django Template 模板引擎 |
| 数据库 | MySQL / SQLite | MySQL（生产）/ SQLite（本地开发） |
| AI API | Qwen3 | 校内大模型 API |
| 部署 | Railway | 云端部署 |

## 功能特性

- ✅ AI 智能问答 - 对接校内 Qwen3 大模型
- ✅ 问答记录管理 - 检索、删除、批量清空
- ✅ 数据导出 - 导出为 TXT 文件
- ✅ 管理员鉴权 - Session 登录保护
- ✅ 分页展示 - 高效浏览大量记录
- ✅ 响应式设计 - 适配桌面与移动端

## 快速开始（本地开发）

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd ai_qa_backend
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，填写真实配置：

```bash
cp .env.example .env
```

### 4. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 启动服务

```bash
python manage.py runserver
```

访问 http://localhost:8000 即可使用。

## API 接口清单

| 方法 | 接口 | 功能 |
|------|------|------|
| POST | /api/chat | 提问（调用 AI 接口） |
| GET | /api/chat/list | 获取问答记录列表（支持分页+搜索） |
| POST | /api/chat/delete | 删除单条记录 |
| POST | /api/chat/batch-clear | 批量清空记录 |
| GET | /api/chat/export | 导出记录为 TXT |
| POST | /api/admin/login | 管理员登录 |
| GET | /api/admin/check | 检查登录状态 |
| GET | /api/admin/logout | 退出登录 |

## 部署到 Railway 🌐

### 前提条件

1. 注册 [Railway](https://railway.app/) 账号（推荐 GitHub 登录）
2. 将项目代码推送到 GitHub 仓库

### 部署步骤

#### 1. 推送代码到 GitHub

```bash
git init
git add .
git commit -m "init: AI QA backend system"
git remote add origin https://github.com/你的用户名/ai_qa_backend.git
git push -u origin main
```

#### 2. 在 Railway 中创建项目

1. 打开 Railway Dashboard → **New Project**
2. 选择 **Deploy from GitHub repo**
3. 授权并选择你的 `ai_qa_backend` 仓库
4. Railway 会自动检测 `railway.json` 并开始构建部署

#### 3. 添加 MySQL 数据库

1. 在项目页面点击 **New** → **Database** → **Add MySQL**
2. Railway 会自动创建 MySQL 并注入环境变量：
   - `MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_DATABASE`
   - `MYSQL_USER`、`MYSQL_PASSWORD`
   - `DATABASE_URL`（完整连接字符串）

#### 4. 配置环境变量

在 Railway Dashboard → 项目 → **Variables** 中添加：

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `DJANGO_SECRET_KEY` | Django 密钥（必填） | `python -c "import secrets; print(secrets.token_urlsafe(50))"` 生成 |
| `DJANGO_DEBUG` | 生产环境设为 False | `False` |
| `QWEN3_API_KEY` | 校内 Qwen3 API 密钥 | `sk-xxxx` |
| `QWEN3_BASE_URL` | 校内 API 地址 | `https://ai-api.school.edu.cn/v1` |
| `QWEN3_MODEL` | 模型名称 | `qwen3-7b` |
| `ADMIN_USERNAME` | 管理员用户名 | `admin` |
| `ADMIN_PASSWORD` | 管理员密码 | `your-strong-password` |

> **注意**: `MYSQL_*` 和 `DATABASE_URL` 由 Railway MySQL 插件自动注入，无需手动设置。

#### 5. 自动部署

Railway 会在以下情况自动重新部署：
- GitHub 仓库有新的推送
- 环境变量发生变化
- 数据库插件重启

部署状态可在 Railway Dashboard 中实时查看。

#### 6. 访问应用

部署完成后，Railway 会生成一个 `*.railway.app` 或 `*.up.railway.app` 域名，直接访问即可。

### Railway 部署架构

```
用户请求 → Railway Router → Gunicorn (4 workers)
                                   │
                            ┌──────┴──────┐
                            │  WhiteNoise  │ (静态文件服务)
                            └──────┬──────┘
                                   │
                            Django Application
                                   │
                            ┌──────┴──────┐
                            │   MySQL DB   │ (Railway MySQL)
                            └─────────────┘
```

### 注意事项

- **校园网限制**: AI 接口仅限校园网访问，部署后 API 调用需确保 Railway 能连接到校内网络
- **密钥安全**: 所有敏感信息通过 Railway 环境变量注入，不要提交 `.env` 文件到 Git
- **数据库备份**: Railway MySQL 会自动备份，可在 Dashboard 中管理
- **日志查看**: 在 Railway Dashboard → Deployments → 选择部署 → **Logs** 查看实时日志

## 项目结构

```
ai_qa_backend/
├── manage.py                 # Django 管理入口
├── requirements.txt          # Python 依赖
├── railway.json              # Railway 部署配置
├── Procfile                  # 进程启动文件
├── start.sh                  # 启动脚本
├── .env.example              # 环境变量示例
├── .gitignore                # Git 忽略规则
├── README.md                 # 项目文档
│
├── ai_qa_backend/            # Django 项目配置
│   ├── __init__.py           # pymysql 适配
│   ├── settings.py           # 核心配置（MySQL/SQLite双模式）
│   ├── urls.py               # 根路由
│   └── wsgi.py               # WSGI 入口
│
├── qa_app/                   # 问答应用
│   ├── models.py             # QARecord 数据模型
│   ├── views.py              # 全部视图与 API 逻辑
│   ├── urls.py               # 应用路由（11个接口）
│   ├── admin.py              # Django Admin 注册
│   └── templates/qa_app/
│       ├── base.html         # 基础模板
│       ├── chat.html         # AI 问答页面
│       ├── login.html        # 管理员登录
│       └── dashboard.html    # 管理后台
│
├── static/                   # 静态资源
│   └── css/style.css         # 主样式表
│
└── staticfiles/              # collectstatic 输出（生产用）
```
