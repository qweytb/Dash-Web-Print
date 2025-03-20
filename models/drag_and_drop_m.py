from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    TypeDecorator,
    Text,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import json


# 自定义 JSON 类型
class JSONEncodedText(TypeDecorator):
    impl = Text  # 底层使用 Text 类型存储

    def process_bind_param(self, value, dialect):
        # 将 Python 对象转为 JSON 字符串，禁用 ensure_ascii
        if value is not None:
            value = json.dumps(value, ensure_ascii=False)
        return value

    def process_result_value(self, value, dialect):
        # 将 JSON 字符串反序列化为 Python 对象
        if value is not None:
            value = json.loads(value)
        return value


# 创建数据库引擎
# - 'sqlite:///components.db': 使用 SQLite 数据库，文件名为 components.db
# - echo=True: 启用 SQL 语句日志输出，便于调试，生产环境可设为 False
engine = create_engine("sqlite:///components.db", echo=False)

# 创建 ORM 的基类
# - declarative_base() 用于定义数据库模型的基类，所有模型类都将继承它
Base = declarative_base()


# 定义纸张大小的数据库模型
class PaperSize(Base):
    __tablename__ = "paper_sizes"

    id = Column(Integer, primary_key=True)
    # 模板名称，字符串类型，最长 100 个字符，可为空
    template_name = Column(String(100))
    # 纸张类型名称，例如 "A4", "A3", "Custom"
    type_name = Column(String(50), nullable=False, unique=True)
    # 宽度（毫米），整数类型
    width_mm = Column(Integer, nullable=False)
    # 高度（毫米），整数类型
    height_mm = Column(Integer, nullable=False)
    # 可选的额外数据（JSON），用于扩展（例如边距、方向等）
    extra = Column(JSONEncodedText, nullable=True)

    def __repr__(self):
        return (
            f"<PaperSize(id={self.id}, type_name='{self.type_name}', "
            f"width_mm={self.width_mm}, height_mm={self.height_mm})>"
        )


# 定义组件布局的数据库模型
class ComponentLayout(Base):
    # 指定数据库表名
    __tablename__ = "component_layouts"

    # 主键，自增整数
    # - primary_key=True 表示这是表的主键
    id = Column(Integer, primary_key=True)

    # 组件 ID，字符串类型，最长 50 个字符，不允许为空
    # - 用于唯一标识每个组件，与前端的组件 ID 对应
    component_id = Column(String(50), nullable=False)

    # 模板名称，字符串类型，最长 100 个字符，可为空
    # - 用于分组组件，表示这些组件属于哪个模板
    template_name = Column(String(100))

    # 布局数据，JSON 类型
    # - 存储组件的详细布局信息（如位置、大小、类型等），使用 JSON 格式便于灵活扩展
    # 使用自定义的 UTF8JSON 类型
    layout_data = Column(JSONEncodedText)

    # 创建时间，日期时间类型，默认值为当前 UTC 时间
    # - 记录组件首次保存的时间
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # 更新时间，日期时间类型，默认值和更新时均为当前 UTC 时间
    # - 每次更新记录时自动更新时间戳
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # 定义对象的字符串表示形式，便于调试和日志输出
    def __repr__(self):
        return f"<ComponentLayout(id={self.id}, component_id='{self.component_id}', template_name='{self.template_name}')>"


# 初始化数据库函数
# - 创建所有定义的表结构，仅需在首次运行或表结构变更时调用
def init_db():
    # 使用 Base.metadata.create_all() 创建所有继承自 Base 的表
    Base.metadata.create_all(engine)


# 创建会话工厂
# - Session 用于生成数据库会话实例，提供事务管理和查询功能
# - bind=engine 将会话绑定到指定的数据库引擎
Session = sessionmaker(bind=engine)

# 仅在直接运行此文件时初始化数据库
# - 防止在导入模块时意外执行初始化操作
if __name__ == "__main__":
    init_db()
