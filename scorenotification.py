import imp
import requests
import re
import json
import pickle
import time
import random
import sys
from zjusess import zjusess

def updatescore():

    session = zjusess()

    try:
        with open('cookies.pkl', 'rb') as f:
            cookies = pickle.load(f)
    except:
        print('You have not logged in. Please use -i to log in first.')
        sys.exit()

    try:
        with open('database.json', 'r') as f:
            userdata = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        print('Cannot find your userdata. Please use -i to log in first.')
        sys.exit()
    else:
        username = userdata['username']
        url = userdata.get('url', 'https://oapi.dingtalk.com/robot/send?access_token=')

    
    session.cookies = cookies

    res = session.post('http://jwbinfosys.zju.edu.cn/default2.aspx')
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

    try:
        with open("dingscore.json", 'r') as load_f:
            userscore = json.load(load_f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        userscore = {}

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
        try:
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
        except requests.exceptions.MissingSchema:
            print('The DingTalk Webhook URL is in valid. Please use -d [DingWebhook] to reset it first.')
        
        print('考试成绩通知\n选课课号\t%s\n课程名称\t%s\n成绩\t%s\n学分\t%s\n绩点\t%s\n成绩变化\t%.2f(%+.2f) / %.1f(%+.1f)' % (id, name, score, credit, gp, newgpa, newgpa - gpa, newtotcredits, newtotcredits - totcredits))
        totcredits = newtotcredits
        totgp = newtotgp
        gpa = newgpa

    #保存新的数据
    with open("dingscore.json", 'w') as load_f:
        load_f.write(json.dumps(userscore))
    
    print(time.ctime() + ' Success')

def scorenotification():
    # updatescore()
    while True:
        try:
            updatescore()
        except Exception as e:
            print(time.ctime() + " Fail with exception: " + str(e))
        finally:
            time.sleep(random.randint(60, 300))