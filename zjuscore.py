import argparse
import json
import difflib
import sys
import requests
from zjusess import zjusess
from scorenotification import scorenotification

# 用于中文对齐输出 
def pad_len(string, length):
    return length - len(string.encode('GBK')) + len(string)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ZJU Score Assistant')
    parser.add_argument('-i', '--initial', nargs=2, metavar=('username', 'password'), help='initialize your information')
    parser.add_argument('-u', '--update', action='store_true', help='update the course score')
    parser.add_argument('-ls', '--list', nargs='*', metavar=('YEAR', 'SEMESTER'), help='list the course and score in a certain year/semester')
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

        username = args.initial[0]
        password = args.initial[1]

        session = zjusess()
        if not session.login(username, password):
            print('Invalid username or password. Please check them again and use -i to reset them.')
            sys.exit()
        else:
            with open("database.json", 'w') as load_f:
                load_f.write(json.dumps(database))
            print('Initial Success!')
        session.close()

    data = {}
    if args.update:
        session = zjusess()
        with open('database.json', 'r') as f:
            userdata = json.load(f)
        username = userdata['username']
        password = userdata['password']
        try:
            res = session.login(username, password)
        except requests.exceptions.ConnectionError:
            print('Cannot connect to the Internet. Please check your Internet connection.')
        else:
            if not res:
                print('Login failed. Please check your username and password. Remember to use -i to reset them.')
            else:
                #打开成绩查询网站
                res = session.get(r'http://appservice.zju.edu.cn/zdjw/cjcx/cjcxjg?lx=0&xn=&xq=&cjd=&xqtit=%E6%98%A5%E3%80%81%E5%A4%8F')
                res = session.post('http://appservice.zju.edu.cn/zju-smartcampus/zdydjw/api/kkqk_cxXscjxx')

                data = dict(enumerate(res.json()['data']['list']))
                with open('userscore.json', 'w') as f:
                    f.write(json.dumps(data))
                print('Updated Success!')
    else:
        try:
            with open('userscore.json', 'r') as f:
                data = json.load(f)
        except:
            print('Cannot find your score data, please use -u to update first.')

    if args.list != None:
        if len(args.list) == 0:
            
            courses = data.values()
            if len(courses) == 0:
                print(f'Cannot find any courses.')
            else:
                print(f'{"Semeter":16s}{"Name":20s}\tMark\tGP\tCredit')
                for course in courses:
                    print('{0:<{len0}}{1:<{len1}}\t{2}\t{3}\t{4}'.format(
                        f"{course.get('xn')} {course.get('xq')}", 
                        course.get('kcmc'),
                        course.get('cj'),
                        course.get('jd'),
                        course.get('xf'),
                        len0 = pad_len(f"{course.get('xn')} {course.get('xq')}", 16),
                        len1 = pad_len(course.get('kcmc'), 20)))

        elif len(args.list) == 1:

            courses = [i for i in data.values() if i.get('xn').find(args.list[0]) == 0]

            if len(courses) == 0:
                print(f'Cannot find any courses.')
            else:
                print(f'{"Semeter":16s}{"Name":20s}\tMark\tGP\tCredit')
                for course in courses:
                    print('{0:<{len0}}{1:<{len1}}\t{2}\t{3}\t{4}'.format(
                        f"{course.get('xn')} {course.get('xq')}", 
                        course.get('kcmc'),
                        course.get('cj'),
                        course.get('jd'),
                        course.get('xf'),
                        len0 = pad_len(f"{course.get('xn')} {course.get('xq')}", 16),
                        len1 = pad_len(course.get('kcmc'), 20)))

        elif len(args.list) >= 2:
            if len(args.list) > 2:
                print(f'The following argument(s) will be ignored:\n\t{" ".join(args.list[2:])}')

            courses = [i for i in data.values() if i.get('xn').find(args.list[0]) == 0 and args.list[1].find(i.get('xq')) != -1]

            if len(courses) == 0:
                print(f'Cannot find any courses.')
            else:
                print(f'{"Semeter":16s}{"Name":20s}\tMark\tGP\tCredit')
                for course in courses:
                    print('{0:<{len0}}{1:<{len1}}\t{2}\t{3}\t{4}'.format(
                        f"{course.get('xn')} {course.get('xq')}", 
                        course.get('kcmc'),
                        course.get('cj'),
                        course.get('jd'),
                        course.get('xf'),
                        len0 = pad_len(f"{course.get('xn')} {course.get('xq')}", 16),
                        len1 = pad_len(course.get('kcmc'), 20)))

    if args.name:
        coursename = [i.get('kcmc') for i in data.values()]
        res = []
        for searchcourse in args.name:
            res += difflib.get_close_matches(searchcourse, coursename, cutoff=0.3)
        res = list(dict().fromkeys(res).keys())
        if len(res) == 0:
            print(f'Cannot find any course matching keyword(s) {" ".join(args.name)}')
        else:
            print(f'{"Semeter":16s}{"Name":20s}\tMark\tGP\tCredit')
            for name in res:
                for course in data.values():
                    if course.get('kcmc') == name:
                        print('{0:<{len0}}{1:<{len1}}\t{2}\t{3}\t{4}'.format(
                        f"{course.get('xn')} {course.get('xq')}", 
                        course.get('kcmc'),
                        course.get('cj'),
                        course.get('jd'),
                        course.get('xf'),
                        len0 = pad_len(f"{course.get('xn')} {course.get('xq')}", 16),
                        len1 = pad_len(course.get('kcmc'), 20)))

    if args.gpa != None:
        if len(args.gpa) == 0:
            
            grade = [i.get('jd') for i in data.values()]
            credit = [float(i.get('xf')) for i in data.values()]

            if len(grade) == 0:
                print('Cannot find any courses.')
            else:
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

            grade = [i.get('jd') for i in data.values() if i.get('xn').find(args.gpa[0]) == 0 and args.gpa[1].find(i.get('xq')) != -1]
            credit = [float(i.get('xf')) for i in data.values() if i.get('xn').find(args.gpa[0]) == 0 and args.gpa[1].find(i.get('xq')) != -1]

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