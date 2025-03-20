import dash
from server import app
from dash.dependencies import Input, Output

from views.drag_and_drop import DragAndDrop
from views.print_preview import PrintPreview


@app.callback(
    Output("root-container", "children"),
    [
        Input("root-url", "href"),
        Input("root-url", "pathname"),
    ],
)
def router_root(href, pathname):
    if not pathname:
        return dash.no_update

    # http://yangtianbao.cn:6969/print_preview?template=%E6%89%93%E5%8D%B0%E6%A8%A1%E6%9D%BF1&order_ID=12345
    if pathname == "/print_preview":
        return PrintPreview(href)
    elif pathname == "/":
        return DragAndDrop()
    else:
        return dash.no_update
