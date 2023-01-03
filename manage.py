from flask_script import Manager
from app import app

manager = Manager(app)


@manager.command
def hello():
    print('hello world')


@manager.command
def demo():
    print('无参命令')


@manager.option("-u", "--username", dest="username")
@manager.option("-p", "--password", dest="password")
def login(username, password):
    print("用户名:{}  密码: {}".format(username, password))


if __name__ == '__main__':
    manager.run()

