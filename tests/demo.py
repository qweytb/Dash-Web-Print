import dash
from dash import html, dcc, callback, Output, Input, State
import feffery_antd_components as fac
import feffery_utils_components as fuc

# 初始化 Dash 应用，加载 Fabric.js
app = dash.Dash(
    __name__,
    external_scripts=[
        "https://cdnjs.cloudflare.com/ajax/libs/fabric.js/6.6.1/fabric.min.js"
    ],
)

# 定义页面布局
app.layout = html.Div(
    [
        # 使用 feffery-antd-components 的按钮
        fac.AntdButton("添加矩形", id="add-rect-btn", type="primary"),
        fac.AntdButton(
            "添加文字", id="add-text-btn", type="dashed", style={"marginLeft": "10px"}
        ),
        # 使用 feffery-utils-components 添加样式
        fuc.FefferyStyle(
            rawStyle="""
        #canvas-container { margin-top: 20px; }
        #fabric-canvas { border: 1px solid #ddd; }
    """
        ),
        # 画布容器
        html.Div(
            [html.Canvas(id="fabric-canvas", width=600, height=400)],
            id="canvas-container",
        ),
        # 用于触发 JavaScript 执行的组件
        fuc.FefferyExecuteJs(id="execute-js"),
        # 初始化标志
        dcc.Store(id="canvas-init", data="init"),
    ]
)


# 回调：初始化 Fabric.js 画布
@callback(
    Output("execute-js", "jsString"),
    Input("canvas-init", "data"),
    # prevent_initial_call=False,
)
def init_canvas(init):
    js_code = """
    if (typeof fabric !== 'undefined' && !window.canvas) {
        var canvas = new fabric.Canvas('fabric-canvas');
        window.canvas = canvas;
        fabric.Object.prototype.transparentCorners = false;
        fabric.Object.prototype.cornerColor = 'blue';
        fabric.Object.prototype.cornerStyle = 'circle';
        console.log('Canvas initialized');
    }
    """
    return js_code


# 回调：添加矩形和文字
@callback(
    Output("execute-js", "jsString", allow_duplicate=True),
    Input("add-rect-btn", "nClicks"),
    prevent_initial_call=True,
)
def update_canvas(nClicks):
    if not nClicks:
        return ""

    # 定义删除和克隆图标的 SVG 数据
    js_code = """
    if (typeof fabric === 'undefined' || !window.canvas) {
        console.log('Fabric.js 未加载或画布未初始化');
        return;
    }

    const deleteIcon = "data:image/svg+xml,%3C%3Fxml version='1.0' encoding='utf-8'%3F%3E%3C!DOCTYPE svg PUBLIC '-//W3C//DTD SVG 1.1//EN' 'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'%3E%3Csvg version='1.1' id='Ebene_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' width='595.275px' height='595.275px' viewBox='200 215 230 470' xml:space='preserve'%3E%3Ccircle style='fill:%23F44336;' cx='299.76' cy='439.067' r='218.516'/%3E%3Cg%3E%3Crect x='267.162' y='307.978' transform='matrix(0.7071 -0.7071 0.7071 0.7071 -222.6202 340.6915)' style='fill:white;' width='65.545' height='262.18'/%3E%3Crect x='266.988' y='308.153' transform='matrix(0.7071 0.7071 -0.7071 0.7071 398.3889 -83.3116)' style='fill:white;' width='65.544' height='262.179'/%3E%3C/g%3E%3C/svg%3E";
    const cloneIcon = "data:image/svg+xml,%3C%3Fxml version='1.0' encoding='iso-8859-1'%3F%3E%3Csvg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 55.699 55.699' width='100px' height='100px' xml:space='preserve'%3E%3Cpath style='fill:%23010002;' d='M51.51,18.001c-0.006-0.085-0.022-0.167-0.05-0.248c-0.012-0.034-0.02-0.067-0.035-0.1 c-0.049-0.106-0.109-0.206-0.194-0.291v-0.001l0,0c0,0-0.001-0.001-0.001-0.002L34.161,0.293c-0.086-0.087-0.188-0.148-0.295-0.197 c-0.027-0.013-0.057-0.02-0.086-0.03c-0.086-0.029-0.174-0.048-0.265-0.053C33.494,0.011,33.475,0,33.453,0H22.177 c-3.678,0-6.669,2.992-6.669,6.67v1.674h-4.663c-3.678,0-6.67,2.992-6.67,6.67V49.03c0,3.678,2.992,6.669,6.67,6.669h22.677 c3.677,0,6.669-2.991,6.669-6.669v-1.675h4.664c3.678,0,6.669-2.991,6.669-6.669V18.069C51.524,18.045,51.512,18.025,51.51,18.001z M34.454,3.414l13.655,13.655h-8.985c-2.575,0-4.67-2.095-4.67-4.67V3.414z M38.191,49.029c0,2.574-2.095,4.669-4.669,4.669H10.845 c-2.575,0-4.67-2.095-4.67-4.669V15.014c0-2.575,2.095-4.67,4.67-4.67h5.663h4.614v10.399c0,3.678,2.991,6.669,6.668,6.669h10.4 v18.942L38.191,49.029L38.191,49.029z M36.777,25.412h-8.986c-2.574,0-4.668-2.094-4.668-4.669v-8.985L36.777,25.412z M44.855,45.355h-4.664V26.412c0-0.023-0.012-0.044-0.014-0.067c-0.006-0.085-0.021-0.167-0.049-0.249 c-0.012-0.033-0.021-0.066-0.036-0.1c-0.048-0.105-0.109-0.205-0.194-0.29l0,0l0,0c0-0.001-0.001-0.002-0.001-0.002L22.829,8.637 c-0.087-0.086-0.188-0.147-0.295-0.196c-0.029-0.013-0.058-0.021-0.088-0.031c-0.086-0.03-0.172-0.048-0.263-0.053 c-0.021-0.002-0.04-0.013-0.062-0.013h-4.614V6.67c0-2.575,2.095-4.67,4.669-4.67h10.277v10.4c0,3.678,2.992,6.67,6.67,6.67h10.399 v21.616C49.524,43.26,47.429,45.355,44.855,45.355z'/%3E%3C/svg%3E%0A";

    const deleteImg = document.createElement('img');
    deleteImg.src = deleteIcon;
    const cloneImg = document.createElement('img');
    cloneImg.src = cloneIcon;

    // 定义删除和克隆函数
    function deleteObject(eventData, transform) {
        const canvas = transform.target.canvas;
        canvas.remove(transform.target);
        canvas.requestRenderAll();
    }

    function cloneObject(eventData, transform) {
        const canvas = transform.target.canvas;
        transform.target.clone().then((cloned) => {
            cloned.left += 10;
            cloned.top += 10;
            cloned.controls.deleteControl = transform.target.controls.deleteControl;
            cloned.controls.cloneControl = transform.target.controls.cloneControl;
            canvas.add(cloned);
        });
    }

    function renderIcon(icon) {
        return function(ctx, left, top, styleOverride, fabricObject) {
            const size = this.cornerSize;
            ctx.save();
            ctx.translate(left, top);
            ctx.rotate(fabric.util.degreesToRadians(fabricObject.angle));
            ctx.drawImage(icon, -size / 2, -size / 2, size, size);
            ctx.restore();
        };
    }

    // 创建矩形并添加控件
    const rect = new fabric.Rect({
        left: 100,
        top: 50,
        fill: 'yellow',
        width: 200,
        height: 100,
        objectCaching: false,
        stroke: 'lightgreen',
        strokeWidth: 4
    });

    rect.controls.deleteControl = new fabric.Control({
        x: 0.5,
        y: -0.5,
        offsetY: -16,
        offsetX: 16,
        cursorStyle: 'pointer',
        mouseUpHandler: deleteObject,
        render: renderIcon(deleteImg),
        cornerSize: 24
    });

    rect.controls.cloneControl = new fabric.Control({
        x: -0.5,
        y: -0.5,
        offsetY: -16,
        offsetX: -16,
        cursorStyle: 'pointer',
        mouseUpHandler: cloneObject,
        render: renderIcon(cloneImg),
        cornerSize: 24
    });

    window.canvas.add(rect);
    window.canvas.setActiveObject(rect);
    window.canvas.renderAll();
    console.log('矩形已添加');
    """
    return js_code


# 运行应用
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6969, debug=True)
