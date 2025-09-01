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

# 从 数据文件导入
from models.drag_and_drop_m import (
    ComponentLayout,
    PaperSize,
    DataSource,
    Session,
)


# 添加模版
@app.callback(
    Output("RND-Template-List-msg", "children"),
    Input("RND-Button-Add-Template", "nClicks"),
    prevent_initial_call=True,
)
def Modal_Print_Template(nClicks):
    if not nClicks:
        return dash.no_update
    return fac.AntdModal(
        fac.AntdForm(
            [
                fac.AntdFormItem(
                    fac.AntdInput(id="Template-Name"), label="输入模版名称"
                ),
                fac.AntdFormItem(
                    fac.AntdSelect(
                        id="Template-paper",
                        options=[
                            {"label": f"纸张-{i}", "value": f"{i}"}
                            for i in ["A4", "A5", "A4/3"]
                        ],
                    ),
                    label="选择纸张",
                ),
                fac.AntdFormItem(
                    fac.AntdInput(id="Template-comment", mode="text-area"),
                    label="模版说明",
                ),
                fac.AntdFormItem(
                    fac.AntdButton(
                        "添加模版数据", id="Add-Button", type="primary", block=True
                    )
                ),
            ],
            layout="vertical",
            # style={"width": 300},
        ),
        id="RND-Template-Modal",
        title="添加模版",
        width=300,
        visible=True,
    )


# 保存模版数据
@app.callback(
    Input("Add-Button", "nClicks"),
    State("Template-Name", "value"),
    State("Template-paper", "value"),
    State("Template-comment", "value"),
    prevent_initial_call=True,
)
def Add_Print_Template(nClicks, template_name_, template_paper, template_comment):
    # print(template_name_, template_paper, template_comment)

    # 根据选择确定纸张大小
    if template_paper == "A4":
        width_mm, height_mm = 210, 297
    elif template_paper == "A5":
        width_mm, height_mm = 210, 148
    elif template_paper == "A4/3":
        width_mm, height_mm = 210, 99

    session = Session()
    # 查询原有纸张大小
    paper_size = (
        session.query(PaperSize).filter_by(template_name=template_name_).first()
    )

    if paper_size:
        set_props(
            "RND-Template-List-msg",
            {"children": fac.AntdMessage(content="模版名称已存在", type="warning")},
        )
        return dash.no_update

    paper = PaperSize(
        template_name=template_name_,
        type_name=template_paper,
        width_mm=width_mm,
        height_mm=height_mm,
        extra={
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comment": template_comment,
        },
    )
    session.add(paper)
    session.commit()
    set_props(
        "RND-Template-List-msg",
        {"children": fac.AntdMessage(content="添加成功", type="success")},
    )


# 删除模版数据
@app.callback(
    Input({"type": "delete", "template": ALL}, "nClicks"),
    prevent_initial_call=True,
)
def Delete_Print_Template(nClicks):
    if not nClicks:
        return dash.no_update

    triggered_id = dash.ctx.triggered_id.get("template")

    session = Session()
    try:
        # 查询要删除的数据
        paper = session.query(PaperSize).filter_by(id=triggered_id).first()
        # 删除对应模板
        session.query(PaperSize).filter_by(id=triggered_id).delete()

        session.query(ComponentLayout).filter_by(
            template_name=paper.template_name
        ).delete()

        session.commit()
        set_props(
            "RND-Template-List-msg",
            {
                "children": fac.AntdMessage(
                    content=f"已删除模板：{paper.template_name}", type="success"
                )
            },
        )
    except Exception as e:
        set_props(
            "RND-Template-List-msg",
            {"children": fac.AntdMessage(content=f"删除失败: {e}", type="error")},
        )
    finally:
        session.close()


# 数据源管理
@app.callback(
    Output("RND-Template-List-msg", "children", allow_duplicate=True),
    Input("RND-Button-Data-Source", "nClicks"),
    prevent_initial_call=True,
)
def Manage_Data_Source(nClicks):
    if not nClicks:
        return dash.no_update
    return fac.AntdModal(
        fac.AntdForm(
            [
                fac.AntdFormItem(fac.AntdInput(id="Data-Name"), label="数据源名称"),
                fac.AntdFormItem(
                    fac.AntdSelect(
                        id="Data-type",
                        options=[
                            {"label": f"字段类型-{i}", "value": f"{i}"}
                            for i in ["文本", "数字"]
                        ],
                    ),
                    label="数据类型",
                ),
                fac.AntdFormItem(
                    fac.AntdInput(id="Data-comment", mode="text-area"),
                    label="数据源说明",
                ),
                fac.AntdFormItem(
                    fac.AntdButton(
                        "添加模版数据", id="Add-Button-Data", type="primary", block=True
                    )
                ),
            ],
            layout="vertical",
        ),
        title="添加模版",
        width=300,
        visible=True,
    )


# 保存数据源的字段
@app.callback(
    Input("Add-Button-Data", "nClicks"),
    State("Data-Name", "value"),
    State("Data-type", "value"),
    State("Data-comment", "value"),
    prevent_initial_call=True,
)
def Add_Data_Source(nClicks, data_name, data_type, data_comment):
    if not nClicks:
        return dash.no_update

    session = Session()
    try:
        data_source = DataSource(
            name=data_name,
            type=data_type,
            config={"content": data_comment},
        )
        session.add(data_source)
        session.commit()

        set_props(
            "RND-Template-List-msg",
            {"children": fac.AntdMessage(content="添加成功", type="success")},
        )
    except Exception as e:
        set_props(
            "RND-Template-List-msg",
            {"children": fac.AntdMessage(content=f"添加失败: {e}", type="error")},
        )
    finally:
        session.close()
