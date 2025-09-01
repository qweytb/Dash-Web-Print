from server import app
import dash
from dash import html, set_props
from dash.dependencies import Input, Output, State, ALL
import json
from feffery_dash_utils.style_utils import style
import feffery_utils_components as fuc
import feffery_antd_components as fac

from uuid import uuid4
from datetime import datetime
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
    """监听拖拽事件"""

    uuid = str(uuid4())
    component = render_component(uuid, drop_data=dropEvent, disableDragging=False)

    logger.debug(f"拖拽的组件: {component}====={dropEvent}")

    return [component] if children is None else [*children, component]


# 表单生成
@app.callback(
    Output("component-edit-container", "children"),
    # Output("component-settings-tree", "selectedKeys"),
    Input({"type": "RND", "id": ALL}, "position"),
    Input({"type": "RND", "id": ALL}, "size"),
    Input({"type": "RND", "id": ALL}, "selected"),
    Input({"type": "RND", "id": ALL}, "key"),
    Input({"type": "RND-Data-Source-Drop-Zone-List", "id": ALL}, "dropEvent"),
    State("load-template-input", "value"),
    prevent_initial_call=True,
)
def component_edit_container(
    position, size, selected, key, dropEvent, load_template_input
):
    """最右边，组件编辑容器 表单的生成"""
    # print("拖拽的组件", position, size, selected, key, selectedKeys)

    # if not any(selected):
    #     return dash.no_update

    if not dropEvent or dropEvent == [None]:
        Data_Source = None
    else:
        Data_Source = dropEvent[0]["data"]["info"]

    triggered_id = dash.ctx.triggered_id

    # 创建数据库会话
    session = Session()
    # 检查是否已存在相同 component_id 的记录
    existing = (
        session.query(ComponentLayout)
        .filter_by(component_id=key[-1].split("+")[0])
        .first()
    )
    # 关闭数据库会话
    session.close()

    # logger.debug(f"触发的组件ID: {existing}")

    if existing:
        logger.debug("已存在的组件被选中，更新表单数据")
        # 如果是已存在的组件
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
    else:
        logger.debug("新组件被选中，创建新的表单数据")
        # 处理新组件的情况
        rnd_id = key[-1].split("+")
        component_key = rnd_id[1]  # 获取组件的key
        data = {
            "坐标": position[-1],
            "大小": {
                key: int(value.replace("px", "")) if isinstance(value, str) else value
                for key, value in size[-1].items()
            },
            "key": component_key,
            "id": rnd_id[0],  # 获取组件的ID
        }

    config = COMPONENT_CONFIGS.get(component_key)
    if not config:
        return dash.no_update

    default_values = config["default_values"](data)

    id = default_values["组件ID"]  # 提取组件ID

    # print("component_key", component_key)
    # print("default_values", default_values)
    if not existing:
        pass
        # 准备要保存到数据库的布局数据
        layout_data = {
            "position": {"x": default_values["X"], "y": default_values["Y"]},
            "size": {},
            "type": component_key,
            "extra": {},
        }
        # 提前保存布局数据到数据库
        if component_key == "横线":
            layout_data["size"] = {"width": default_values["W"], "height": 2}
            layout_data["type"] = "horizontal_line"
        elif component_key == "竖线":
            layout_data["size"] = {"width": 2, "height": default_values["H"]}
            layout_data["type"] = "vertical_line"
        elif component_key == "文本":
            layout_data["size"] = {
                "width": default_values["W"],
                "height": default_values["H"],
            }
            layout_data["type"] = "text"
            layout_data["extra"] = {
                "data_type": default_values["数据类型"],
                "content": default_values["内容"],
                "fontSize": default_values["字体大小"],
            }
        elif component_key == "矩形":
            layout_data["size"] = {
                "width": default_values["W"],
                "height": default_values["H"],
            }
            layout_data["type"] = "rectangle"
        elif component_key == "二维码":
            layout_data["size"] = {
                "width": default_values["二维码大小"],
                "height": default_values["二维码大小"],
            }
            layout_data["type"] = "qrcode"
            layout_data["extra"] = {
                "data_type": default_values["数据类型"],
                "content": default_values["数据框"],
                "size": default_values["二维码大小"],
            }
        elif component_key == "图片":
            layout_data["size"] = {
                "width": default_values["图片大小"],
                "height": default_values["图片大小"],
            }
            layout_data["type"] = "image"
            layout_data["extra"] = {
                "data_type": default_values["数据类型"],
                "content": default_values["base64"],
                "size": default_values["图片大小"],
            }
        elif component_key == "表格":
            layout_data["type"] = "table"
            layout_data["extra"] = {
                "content": default_values["columns"],
            }
            # print("表格默认值", default_values)
            # print("表格数据", existing)
            pass

        # 保存到数据库
        try:
            # 创建数据库会话
            session = Session()
            logger.debug(f"组件 {id} 不存在，创建新记录")
            # print(layout_data)
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

    table_data = []
    # 保存到数据库
    try:
        # 创建数据库会话
        session = Session()
        # 检查是否已存在相同 component_id 的记录
        existing = session.query(ComponentLayout).filter_by(component_id=id).first()
        if existing:
            comp_type = existing.layout_data.get("type")
            if comp_type == "horizontal_line":
                pass
            elif comp_type == "vertical_line":
                pass
            elif comp_type == "text":
                default_values["内容"] = (
                    existing.layout_data["extra"]["content"]
                    if not Data_Source
                    else Data_Source
                )

                default_values["数据类型"] = (
                    existing.layout_data["extra"]["data_type"]
                    if not Data_Source
                    else "动态数据"
                )
                default_values["字体大小"] = existing.layout_data["extra"]["fontSize"]
            elif comp_type == "rectangle":
                pass
            elif comp_type == "table":
                table_data = existing.layout_data["extra"]["content"]
            elif comp_type == "qrcode":
                default_values["数据类型"] = (
                    existing.layout_data["extra"]["data_type"]
                    if not Data_Source
                    else "动态数据"
                )
                default_values["二维码大小"] = existing.layout_data["extra"]["size"]
                default_values["数据框"] = (
                    existing.layout_data["extra"]["content"]
                    if not Data_Source
                    else Data_Source
                )
            elif comp_type == "image":
                default_values["数据类型"] = (
                    existing.layout_data["extra"]["data_type"]
                    if not Data_Source
                    else "动态数据"
                )
                default_values["图片大小"] = existing.layout_data["extra"]["size"]
                default_values["base64"] = (
                    existing.layout_data["extra"]["content"]
                    if not Data_Source
                    else Data_Source
                )

    # 捕获任何可能发生的异常
    except Exception as e:
        logger.debug(f"组件数据替换错误: {str(e)}")
        # 如果发生错误，回滚会话，撤销所有未提交的更改
        session.rollback()
    # 无论成功还是失败，都会执行的清理操作
    finally:
        # 关闭数据库会话，释放资源
        session.close()

    # 生成表单项
    form_items = [
        create_form_item(field, data, table_data) for field in config["fields"]
    ]

    # 添加确认和移除按钮
    form_items.append(
        fac.AntdCol(
            [
                # 通过FefferyListenDrop绑定拖拽元素放置目标容器
                fuc.FefferyListenDrop(
                    id={"type": "RND-Data-Source-Drop-Zone-List", "id": data["id"]},
                    targetSelector=f"#RND_FORM_DATA_{data['id']}",
                ),
                fuc.FefferyDiv(
                    "数据源拖拽放置区",
                    id=f"RND_FORM_DATA_{data['id']}",
                    border="1px dashed black",
                    style=style(
                        width="100%",
                        height="40px",
                        padding="5px",
                        boxSizing="border-box",
                        marginBottom="10px",
                    ),
                ),
                fac.AntdFlex(
                    [
                        fac.AntdButton(
                            "确认",
                            id={"type": "RND_Button_Confirm", "id": data["id"]},
                            type="primary",
                            style=style(width="50%"),
                        ),
                        fac.AntdButton(
                            "移除",
                            id={"type": "RND_Button_Cancel", "id": data["id"]},
                            type="primary",
                            style=style(width="50%"),
                        ),
                    ],
                    gap=10,
                ),
            ],
            span=24,
        )
    )

    return (
        fac.AntdForm(
            fac.AntdRow(form_items, gutter=10),
            id={"type": "RND_FORM_DATA", "id": data["id"]},
            enableBatchControl=True,
            layout="vertical",
            values=default_values,
            className={".ant-form-item": {"margin-bottom": "10px"}},
        ),
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
def Set_up_Printed_paper(value, w, h, _width, _height, template_name_):
    if not template_name_:  # 检查模板名称是否为空
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
        paper = session.query(PaperSize).filter_by(template_name=template_name_).first()
        paper_dict = {k: v for k, v in paper.__dict__.items() if not k.startswith("_")}
        logger.debug(f"当前纸张大小记录: {paper_dict}")

        if paper:
            # 先获取原有 extra 字段
            old_extra = paper.extra or {}
            new_extra = {
                "xp_width": _width,
                "xp_height": _height,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            # 合并 old_extra 和 new_extra
            merged_extra = {**old_extra, **new_extra}
            # 如果记录存在，直接更新所有字段
            paper.type_name = type_name
            paper.width_mm = width_mm
            paper.height_mm = height_mm
            paper.extra = merged_extra
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
    State("local-large-storage", "data"),
    prevent_initial_call=True,
)
def RND_Button_Confirm(nClicks, values, table_data, load_template_input, local_data):
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
    elif values[0].get("内容"):  # 文本
        layout_data["size"] = {"width": values[0]["W"], "height": values[0]["H"]}
        layout_data["type"] = "text"
        layout_data["extra"] = {
            "data_type": values[0]["数据类型"],
            "content": values[0]["内容"],
            "fontSize": values[0]["字体大小"],
        }
        data_ = (local_data.get(values[0]["内容"], ""),)

        set_props(
            {"type": "RND", "id": id},
            {
                "position": {"x": values[0]["X"], "y": values[0]["Y"]},
                "children": fac.AntdText(
                    values[0]["内容"] if not data_ else data_,
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
    elif len(table_data) > 0:  # 表格
        logger.debug(f"表格数据：{table_data}")

        layout_data["type"] = "table"
        layout_data["size"] = {"width": values[0]["W"], "height": values[0]["H"]}
        layout_data["extra"] = {
            "columns": [
                {"title": i["名称"], "dataIndex": i["绑定"], "width": i["宽度"]}
                for i in table_data[0]
            ],
            "data": [{f"{i['绑定']}": f"{i['绑定']}" for i in table_data[0]}],
        }
        set_props(
            {"type": "RND", "id": id},
            {
                "position": {"x": values[0]["X"], "y": values[0]["Y"]},
                "children": fac.AntdTable(
                    columns=[
                        {"title": i["名称"], "dataIndex": i["绑定"], "width": i["宽度"]}
                        for i in table_data[0]
                    ],
                    data=[{f"{i['绑定']}": f"{i['绑定']}" for i in table_data[0]}],
                    bordered=True,
                    pagination=False,
                    style=style(
                        width="100%",
                        height="100%",
                    ),
                ),
            },
        )
    elif values[0].get("二维码大小"):  # 二维码
        layout_data["size"] = {
            "width": values[0]["二维码大小"],
            "height": values[0]["二维码大小"],
        }
        layout_data["type"] = "qrcode"
        layout_data["extra"] = {
            "data_type": values[0]["数据类型"],
            "content": values[0]["数据框"],
            "size": values[0]["二维码大小"],
        }

        data_ = (local_data.get(values[0]["数据框"], ""),)

        set_props(
            {"type": "RND", "id": id},
            {
                "position": {"x": values[0]["X"], "y": values[0]["Y"]},
                "children": fuc.FefferyQRCode(
                    value=values[0]["数据框"] if not data_ else data_,
                    size=values[0]["二维码大小"],
                ),
                "size": {
                    "width": values[0]["二维码大小"],
                    "height": values[0]["二维码大小"],
                },
            },
        )
    elif values[0].get("base64"):  # 图片
        layout_data["size"] = {
            "width": values[0]["图片大小"],
            "height": values[0]["图片大小"],
        }
        layout_data["type"] = "image"
        layout_data["extra"] = {
            "data_type": values[0]["数据类型"],
            "content": values[0]["base64"],
            "size": values[0]["图片大小"],
        }
        data_ = (local_data.get(values[0]["base64"], ""),)
        set_props(
            {"type": "RND", "id": id},
            {
                "position": {"x": values[0]["X"], "y": values[0]["Y"]},
                "children": html.Img(
                    src=values[0]["base64"] if not data_ else data_,
                    style={
                        "width": f"{values[0]['图片大小']}px",
                        "height": f"{values[0]['图片大小']}px",
                    },
                ),
                "size": {
                    "width": values[0]["图片大小"],
                    "height": values[0]["图片大小"],
                },
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
        # 如果存在，则更新记录；如果不存在，则创建新记录
        if existing:
            # 更新现有记录
            existing.template_name = load_template_input
            existing.layout_data = layout_data
        else:
            logger.debug(f"组件 {id} 不存在，创建新记录")
            # print(layout_data)
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


# 客户端临时存储
@app.callback(
    Output("local-large-storage", "data"),
    Output("json-viewer-storage", "data"),
    Output("json-data-input", "value"),
    Input("json-data-input", "debounceValue"),
    State("local-large-storage", "data"),
    prevent_initial_call=True,
)
def update_local_large_storage(value, data):
    # print("更新临时存储", value)
    # id = dash.ctx.triggered_id
    # print("触发的组件ID:", id)
    if not value:
        return dash.no_update, data, json.dumps(data, ensure_ascii=False, indent=4)
    # 先判断类型
    if isinstance(value, dict):
        logger.debug(f"本地大数据存储更新: {value}")
        # print("更新后的临时存储", value)
        return value, value, json.dumps(value, ensure_ascii=False, indent=4)
    if isinstance(value, str):
        # print("这是字符串")
        try:
            logger.debug("这是字符串", value)
            value_dict = json.loads(value)
            logger.debug(
                f"这是反序列化后的数据{value_dict}",
            )
            return (
                value_dict,
                value_dict,
                json.dumps(value_dict, ensure_ascii=False, indent=4),
            )
        except Exception as e:
            logger.debug(f"JSON解析失败: {e}")
            return dash.no_update, data, json.dumps(data, ensure_ascii=False, indent=4)


# 复制模版
@app.callback(
    Output("Copy-Template-Modal", "children"),
    Input("RND-Button-Copy-Template", "nClicks"),
    State("load-template-input", "value"),
    prevent_initial_call=True,
)
def copy_toggle_modal(nClicks, load_template_input):
    if not nClicks:
        return dash.no_update

    session = Session()
    # 查询原有纸张大小
    paper_size = (
        session.query(PaperSize).filter_by(template_name=load_template_input).first()
    )
    # 查询原有组件模版（可能有多个组件）
    components = (
        session.query(ComponentLayout)
        .filter_by(template_name=load_template_input)
        .all()
    )

    # for comp in components:
    #     print(comp.component_id, comp.type)

    组件数量 = len(components)
    横线数量 = sum(
        1 for _ in components if _.layout_data.get("type") == "horizontal_line"
    )
    竖线数量 = sum(
        1 for _ in components if _.layout_data.get("type") == "vertical_line"
    )
    矩形数量 = sum(1 for _ in components if _.layout_data.get("type") == "rectangle")
    文本数量 = sum(1 for _ in components if _.layout_data.get("type") == "text")
    二维码数量 = sum(1 for _ in components if _.layout_data.get("type") == "qrcode")
    图片数量 = sum(1 for _ in components if _.layout_data.get("type") == "image")

    纸张大小 = paper_size.type_name

    session.close()

    return fac.AntdModal(
        [
            fac.AntdDivider("复制的模版数据", variant="solid", lineColor="#595959"),
            fuc.FefferyScrollbars(
                fac.AntdSpace(
                    [
                        fac.AntdText(f"组件数量: {组件数量}", mark=True),
                        fac.AntdText(f"横线数量: {横线数量}", mark=True),
                        fac.AntdText(f"竖线数量: {竖线数量}", mark=True),
                        fac.AntdText(f"矩形数量: {矩形数量}", mark=True),
                        fac.AntdText(f"文本数量: {文本数量}", mark=True),
                        fac.AntdText(f"二维码数量: {二维码数量}", mark=True),
                        fac.AntdText(f"图片数量: {图片数量}", mark=True),
                        fac.AntdText(f"纸张大小: {纸张大小}", mark=True),
                    ],
                    wrap=True,
                    style={"width": "100%"},
                ),
                style=style(
                    maxHeight="150px",
                    # maxWidth="200px",
                    width="100%",
                    border="1px dashed #e1dfdd",
                ),
            ),
            fac.AntdDivider("模版操作区域", variant="solid", lineColor="#595959"),
            html.Div(
                fac.AntdForm(
                    fac.AntdRow(
                        [
                            fac.AntdCol(
                                fac.AntdFormItem(
                                    fac.AntdInput(
                                        id="load-template-input-copy",
                                        placeholder="请输入",
                                        style={"width": "100%"},
                                    ),
                                    label=f"模版名称",
                                ),
                                span=12,
                            ),
                            fac.AntdCol(
                                fac.AntdFormItem(
                                    fac.AntdSelect(
                                        id="load-template-paper-copy",
                                        options=[
                                            {"label": f"纸张-{i}", "value": f"{i}"}
                                            for i in ["A4", "A5", "A4/3"]
                                        ],
                                        value=paper_size.type_name,
                                    ),
                                    label=f"纸张大小",
                                ),
                                span=12,
                            ),
                            fac.AntdCol(
                                fac.AntdFormItem(
                                    fac.AntdInput(
                                        id="load-template-description-copy",
                                        placeholder='mode="text-area"',
                                        mode="text-area",
                                        style={"width": "100%"},
                                    ),
                                    label=f"模版说明",
                                ),
                                span=24,
                            ),
                            fac.AntdCol(
                                fac.AntdFormItem(
                                    fac.AntdButton(
                                        "保存到新模版",
                                        id="RND-Button-Save-New-Template",
                                        type="primary",
                                        block=True,
                                    )
                                ),
                                span=24,
                            ),
                        ],
                        gutter=25,
                    ),
                    # labelCol={"span": 6},
                    # wrapperCol={"span": 18},
                    layout="vertical",
                )
            ),
        ],
        title="模版复制",
        visible=True,
    )


@app.callback(
    Output("Copy-Template-Modal", "children", allow_duplicate=True),
    Input("RND-Button-Save-New-Template", "nClicks"),
    State("load-template-input", "value"),
    State("load-template-input-copy", "value"),
    State("load-template-paper-copy", "value"),
    State("load-template-description-copy", "value"),
    prevent_initial_call=True,
)
def save_new_template(
    nClicks,
    load_template_input,
    load_template_input_copy,
    load_template_paper_copy,
    load_template_description_copy,
):
    if not nClicks:
        return dash.no_update

        # 根据选择确定纸张大小
    if load_template_paper_copy == "A4":
        width_mm, height_mm = 210, 297
    elif load_template_paper_copy == "A5":
        width_mm, height_mm = 210, 148
    elif load_template_paper_copy == "A4/3":
        width_mm, height_mm = 210, 99

    # 处理保存新模版的逻辑
    logger.debug("保存新模版", load_template_input)

    # 处理复制模版的逻辑
    logger.debug("复制模版", load_template_input)

    session = Session()
    try:
        # 查询原有组件模版（可能有多个组件）
        components = (
            session.query(ComponentLayout)
            .filter_by(template_name=load_template_input)
            .all()
        )
        # 查询原有纸张大小
        paper_size = (
            session.query(PaperSize)
            .filter_by(template_name=load_template_input)
            .first()
        )
        if load_template_input_copy != load_template_input:
            # 复制纸张大小
            if paper_size:
                extra = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "comment": load_template_description_copy,
                }
                new_paper = PaperSize(
                    template_name=load_template_input_copy,
                    type_name=paper_size.type_name,
                    width_mm=width_mm,
                    height_mm=height_mm,
                    extra=extra,
                )
                session.add(new_paper)

            # 复制所有组件
            for comp in components:
                new_comp = ComponentLayout(
                    component_id=str(uuid4()),  # 新组件ID
                    template_name=load_template_input_copy,
                    layout_data=comp.layout_data.copy() if comp.layout_data else None,
                )
                session.add(new_comp)

            session.commit()
            logger.debug(f"模版 {load_template_input} 复制成功")
            return fac.AntdMessage(
                content=f"模版 {load_template_input} 已复制为 {load_template_input_copy}",
                type="info",
            )
        else:
            return fac.AntdMessage(
                content="新模版名称不能与原模版名称相同",
                type="warning",
            )
    except Exception as e:
        logger.debug(f"复制模版失败: {e}")
        session.rollback()
        return fac.AntdMessage(
            content="复制模版失败",
            type="error",
        )
    finally:
        session.close()
        return dash.no_update
