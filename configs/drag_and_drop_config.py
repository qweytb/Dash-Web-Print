from typing import Dict, Any
from dash import html
import feffery_utils_components as fuc
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style


# 组件渲染函数（复用逻辑）
def render_component(component_id, layout_data, disableDragging=False, json_data=None):
    """
    根据数据库中的 layout_data 和可选的 JSON 数据渲染组件。

    参数:
        component_id (str): 组件的唯一标识符
        layout_data (dict): 从数据库中获取的组件布局数据，包含位置、大小、类型等
        json_data (dict, optional): 外部传入的 JSON 数据，用于动态填充组件内容

    返回:
        FefferyRND: 渲染后的拖拽组件对象，或 None（如果类型不支持）
    """
    # 提取布局数据中的基本属性
    position = layout_data["position"]
    size = layout_data["size"]
    comp_type = layout_data["type"]
    extra = layout_data.get("extra", {}).copy()  # 复制 extra，避免修改原始数据

    # 如果提供了 JSON 数据，更新 extra 中的内容
    if json_data:
        if comp_type == "text":
            # print(extra.get("ddata_type", ""))

            if extra.get("ddata_type", "") != "静态数据":
                # 文本组件：使用 content_key 映射 JSON 数据，fallback 到默认 content
                content_key = extra.get("content_key", extra.get("content", ""))
                extra["content"] = json_data.get(content_key, extra.get("content", ""))
        elif comp_type == "table":
            # 表格组件：使用 JSON 数据中的 items 或其他指定键覆盖默认数据
            data_key = extra.get("data_key", "items")
            extra["data"] = json_data.get(data_key, extra.get("data", []))
        elif comp_type == "qrcode":
            if extra.get("ddata_type", "") != "静态数据":
                # 二维码组件：使用 JSON 数据中的 qrcode_url 或指定键覆盖默认值
                value_key = extra.get("value_key", "qrcode_url")
                extra["value"] = json_data.get(value_key, extra.get("value", ""))

    # 根据组件类型渲染
    if comp_type == "horizontal_line":
        return fuc.FefferyRND(
            [html.Div(style={"width": "100%", "borderTop": "2px solid #000"})],
            key=f"{component_id}+横线",
            id={"type": "RND", "id": component_id},
            size=size,
            maxHeight=2,
            position=position,
            disableDragging=disableDragging,
            direction=["right", "left"] if disableDragging == False else [],
            bounds="parent",
            selected=False,
        )
    elif comp_type == "vertical_line":
        return fuc.FefferyRND(
            [html.Div(style={"height": "100%", "borderLeft": "2px solid #000"})],
            key=f"{component_id}+竖线",
            id={"type": "RND", "id": component_id},
            size=size,
            maxWidth=2,
            position=position,
            disableDragging=disableDragging,
            direction=["top", "bottom"] if disableDragging == False else [],
            bounds="parent",
            selected=False,
        )
    elif comp_type == "text":
        return fuc.FefferyRND(
            [
                fac.AntdText(
                    extra["content"],  # 使用更新后的 content
                    strong=True,
                    style={"fontSize": extra["fontSize"]},
                )
            ],
            key=f"{component_id}+文本",
            id={"type": "RND", "id": component_id},
            size=size,
            position=position,
            disableDragging=disableDragging,
            direction=["top", "right", "bottom", "left"]
            if disableDragging == False
            else [],
            bounds="parent",
            selected=False,
            style=style(
                # 左边框 黑色 虚线
                border="1px dashed #000",
            )
            if disableDragging == False
            else {},
        )
    elif comp_type == "rectangle":
        return fuc.FefferyRND(
            [
                html.Div(
                    style={
                        "width": "100%",
                        "height": "100%",
                        "border": "2px solid #000",
                    }
                )
            ],
            key=f"{component_id}+矩形",
            id={"type": "RND", "id": component_id},
            size=size,
            minHeight=20,
            minWidth=20,
            position=position,
            disableDragging=disableDragging,
            direction=["top", "right", "bottom", "left"]
            if disableDragging == False
            else [],
            bounds="parent",
            selected=False,
        )
    elif comp_type == "table":
        return fuc.FefferyRND(
            [
                fac.AntdTable(
                    columns=extra["columns"],
                    data=extra["data"],  # 使用更新后的 data
                    bordered=True,
                    pagination=False,
                    style={"width": "100%", "height": "100%"},
                )
            ],
            key=f"{component_id}+表格",
            id={"type": "RND", "id": component_id},
            size=size,
            position=position,
            disableDragging=disableDragging,
            direction=[],
            bounds="parent",
            selected=False,
        )
    elif comp_type == "qrcode":
        return fuc.FefferyRND(
            [
                fuc.FefferyQRCode(
                    value=extra["value"],  # 使用更新后的 value
                    size=extra["size"],
                )
            ],
            key=f"{component_id}+二维码",
            id={"type": "RND", "id": component_id},
            size=size,
            minHeight=10,
            minWidth=10,
            position=position,
            disableDragging=disableDragging,
            direction=[],
            bounds="parent",
            selected=False,
        )
    return None


# 定义组件表单配置
COMPONENT_CONFIGS = {
    "横线": {
        "fields": [
            {"name": "组件ID", "component": "AntdInput", "label": "组件ID", "span": 24},
            {
                "name": "坐标",
                "component": "PositionInputs",
                "label": "坐标",
                "span": 24,
            },
            {
                "name": "W",
                "component": "AntdInputNumber",
                "label": "长度",
                "style": {"width": "100%"},
                "span": 24,
            },
        ],
        "default_values": lambda data: {
            "组件ID": data["id"],
            "X": data["坐标"]["x"],
            "Y": data["坐标"]["y"],
            "W": data["大小"]["width"],
        },
    },
    "竖线": {
        "fields": [
            {"name": "组件ID", "component": "AntdInput", "label": "组件ID", "span": 24},
            {
                "name": "坐标",
                "component": "PositionInputs",
                "label": "坐标",
                "span": 24,
            },
            {
                "name": "H",
                "component": "AntdInputNumber",
                "label": "长度",
                "style": {"width": "100%"},
                "span": 24,
            },
        ],
        "default_values": lambda data: {
            "组件ID": data["id"],
            "X": data["坐标"]["x"],
            "Y": data["坐标"]["y"],
            "H": data["大小"]["height"],
        },
    },
    "文本": {
        "fields": [
            {
                "name": "组件ID",
                "component": "AntdInput",
                "label": "组件ID",
                "span": 24,
            },  # 一行两个
            {
                "name": "坐标",
                "component": "PositionInputs",
                "label": "坐标",
                "span": 24,
            },  # 一行两个
            {
                "name": "宽高",
                "component": "SizeInputs",
                "label": "宽高",
                "span": 24,
            },
            {
                "name": "类型",
                "component": "AntdSelect",
                "label": "类型",
                "options": [{"label": i, "value": i} for i in ["静态数据", "动态数据"]],
                "span": 12,
            },  # 一行两个
            {
                "name": "字体大小",
                "component": "AntdInputNumber",
                "label": "字体大小",
                "style": {"width": "100%"},
                "span": 12,
            },  # 一行两个
            {
                "name": "内容",
                "component": "AntdInput",
                "label": "内容",
                "mode": "text-area",
            },  # 默认一行
        ],
        "default_values": lambda data: {
            "组件ID": data["id"],
            "X": data["坐标"]["x"],
            "Y": data["坐标"]["y"],
            "W": data["大小"]["width"],
            "H": data["大小"]["height"],
            "内容": "示例文本",
            "类型": "静态数据",
            "字体大小": 14,
        },
    },
    "矩形": {
        "fields": [
            {"name": "组件ID", "component": "AntdInput", "label": "组件ID"},
            {"name": "坐标", "component": "PositionInputs", "label": "坐标"},
            {"name": "宽高", "component": "SizeInputs", "label": "宽高"},
        ],
        "default_values": lambda data: {
            "组件ID": data["id"],
            "X": data["坐标"]["x"],
            "Y": data["坐标"]["y"],
            "W": data["大小"]["width"],
            "H": data["大小"]["height"],
        },
    },
    "表格": {
        "fields": [
            {"name": "组件ID", "component": "AntdInput", "label": "组件ID"},
            {"name": "坐标", "component": "PositionInputs", "label": "坐标"},
            {
                "name": "添加表格字段",
                "component": "AntdButton",
                "label": "添加表格字段",
                "type": "primary",
                "style": {"width": "100%"},
            },
            {
                "name": "table",
                "component": "TableEditor",
                "label": "表格字段",
                "id": lambda data: {
                    "type": "RND_FORM_DATA_TABLE_DATAINDEX",
                    "id": data["id"],
                },
            },
        ],
        "default_values": lambda data: {
            "组件ID": data["id"],
            "X": data["坐标"]["x"],
            "Y": data["坐标"]["y"],
        },
    },
    "二维码": {
        "fields": [
            {
                "name": "组件ID",
                "component": "AntdInput",
                "label": "组件ID",
                "span": 24,
            },  # 一行两个
            {
                "name": "坐标",
                "component": "PositionInputs",
                "label": "坐标",
                "span": 24,
            },  # 一行两个
            {
                "name": "数据类型",
                "component": "AntdSelect",
                "label": "数据类型",
                "options": [
                    {"label": i, "value": i} for i in ["静态数据", "动态数据", "URL"]
                ],
                "style": {"width": "100%"},
                "span": 12,
            },  # 一行两个
            {
                "name": "大小",
                "component": "AntdInputNumber",
                "label": "二维码大小",
                "style": {"width": "100%"},
                "span": 12,
            },  # 一行两个
            {"name": "数据框", "component": "AntdInput", "label": "数据框"},  # 默认一行
        ],
        "default_values": lambda data: {
            "组件ID": data["id"],
            "X": data["坐标"]["x"],
            "Y": data["坐标"]["y"],
            "数据类型": "静态数据",
            "大小": 100,
            "数据框": "数据框",
        },
    },
}


# 辅助函数：创建表单项
def create_form_item(
    config: Dict[str, Any], data: Dict[str, Any], is_button_row: bool = False
):
    component_map = {
        "AntdInput": fac.AntdInput,
        "AntdInputNumber": fac.AntdInputNumber,
        "AntdSelect": fac.AntdSelect,
        "AntdButton": lambda **kwargs: fac.AntdButton(
            children=config.get(
                "label", "按钮"
            ),  # 直接从 config 获取 label，不依赖 kwargs
            type=kwargs.get("type", "default"),
            style=kwargs.get("style"),
        ),
        "PositionInputs": lambda **kwargs: fac.AntdFlex(
            [
                fac.AntdInputNumber(name="X", addonBefore="X"),
                fac.AntdInputNumber(name="Y", addonBefore="Y"),
            ],
            gap=10,
        ),
        "SizeInputs": lambda **kwargs: fac.AntdFlex(
            [
                fac.AntdInputNumber(name="W", addonBefore="W"),
                fac.AntdInputNumber(name="H", addonBefore="H"),
            ],
            gap=10,
        ),
        "TableEditor": lambda **kwargs: fuc.FefferyDiv(
            [
                fac.AntdTable(
                    id=kwargs.get("id"),
                    columns=[
                        {
                            "title": "名称",
                            "dataIndex": "名称",
                            "editable": True,
                            "width": "25%",
                            "renderOptions": {"renderType": "ellipsis"},
                        },
                        {
                            "title": "绑定",
                            "dataIndex": "绑定",
                            "editable": True,
                            "width": "25%",
                            "renderOptions": {"renderType": "ellipsis"},
                        },
                        {
                            "title": "宽度",
                            "dataIndex": "宽度",
                            "editable": True,
                            "width": "25%",
                        },
                        {
                            "title": "操作",
                            "dataIndex": "操作",
                            "width": "25%",
                            "renderOptions": {
                                "renderType": "button",
                                "renderButtonPopConfirmProps": {
                                    "title": "确认执行？",
                                    "okText": "确认",
                                    "cancelText": "取消",
                                },
                            },
                        },
                    ],
                    data=[
                        {
                            "名称": "字段名称",
                            "绑定": "绑定字段",
                            "宽度": "宽度",
                            "操作": [
                                {
                                    "content": "删除",
                                    "type": "dashed",
                                    "danger": True,
                                    "custom": "balabalabalabala",
                                }
                            ],
                        }
                    ],
                    bordered=True,
                    pagination=False,
                )
            ],
            className={"ant-table-cell": {"padding": "0px"}},
        ),
    }

    Component = component_map[config["component"]]
    component_kwargs = {
        k: v
        for k, v in config.items()
        if k not in ["name", "component", "label", "span"]
    }
    if "id" in config:
        component_kwargs["id"] = config["id"](data)

    # 根据是否是按钮行或配置中的 span 值设置宽度
    span = 24 if is_button_row else config.get("span", 24)

    # 对于非按钮组件，保留 name 属性以确保表单值绑定
    if config["component"] != "AntdButton":
        component_kwargs["name"] = config.get("name")

    return fac.AntdCol(
        fac.AntdFormItem(
            Component(**component_kwargs),
            label=config.get("label", config.get("name", ""))
            if config["component"] != "AntdButton"
            else None,
        ),
        span=span,
    )
