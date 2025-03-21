from server import app
import dash
from dash import html, set_props
from dash.dependencies import Input, Output, State, ALL
import json
from feffery_dash_utils.style_utils import style
import feffery_utils_components as fuc
import feffery_antd_components as fac

from uuid import uuid4
from loguru import logger

# 从 数据文件导入
from models.drag_and_drop_m import (
    ComponentLayout,
    PaperSize,
    Session,
)

from configs.drag_and_drop_config import (
    COMPONENT_CONFIGS,
    create_form_item,
    render_component,
)


# 监听拖拽事件
@app.callback(
    Output("listen-drop-target", "children"),
    Input("listen-drop", "dropEvent"),
    State("listen-drop-target", "children"),
    prevent_initial_call=True,
)
def listen_drop_event(dropEvent, children):
    uuid = str(uuid4())
    component = render_component(uuid, drop_data=dropEvent, disableDragging=False)
    return [component] if children is None else [*children, component]

    # """
    # {
    # "time": 1741185250633,
    # "data": {},
    # "pageX": 734,
    # "pageY": 329,
    # "clientX": 734,
    # "clientY": 329,
    # "screenX": 734,
    # "screenY": 416
    # }
    # """
    # pageX = dropEvent["pageX"] - 340
    # pageY = dropEvent["pageY"] - 140
    # data = dropEvent["data"]["info"]

    # uuid = str(uuid4())

    # if data == "横线":
    #     拖拽模块 = fuc.FefferyRND(
    #         [
    #             html.Div(
    #                 key=uuid,
    #                 style=style(
    #                     width="100%",
    #                     # 上边框 黑色
    #                     borderTop="2px solid #000",
    #                 ),
    #             )
    #         ],
    #         key=uuid + "+横线",
    #         id={"type": "RND", "id": uuid},
    #         size={"width": 100, "height": 2},
    #         maxHeight=2,
    #         position={"x": pageX, "y": pageY},
    #         direction=["right", "left"],
    #         bounds="parent",
    #         selected=True,
    #     )
    # elif data == "竖线":
    #     拖拽模块 = fuc.FefferyRND(
    #         [
    #             html.Div(
    #                 key=uuid,
    #                 style=style(
    #                     height="100%",
    #                     # 左边框 黑色
    #                     borderLeft="2px solid #000",
    #                 ),
    #             )
    #         ],
    #         key=uuid + "+竖线",
    #         id={"type": "RND", "id": uuid},
    #         size={"width": 2, "height": 200},
    #         maxWidth=2,
    #         position={"x": pageX, "y": pageY},
    #         direction=["top", "bottom"],
    #         bounds="parent",
    #         selected=True,
    #     )
    # elif data == "文本":
    #     拖拽模块 = fuc.FefferyRND(
    #         [
    #             fac.AntdText("示例文本", strong=True, style=style(fontSize=14)),
    #         ],
    #         key=uuid + "+文本",
    #         id={"type": "RND", "id": uuid},
    #         size={"width": 60, "height": 26},
    #         position={"x": pageX, "y": pageY},
    #         direction=["top", "right", "bottom", "left"],
    #         bounds="parent",
    #         selected=True,
    #         style=style(
    #             # 左边框 黑色 虚线
    #             border="1px dashed #000",
    #         ),
    #     )
    # elif data == "矩形":
    #     拖拽模块 = fuc.FefferyRND(
    #         [
    #             html.Div(
    #                 style=style(
    #                     width="100%",
    #                     height="100%",
    #                     # 左边框 黑色
    #                     # border="2px solid #000",
    #                     border="2px solid rgba(0, 123, 255, 1)",  # 内部边框
    #                 )
    #             )
    #         ],
    #         key=uuid + "+矩形",
    #         id={"type": "RND", "id": uuid},
    #         size={"width": 200, "height": 200},
    #         minHeight=20,
    #         minWidth=20,
    #         position={"x": pageX, "y": pageY},
    #         bounds="parent",
    #         # selected=False,
    #         selectedStyle={
    #             "boxShadow": "0 0 8px rgba(0, 123, 255, 0.6)",  # 外部阴影
    #             "border": "2px solid rgba(0, 123, 255, 0.8)",  # 外部边框
    #             "opacity": 0.9,  # 选中时的透明度
    #         },
    #     )
    # elif data == "表格":
    #     拖拽模块 = fuc.FefferyRND(
    #         [
    #             fac.AntdTable(
    #                 columns=[
    #                     {"title": "int型示例", "dataIndex": "int型示例"},
    #                     {"title": "float型示例", "dataIndex": "float型示例"},
    #                     {"title": "str型示例", "dataIndex": "str型示例"},
    #                 ],
    #                 data=[
    #                     {
    #                         "int型示例": 123,
    #                         "float型示例": 1.23,
    #                         "str型示例": "示例字符",
    #                     }
    #                 ],
    #                 bordered=True,
    #                 pagination=False,
    #                 style=style(
    #                     width="100%",
    #                     height="100%",
    #                 ),
    #             )
    #         ],
    #         key=uuid + "+表格",
    #         id={"type": "RND", "id": uuid},
    #         size={"width": 500, "height": 100},
    #         position={"x": 5, "y": pageY},
    #         direction=[],  # 关闭尺寸调整功能
    #         # dragAxis='y',
    #         bounds="parent",
    #         selected=True,
    #     )
    # elif data == "二维码":
    #     拖拽模块 = fuc.FefferyRND(
    #         [
    #             fuc.FefferyQRCode(
    #                 value="FefferyQRCode示例",
    #                 size=100,
    #             )
    #         ],
    #         key=uuid + "+二维码",
    #         id={"type": "RND", "id": uuid},
    #         size={"width": 100, "height": 100},
    #         minHeight=10,
    #         minWidth=10,
    #         position={"x": pageX, "y": pageY},
    #         direction=[],  # 关闭尺寸调整功能
    #         bounds="parent",
    #         selected=True,
    #     )

    # return [拖拽模块] if children == None else [*children, 拖拽模块]


# 更新回调中的表单生成逻辑
@app.callback(
    Output("component-edit-container", "children"),
    Input({"type": "RND", "id": ALL}, "position"),
    Input({"type": "RND", "id": ALL}, "size"),
    Input({"type": "RND", "id": ALL}, "selected"),
    Input({"type": "RND", "id": ALL}, "key"),
    prevent_initial_call=True,
)
def component_edit_container(position, size, selected, key):
    if not any(selected):
        return dash.no_update

    triggered_id = dash.ctx.triggered_id
    for i, k in enumerate(key):
        if k.split("+")[0] == triggered_id["id"]:
            component_key = k.split("+")[1]
            # logger.debug(size[i])
            data = {
                "坐标": position[i],
                "大小": {
                    key: int(value.replace("px", ""))
                    if isinstance(value, str)
                    else value
                    for key, value in size[i].items()
                },
                "key": component_key,
                "id": triggered_id["id"],
            }
            break
    else:
        return dash.no_update

    config = COMPONENT_CONFIGS.get(component_key)
    if not config:
        return dash.no_update

    form_items = [create_form_item(field, data) for field in config["fields"]]
    form_items.append(
        fac.AntdCol(
            fac.AntdFlex(
                [
                    fac.AntdButton(
                        "确认",
                        id={"type": "RND_Button_Confirm", "id": data["id"]},
                        type="primary",
                        style=style(width="50%"),
                    ),
                    fac.AntdButton(
                        "取消",
                        id={"type": "RND_Button_Cancel", "id": data["id"]},
                        type="primary",
                        style=style(width="50%"),
                    ),
                ],
                gap=10,
            ),
            span=24,
        )
    )

    default_values = config["default_values"](data)
    id = default_values["组件ID"]  # 提取组件ID
    # 保存到数据库
    try:
        # 创建数据库会话
        session = Session()
        # 检查是否已存在相同 component_id 的记录
        existing = session.query(ComponentLayout).filter_by(component_id=id).first()
        if existing:
            logger.debug(f"组件数据替换成功: {existing.layout_data}")
            comp_type = existing.layout_data.get("type")
            # default_values["X"] = existing.layout_data["position"]["x"]
            # default_values["Y"] = existing.layout_data["position"]["y"]
            if comp_type == "horizontal_line":
                pass
                # default_values["W"] = existing.layout_data["size"]["width"]
            elif comp_type == "vertical_line":
                pass
                # default_values["W"] = existing.layout_data["size"]["height"]
            elif comp_type == "text":
                default_values["内容"] = existing.layout_data["extra"]["content"]
                default_values["类型"] = existing.layout_data["extra"]["data_type"]
                default_values["字体大小"] = existing.layout_data["extra"]["fontSize"]
            elif comp_type == "rectangle":
                pass
                # default_values["W"] = existing.layout_data["size"]["width"]
                # default_values["W"] = existing.layout_data["size"]["height"]
            elif comp_type == "table":
                # default_values['X'] = existing.layout_data.get("X")
                # default_values['Y'] = existing.layout_data.get("Y")
                pass
            elif comp_type == "qrcode":
                default_values["数据类型"] = existing.layout_data["extra"]["data_type"]
                default_values["大小"] = existing.layout_data["extra"]["size"]
                default_values["数据框"] = existing.layout_data["extra"]["value"]

            # 捕获任何可能发生的异常
    except Exception as e:
        logger.debug(f"组件数据替换错误: {str(e)}")
        # 如果发生错误，回滚会话，撤销所有未提交的更改
        session.rollback()
    # 无论成功还是失败，都会执行的清理操作
    finally:
        # 关闭数据库会话，释放资源
        session.close()

    return fac.AntdForm(
        fac.AntdRow(form_items, gutter=10),
        id={"type": "RND_FORM_DATA", "id": data["id"]},
        enableBatchControl=True,
        layout="vertical",
        values=default_values,
        className={".ant-form-item": {"margin-bottom": "10px"}},
    )


# 设置纸张大小
@app.callback(
    Output("listen-drop-target", "style"),
    Input("Printed-paper", "value"),
    Input("Printed-paper-W", "value"),
    Input("Printed-paper-H", "value"),
    Input("listen-drop-target", "_width"),
    Input("listen-drop-target", "_height"),
    State("load-template-input", "value"),  # 新增：获取模板名称
    prevent_initial_call=True,
)
def Set_up_Printed_paper(value, w, h, _width, _height, template_name):
    if not template_name:  # 检查模板名称是否为空
        return dash.no_update

    # 根据选择确定纸张大小
    if value == "A4":
        width_mm, height_mm = 210, 297
        type_name = "A4"
    elif value == "A5":
        width_mm, height_mm = 210, 148
        type_name = "A5"
    elif value == "A4/3":
        width_mm, height_mm = 210, 99
        type_name = "A4/3"
    elif value == "自定义":
        if not w and not h:
            return dash.no_update
        width_mm, height_mm = int(w), int(h)
        type_name = f"Custom_{width_mm}x{height_mm}"
    else:
        return dash.no_update

    logger.debug(
        f"设置纸张大小为：{width_mm}mm x {height_mm}mm，xp宽高为：{_width}px x {_height}px"
    )

    try:
        session = Session()
        # 检查是否已有该模板的纸张大小记录
        paper = session.query(PaperSize).filter_by(template_name=template_name).first()
        if paper:
            # 如果记录存在，直接更新所有字段
            paper.type_name = type_name
            paper.width_mm = width_mm
            paper.height_mm = height_mm
            paper.extra = {
                "xp_width": _width,
                "xp_height": _height,
            }  # 修正：extra 应为字典
            session.commit()
        else:
            # 如果记录不存在，创建新记录
            paper = PaperSize(
                template_name=template_name,
                type_name=type_name,
                width_mm=width_mm,
                height_mm=height_mm,
                extra={"xp_width": _width, "xp_height": _height},
            )
            session.add(paper)
            session.commit()

    except Exception as e:
        logger.debug(f"Error: {e}")
    finally:
        session.close()  # 确保会话关闭

    # 返回样式
    return style(width=f"{width_mm}mm", height=f"{height_mm}mm")


# 修改并且保存拖拽的组件
@app.callback(
    Input({"type": "RND_Button_Confirm", "id": ALL}, "nClicks"),
    State({"type": "RND_FORM_DATA", "id": ALL}, "values"),
    State({"type": "RND_FORM_DATA_TABLE_DATAINDEX", "id": ALL}, "data"),
    State("load-template-input", "value"),
    prevent_initial_call=True,
)
def RND_Button_Confirm(nClicks, values, table_data, load_template_input):
    id = dash.ctx.triggered_id["id"]

    # 准备要保存到数据库的布局数据
    layout_data = {
        "position": {"x": values[0]["X"], "y": values[0]["Y"]},
        "size": {},
        "type": None,
        "extra": {},
    }

    if values[0].get("W") and not values[0].get("H"):  # 横线
        layout_data["size"] = {"width": values[0]["W"], "height": 2}
        layout_data["type"] = "horizontal_line"
        set_props(
            {"type": "RND", "id": id},
            {
                "position": {"x": values[0]["X"], "y": values[0]["Y"]},
                "size": {"width": values[0]["W"], "height": 2},
            },
        )
    elif values[0].get("H") and not values[0].get("W"):  # 竖线
        layout_data["size"] = {"width": 2, "height": values[0]["H"]}
        layout_data["type"] = "vertical_line"
        set_props(
            {"type": "RND", "id": id},
            {
                "position": {"x": values[0]["X"], "y": values[0]["Y"]},
                "size": {"width": 2, "height": values[0]["H"]},
            },
        )
    elif values[0].get("类型"):  # 文本
        layout_data["size"] = {"width": values[0]["W"], "height": values[0]["H"]}
        layout_data["type"] = "text"
        layout_data["extra"] = {
            "data_type": values[0]["类型"],
            "content": values[0]["内容"],
            "fontSize": values[0]["字体大小"],
        }
        set_props(
            {"type": "RND", "id": id},
            {
                "position": {"x": values[0]["X"], "y": values[0]["Y"]},
                "children": fac.AntdText(
                    values[0]["内容"],
                    strong=True,
                    style=style(fontSize=values[0]["字体大小"]),
                ),
                "size": {"width": values[0]["W"], "height": values[0]["H"]},
            },
        )
    elif values[0].get("W") and values[0].get("H"):  # 矩形
        layout_data["size"] = {"width": values[0]["W"], "height": values[0]["H"]}
        layout_data["type"] = "rectangle"
        set_props(
            {"type": "RND", "id": id},
            {
                "position": {"x": values[0]["X"], "y": values[0]["Y"]},
                "size": {"width": values[0]["W"], "height": values[0]["H"]},
            },
        )
    elif table_data:  # 表格
        layout_data["type"] = "table"
        layout_data["extra"] = {
            "columns": [
                {"title": "int型示例", "dataIndex": "int型示例"},
                {"title": "float型示例", "dataIndex": "float型示例"},
                {"title": "str型示例", "dataIndex": "str型示例"},
            ],
            "data": [
                {
                    "int型示例": 123,
                    "float型示例": 1.23,
                    "str型示例": "示例字符",
                }
            ],
        }
        set_props(
            {"type": "RND", "id": id},
            {
                "position": {"x": values[0]["X"], "y": values[0]["Y"]},
                "children": fac.AntdTable(
                    columns=[
                        {"title": "int型示例", "dataIndex": "int型示例"},
                        {"title": "float型示例", "dataIndex": "float型示例"},
                        {"title": "str型示例", "dataIndex": "str型示例"},
                    ],
                    data=[
                        {
                            "int型示例": 123,
                            "float型示例": 1.23,
                            "str型示例": "示例字符",
                        }
                    ],
                    bordered=True,
                    pagination=False,
                    style=style(
                        width="100%",
                        height="100%",
                    ),
                ),
            },
        )
    elif values[0].get("大小"):  # 二维码
        layout_data["size"] = {"width": values[0]["大小"], "height": values[0]["大小"]}
        layout_data["type"] = "qrcode"
        layout_data["extra"] = {
            "data_type": values[0]["数据类型"],
            "value": values[0]["数据框"],
            "size": values[0]["大小"],
        }
        set_props(
            {"type": "RND", "id": id},
            {
                "position": {"x": values[0]["X"], "y": values[0]["Y"]},
                "children": fuc.FefferyQRCode(
                    value=values[0]["数据框"],
                    size=values[0]["大小"],
                ),
                "size": {"width": values[0]["大小"], "height": values[0]["大小"]},
            },
        )
    else:
        set_props(
            "global-redirect",
            {"children": fac.AntdMessage(content="数据保存错误", type="info")},
        )

    # 保存到数据库
    try:
        # 创建数据库会话
        session = Session()
        # 检查是否已存在相同 component_id 的记录
        existing = session.query(ComponentLayout).filter_by(component_id=id).first()
        if existing:
            # 更新现有记录
            existing.template_name = load_template_input
            existing.layout_data = layout_data
        else:
            # 创建新记录
            component = ComponentLayout(
                component_id=id,
                template_name=load_template_input,
                layout_data=layout_data,
            )
            # 将新创建的组件对象添加到会话中准备保存
            session.add(component)
        # 提交事务，将更改保存到数据库
        session.commit()
        logger.debug(f"组件 {id} 保存成功")
    # 捕获任何可能发生的异常
    except Exception as e:
        logger.debug(f"保存到数据库失败: {str(e)}")
        # 如果发生错误，回滚会话，撤销所有未提交的更改
        session.rollback()
    # 无论成功还是失败，都会执行的清理操作
    finally:
        # 关闭数据库会话，释放资源
        session.close()


# 移除组件并且删除组件
@app.callback(
    Output("listen-drop-target", "children", allow_duplicate=True),
    Output("component-edit-container", "children", allow_duplicate=True),
    Input({"type": "RND_Button_Cancel", "id": ALL}, "nClicks"),
    State("listen-drop-target", "children"),
    State({"type": "RND_FORM_DATA", "id": ALL}, "values"),
    prevent_initial_call=True,
)
def remove_component_and_delete(n_clicks, children, values):
    if not n_clicks[0]:  # 如果没有点击按钮，则不执行任何操作
        return dash.no_update

    # 组件ID = {"type": "RND", "id": values[0]["组件ID"]}

    target_id = values[0]["组件ID"]  # 要删除的组件ID
    # 调试信息
    # for child in children:
    #     child_id = child.get("props", {}).get("id", {}).get("id", None)
    # logger.debug(f"检查组件ID: {child_id}")

    try:
        session = Session()
        # 检查并删除
        existing = (
            session.query(ComponentLayout).filter_by(component_id=target_id).first()
        )
        if existing:
            session.delete(existing)
            session.commit()
        else:
            # return f"未找到 component_id 为 {target_id} 的记录"
            return dash.no_update
    except Exception as e:
        session.rollback()  # 出错时回滚
        return dash.no_update
    finally:
        session.close()  # 确保关闭会话

        # 过滤掉目标ID的组件
        updated_children = [
            child
            for child in children
            if child.get("props", {}).get("id", {}).get("id", None) != target_id
        ]
        # logger.debug(f"更新后的children: {updated_children}")
        return updated_children, []


# 加载模板
@app.callback(
    Output("listen-drop-target", "children", allow_duplicate=True),
    Input("load-template", "nClicks"),
    State("load-template-input", "value"),
    State("json-data-input", "value"),  # 新增：JSON 数据输入框的值
    prevent_initial_call=True,
)
def load_components_from_db(n_clicks, template_name, json_data_str):
    """
    从数据库加载指定模板的组件并渲染到界面上。

    参数:
        n_clicks (int): 按钮点击次数，用于触发回调
        template_name (str): 用户输入的模板名称，用于查询数据库

    返回:
        list: 渲染后的组件列表，或 dash.no_update 表示不更新
    """
    # 检查模板名称是否为空
    # - 如果用户未输入模板名称，则无需执行后续逻辑，直接返回不更新
    if not template_name:
        return dash.no_update

    # 如果提供了 JSON 数据，尝试解析
    json_data = {}
    if json_data_str:
        try:
            json_data = json.loads(json_data_str)
        except json.JSONDecodeError:
            return dash.no_update

    # logger.debug("这是输入的json数据", json_data)
    try:
        # 创建数据库会话
        # - Session() 生成一个新的数据库会话实例，用于执行查询
        session = Session()
        # 查询数据库
        # - 从 ComponentLayout 表中筛选出 template_name 匹配的记录
        # - .all() 返回所有匹配的结果列表
        components = (
            session.query(ComponentLayout).filter_by(template_name=template_name).all()
        )
        # 关闭会话
        # - 查询完成后释放数据库连接，避免资源泄漏
        session.close()

        # 如果没有找到任何组件
        # - 返回空列表，清空目标容器内容
        if not components:
            return []
        rendered_components = [
            render_component(
                comp.component_id,
                comp.layout_data,
                disableDragging=False,
                json_data=json_data,
            )
            for comp in components
            if render_component(comp.component_id, comp.layout_data)
        ]
        return rendered_components
    except Exception as e:
        logger.debug(f"加载组件失败: {str(e)}")
        return dash.no_update


# 跳转预览
@app.callback(
    Output("jump-preview", "href"),
    Input("load-template-input", "value"),
    prevent_initial_call=True,
)
def preview_href(value):
    """
    生成预览页面的链接，并返回给前端。

    参数:
        n_clicks (int): 按钮点击次数，用于触发回调
        template_name (str): 用户输入的模板名称，用于生成链接

    返回:
        str: 生成的预览页面链接
    """
    # 如果模板名称为空，则返回空字符串

    return f"/print_preview?template={value}&order_ID=12345"
