from dash import html
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
import json
from loguru import logger
from yarl import URL

# 导入监听拖拽和放置的回调函数
from callbacks import drag_and_drop_c


# 从 数据文件导入
from models.drag_and_drop_m import (
    ComponentLayout,
    PaperSize,
    DataSource,
    Session,
)

# 导入测试参数
from configs.demo_config import Demo_Config

from configs.drag_and_drop_config import (
    COMPONENT_CONFIGS,
    create_form_item,
    render_component,
)


def components_treeData_db(components):
    # 组件树形结构
    horizontal_line = []
    vertical_line = []
    text = []
    rectangle = []
    table = []
    qr_code = []
    image = []
    for comp in components:
        comp_type = comp.layout_data.get("type")
        if comp_type == "horizontal_line":
            horizontal_line.append({"title": "横线", "key": comp.component_id})
        elif comp_type == "vertical_line":
            vertical_line.append({"title": "竖线", "key": comp.component_id})
        elif comp_type == "text":
            text.append({"title": "文本", "key": comp.component_id})
        elif comp_type == "rectangle":
            rectangle.append({"title": "矩形", "key": comp.component_id})
        elif comp_type == "table":
            table.append({"title": "表格", "key": comp.component_id})
        elif comp_type == "qr_code":
            qr_code.append({"title": "二维码", "key": comp.component_id})
        elif comp_type == "image":
            image.append({"title": "图片", "key": comp.component_id})
    treeData = [
        {"title": "横线", "key": "horizontal_line", "children": horizontal_line},
        {"title": "竖线", "key": "vertical_line", "children": vertical_line},
        {"title": "文本", "key": "text", "children": text},
        {"title": "矩形", "key": "rectangle", "children": rectangle},
        {"title": "表格", "key": "table", "children": table},
        {"title": "二维码", "key": "qr_code", "children": qr_code},
        {"title": "图片", "key": "image", "children": image},
    ]

    return treeData


def DragAndDrop(href, data):
    url_href = URL(href)
    get_query = url_href.query

    template_name = get_query.get("template")

    # 查询模版信息
    session = Session()
    # 查询模版的纸张大小
    paper = session.query(PaperSize).filter_by(template_name=template_name).first()

    # 查询布局
    components = (
        session.query(ComponentLayout).filter_by(template_name=template_name).all()
    )
    # 查询数据源字段
    data_source = session.query(DataSource).filter_by().all()

    session.close()

    if not paper:
        logger.warning(f"Template '{template_name}' not found.")
        return fac.AntdResult(
            title="模版不存在", subTitle=template_name, status="error"
        )

    # 解析布局组件
    rendered_components = [
        render_component(
            comp.component_id,
            comp.layout_data,
            disableDragging=False,
            json_data=data,
        )
        for comp in components
        if render_component(comp.component_id, comp.layout_data)
    ]

    return (
        fac.AntdFlex(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                # 根节点url监听
                                fac.Fragment(id="Copy-Template-Modal"),
                                fac.AntdSpace(
                                    [
                                        fac.AntdInput(
                                            id="load-template-input",
                                            variant="filled",
                                            value=template_name,
                                            disabled=True,
                                        ),
                                        fac.AntdButton(
                                            "复制",
                                            id="RND-Button-Copy-Template",
                                            color="gold",
                                            variant="dashed",
                                        ),
                                        fac.AntdButton(
                                            "预览",
                                            color="primary",
                                            variant="dashed",
                                            href=f"/print_preview?template={template_name}&order_id=demo",
                                            target="_blank",
                                        ),
                                    ],
                                    size="small",
                                ),
                                fac.AntdDivider(
                                    variant="solid",
                                    lineColor="#595959",
                                    className={"margin": "10px 0"},
                                ),
                            ],
                            style=style(
                                width="100%",
                                margin="10px 0px",
                            ),
                        ),
                        # 通过一一对应的FefferyListenDrag绑定可拖拽元素
                        fac.Fragment(
                            [
                                fuc.FefferyListenDrag(
                                    targetSelector=f"#drag-target-{i}"
                                    if i != "表格"
                                    else None,
                                    data={"info": f"{i}"},
                                )
                                for i in [
                                    "横线",
                                    "竖线",
                                    "文本",
                                    "矩形",
                                    "表格",
                                    "二维码",
                                    "图片",
                                ]
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdCenter(
                                        f"{i}",
                                        id=f"drag-target-{i}",
                                        style=style(
                                            height=80,
                                            background="#91d5ff"
                                            if i != "表格"
                                            else "#B1A2A2FF",
                                            cursor="move",
                                            fontSize=20,
                                            color="white",
                                        ),
                                    ),
                                    span=8,
                                )
                                for i in [
                                    "横线",
                                    "竖线",
                                    "文本",
                                    "矩形",
                                    "表格",
                                    "二维码",
                                    "图片",
                                ]
                            ],
                            gutter=[8, 8],
                        ),
                        html.Div(
                            [
                                fac.AntdDivider(
                                    "JSON数据样式",
                                    variant="solid",
                                    lineColor="#595959",
                                ),
                                fac.AntdInput(
                                    id="json-data-input",
                                    placeholder="JSON数据",
                                    debounceWait=500,
                                    persistence=True,
                                    persisted_props=["value"],
                                    persistence_type="session",
                                    mode="text-area",
                                    # value=json.dumps(
                                    #     Demo_Config.data, ensure_ascii=False, indent=4
                                    # ),
                                ),
                                fuc.FefferyJsonViewer(
                                    id="json-viewer-storage",
                                    theme="ashes",
                                    data={
                                        # "int示例": 999,
                                        # "float示例": 0.999,
                                        # "string示例": "我爱dash",
                                        # "数组示例": [0, 1, 2, 3],
                                        # "字典示例": {"a": 1, "b": 2, "c": 3},
                                    },
                                    style=style(marginTop=10),
                                ),
                            ],
                            style=style(
                                # width="100%",
                                margin="10px 0px",
                            ),
                        ),
                    ],
                    style=style(
                        width="300px",
                        # height='100%',
                        # 内边距
                        padding="5px",
                        boxSizing="border-box",
                        # 边框
                        # border='1px dashed black',
                    ),
                ),
                html.Div(
                    [
                        fac.AntdFlex(
                            [
                                fuc.FefferyStyle(
                                    rawStyle="""
                                    .check-card-group-custom-style-demo .ant-pro-checkcard-content {
                                        padding: 5px 12px;
                                    }
                                    """
                                ),
                                fac.AntdCheckCardGroup(
                                    [
                                        fac.AntdCheckCard(
                                            f"纸张-{i}",
                                            value=i,
                                            style={
                                                "width": "auto",
                                                "marginRight": 3,
                                                "marginBottom": 3,
                                                "borderRadius": 5,
                                            },
                                        )
                                        for i in ["A4", "A5", "A4/3", "自定义"]
                                    ],
                                    id="Printed-paper",
                                    defaultValue=paper.type_name,
                                    className="check-card-group-custom-style-demo",
                                    multiple=False,
                                ),
                                fac.AntdInputNumber(
                                    id="Printed-paper-W",
                                    placeholder="宽度/mm",
                                    style={"width": "100px"},
                                ),
                                fac.AntdInputNumber(
                                    id="Printed-paper-H",
                                    placeholder="高度/mm",
                                    style={"width": "100px"},
                                ),
                            ],
                            gap=5,
                        ),
                        fac.AntdDivider(
                            variant="solid",
                            lineColor="#595959",
                            className={"margin": "10px 0"},
                        ),
                        # 通过FefferyListenDrop绑定拖拽元素放置目标容器
                        fuc.FefferyListenDrop(
                            id="listen-drop",
                            targetSelector="#listen-drop-target",
                        ),
                        fuc.FefferyDiv(
                            id="listen-drop-target",
                            children=rendered_components,
                            border="1px dashed black",
                            enableEvents=["size"],
                            style=style(
                                width="210mm",
                                height="148mm",
                            ),
                        ),
                    ],
                    style=style(
                        width="calc(100% - 300px - 300px)",
                        height="100%",
                        # 内边距
                        padding="10px",
                        boxSizing="border-box",
                    ),
                ),
                # 组件设置树
                html.Div(
                    [
                        fac.AntdTitle("数据源字段", level=5),
                        fuc.FefferyDiv(
                            [
                                # 通过一一对应的FefferyListenDrag绑定可拖拽元素
                                fac.Fragment(
                                    [
                                        fuc.FefferyListenDrag(
                                            targetSelector=f"#data-source-{i}",
                                            data={"info": f"{i}"},
                                        )
                                        for i in [i.name for i in data_source]
                                        # [
                                        #     "sample_id",
                                        #     "hospital_name",
                                        #     "hospital_address",
                                        #     "hospital_contact",
                                        #     "machine_model",
                                        #     "machine_id",
                                        #     "patient_name",
                                        #     "patient_age",
                                        #     "patient_gender",
                                        #     "base64",
                                        #     "logo_base64",
                                        #     "result_image_base64",
                                        # ]
                                    ]
                                ),
                                fac.AntdRow(
                                    [
                                        fac.AntdCol(
                                            fac.AntdCenter(
                                                f"{k}",
                                                id=f"data-source-{v}",
                                                style=style(
                                                    height=20,
                                                    # background="#91d5ff" if i != "表格" else "grey",
                                                    background="#8d598f",
                                                    cursor="move",
                                                    fontSize=12,
                                                    color="white",
                                                ),
                                            ),
                                            span=8,
                                        )
                                        for k, v in {
                                            i.config["content"]: i.name
                                            for i in data_source
                                        }.items()
                                        # {
                                        #     "样本ID": "sample_id",
                                        #     "医院名称": "hospital_name",
                                        #     "医院地址": "hospital_address",
                                        #     "联系电话": "hospital_contact",
                                        #     "仪器型号": "machine_model",
                                        #     "仪器编号": "machine_id",
                                        #     "患者姓名": "patient_name",
                                        #     "患者年龄": "patient_age",
                                        #     "患者性别": "patient_gender",
                                        #     "图像数据": "base64",
                                        #     "医院 Logo": "logo_base64",
                                        #     "检测结果图": "result_image_base64",
                                        # }.items()
                                    ],
                                    gutter=[8, 8],
                                ),
                            ],
                            border="1px dashed black",
                            style=style(
                                padding="5px",
                                boxSizing="border-box",
                            ),
                        ),
                    ],
                    style=style(
                        width="300px",
                        # height=400,
                        # 内边距
                        padding="5px",
                        boxSizing="border-box",
                        # 边框
                        # border="1px dashed black",
                    ),
                ),
                html.Div(
                    # 组件编辑容器
                    id="component-edit-container",
                    style=style(
                        width="300px",
                        # height='100%',
                        # 内边距
                        padding="5px",
                        boxSizing="border-box",
                        # 边框
                        # border='1px dashed black',
                    ),
                ),
            ],
            gap=10,
            style=style(
                width="100vw",
                height="100vh",
                # 内边距
                padding="20px",
                boxSizing="border-box",
            ),
        ),
    )
