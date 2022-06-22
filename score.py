from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import random
import json
import requests

def updatescore():
    #获取学号、密码、钉钉机器人Webhook
    with open("database.json", 'r') as load_f:
        userdata = json.load(load_f)

    username = userdata['username']
    password = userdata['password']
    url = userdata.get('url', 'https://oapi.dingtalk.com/robot/send?access_token=')

    #打开无头浏览器
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    #打开教务系统
    driver.get('https://zjuam.zju.edu.cn/cas/login?service=http://jwbinfosys.zju.edu.cn/default2.aspx')

    #登录
    driver.find_element(by=By.ID, value='username').send_keys(username)
    driver.find_element(by=By.ID, value='password').send_keys(password)
    driver.find_element(by=By.ID, value='dl').click()
    sleep(0.5)

    #关闭通知
    driver.find_element(by=By.ID, value='Button1').click()

    #成绩查询
    driver.find_element(by=By.ID, value='xsmain_cx.htm').click()
    driver.find_element(by=By.CLASS_NAME, value='iconcjcx').click()

    #切换到新页面
    handle = driver.window_handles
    driver.switch_to.window(handle[-1])

    #在校成绩查询
    driver.find_element(by=By.ID, value='Button2').click()

    #获取成绩信息表格
    table = driver.find_element(by=By.ID, value='DataGrid1').find_elements(by=By.TAG_NAME, value='tr')

    #获取存在本地的成绩信息表格
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
    for tr in table:
        content = (tr.text).split()
        # print(content)
        if content[0] == '选课课号':
            continue
        if userscore.get(content[0]) != None:
            continue
        
        #新的成绩更新
        userscore[content[0]] = {
            'name': content[1],
            'score': content[2],
            'credit': content[3],
            'gp': content[4]
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
 - **成绩变化**\t%.2f(%+.2f) / %.1f(%+.1f)" % (content[0], content[1], content[2], content[3], content[4], newgpa, newgpa - gpa, newtotcredits, newtotcredits - totcredits)
            }
        })
        print('考试成绩通知\n选课课号\t%s\n课程名称\t%s\n成绩\t%s\n学分\t%s\n绩点\t%s\n成绩变化\t%.2f(%+.2f) / %.1f(%+.1f)' % (content[0], content[1], content[2], content[3], content[4], newgpa, newgpa - gpa, newtotcredits, newtotcredits - totcredits))
        totcredits = newtotcredits
        totgp = newtotgp
        gpa = newgpa

    #保存新的数据
    with open("userscore.json", 'w') as load_f:
        load_f.write(json.dumps(userscore))

    driver.quit()

while True:
    updatescore()
    sleep(random.randint(60, 420))