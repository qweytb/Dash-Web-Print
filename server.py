import dash
from flask import request, abort
import ipaddress
from user_agents import parse
from flask_login import LoginManager, UserMixin

from configs import ip_config, BaseConfig

VERSION = "0.1.4"  # 定义版本号

app = dash.Dash(
    __name__,
    title=f"布局助手{VERSION}",
    suppress_callback_exceptions=True,
    compress=True,  # 隐式依赖flask-compress
    update_title=None,
    serve_locally=True,
)

server = app.server

# 设置应用密钥
app.server.secret_key = "ytb_147258369"

# 为当前应用添加flask-login用户登录管理
login_manager = LoginManager()
login_manager.init_app(app.server)


class User(UserMixin):
    """flask-login专用用户类"""

    def __init__(
        self, id: str, user_name: str, user_role: str, session_token: str = None
    ) -> None:
        """初始化用户信息"""

        self.id = id
        self.user_name = user_name
        self.user_role = user_role
        self.session_token = session_token


@login_manager.user_loader
def user_loader(user_id):
    """flask-login内部专用用户加载函数"""

    # 当前用户实例化
    user = User(
        id="admin",
    )
    return user


@server.before_request
def validate_ip_range():
    """IP 白名单和黑名单验证"""

    client_ip = request.remote_addr

    # 如果启用黑名单，先检查黑名单
    if ip_config.ENABLE_IP_BLACKLIST and ip_config.is_ip_in_list(
        client_ip, ip_config.BLACK_IP_LIST
    ):
        # 记录被拒绝的IP
        print(f"拒绝IP访问（黑名单）: {client_ip}")
        # 返回自定义错误响应
        abort(403, description="禁止：您的IP地址被列入黑名单。")

    # 如果启用白名单，检查白名单
    if ip_config.ENABLE_IP_WHITELIST and not ip_config.is_ip_in_list(
        client_ip, ip_config.WHITE_IP_LIST
    ):
        # 记录被拒绝的IP
        print(f"拒绝IP访问（不在白名单中）: {client_ip}")
        # 返回自定义错误响应
        abort(403, description="禁止：您的IP地址是不允许的。")


def is_ip_allowed(ip, white_list):
    """检查IP是否在白名单中"""
    try:
        ip_addr = ipaddress.ip_address(ip)
        for allowed_ip in white_list:
            if ip_addr in ipaddress.ip_network(allowed_ip):
                return True
    except ValueError:
        # 处理无效的IP地址格式
        pass
    return False


@app.server.before_request
def check_browser():
    """检查浏览器版本是否符合最低要求"""

    # 提取当前请求对应的浏览器信息
    user_agent = parse(str(request.user_agent))

    # 若浏览器版本信息有效
    if user_agent.browser.version != ():
        # IE相关浏览器直接拦截
        if user_agent.browser.family == "IE":
            return (
                "<div style='font-size: 16px; color: red; position: fixed; top: 40%; left: 50%; transform: translateX(-50%);'>"
                "请不要使用IE浏览器，或开启了IE内核兼容模式的其他浏览器访问本应用</div>"
            )
        # 基于BaseConfig.min_browser_versions配置，对相关浏览器最低版本进行检查
        for rule in BaseConfig.min_browser_versions:
            # 若当前请求对应的浏览器版本，低于声明的最低支持版本
            if (
                user_agent.browser.family == rule["browser"]
                and user_agent.browser.version[0] < rule["version"]
            ):
                return (
                    "<div style='font-size: 16px; color: red; position: fixed; top: 40%; left: 50%; transform: translateX(-50%);'>"
                    "您的{}浏览器版本低于本应用最低支持版本（{}），请升级浏览器后再访问</div>"
                ).format(rule["browser"], rule["version"])

        # 若开启了严格的浏览器类型限制
        if BaseConfig.strict_browser_type_check:
            # 若当前浏览器不在声明的浏览器范围内
            if user_agent.browser.family not in [
                rule["browser"] for rule in BaseConfig.min_browser_versions
            ]:
                return (
                    "<div style='font-size: 16px; color: red; position: fixed; top: 40%; left: 50%; transform: translateX(-50%);'>"
                    "当前浏览器类型不在支持的范围内，支持的浏览器类型有：{}</div>"
                ).format(
                    "、".join(
                        [rule["browser"] for rule in BaseConfig.min_browser_versions]
                    )
                )
