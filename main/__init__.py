from flask import Blueprint

# 两个参数分别指定蓝本的名字、蓝本所在的包或模块
main = Blueprint('main', __name__)

"""
 导入路由模块、错误处理模块，将其和蓝本关联起来

 1、应用的路由保存在包里的 views.py 模块中
 2、导入这两个模块就能把路由与蓝本关联起来
 3、注意，这些模块在 app/__init__.py 脚本的末尾导入，原因是：
    为了避免循环导入依赖，因为在 app/views.py 中还要导入api蓝本，所以除非循环引用出现在定义 api 之后，否则会致使导入出错。

"""
from main import views

