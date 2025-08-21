import dash
from dash import html
import feffery_utils_components as fuc
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style
from yarl import URL

from loguru import logger


# 从 数据文件导入
from models.drag_and_drop_m import (
    ComponentLayout,
    PaperSize,
    Session,
)

#  从 配置文件导入
from configs.drag_and_drop_config import (
    render_component,
)

import callbacks.print_preview_c

# 导入测试参数 
from configs.demo_config import Demo_Config


# http://127.0.0.1:6969/print_preview?template=打印模板1&order_ID=12345
def PrintPreview(href):
    url_href = URL(href)
    get_query = url_href.query
    if get_query:
        # print(f"查询参数：{get_query}")

        # 模板名称
        template_name = get_query.get("template")

        # 获取数据库订单数据data
        order_ID = get_query.get("order_ID")
        # 模拟数据
        json_data =Demo_Config.data

        # print("这是输入的json数据", json_data)
        try:
            # 创建数据库会话
            # - Session() 生成一个新的数据库会话实例，用于执行查询
            session = Session()
            # 查询数据库
            # - 从 ComponentLayout 表中筛选出 template_name 匹配的记录
            # - .all() 返回所有匹配的结果列表
            components = (
                session.query(ComponentLayout)
                .filter_by(template_name=template_name)
                .all()
            )

            # 检查是否已有该模板的纸张大小记录
            paper = (
                session.query(PaperSize).filter_by(template_name=template_name).first()
            )

            # 关闭会话
            # - 查询完成后释放数据库连接，避免资源泄漏
            session.close()

            # 如果没有找到任何组件
            # - 返回空列表，清空目标容器内容
            if not components:
                return []
            # 存储渲染后的组件
            rendered_components = []
            # 遍历查询结果
            # - 对每个组件调用 render_component 函数进行渲染
            for component in components:
                rendered_comp = render_component(
                    component.component_id,  # 组件的唯一标识符
                    component.layout_data,  # 组件的布局数据（JSON 格式）
                    disableDragging=True,  # 新增：禁用拖拽功能
                    json_data=json_data,  # 新增：传递 JSON 数据
                )
                # 如果渲染成功，则添加到列表中
                if rendered_comp:
                    rendered_components.append(rendered_comp)
        except Exception as e:
            # 捕获可能的异常（如数据库连接失败）
            # - 打印错误信息，便于调试
            # - 返回 dash.no_update，避免界面出错
            logger.debug(f"加载组件失败: {str(e)}")
            return dash.no_update

        return [
            fac.AntdSpace(
                [
                    fuc.FefferyDiv(
                        id="print-preview-container",
                        children=rendered_components,
                        shadow="always-shadow-light",
                        style=style(
                            width=f"{paper.width_mm}mm",
                            height=f"{paper.height_mm}mm",
                        ),
                    ),
                    # 示例http请求组件
                    fuc.FefferyHttpRequests(id="http-requests"),
                    fuc.FefferyWebSocket(
                        id="websocket-print",
                        socketUrl="ws://127.0.0.1:12212/printer",
                    ),
                    # 元素转图片
                    fuc.FefferyDom2Image(id="print-target"),
                    fac.AntdSpace(
                        [
                            fuc.FefferyExecuteJs(id="print-js-window"),
                            # 元素转图片
                            fuc.FefferyDom2Image(id="print-target-window"),
                            fac.AntdButton(
                                "弹窗打印",
                                id="print-popup-window",
                                type="primary",
                            ),
                             fac.AntdButton(
                                "PDF打印",
                                id="print-target-trigger-pdf",
                                type="primary",
                                # autoSpin=True,
                                # loadingChildren="打印中",
                            ),
                            fac.AntdButton(
                                "静默打印",
                                id="print-target-trigger",
                                type="primary",
                                # autoSpin=True,
                                # loadingChildren="打印中",
                            ),
                            fac.AntdButton(
                                "连接ws打印服务器",
                                id="print-target-ws",
                                type="primary",
                                autoSpin=True,
                                loadingChildren="连接中",
                            ),
                            fac.AntdCompact(
                                [
                                    fac.AntdButton(
                                        "获取打印机列表",
                                        id="print-target-list",
                                        type="primary",
                                        autoSpin=True,
                                        loadingChildren="获取中",
                                    ),
                                    fac.AntdSelect(
                                        id="print-target-select",
                                        style={"width": 380},
                                    ),
                                ]
                            ),
                        ]
                    ),
                ],
                direction="vertical",
            )
        ]
