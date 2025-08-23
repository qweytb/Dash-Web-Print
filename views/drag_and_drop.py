from dash import html
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
import json

# 导入监听拖拽和放置的回调函数
from callbacks import drag_and_drop_c

# 导入测试参数
from configs.demo_config import Demo_Config


def DragAndDrop():
    return (
        fac.AntdFlex(
            [
                html.Div(
                    [
                        html.Div(
                            fac.AntdFlex(
                                [
                                    fac.AntdSelect(
                                        options=[
                                            {"label": f"{i}", "value": f"{i}"}
                                            for i in [
                                                "打印模板1",
                                                "打印模板2",
                                                "打印模板3",
                                            ]
                                        ],
                                        value="打印模板1",
                                        id="load-template-input",
                                        style={"width": "50%"},
                                    ),
                                    fac.AntdButton(
                                        "加载模板",
                                        id="load-template",
                                        style=style(width="25%"),
                                    ),
                                    fac.AntdButton(
                                        "跳转预览",
                                        id="jump-preview",
                                        href="/print_preview?template=打印模板1&order_ID=12345",
                                        target="_blank",
                                        style=style(width="25%"),
                                    ),
                                ],
                                gap=10,
                            ),
                            style=style(
                                width="100%",
                                margin="10px 0px",
                            ),
                        ),
                        # 通过一一对应的FefferyListenDrag绑定可拖拽元素
                        fac.Fragment(
                            [
                                fuc.FefferyListenDrag(
                                    # targetSelector=f"#drag-target-{i if i != '表格' else None}",
                                    targetSelector=f"#drag-target-{i}",
                                    data={"info": f"{i}"},
                                )
                                for i in [
                                    "横线",
                                    "竖线",
                                    "文本",
                                    "矩形",
                                    "表格",
                                    "二维码",
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
                                            # background="#91d5ff" if i != "表格" else "grey",
                                            background="#91d5ff",
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
                                    mode="text-area",
                                    value=json.dumps(
                                        Demo_Config.data, ensure_ascii=False, indent=4
                                    ),
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
                                    className="check-card-group-custom-style-demo",
                                    # defaultValue="A5",
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
                        # html.Div(
                        #     fac.AntdSpace(
                        #         [
                        #             fac.AntdButton(i, type="default")
                        #             for i in ["直接打印", "打印预览", "导出PDF"]
                        #         ],
                        #         wrap=True,
                        #     )
                        # ),
                        # fac.AntdDivider(
                        #     variant="solid",
                        #     lineColor="#595959",
                        #     className={"margin": "10px 0"},
                        # ),
                        # 通过FefferyListenDrop绑定拖拽元素放置目标容器
                        fuc.FefferyListenDrop(
                            id="listen-drop",
                            targetSelector="#listen-drop-target",
                        ),
                        fuc.FefferyDiv(
                            id="listen-drop-target",
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
