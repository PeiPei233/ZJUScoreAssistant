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
    res = session.get('https://zjuam.zju.edu.cn/cas/login?service=http://zdbk.zju.edu.cn/jwglxt/xtgl/login_ssologin.html')
    # 获取execution的值以用于登录
    execution = re.findall(r'<input type="hidden" name="execution" value="(.*?)" />', res.text)[0]
    # 获取RSA公钥
    res = session.get('https://zjuam.zju.edu.cn/cas/v2/getPubKey')
    modulus = res.json()['modulus']
    exponent = res.json()['exponent']

    with open('database.json', 'r', encoding="utf-8") as f:
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
    res = session.post('https://zjuam.zju.edu.cn/cas/login?service=http://zdbk.zju.edu.cn/jwglxt/xtgl/login_ssologin.html', data)
    
    gnmkdm = re.findall(r"onclick=\"clickMenu\('(N\d+)','[^']*','成绩查询'", res.text)[0]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Redmi K30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
    }

    res = session.post(url=f'http://zdbk.zju.edu.cn/jwglxt/cxdy/xscjcx_cxXscjIndex.html?doType=query&gnmkdm={gnmkdm}&su={username}', data={
        'xn': None,
        'xq': None,
        'zscjl': None,
        'zscjr': None,
        '_search': 'false',
        'nd': str(int(time.time() * 1000)),
        'queryModel.showCount': 5000,
        'queryModel.currentPage': 1,
        'queryModel.sortName': 'xkkh',
        'queryModel.sortOrder': 'asc',
        'time': 0,
    }, headers=headers)

    new_score = res.json()['items']
    
    try:
        with open("dingscore.json", 'r', encoding="utf-8") as load_f:
            userscore = json.load(load_f)
    except json.decoder.JSONDecodeError:
        userscore = {}
    except FileNotFoundError:
        userscore = {}

    totcredits = 0
    totgp = 0
    for lesson in userscore:
        if userscore[lesson]['score'] in ['合格', '不合格', '弃修']:
            continue
        totgp += float(userscore[lesson]['gp']) * float(userscore[lesson]['credit'])
        totcredits += float(userscore[lesson]['credit'])
    try:
        gpa = totgp / totcredits
    except:
        gpa = 0
    
    #对比以更新
    for lesson in new_score:
        id = lesson['xkkh']
        name = lesson['kcmc']
        score = lesson['cj']
        credit = lesson['xf']
        gp = lesson['jd']
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
            if userscore[lesson]['score'] in ['合格', '不合格', '弃修']:
                continue
            newtotgp += float(userscore[lesson]['gp']) * float(userscore[lesson]['credit'])
            newtotcredits += float(userscore[lesson]['credit'])
        try:
            newgpa = newtotgp / newtotcredits
        except:
            newgpa = 0
        
        #钉钉推送消息
        try:
            requests.post(url=url, json={
                "msgtype": "markdown",
                "markdown" : {
                    "title": "考试成绩通知",
                    "text": """
### 考试成绩通知\n
 - **选课课号**\t%s\n
 - **课程名称**\t%s\n
 - **成绩**\t%s\n
 - **学分**\t%s\n
 - **绩点**\t%s\n
 - **成绩变化**\t%.2f(%+.2f) / %.1f(%+.1f)""" % (id, name, score, credit, gp, newgpa, newgpa - gpa, newtotcredits, newtotcredits - totcredits)
                }
            })
        except requests.exceptions.MissingSchema:
            print('The DingTalk Webhook URL is invalid. Please use -d [DingWebhook] to reset it first.')
        
        print('考试成绩通知\n选课课号\t%s\n课程名称\t%s\n成绩\t%s\n学分\t%s\n绩点\t%s\n成绩变化\t%.2f(%+.2f) / %.1f(%+.1f)' % (id, name, score, credit, gp, newgpa, newgpa - gpa, newtotcredits, newtotcredits - totcredits))
        totcredits = newtotcredits
        totgp = newtotgp
        gpa = newgpa

    #保存新的数据
    with open("dingscore.json", 'w', encoding="utf-8") as load_f:
        load_f.write(json.dumps(userscore, indent=4, ensure_ascii=False))

def scorenotification():
    while True:
        try:
            updatescore()
        except Exception as e:
            print(time.ctime() + " " + str(e))
        finally:
            time.sleep(random.randint(60, 300))