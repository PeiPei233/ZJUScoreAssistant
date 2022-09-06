import argparse
import pickle
import json
import difflib
import sys
import requests
import os
import getpass
from zjusess import zjusess
from scorenotification import scorenotification

# 用于中文对齐输出 
def pad_len(string, length):
    return length - len(string.encode('GBK')) + len(string)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ZJU Score Assistant')
    parser.add_argument('-i', '--login', action='store_true', help='log in with ZJUAM account')
    parser.add_argument('-o', '--logout', action='store_true', help='log out')
    parser.add_argument('-u', '--update', action='store_true', help='update the course score')
    parser.add_argument('-ls', '--list', nargs='*', metavar=('YEAR', 'SEMESTER'), help='list the course and score in a certain year/semester')
    parser.add_argument('-n', '--name', nargs='+', help='search score by the name of the course')
    parser.add_argument('-g', '--gpa', nargs='*', metavar=('YEAR', 'SEMESTER'), help='calculator the gpa')
    parser.add_argument('-d', '--ding', nargs='?', metavar=('DingWebhook'), default=argparse.SUPPRESS, help='set your DingTalk Robot Webhook. Empty means disabled')
    parser.add_argument('-dn', '--dnotification', action='store_true', help='enable dingtalk score notification')
    args = parser.parse_args()

    if args.login:

        username = input("ZJUAM account's username: ")
        password = getpass.getpass(f"ZJUAM {username}'s password: ")

        session = zjusess()

        try:
            if not session.login(username, password):
                print('Log in failed. Please check your username and password again and use -i to reset them.')
                sys.exit()
        except requests.exceptions.ConnectionError:
            print('Cannot connect to the Internet. Please check your Internet connection.')
            sys.exit()
        else:
            with open("cookies.pkl", 'wb') as load_f:
                pickle.dump(session.cookies, load_f)
            print('Login succeeded!')
        session.close()

        try:
            with open('database.json', 'r') as f:
                userdata = json.load(f)
        except:
            userdata = {}
        userdata['username'] = username
        with open('database.json', 'w') as f:
            f.write(json.dumps(userdata))

    if args.logout:
        try:
            os.remove('cookies.pkl')
        except FileNotFoundError:
            print('You have not logged in.')
        else:
            print('Logout succeeded!')

    data = {}
    if args.update:
        session = zjusess()
        try:
            with open('cookies.pkl', 'rb') as f:
                cookies = pickle.load(f)
        except:
            print('You have not logged in. Please use -i to log in first.')
            sys.exit()
        
        session.cookies = cookies

        try:
            res = session.get('https://zjuam.zju.edu.cn/cas/login')
            if res.text.find('统一身份认证平台'):
                print('The identity authentication has expired. Please use -i to log in again.')
                sys.exit()

            #打开成绩查询网站
            res = session.get(r'http://appservice.zju.edu.cn/zdjw/cjcx/cjcxjg?lx=0&xn=&xq=&cjd=&xqtit=%E6%98%A5%E3%80%81%E5%A4%8F')
            res = session.post('http://appservice.zju.edu.cn/zju-smartcampus/zdydjw/api/kkqk_cxXscjxx')

            data = dict(enumerate(res.json()['data']['list']))
            with open('userscore.json', 'w') as f:
                f.write(json.dumps(data))
            print('Updated Successfully!')
        except requests.exceptions.ConnectionError:
            print('Cannot connect to the Internet. Please check your Internet connection.')
            sys.exit()
        session.close()
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
                print(f'Cannot find any courses about the academic year of {args.list[0]}.')
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
                print(f'Warning: The following argument(s) will be ignored:\n\t{" ".join(args.list[2:])}')

            courses = [i for i in data.values() if i.get('xn').find(args.list[0]) == 0 and args.list[1].find(i.get('xq')) != -1]

            if len(courses) == 0:
                print(f'Cannot find any courses about the semester of {" ".join(args.list[:2])}.')
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
                print(f'Warning: The following argument(s) will be ignored:\n\t{" ".join(args.gpa[2:])}')

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