# ZJUScoreAssistant

Assistant of ZJU score.

This is a very naive command line score assistant, which is used for querying your score in ZJU, calculating your GPA, score update notification and so on.

[中文文档](./README_CN.md)

## Run

Download the zip from this repository and unzip, or git this repository to your computer. Then run `python zjuscore.py -h` to get the help.

## Usage Manual

You can use the score assistant through the following arguments:

```powershell
python zjuscore.py [-h] [-i username password] [-u] [-ls [YEAR [SEMESTER ...]]] [-n NAME [NAME ...]]
                   [-g [YEAR [SEMESTER ...]]] [-d [DingWebhook]] [-dn]
```

### Get Help

Use `-h` or `--help` to get help.

```powershell
PS > python zjuscore.py -h
usage: zjuscore.py [-h] [-i] [-u] [-ls [YEAR [SEMESTER ...]]] [-n NAME [NAME ...]]
                   [-g [YEAR [SEMESTER ...]]] [-d [DingWebhook]] [-dn]

ZJU Score Assistant

options:
  -h, --help            show this help message and exit
  -i, --initial         initialize your information
  -u, --update          update the course score
  -ls [YEAR [SEMESTER ...]], --list [YEAR [SEMESTER ...]]
                        list the course and score in a certain year/semester
  -n NAME [NAME ...], --name NAME [NAME ...]
                        search score by the name of the course
  -g [YEAR [SEMESTER ...]], --gpa [YEAR [SEMESTER ...]]
                        calculator the gpa
  -d [DingWebhook], --ding [DingWebhook]
                        set your DingTalk Robot Webhook. Empty means disabled
  -dn, --dnotification  enable dingtalk score notification
```

### Initialize the Score Assistant

You need to log in to get your score information, so it is necessary to let the assistant to know your username (usually your student ID) and password. You can use `-i` or `--initial` to initialize. Then the program will ask for your information and automatically verify your username and password. Your information will be saved on your computer.

```powershell
PS > python zjuscore.py -i
ZJUAM account's username: 3200106666
ZJUAM 3200106666's password: 
Error: Invalid username or password. Please check them again and use -i to reset them.

PS > python zjuscore.py -i
ZJUAM account's username: 3200106666
ZJUAM 3200106666's password: 
Done: Initial Success!
```

### Update the Score on your Computer

You can use the argument `-u` or `--update` to update the score information stord on your computer. This operation is used to avoid wasting time by having to get your information every time you use the program. 

```powershell
PS > python zjuscore.py -u
Updated Success!
```

### Score Query

Use `-ls` or `--list` to query your score. It supports the following three ways to use it:

- `python zjuscore.py -ls` can query all your score information during college.
- `python zjuscore.py -ls <ACADEMIC YEAR>` can query your information during a certain academic year. You can replace `<ACADEMIC YEAR>` with `2021` or `2021-2022` to query all your courses' score in the 2021-2022 academic year.
- `python zjuscore.py -ls <ACADEMIC YEAR> <SEMESTER>` can query your score information during a certain semester. You can replace `<ACADEMIC YEAR>` with `2021` or `2021-2022`, and replace `<SEMESTER>` with `春` `夏` `秋` `冬` or `春夏` `秋冬` and so on, to query all the grades of courses in a certain semester of 2021-2022 academic year.

For example:
```powershell
PS > python zjuscore.py -ls
Semeter         Name                    Mark    GP      Credit
2021-2022 春夏  离散数学及其应用           60      1.5     4.0
2021-2022 夏    社会主义发展史            79      3.3     1.5
......

PS > python zjuscore.py -ls 2021
Semeter         Name                    Mark    GP      Credit
2021-2022 春夏  离散数学及其应用           60      1.5     4.0
......

PS > python zjuscore.py -ls 2021 夏
Semeter         Name                    Mark    GP      Credit
2021-2022 夏    社会主义发展史             79      3.3     1.5
```

In addition, you can use `-n` or `--name` to search for score information, the name of which matching the course name in the following argument(s).

```powershell
PS > python zjuscore.py -n 离散
Semeter         Name                    Mark    GP      Credit
2021-2022 春夏  离散数学及其应用           60      1.5     4.0

PS > python zjuscore.py -n 微寄分 大物
Semeter         Name                    Mark    GP      Credit
2021-2022 春夏  微积分（甲）Ⅱ             80      3.3     5.0
2021-2022 秋冬  微积分（甲）Ⅰ             80      3.3     5.0
2021-2022 春夏  大学物理（乙）Ⅰ           80      3.3     3.0

PS > python zjuscore.py --name 汇编
Cannot find any course matching keyword(s) 汇编
```

### Calculate GPA

Use `-g` or `--gpa` to obtain your GPA of a certain period. The argument(s) and usage of this is consistent with those of `-ls`.

```powershell
PS > python zjuscore.py -g     
Your GPA during the whole college is 3.95

PS > python zjuscore.py -g 2021
Your GPA during the academic year of 2021-2022 is 3.95

PS > python zjuscore.py -g 2021 夏
Your GPA during the semester of 2021-2022 夏 is 3.90
```

### Score Update Notification

Before running the notification assistant, you should use `-d` or `--ding` to set the URL of DingTalk Robot.

- `python zjuscore.py -d https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxx` Set the URL of dingtalk robot webhook.
- `python zjuscore.py -d` Reset the URL of dingtalk robot webhook. This means that you can unable the notification assistant in dingtalk.

You should configure your Dingtalk Robot first to get the URL. You can follow the following steps:

1. Add custom robot.
2. In the robot security setting, just add `成绩` to the custom keyword. You can customized your robot's photo and name like the following examples.
3. Copy the webhook URL provided by the robot and use `-d` to tell the notificaiton assistant mentioned above.

After that, use `python zjuscore.py -dn` or `python zjuscore.py -dnotification` to enable the score update notification. The application will run continuously and synchronize your score from ZJU every 1 to 5 minutes and inform you the updated information by DingTalk Robot.

Once there is an updated information, your dingtalk robot will push the following information automatically:

![](./screenshot/notification.jpg)

![](./screenshot/dingtalkrobot.jpg)

**NOTICE** For a better experience, it is recommended that you put this application on the server when you use notification assistant.

### Arguments Combination

Use the mutiple combination of arguments to simplied the use process. For example:

- Run `python zjuscore.py -i -u -g` to initialize and obtain your GPA.
- Run `python zjuscore.py -i -d https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxx -dn` to initialize and enable the notification assistant.
- Run `python zjuscore.py -u -n xxx` `python zjuscore.py -u -ls` or `python zjuscore.py -u -ls` to make the assistant resynchronize your score information from ZJU every time you query the score information.