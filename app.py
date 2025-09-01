from dash import html, dcc
import feffery_antd_components as fac
import feffery_utils_components as fuc

from server import app

import router.router_root

from configs.demo_config import Demo_Config

app.layout = lambda: fuc.FefferyTopProgress(
    [
        # 全局消息提示
        fac.Fragment(id="global-message"),
        # 全局重定向
        fac.Fragment(id="global-redirect"),
        # 根节点url监听
        fuc.FefferyLocation(id="root-url"),
        # 用于临时存模拟数据
        dcc.Store(
            id="local-large-storage", data=Demo_Config.data, storage_type="local"
        ),
        # 应用根容器
        html.Div(
            id="root-container",
        ),
    ],
    listenPropsMode="include",
    includeProps=["root-container.children"],
    minimum=0.33,
    color="#1677ff",
)


if __name__ == "__main__":
    # 非正式环境下开发调试预览用
    # 生产环境推荐使用gunicorn启动
    app.run(host="127.0.0.1", port=6969, debug=True)
