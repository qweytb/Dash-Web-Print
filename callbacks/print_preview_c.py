from server import app
import dash
from dash import html, set_props
from dash.dependencies import Input, Output, State, ALL
import json
from feffery_dash_utils.style_utils import style
import feffery_utils_components as fuc
import feffery_antd_components as fac

from uuid import uuid4

from utils.ba64_pdf import base64_to_pdf_base64


# 路由里面渲染的组件，打印指定元素ding
@app.callback(
    Output("print-target", "targetSelector"),
    Input("print-target-trigger", "nClicks"),
    prevent_initial_call=True,
)
def get_print_target(静默):
    return "#print-preview-container"


# 获取转换好的图片消息，发送给打印客户端
@app.callback(
    Output("websocket-print", "operation", allow_duplicate=True),
    Output("websocket-print", "message"),
    Input("print-target", "screenshotResult"),
    State("print-target-select", "value"),
    prevent_initial_call=True,
)
def on_screenshot_result(screenshot_result, value):
    data = screenshot_result.get("dataUrl").split("base64,")[-1]

    uuid = str(uuid4())

    data = base64_to_pdf_base64(data)

    return "send", json.dumps(
        {
            "type": f"{value}",
            "url": f"{uuid}.pdf",
            "file_content": f"{data}",
        }
    )


# @app.callback(
#     Input("http-requests", "responseResult"),
#     prevent_initial_call=True,
# )
# def grt_http(responseResult):
#     print(responseResult)
#     if responseResult.get("status") == 200:
#         data = responseResult.get("data")
#         set_props(
#             "global-redirect",
#             {"children": fac.AntdMessage(content=f"返回的内容：{data}", type="info")},
#         )


# 获取打印机列表
@app.callback(
    Output("http-requests", "requestConfig", allow_duplicate=True),
    Input("print-target-list", "nClicks"),
    prevent_initial_call=True,
)
def get_printers(nClicks):
    return {"url": "http://127.0.0.1:12212/system/printers.json"}


@app.callback(
    Output("print-target-select", "value"),
    Output("print-target-select", "options"),
    Output("print-target-list", "loading"),
    Input("http-requests", "responseResult"),
    prevent_initial_call=True,
)
def get_printers_list(responseResult):
    if responseResult.get("status") == 200:
        data = responseResult.get("data")
        options = [
            {"label": printer["name"], "value": printer["name"]} for printer in data
        ]
        return data[0]["name"], options, False
    else:
        return dash.no_update


# 获取ws客户端的连接状态
@app.callback(
    Output("print-target-ws", "children"),
    Output("print-target-ws", "loading"),
    Output("websocket-print", "operation"),
    Input("websocket-print", "state"),
    Input("print-target-ws", "nClicks"),
    prevent_initial_call=True,
)
def get_ws_status(state, nClicks):
    if state == "open":
        return "已连接", False, dash.no_update
    elif state == "connecting":
        return "连接中", True, dash.no_update
    elif state == "closed":
        return "断开连接（点击重连）", False, "connect"  # （重新连接）
    elif state == "closing":
        return "断开连接中", False, dash.no_update
    else:
        return dash.no_update


@app.callback(
    Input("websocket-print", "latestMessage"),
    prevent_initial_call=True,
)
def get_ws_message(latestMessage):
    set_props(
        "global-redirect",
        {"children": fac.AntdMessage(content=latestMessage, type="info")},
    )


# 路由里面渲染的组件，打印指定元素ding
@app.callback(
    Output("print-target-window", "targetSelector"),
    Input("print-popup-window", "nClicks"),
    prevent_initial_call=True,
)
def get_print_target_2(nClicks):
    return "#print-preview-container"


@app.callback(
    Output("print-js-window", "jsString"),
    Input("print-target-window", "screenshotResult"),
    prevent_initial_call=True,
)
def execute_js_demo_2(screenshotResult):
    data = screenshotResult.get("dataUrl")  # .split("base64,")[-1]

    # 创建包含 base64 图像的 HTML 内容
    html_content = f"""
    <html>
        <body>
            <img src="{data}" style="width:100%;">
        </body>
    </html>
    """

    # 使用 iframe 打印
    js = f"""
    var iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    document.body.appendChild(iframe);
    iframe.contentDocument.write(`{html_content}`);
    iframe.contentDocument.close();
    iframe.onload = function() {{
        iframe.contentWindow.print();
        document.body.removeChild(iframe);
    }};
    """

    return js
