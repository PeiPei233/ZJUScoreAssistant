# ScoreNotification
Notification of ZJU score based on Selenium

The application will get your score in ZJU every 5 minutes and inform you by DingTalk Robot

## Usage
1. Download the zip from this repository.
2. Using `pip install -r requirements.txt` to install the requirements
3. Download the chromedriver suitable to your chrome version from <https://chromedriver.chromium.org/downloads>
3. Set your DingTalk Robot. In the robot security setting, just add `成绩` to the custom keyword. You can customized your robot's photo and name like the following example.
4. Add your information into `database.json`
    - `username`    the username to log in ZJU Unfied Identity Authentication, usually your Student ID in ZJU
    - `password`    the password to log in ZJU Unfied Identity Authentication.
    - `url` the Webhook of your DingTalk Robot
5. Run `python score.py`

**Notice** For a better experience, it is recommended that you put this application on the server.

## Examples:

![notification](./screenshot/notification.jpg)

![dingtalkrobot](./screenshot/dingtalkrobot.jpg)
