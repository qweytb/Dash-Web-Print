from typing import Dict, Any
from dash import html
import feffery_utils_components as fuc
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style
from dash import set_props


# 组件渲染函数（统一处理拖拽创建和数据库加载）
def render_component(
    component_id,
    layout_data=None,
    drop_data=None,
    disableDragging=False,
    json_data=None,
):
    """
    统一渲染组件，支持从数据库加载或拖拽创建。

    参数:
        component_id (str): 组件ID
        layout_data (dict): 从数据库加载的布局数据 (可选)
        drop_data (dict): 从拖拽事件传入的数据 (可选)
        disableDragging (bool): 是否禁用拖拽
        json_data (dict): 动态JSON数据 (可选)
    """
    if layout_data:
        position = layout_data["position"]
        size = layout_data["size"]
        comp_type = layout_data["type"]
        extra = layout_data.get("extra", {}).copy()
    elif drop_data:
        position = {"x": drop_data["pageX"] - 340, "y": drop_data["pageY"] - 140}
        comp_type = drop_data["data"]["info"]
        size = None
        extra = {}
    else:
        return None

    # 处理JSON动态数据
    if json_data and comp_type in ["text", "table", "qrcode"]:
        if comp_type == "text" and extra.get("data_type", "静态数据") != "静态数据":
            content_key = extra.get("content_key", extra.get("content", ""))
            extra["content"] = json_data.get(content_key, extra.get("content", ""))
        elif comp_type == "table":
            data_key = extra.get("data_key", "items")
            extra["data"] = json_data.get(data_key, extra.get("data", []))
        elif comp_type == "qrcode" and extra.get("data_type", "静态数据") != "静态数据":
            value_key = extra.get("value_key", "qrcode_url")
            extra["value"] = json_data.get(value_key, extra.get("value", ""))

    # 通用组件配置（移除direction）
    base_config = {
        "id": {"type": "RND", "id": component_id},
        "position": position,
        "disableDragging": disableDragging,
        "bounds": "parent",
        "selected": False if layout_data else True,  # 拖拽时默认选中
    }

    # 类型特定配置
    if comp_type == "横线":
        size = size or {"width": 100, "height": 2}
        return fuc.FefferyRND(
            [html.Div(style=style(width="100%", borderTop="2px solid #000"))],
            key=f"{component_id}+横线",
            size=size,
            maxHeight=2,
            direction=["right", "left"] if not disableDragging else [],
            **base_config,
        )
    elif comp_type == "竖线":
        size = size or {"width": 2, "height": 200}
        return fuc.FefferyRND(
            [html.Div(style=style(height="100%", borderLeft="2px solid #000"))],
            key=f"{component_id}+竖线",
            size=size,
            maxWidth=2,
            direction=["top", "bottom"] if not disableDragging else [],
            **base_config,
        )
    elif comp_type in ["文本", "text"]:
        size = size or {"width": 60, "height": 26}
        extra.setdefault("content", "示例文本")
        extra.setdefault("fontSize", 14)
        return fuc.FefferyRND(
            [
                fac.AntdText(
                    extra["content"],
                    strong=True,
                    style=style(fontSize=extra["fontSize"]),
                )
            ],
            key=f"{component_id}+文本",
            size=size,
            style=style(border="1px dashed #000") if not disableDragging else {},
            direction=["top", "right", "bottom", "left"] if not disableDragging else [],
            **base_config,
        )
    elif comp_type in ["矩形", "rectangle"]:
        size = size or {"width": 200, "height": 200}
        return fuc.FefferyRND(
            [
                html.Div(
                    style=style(
                        width="100%",
                        height="100%",
                        border="2px solid rgba(0, 123, 255, 1)",
                    )
                )
            ],
            key=f"{component_id}+矩形",
            size=size,
            minHeight=20,
            minWidth=20,
            direction=["top", "right", "bottom", "left"] if not disableDragging else [],
            **base_config,
        )
    elif comp_type in ["表格", "table"]:
        size = size or {"width": 500, "height": 100}
        extra.setdefault(
            "columns",
            [
                {"title": "int型示例", "dataIndex": "int型示例"},
                {"title": "float型示例", "dataIndex": "float型示例"},
                {"title": "str型示例", "dataIndex": "str型示例"},
            ],
        )
        extra.setdefault(
            "data", [{"int型示例": 123, "float型示例": 1.23, "str型示例": "示例字符"}]
        )
        return fuc.FefferyRND(
            [
                fac.AntdTable(
                    columns=extra["columns"],
                    data=extra["data"],
                    bordered=True,
                    pagination=False,
                    style=style(width="100%", height="100%"),
                )
            ],
            key=f"{component_id}+表格",
            size=size,
            direction=[],  # 表格默认不可调整大小
            **base_config,
        )
    elif comp_type in ["二维码", "qrcode"]:
        size = size or {"width": 100, "height": 100}
        extra.setdefault("value", "FefferyQRCode示例")
        extra.setdefault("size", 100)
        return fuc.FefferyRND(
            [fuc.FefferyQRCode(value=extra["value"], size=extra["size"])],
            key=f"{component_id}+二维码",
            size=size,
            minHeight=10,
            minWidth=10,
            direction=[],  # 二维码默认不可调整大小
            **base_config,
        )
    return None


# 组件更新函数
def update_component(component_id, layout_data):
    """更新组件的属性并应用到UI"""
    comp_type = layout_data["type"]
    props = {"position": layout_data["position"], "size": layout_data["size"]}

    if comp_type in ["文本", "text"]:
        props["children"] = fac.AntdText(
            layout_data["extra"]["content"],
            strong=True,
            style=style(fontSize=layout_data["extra"]["fontSize"]),
        )
    elif comp_type in ["二维码", "qrcode"]:
        props["children"] = fuc.FefferyQRCode(
            value=layout_data["extra"]["value"], size=layout_data["extra"]["size"]
        )
    elif comp_type in ["表格", "table"]:
        props["children"] = fac.AntdTable(
            columns=layout_data["extra"]["columns"],
            data=layout_data["extra"]["data"],
            bordered=True,
            pagination=False,
            style=style(width="100%", height="100%"),
        )

    set_props({"type": "RND", "id": component_id}, props)


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
