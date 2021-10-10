from flask import Blueprint, request, Response
import json
import re
from mysql.pymysql import SQLMysql

env_variable = Blueprint('env_variable', __name__)


@env_variable.route('/env', methods=['GET'])
def env_var():
    page = request.args.get('page', 1)
    limit = request.args.get('limit', 10)
    group_name = request.args.get('group_name', None)
    context = request.args.get('context', None)
    # 处理
    pattern = re.compile(r'^[\d]{1,3}$')
    page = pattern.search(str(page))
    limit = pattern.search(str(limit))
    if page is None or limit is None:
        data = {
            "object": None,
            "msg": "参数非法",
            "code": 7998,
            "result": False,
            "status": "success"
        }
        return Response(json.dumps(data), content_type='application/json')
    else:
        s = SQLMysql()
        s_sql = "select group_id from jk_vgroups where group_name=%s"
        s_all = "select group_id from jk_vgroups"
        sql = "select v_id, v_name, v_data, group_id from jk_variable where is_delete=0 and group_id=%s and v_data like %s"
        if group_name is None:
            group_ids = s.query_all(s_all)
            if not group_ids:
                data = {
                    "object": None,
                    "msg": "暂无数据",
                    "code": 7994,
                    "result": True,
                    "status": "success"
                }
                return Response(json.dumps(data), content_type='application/json')
            else:
                sql = "select v.v_id, v.v_name, v.v_data, g.group_name from jk_vgroups g, jk_variable v WHERE v.group_id=g.group_id and g.status=1"
                l_n = s.query_all(sql)
                if not l_n:
                    data = {
                        "object": None,
                        "msg": "暂无数据",
                        "code": 7993,
                        "result": True,
                        "status": "success"
                    }
                    return Response(json.dumps(data), content_type='application/json')
                else:
                    lists_all = []
                    for i in range(len(l_n)):
                        v_id, v_name, v_data, group_name = l_n[i]
                        lists_all.append({
                            "id": v_id,
                            "name": v_name,
                            "data": v_data,
                            "group_name": group_name
                        })
                    data = {
                        "object": lists_all,
                        "msg": "查询成功",
                        "code": 7992,
                        "result": True,
                        "status": "success"
                    }
                    return Response(json.dumps(data), content_type='application/json')
        else:
            group_id = s.query_one(s_sql, [str(group_name), ])
            if group_id is None:
                data = {
                    "object": None,
                    "msg": "无相关结果",
                    "code": 7997,
                    "result": False,
                    "status": "success"
                }
                return Response(json.dumps(data), content_type='application/json')
            li = s.query_all(sql, [group_id, ('%' + context + '%'), ])
            if not li:
                data = {
                    "object": None,
                    "msg": "暂无数据",
                    "code": 7996,
                    "result": True,
                    "status": "success"
                }
                return Response(json.dumps(data), content_type='application/json')
            else:
                list_s = []
                for i in range(len(li)):
                    v_id, v_name, v_data, group_id = li[i]
                    list_s.append({
                        "id": v_id,
                        "name": v_name,
                        "data": v_data,
                        "group_name": group_name
                    })
                data = {
                    "object": list_s,
                    "msg": "查询成功",
                    "code": 7995,
                    "result": True,
                    "status": "success"
                }
                return Response(json.dumps(data), content_type='application/json')


@env_variable.route('/env/add_v', methods=['POST'])
def env_add_var():
    # 处理没有传参的问题
    if not request.json:
        data = {
            "object": None,
            "msg": "缺少参数",
            "code": 10000,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    variable = request.json.get('variable', None)
    status = request.json.get('status', 0)
    context = request.json.get('context', None)
    name = request.json.get('name', None)
    data = request.json.get('data', None)
    status = 1 if status == 1 else 0
    if context is None or variable is None or not name or not data:
        data = {
            "object": None,
            "msg": "缺少参数",
            "code": 7999,
            "result": False,
            "status": "success"
        }
        return Response(json.dumps(data), content_type='application/json')
    s = SQLMysql()
    sql = "select group_id from jk_vgroups where group_name=%s"
    # 判断要添加的环境变量，所属的分组是否存在
    is_null = s.query_one(sql, [variable, ])
    if is_null is None:
        data = {
            "object": None,
            "msg": "添加失败，请检查添加数据是否正确",
            "code": 7994,
            "result": False,
            "status": "success"
        }
        return Response(json.dumps(data), content_type='application/json')
    sql_add = "insert into jk_variable (v_name, v_data, group_id, status, create_time) values (%s, %s, %s, %s, now())"
    ok = s.create_one(sql_add, [name, data, (is_null[0]), status, ])
    if ok:
        data = {
            "object": None,
            "msg": "添加成功",
            "code": 7993,
            "result": True,
            "status": "success"
        }
        return Response(json.dumps(data), content_type='application/json')
    else:
        data = {
            "object": None,
            "msg": "未知异常",
            "code": 7992,
            "result": False,
            "status": "success"
        }
        return Response(json.dumps(data), content_type='application/json')


@env_variable.route('/env/add_group', methods=['POST'])
def env_add_group():
    # 处理缺少参数问题
    if not request.json:
        data = {
            "object": None,
            "msg": "缺少参数",
            "code": 10000,
            "result": False,
            "status": "success"
        }
        return Response(json.dumps(data), content_type='application/json')
    group_name = request.json.get('group_name', None)
    status = request.json.get('status', 0)
    status = 1 if status == 1 else 0
    if not group_name:
        data = {
            "object": None,
            "msg": "缺少参数",
            "code": 7899,
            "result": False,
            "status": "success"
        }
        return Response(json.dumps(data), content_type='application/json')
    s = SQLMysql()
    sql = "select group_id from jk_vgroups where group_name=%s"
    # 判断当前是否已经存在分组
    is_null = s.query_one(sql, [group_name, ])
    if is_null:
        data = {
            "object": None,
            "msg": "当前分组已存在，请勿重复添加",
            "code": 7898,
            "result": False,
            "status": "success"
        }
        return Response(json.dumps(data), content_type='application/json')
    sql_add = "insert into jk_vgroups (group_name, status, create_time) values (%s, %s, now())"
    ok = s.create_one(sql_add, [group_name, status, ])
    if ok:
        data = {
            "object": None,
            "msg": "添加成功",
            "code": 7897,
            "result": True,
            "status": "success"
        }
        return Response(json.dumps(data), content_type='application/json')
    else:
        data = {
            "object": None,
            "msg": "未知异常",
            "code": 7896,
            "result": False,
            "status": "success"
        }
        return Response(json.dumps(data), content_type='application/json')


@env_variable.route('/env/update_v', methods=['POST'])
def env_update_v():
    # 处理没有传参的问题
    if not request.json:
        data = {
            "object": None,
            "msg": "缺少参数",
            "code": 10000,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    name = request.json.get('name', None)
    v_id = request.json.get('v_id', None)
    data = request.json.get('data', None)
    status = request.json.get('status', None)
    print(status)
    status = status if status == 0 or status == 1 else None
    print(name, v_id, status, data)
    if not status or not name or not data or not v_id:
        data = {
            "object": None,
            "msg": "参数非法",
            "code": 7799,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    sql_s = "select v_id, group_id from jk_variable where v_id=%s"
    s = SQLMysql()
    # 判断修改的值是否存在
    is_null = s.query_one(sql_s, [v_id, ])
    if not is_null:
        data = {
            "object": None,
            "msg": "修改失败",
            "code": 7798,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    sql_y = "select status from jk_vgroups where group_id=%s"
    kill = s.query_one(sql_y, [(is_null[1]), ])
    # 判断当前环境变量分组是否是禁用状态，所在分组处于禁用状态时，不允许修改环境变量内容
    if kill[0] == 0:
        data = {
            "object": None,
            "msg": "当前环境变量所在分组已被禁用，无法修改环境变量",
            "code": 7797,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    sql_u = "update jk_variable set v_name=%s, v_data=%s, status=%s, modfiy_time=now() where v_id=%s"
    ok = s.update_one(sql_u, [name, data, status, v_id, ])
    if ok:
        data = {
            "object": None,
            "msg": "修改成功",
            "code": 7796,
            "result": True
        }
        return Response(json.dumps(data), content_type='application/json')
    else:
        data = {
            "object": None,
            "msg": "未知异常",
            "code": 7795,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')


@env_variable.route('/env/update_g', methods=['POST'])
def env_update_g():
    # 处理没有传参的问题
    if not request.json:
        data = {
            "object": None,
            "msg": "缺少参数",
            "code": 10000,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    group_id = request.json.get('group_id', None)
    group_name = request.json.get('group_name', None)
    status = request.json.get('status', None)
    status = status if status == 1 or status == 0 else None
    if not group_id or not group_name or not status:
        data = {
            "object": None,
            "msg": "参数非法",
            "code": 7699,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    s = SQLMysql()
    # 判断修改的分组是否存在
    sql_y = "select group_id from jk_vgroups where group_name=%s"
    is_null = s.query_one(sql_y, [group_name, ])
    if not is_null:
        data = {
            "object": None,
            "msg": "分组不存在",
            "code": 7698,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    sql = "update jk_vgroups set group_name=%s, status=%s, modfiy_time=now() where group_id=%s"
    ok = s.update_one(sql, [group_name, status, group_id, ])
    if ok:
        data = {
            "object": None,
            "msg": "修改成功",
            "code": 7796,
            "result": True
        }
        return Response(json.dumps(data), content_type='application/json')
    else:
        data = {
            "object": None,
            "msg": "未知异常",
            "code": 7795,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')


@env_variable.route('/env/delete_v', methods=['POST'])
def env_delete_v():
    # 处理没有传参的问题
    if not request.json:
        data = {
            "object": None,
            "msg": "缺少参数",
            "code": 10000,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    v_id = request.json.get('v_id', None)
    if not v_id:
        data = {
            "object": None,
            "msg": "参数非法",
            "code": 7794,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    s = SQLMysql()
    # 判断是否存在此变量
    sql = "select v_id from jk_variable where v_id=%s"
    is_null = s.query_one(sql, [v_id, ])
    if not is_null:
        data = {
            "object": None,
            "msg": "数据不存在",
            "code": 7793,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    sql_d = "delete from jk_variable where v_id=%s"
    ok = s.update_one(sql_d, [v_id, ])
    if ok:
        data = {
            "object": None,
            "msg": "删除成功",
            "code": 7792,
            "result": True
        }
        return Response(json.dumps(data), content_type='application/json')
    else:
        data = {
            "object": None,
            "msg": "未知异常",
            "code": 7791,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')


@env_variable.route('/env/delete_g', methods=['POST'])
def env_delete_g():
    # 处理没有传参的问题
    if not request.json:
        data = {
            "object": None,
            "msg": "缺少参数",
            "code": 10000,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    group_id = request.json.get('group_id', None)
    if not group_id:
        data = {
            "object": None,
            "msg": "参数非法",
            "code": 7599,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    s = SQLMysql()
    # 判断当前分组是否存在
    sql_s = "select group_id from jk_vgroups where group_id=%s"
    is_null = s.query_one(sql_s, [group_id, ])
    if not is_null:
        data = {
            "object": None,
            "msg": "分组数据不存在，删除失败",
            "code": 7598,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    # 判断该分组下，是否还有环境变量，如果有的话，不允许删除分组 保证数据完整性
    sql_y = "select v_id from jk_variable where group_id=%s"
    is_n = s.query_one(sql_y, [(is_null[0]), ])
    if is_n:
        data = {
            "object": None,
            "msg": "当前分组下存在关联环境变量，无法删除，请先删除该分组下的所有环境变量",
            "code": 7597,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')
    # 如果不存在环境变量，则可以直接删除
    sql_del = "delete from jk_vgroups where group_id=%s"
    ok = s.update_one(sql_del, [(is_null[0]), ])
    if ok:
        data = {
            "object": None,
            "msg": "删除成功",
            "code": 7596,
            "result": True
        }
        return Response(json.dumps(data), content_type='application/json')
    else:
        data = {
            "object": None,
            "msg": "未知异常",
            "code": 7595,
            "result": False
        }
        return Response(json.dumps(data), content_type='application/json')

