import dash
from dash import html
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash.dependencies import Input, Output

# 实例化Dash应用对象
app = dash.Dash(__name__)

app.layout = fuc.FefferyDiv(
    id="div-demo1",
    enableEvents=["size"],
    style={
        "height": "200px",
        "background": "grey",
        "borderRadius": "8px",
        "color": "white",
        "padding": "20px",
    },
)


@app.callback(
    Output("div-demo1", "children"),
    [Input("div-demo1", "_width"), Input("div-demo1", "_height")],
    # prevent_initial_call=True,
)
def div_demo1(_width, _height):
    return f"_width: {_width}  _height: {_height}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6969, debug=True)
