from flask import make_response, jsonify, request
from api import api

__version__ = 'v1.0'
@api.route(f'/{__version__}/test/', methods=['GET', 'POST'])
def test():
    """
     上面 /v1.0/test/ 定义的url最后带上"/"：
     1、如果接收到的请求url没有带"/"，则会自动补上，同时响应视图函数
     2、如果/v1.0/test/这条路由的结尾没有带"/"，则接收到的请求里也不能以"/"结尾，否则无法响应
    """
    # 获取参数
    #if request.method == "POST":
    		 # 获取表单参数
    #    username = request.form.get("username")
    #    password = request.form.get("password")
    		 # 获取json参数
    #    data = request.get_json()
    #else:
    		 #获取get参数
    #    username = request.args.get("username")
    #    password = request.args.get("password")
    data = {'username': 'xxx', 'password': 'xxxx'}
    response = jsonify(code=200,
                       msg="success",
                       data=data)
    return response
    # 也可以使用 make_response 生成指定状态码的响应
    # return make_response(response, 200)

