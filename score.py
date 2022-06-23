import requests
import re
import json
import math
import time
import random

def rsa_no_padding(src, modulus, exponent):
    m = int(modulus, 16)
    e = int(exponent, 16)
    t = bytes(src, 'ascii')
    # 字符串转换为bytes
    input_nr = int.from_bytes(t, byteorder='big')
    # 将字节转化成int型数字，如果没有标明进制，看做ascii码值
    crypt_nr = pow(input_nr, e, m)
    # 计算x的y次方，如果z在存在，则再对结果进行取模，其结果等效于pow(x,y) %z
    length = math.ceil(m.bit_length() / 8)
    # 取模数的比特长度(二进制长度)，除以8将比特转为字节
    crypt_data = crypt_nr.to_bytes(length, byteorder='big')
    # 将密文转换为bytes存储(8字节)，返回hex(16字节)
    return crypt_data.hex()

def updatescore():
    session = requests.session()

    # 打开网站
    res = session.get('https://zjuam.zju.edu.cn/cas/login?service=http://jwbinfosys.zju.edu.cn/default2.aspx')
    # 获取execution的值以用于登录
    execution = re.findall(r'<input type="hidden" name="execution" value="(.*?)" />', res.text)[0]
    # 获取RSA公钥
    res = session.get('https://zjuam.zju.edu.cn/cas/v2/getPubKey')
    modulus = res.json()['modulus']
    exponent = res.json()['exponent']

    with open('database.json', 'r') as f:
        userdata = json.load(f)
    username = userdata['username']
    password = userdata['password']
    url = userdata.get('url', 'https://oapi.dingtalk.com/robot/send?access_token=')

    rsapwd = rsa_no_padding(password, modulus, exponent)

    data = {
        'username': username,
        'password': rsapwd,
        'execution': execution,
        '_eventId': 'submit'
    }
    # 登录
    res = session.post('https://zjuam.zju.edu.cn/cas/login?service=http://jwbinfosys.zju.edu.cn/default2.aspx', data)
    #打开成绩查询网站
    res = session.get('http://jwbinfosys.zju.edu.cn/xsdhqt.aspx?dl=iconcjcx')
    #获取__VIEWSTATE以用于查询
    viewstate = re.findall(r'<input type="hidden" name="__VIEWSTATE" value="(.*?)" />', res.text)[0]
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }

    res = session.post(url='http://jwbinfosys.zju.edu.cn/xscj.aspx?xh=' + username,
        data={
            '__VIEWSTATE': viewstate,
            'ddlXN': '',
            'ddlXQ': '',
            'txtQSCJ': '',
            'txtZZCJ': '',
            'Button2': r'%D4%DA%D0%A3%D1%A7%CF%B0%B3%C9%BC%A8%B2%E9%D1%AF'
        },
        headers=headers
        )

    # 成绩的表格
    table = re.finditer(r'<td>(?P<id>.*?)</td><td>(?P<name>.*?)</td><td>(?P<score>.*?)</td><td>(?P<credit>.*?)</td><td>(?P<gp>.*?)</td>', res.text)

    with open("userscore.json", 'r') as load_f:
            userscore = json.load(load_f)
    totcredits = 0
    totgp = 0
    for lesson in userscore:
        totgp += float(userscore[lesson]['gp']) * float(userscore[lesson]['credit'])
        totcredits += float(userscore[lesson]['credit'])
    try:
        gpa = totgp / totcredits
    except:
        gpa = 0

    #对比以更新
    for lesson in table:
        id = lesson.group('id')
        name = lesson.group('name')
        score = lesson.group('score')
        credit = lesson.group('credit')
        gp = lesson.group('gp')
        if id == '选课课号':
            continue
        if userscore.get(id) != None:
            continue

        #新的成绩更新
        userscore[id] = {
            'name': name,
            'score': score,
            'credit': credit,
            'gp': gp
        }
        newtotcredits = 0
        newtotgp = 0
        for lesson in userscore:
            newtotgp += float(userscore[lesson]['gp']) * float(userscore[lesson]['credit'])
            newtotcredits += float(userscore[lesson]['credit'])
        try:
            newgpa = newtotgp / newtotcredits
        except:
            newgpa = 0

            #钉钉推送消息
            requests.post(url=url, json={
                "msgtype": "markdown",
                "markdown" : {
                    "title": "考试成绩通知",
                    "text": "\
### 考试成绩通知\n\
 - **选课课号**\t%s\n\
 - **课程名称**\t%s\n\
 - **成绩**\t%s\n\
 - **学分**\t%s\n\
 - **绩点**\t%s\n\
 - **成绩变化**\t%.2f(%+.2f) / %.1f(%+.1f)" % (id, name, score, credit, gp, newgpa, newgpa - gpa, newtotcredits, newtotcredits - totcredits)
                }
            })
        print('考试成绩通知\n选课课号\t%s\n课程名称\t%s\n成绩\t%s\n学分\t%s\n绩点\t%s\n成绩变化\t%.2f(%+.2f) / %.1f(%+.1f)' % (id, name, score, credit, gp, newgpa, newgpa - gpa, newtotcredits, newtotcredits - totcredits))
        totcredits = newtotcredits
        totgp = newtotgp
        gpa = newgpa

    #保存新的数据
    with open("userscore.json", 'w') as load_f:
        load_f.write(json.dumps(userscore))

while True:
    try:
        updatescore()
    except:
        print(time.ctime() + " Fail")
    finally:
        time.sleep(random.randint(60, 300))