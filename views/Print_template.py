import dash
from dash import html
import feffery_utils_components as fuc
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style
from yarl import URL

# 从 数据文件导入
from models.drag_and_drop_m import (
    ComponentLayout,
    PaperSize,
    Session,
)

# 导入回调
from callbacks import Print_template_c


def PrintTemplate(href):
    url_href = URL(href)
    get_query = url_href.query

    template_list = get_query.getall("template", [])
    # 数据查询
    session = Session()
    if template_list:
        # 批量查询
        components = (
            session.query(PaperSize).filter(PaperSize.id.in_(template_list)).all()
        )
    else:
        # 没有模版参数就是查询全部
        components = session.query(PaperSize).all()
    session.close()

    # print("这是打印模版数据", components)

    return html.Div(
        [
            fac.AntdSpace(
                [
                    fac.Fragment(id="RND-Template-List-msg"),
                    fac.AntdButton(
                        "添加模板",
                        id="RND-Button-Add-Template",
                        color="primary",
                        variant="dashed",
                        icon=fac.AntdIcon(icon="antd-plus"),
                    ),
                    fac.AntdButton(
                        "添加数据源",
                        id="RND-Button-Data-Source",
                        color="green",
                        variant="dashed",
                        icon=fac.AntdIcon(icon="antd-plus"),
                    ),
                ]
            ),
            fac.AntdDivider(
                variant="solid",
                lineColor="#595959",
                # className={"margin": "0px"},
            ),
            fac.AntdRow(
                [
                    fac.AntdCol(
                        fuc.FefferyDiv(
                            [
                                fac.AntdSpace(
                                    [
                                        fac.AntdText(i.template_name, strong=True),
                                        fac.AntdText(
                                            f"纸张说明: {i.extra.get('comment')}",
                                            type="secondary",
                                        ),
                                        fac.AntdText(
                                            f"创建时间: {i.extra.get('timestamp')}",
                                            type="secondary",
                                        ),
                                        fac.AntdText(
                                            f"更新时间: {i.extra.get('updated_at')}",
                                            type="secondary",
                                        ),
                                    ],
                                    direction="vertical",
                                    size=0,
                                    style=style(
                                        height=160,
                                        padding="10px",
                                        boxSizing="border-box",
                                    ),
                                ),
                                fac.AntdDivider(
                                    variant="solid",
                                    lineColor="#595959",
                                    className={"margin": "0px"},
                                ),
                                fac.AntdCenter(
                                    fac.AntdFlex(
                                        [
                                            fac.AntdButton(
                                                "编辑模版",
                                                color="primary",
                                                variant="dashed",
                                                href=f"/design_template?template={i.template_name}",
                                                target="_blank",
                                                icon=fac.AntdIcon(icon="antd-edit"),
                                                block=True,
                                            ),
                                            fac.AntdButton(
                                                "预览模版",
                                                color="green",
                                                variant="dashed",
                                                href=f"/print_preview?template={i.template_name}&order_id=demo",
                                                target="_blank",
                                                icon=fac.AntdIcon(icon="antd-eye"),
                                                block=True,
                                            ),
                                            fac.AntdButton(
                                                "删除模版",
                                                id={"type": "delete", "template": i.id},
                                                color="danger",
                                                variant="dashed",
                                                icon=fac.AntdIcon(icon="antd-delete"),
                                                block=True,
                                            ),
                                        ],
                                        gap=5,
                                        style=style(width="100%"),
                                    ),
                                    style=style(
                                        height=40,
                                        width="100%",
                                        # backgroundColor="#DF0F0F",
                                        padding="5px 5px",
                                        boxSizing="border-box",
                                    ),
                                ),
                            ],
                            shadow="always-shadow",
                            style=style(
                                backgroundColor="#ffffff",
                                height=200,
                                border="1px solid #697689",
                            ),
                        ),
                        span=6,
                    )
                    for i in components
                ],
                gutter=[20, 20],
            ),
        ],
        style=style(
            # margin="20px",
            backgroundColor="#DFDFDF",
            height="100vh",
            padding="50px",
            boxSizing="border-box",
        ),
    )
