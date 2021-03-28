import os
import requests as r
import json
from requests_html import HTMLSession

# 校园网登录程序，修改账号即可使用
_user_data = {
    'name': '',  # 填写账号
    'password': ''  # 填写密码
}


def login(user):
    base = 'http://10.100.1.34'
    link = base + '/eportal/InterFace.do?method=login'
    link_out = base + '/eportal/InterFace.do?method=logout'

    out_data = {

    }
    my_name = user['name']
    my_password = user['password']

    data = {'service': '', 'queryString': 'null', 'operatorPwd': '', 'operatorUserId': '', 'validcode': '',
            'passwordEncrypt': 'false', 'userId': my_name, 'password': my_password}

    try:
        rq = r.post(link, data=data)
    except r.exceptions.ConnectionError:
        print("登录失败，网络存在问题")
        input('回车键继续...')
    else:
        dict_info = json.loads(rq.text)
        try:
            out_data['userIndex'] = dict_info["userIndex"]
        except KeyError:
            print("登录失败，没有userIndex信息，本脚本可能已经失效")
            input('回车键继续...')
        else:
            if out_data['userIndex'] is not None:
                print("本机登录成功，点击回车键可以进行下线，不想下线就直接关掉这个窗口！")
                input('按回车键下线本机...')
                r.post(link_out, data=out_data)
            else:
                print("登录失败，登录设备可能上限(或者密码错误，账号欠费)")
                logout(user)


def logout(user):
    base_link = 'http://10.100.1.35:8080'
    link_list = base_link + '/selfservice/module/webcontent/web/onlinedevice_list.jsf'
    link_login = base_link + '/selfservice/module/scgroup/web/login_judge.jsf'
    link_logout = base_link + '/selfservice/module/userself/web/userself_ajax.jsf?methodName=indexBean.kickUserBySelfForAjax'

    header = {
        'Cookie': ''
    }

    logout_data = {

    }
    req_setCookie = r.get(link_list)
    cookie = req_setCookie.headers['Set-Cookie']
    header['Cookie'] = cookie.split(';')[0]
    # 进行登录
    r.post(link_login, headers=header, data=user)

    session = HTMLSession()
    req = session.post(link_list, headers=header)

    text = req.html.find('input.xia1')
    # 曲线救国，暂时无法解决乱码问题
    my_android = '�ҵİ�׿'
    my_computer = '�ҵĵ���'
    my_iphone = '�ҵ�ƻ��'
    # 一些临时定义的数据
    dv_id = []
    dv_name = {

    }
    dv_list = {

    }
    dv_num = 1

    for my in text:
        did = my.xpath('//input/@onclick')
        dv_id.append(did[0].split('\'')[1])

    for my in dv_id:

        text = req.html.find('span#aa' + my + ' > span#a1')
        ip = text[0].text.split(' : ')[1]

        text = req.html.find('label#' + my + '.lablesub')
        title = text[0].xpath('//label/@title')[0]
        if title == my_android:
            dv_name[str(dv_num)] = '我的安卓'
            dv_list['我的安卓'] = ip
            dv_num = dv_num + 1
        if title == my_computer:
            dv_name[str(dv_num)] = '我的电脑'
            dv_list['我的电脑'] = ip
            dv_num = dv_num + 1
        if title == my_iphone:
            dv_name[str(dv_num)] = '我的苹果'
            dv_list['我的苹果'] = ip
            dv_num = dv_num + 1

    print(dv_name)
    remove_user(dv_name)
    logout_id = input('输入要下线的设备序号：\n')
    logout_data['key'] = (user['name'] + ':' + dv_list[dv_name[str(logout_id)]])

    # 设备下线操作
    r.post(link_logout, headers=header, data=logout_data)
    # 再次登录
    login(user)


def save_user():
    with open("./user.json", "w") as dump_f:
        json.dump(_user_data, dump_f)
        print('账号密码已保存到当前目录 文件名: user.json')


def remove_user(dv_name):
    if len(dv_name) == 0:
        ch = input('是否删除账号密码文件？(按回车键进行删除，输入n跳过)\n')
        if ch == 'n' or ch == 'N':
            exit()
        os.remove(os.path.join('./user.json'))
        exit(-1)


if __name__ == '__main__':
    try:
        with open("./user.json", 'r') as load_f:
            _user_data = json.load(load_f)
    except:
        print('欢迎使用校园网登录程序！\n')
        name = input('请输入账号：\n')
        password = input('请输入密码：\n')
        _user_data['name'] = name
        _user_data['password'] = password
        save_user()

    login(_user_data)
