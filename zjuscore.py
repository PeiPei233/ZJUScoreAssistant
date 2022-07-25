import argparse
import json
import difflib
from zjusess import zjusess
from scorenotification import scorenotification

parser = argparse.ArgumentParser(description='ZJU Score Assistant')
parser.add_argument('-i', '--initial', nargs=2, metavar=('username', 'password'), help='initialize your information')
parser.add_argument('-u', '--update', action='store_true', help='update the course score')
parser.add_argument('-n', '--name', nargs='+', help='search score by the name of the course')
parser.add_argument('-g', '--gpa', nargs='*', metavar=('YEAR', 'SEMESTER'), help='calculator the gpa')
parser.add_argument('-d', '--ding', nargs='?', metavar=('DingWebhook'), default=argparse.SUPPRESS, help='set your DingTalk Robot Webhook. Empty means disabled')
parser.add_argument('-dn', '--dnotification', action='store_true', help='enable dingtalk score notification')
args = parser.parse_args()

if args.initial:
    database = {
        'username': args.initial[0],
        'password': args.initial[1],
    }

    with open("database.json", 'w') as load_f:
        load_f.write(json.dumps(database))

data = {}
if args.update:
    session = zjusess()
    with open('database.json', 'r') as f:
        userdata = json.load(f)
    username = userdata['username']
    password = userdata['password']

    session.login(username, password)

    #打开成绩查询网站
    res = session.get(r'http://appservice.zju.edu.cn/zdjw/cjcx/cjcxjg?lx=0&xn=&xq=&cjd=&xqtit=%E6%98%A5%E3%80%81%E5%A4%8F')
    res = session.post('http://appservice.zju.edu.cn/zju-smartcampus/zdydjw/api/kkqk_cxXscjxx')

    data = dict(enumerate(res.json()['data']['list']))
    with open('userscore.json', 'w') as f:
        f.write(json.dumps(data))
else:
    try:
        with open('userscore.json', 'r') as f:
            data = json.load(f)
    except:
        print('cannot find your score data, please use -u to update first.')

if args.name:
    coursename = [i.get('kcmc') for i in data.values()]
    res = []
    for searchcourse in args.name:
        res += difflib.get_close_matches(searchcourse, coursename, cutoff=0.3)
    res = list(dict().fromkeys(res).keys())
    for name in res:
        for course in data.values():
            if course.get('kcmc') == name:
                print(course.get('xn'), course.get('xq'), name, course.get('cj'), course.get('xf'), course.get('jd'))

if args.gpa != None:
    if len(args.gpa) == 0:
        
        grade = [i.get('jd') for i in data.values()]
        credit = [float(i.get('xf')) for i in data.values()]
        gp = .0
        for i in range(len(grade)):
            gp += grade[i] * credit[i]
        totcredit = sum(credit)
        gpa = 0
        if totcredit != 0:
            gpa = gp / totcredit
        print('Your GPA during the whole college is %.2f' % gpa)

    elif len(args.gpa) == 1:

        grade = [i.get('jd') for i in data.values() if i.get('xn').find(args.gpa[0]) == 0]
        credit = [float(i.get('xf')) for i in data.values() if i.get('xn').find(args.gpa[0]) == 0]

        if len(grade) == 0:
            print(f'Cannot find any courses about the academic year of {args.gpa[0]}')
        else:
            gp = .0
            for i in range(len(grade)):
                gp += grade[i] * credit[i]
            totcredit = sum(credit)
            gpa = .0
            if totcredit != 0:
                gpa = gp / totcredit
            
            year = args.gpa[0]

            for i in data.values():
                if i.get('xn').find(args.gpa[0]) == 0:
                    year = i.get('xn')
                    break

            print('Your GPA during the academic year of %s is %.2f' % (year, gpa))

    elif len(args.gpa) >= 2:
        if len(args.gpa) > 2:
            print(f'The following argument(s) will be ignored:\n\t{" ".join(args.gpa[2:])}')

        grade = [i.get('jd') for i in data.values() if i.get('xn').find(args.gpa[0]) == 0 and i.get('xq') == args.gpa[1]]
        credit = [float(i.get('xf')) for i in data.values() if i.get('xn').find(args.gpa[0]) == 0 and i.get('xq') == args.gpa[1]]

        if len(grade) == 0:
            print(f'Cannot find any courses about the semester of {" ".join(args.gpa[:2])}')
        else:
            gp = .0
            for i in range(len(grade)):
                gp += grade[i] * credit[i]
            totcredit = sum(credit)
            gpa = .0
            if totcredit != 0:
                gpa = gp / totcredit
            
            year = args.gpa[0]
            semster = args.gpa[1]

            for i in data.values():
                if i.get('xn').find(args.gpa[0]) == 0:
                    year = i.get('xn')
                    break

            print('Your GPA during the semester of %s %s is %.2f' % (year, semster, gpa))

try:
    if args.ding:
        try:
            with open('database.json', 'r') as f:
                userdata = json.load(f)
        except json.decoder.JSONDecodeError:
            userdata = {}
        userdata['url'] = args.ding
        with open("database.json", 'w') as load_f:
            load_f.write(json.dumps(userdata))
    else:
        try:
            with open('database.json', 'r') as f:
                userdata = json.load(f)
        except json.decoder.JSONDecodeError:
            userdata = {}
        userdata['url'] = 'https://oapi.dingtalk.com/robot/send?access_token='
        with open("database.json", 'w') as load_f:
            load_f.write(json.dumps(userdata))
except AttributeError:
    pass

if args.dnotification:
    scorenotification()