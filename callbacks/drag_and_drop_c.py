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


# 表单生成
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
                default_values["内容"] = existing.layout_data["extra"]["content"]
                default_values["类型"] = existing.layout_data["extra"]["data_type"]
                default_values["字体大小"] = existing.layout_data["extra"]["fontSize"]
            elif comp_type == "rectangle":
                pass
            elif comp_type == "table":
                table_data = existing.layout_data["extra"]["columns"]
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

    form_items = [
        create_form_item(field, data, table_data) for field in config["fields"]
    ]
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
                        "移除",
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
        paper_dict = {k: v for k, v in paper.__dict__.items() if not k.startswith('_')}
        logger.debug(f"当前纸张大小记录: {paper_dict}")
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
                template_name=template_name_,
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
        # 如果存在，则更新记录；如果不存在，则创建新记录
        if existing:
            # 更新现有记录
            existing.template_name = load_template_input
            existing.layout_data = layout_data
        else:
            logger.debug(f"组件 {id} 不存在，创建新记录")
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
    Output("Printed-paper", "value"),
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

        # 查询模版的纸张大小
        paper = session.query(PaperSize).filter_by(template_name=template_name).first()

        # 查询数据库,布局模版
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
        return rendered_components, paper.type_name
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
