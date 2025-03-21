## 项目名称：Dash-Web-Print


# 布局助手

**版本：** 0.1.2  
**许可证：** MIT
**最后更新：** 2025年3月21日  

## 项目概览

**布局助手** 是一个基于 [Dash](https://dash.plotly.com/) 和 [Flask](https://flask.palletsprojects.com/) 构建的开源 Web 应用程序，旨在简化布局设计、定制和打印流程。它提供了一个直观的拖拽界面，用户可以通过拖拽组件（如横线、竖线、文本、矩形、表格和二维码）设计模板，并支持通过 JSON 数据动态填充内容。该应用适用于创建发票、标签和其他自定义文档，具备 IP 访问控制、浏览器兼容性检查以及多种打印选项（静默打印、弹窗打印和 WebSocket 打印）。

项目使用 `feffery_antd_components` 和 `feffery_utils_components` 库，结合现代 Web 技术，为用户提供高效的布局设计和打印体验。

---

## 功能介绍

### 核心功能
- **拖拽界面：** 通过拖拽组件（如横线、文本、二维码）到画布上设计布局。
- **模板管理：** 保存、加载和预览存储在数据库中的模板。
- **动态数据集成：** 支持将 JSON 数据绑定到组件（如文本、表格、二维码）以实现动态内容渲染。
- **纸张大小定制：** 支持标准尺寸（A4、A5、A4/3）和自定义尺寸。
- **组件编辑：** 通过右侧表单调整组件属性（如位置、大小、内容）。

### 打印选项
- **静默打印：** 通过 WebSocket 服务器直接打印布局，无需用户交互。
- **WebSocket 打印：** 通过 WebSocket 服务器实时打印布局，无需用户交互。推荐工具：webapp-hardware-bridge，地址：https://github.com/qweytb/Dash-Web-Print/tree/maste
- **弹窗打印：** 在弹窗中生成预览以供手动打印。
- **PDF 导出：** 将布局转换为 PDF 格式（基于 base64 编码）。
- **打印机选择：** 通过 HTTP API 获取并选择可用打印机。

### 安全与兼容性
- **IP 白名单/黑名单：** 根据客户端 IP 地址限制访问。
- **浏览器兼容性检查：** 强制要求最低浏览器版本，阻止不支持的浏览器（如 IE）。
- **用户认证：** 集成 Flask-Login 进行基本用户管理（当前硬编码为 admin 用户）。

### 技术亮点
- 使用 Dash 和 Flask 实现响应式、服务器驱动的 UI。
- 通过 SQLAlchemy 处理数据库交互（基于 `Session` 使用推测为后端 ORM）。
- 支持 WebSocket 实现实时打印机通信。
- 模块化设计，组件和回调可重用。

---

## 项目架构

项目采用典型的 Dash 应用程序模块化结构，集成 Flask 处理服务器端逻辑。以下是核心组件概览：

### 目录结构
```
layout-assistant/
├── server.py              # Dash 应用初始化和 Flask 服务器设置
├── router/
│   └── router_root.py     # 主视图的 URL 路由逻辑
├── views/
│   ├── drag_and_drop.py   # 拖拽布局设计视图
│   └── print_preview.py   # 打印预览和打印功能视图
├── configs/
│   ├── ip_config.py       # IP 白名单/黑名单配置
│   ├── base_config.py     # 浏览器兼容性和基础设置
│   └── drag_and_drop_config.py # 组件渲染和表单配置
├── models/
│   └── drag_and_drop_m.py # 数据库模型（ComponentLayout、PaperSize）
├── callbacks/
│   ├── drag_and_drop_c.py # 拖拽功能的回调
│   └── print_preview_c.py # 打印预览的回调
├── utils/
│   └── ba64_pdf.py        # base64 转 PDF 工具
└── README.md              # 项目文档（本文档）
```

### 关键组件
1. **服务器设置 (`server.py`)：**
   - 初始化 Dash 应用和 Flask 服务器。
   - 配置 Flask-Login 用于用户认证。
   - 实现 IP 过滤和浏览器兼容性检查。

   **主要代码：**
   ```python
   from flask import request, abort
   from dash import Dash
   from flask_login import LoginManager

   app = Dash(__name__, title=f"布局助手{VERSION}", suppress_callback_exceptions=True)
   server = app.server
   server.secret_key = "ytb_147258369"
   login_manager = LoginManager()
   login_manager.init_app(server)

   @server.before_request
   def validate_ip_range():
       client_ip = request.remote_addr
       if ip_config.ENABLE_IP_BLACKLIST and ip_config.is_ip_in_list(client_ip, ip_config.BLACK_IP_LIST):
           abort(403, description="禁止：您的IP地址被列入黑名单。")
       if ip_config.ENABLE_IP_WHITELIST and not ip_config.is_ip_in_list(client_ip, ip_config.WHITE_IP_LIST):
           abort(403, description="禁止：您的IP地址是不允许的。")
   ```

2. **路由 (`router_root.py`)：**
   - 处理根路径 (`/`) 和打印预览 (`/print_preview`) 的 URL 路由。

   **主要代码：**
   ```python
   from dash.dependencies import Input, Output
   from server import app
   from views.drag_and_drop import DragAndDrop
   from views.print_preview import PrintPreview

   @app.callback(
       Output("root-container", "children"),
       [Input("root-url", "href"), Input("root-url", "pathname")]
   )
   def router_root(href, pathname):
       if not pathname:
           return dash.no_update
       if pathname == "/print_preview":
           return PrintPreview(href)
       elif pathname == "/":
           return DragAndDrop()
       return dash.no_update
   ```

3. **视图：**
   - `drag_and_drop.py`：定义拖拽界面，包含组件选择和纸张大小控制。
   - `print_preview.py`：渲染打印预览页面并提供打印选项。

   **拖拽界面代码片段：**
   ```python
   from dash import html
   import feffery_antd_components as fac
   import feffery_utils_components as fuc

   def DragAndDrop():
       return fac.AntdFlex(
           [
               html.Div([...]),  # 左侧组件选择面板
               html.Div([...]),  # 中间画布区域
               html.Div(id="component-edit-container", ...),  # 右侧编辑面板
           ],
           gap=10,
           style={"width": "100vw", "height": "100vh", "padding": "20px"}
       )
   ```

4. **配置 (`drag_and_drop_config.py`)：**
   - 定义组件渲染逻辑和编辑表单配置。

   **组件渲染代码片段：**
   ```python
   def render_component(component_id, layout_data=None, drop_data=None, disableDragging=False, json_data=None):
       if layout_data:
           position = layout_data["position"]
           size = layout_data["size"]
           comp_type = layout_data["type"]
       elif drop_data:
           position = {"x": drop_data["pageX"] - 340, "y": drop_data["pageY"] - 140}
           comp_type = drop_data["data"]["info"]
           size = None
       if comp_type == "文本":
           size = size or {"width": 60, "height": 26}
           return fuc.FefferyRND(
               [fac.AntdText("示例文本", strong=True, style={"fontSize": 14})],
               id={"type": "RND", "id": component_id},
               size=size,
               position=position,
               disableDragging=disableDragging
           )
   ```

5. **回调 (`drag_and_drop_c.py`)：**
   - 处理拖拽事件、组件更新和数据库交互。

   **拖拽事件处理：**
   ```python
   @app.callback(
       Output("listen-drop-target", "children"),
       Input("listen-drop", "dropEvent"),
       State("listen-drop-target", "children")
   )
   def listen_drop_event(dropEvent, children):
       uuid = str(uuid4())
       component = render_component(uuid, drop_data=dropEvent, disableDragging=False)
       return [component] if children is None else [*children, component]
   ```

---

## 安装指南

### 前提条件
- Python 3.10+
- 支持 SQLAlchemy 的关系型数据库（如 SQLite、PostgreSQL）
- WebSocket 打印服务器（运行于 `ws://127.0.0.1:12212/printer`）
- （可选）Gunicorn 用于生产部署

### 安装依赖
```bash
pip install dash flask flask-login feffery_antd_components feffery_utils_components feffery_dash_utils yarl loguru sqlalchemy ipaddress user-agents
```

### 安装步骤
1. **克隆仓库：**
   ```bash
   git clone https://github.com/yourusername/layout-assistant.git
   cd layout-assistant
   ```

2. **配置数据库：**
   - 在 `models/drag_and_drop_m.py` 中更新数据库 URI（例如 `sqlite:///layout.db`）。
   - 初始化数据库表（`ComponentLayout` 和 `PaperSize`）。

3. **运行应用：**
   - 开发环境：
     ```bash
     python server.py
     ```
   - 生产环境（使用 Gunicorn）：
     ```bash
     gunicorn -b 0.0.0.0:6969 server:app.server
     ```

4. **访问应用：**
   - 打开浏览器，访问 `http://localhost:6969`。

---

## 使用方法

### 设计布局
1. **进入设计界面：**
   - 访问根路径 (`/`)。
   - 从下拉菜单选择模板（如 "打印模板1"）或创建新模板。

2. **添加组件：**
   - 从左侧面板拖拽组件（如 "横线"、"文本"）到画布上。
   - 通过拖拽或右侧表单调整位置和大小。

3. **编辑组件：**
   - 点击组件选中，右侧显示编辑表单。
   - 修改属性（如位置、内容）并点击 "确认" 保存。

4. **设置纸张大小：**
   - 选择预设尺寸（A4、A5 等）或输入自定义尺寸。
   - 画布会自动调整。

5. **输入动态数据：**
   - 在文本区域输入 JSON 数据（如订单详情）以填充动态组件。

### 预览与打印
1. **预览布局：**
   - 点击 "跳转预览" 在新标签页打开打印预览。
   - URL 示例：`/print_preview?template=打印模板1&order_ID=12345`。

2. **打印选项：**
   - **弹窗打印：** 点击 "弹窗打印" 打开可打印窗口。
   - **静默打印：** 点击 "连接ws打印服务器" 连接 WebSocket，选择打印机后点击 "静默打印"。

---

## 贡献指南

欢迎为布局助手贡献代码！请按照以下步骤参与：

1. **Fork 仓库：**
   - 在 GitHub 上 Fork 并本地克隆。
   https://github.com/qweytb/Dash-Web-Print/tree/0.1.2
   - 在 gitee 上 Fork 并本地克隆。
   https://gitee.com/yang-tianbao95/dash-web-print/tree/0.1.2/

2. **搭建开发环境：**
   - 按照安装指南操作。

---
**创建环境**
命令根据 environment.yml 文件创建新环境：

mamba env create -f environment.yml