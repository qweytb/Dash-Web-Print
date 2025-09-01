import dash
from server import app
from dash.dependencies import Input, Output, State
from views.drag_and_drop import DragAndDrop
from views.print_preview import PrintPreview
from views.Print_template import PrintTemplate
from loguru import logger

from dash import html
from feffery_dash_utils.style_utils import style


@app.callback(
    Output("root-container", "children"),
    [
        Input("root-url", "href"),
        Input("root-url", "pathname"),
    ],
    State("local-large-storage", "data"),
    prevent_initial_call=True,
)
def router_root(href, pathname, local_data):
    if not pathname:
        return dash.no_update

    # logger.info("客户端缓存数据", local_data)

    # http://yangtianbao.cn:6969/print_preview?template=%E6%89%93%E5%8D%B0%E6%A8%A1%E6%9D%BF1&order_ID=12345
    if pathname == "/print_preview":
        return PrintPreview(href, local_data)
    elif pathname == "/print_template":
        return PrintTemplate(href)
    elif pathname == "/design_template":
        return DragAndDrop(href, local_data)
    else:
        return html.Div(
            [
                html.H1("404"),
            ],
            style=style(margin="20px"),
        )
