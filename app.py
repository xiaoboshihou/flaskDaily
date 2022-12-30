import os

from flask import Flask, flash, url_for, request, render_template, views, redirect, get_flashed_messages
from werkzeug.routing import BaseConverter
from functools import wraps
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.update(TEMPLATES_AUTO_RELOAD=True)
app.secret_key = 'some_secret'

HOST = '127.0.0.1'
PORT = '3306'
DATABASE_NAME = 'daily_flask'
USERNAME = 'root'
PASSWORD = 'Abcde_12345'

DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{databasename}?charset=utf8mb4"\
    .format(username=USERNAME, password=PASSWORD, host=HOST, port=PORT, databasename=DATABASE_NAME)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class TelephoneConverter(BaseConverter):
    regex = '1[3857]\d{9}'  # 右下斜杠d


class ListConverter(BaseConverter):
    regex = '.*'  # 这个regex代表都匹配的意思，可以根据自己的需求制定url规则

    def to_python(self, value):
        '''这个函数用于拿到了路由里的动态参数赋值给value，
          可以在to_python进行操作动态参数，
          返回操作完的的结果给视图函数的形参'''
        return value.split('+')

    def to_url(self, value):
        '''这个函数用于和url_for连用，
           url_for通过指定给动态参数(以关键字实参的形式)赋值给value
           我们可以根据我们的需求操作url_for传进来的参数，
           然后返回一个理想的动态路由内容拼接在url上'''
        return '+'.join(value)


app.url_map.converters['tel'] = TelephoneConverter
app.url_map.converters['list'] = ListConverter


@app.route('/info/')
def info():
    return render_template('info.html')


@app.route('/book_list/')
def book():
    return 'flask_book'


@app.route('/demo2/')
def demo2():
    student_url = url_for('student', id=5, name='mark')  # id就是动态path的key必须赋值，#name将作为查询字符串传入
    print(student_url)

    return student_url


@app.route('/demo3/')
def demo3():
    school_url = url_for('school', school_level='high', name='college')
    # 具体要拼接的查询参数 以关键字实参的形式写在url_for里
    print(school_url)

    return school_url


@app.route('/school/')
def school():
    return 'school message'


@app.route('/student/<tel:telenum>/')
def student_detail(telenum):
    return '学生的手机号码是{}'.format(telenum)


@app.route('/student_list/<list:students>/')
def student_list(students):
    print(url_for('student_list', students=['a', 'b']))  # 输出 /student_list/a+b/

    return '{}'.format(students)


@app.route('/login_inner/', methods=['POST', 'GET'])
def login_inner():
    if request.method == 'GET':  # 判断本次请求是否为get请求
        return render_template('login.html')
    if request.form.get('username') == 'lxy' and request.form.get('password') == '123':
        return 'success'
    return 'error'


def login_verify(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_name = request.args.get('user')
        password = request.args.get('password')
        if user_name == 'lxy' and password == '123':
            return func(*args, **kwargs)
        else:
            return '请登录'

    return wrapper


class CBVTest(views.MethodView):
    methods = ['GET', 'POST']  # 指定可以接收的方法有什么
    decorators = [login_verify, ]  # 指定自定义的装饰器

    def get(self):
        print(url_for('cbvtest'))
        return 'cbv_get'

    def post(self):
        return 'cbv_post'


app.add_url_rule('/cbvtest/', view_func=CBVTest.as_view(name='cbvtest'), endpoint='end_demo')


@app.route('/my_info/')
@login_verify
def my_info():
    return '个人信息页面'


@app.route('/user_info/')
def user_info():
    name = request.args.get('name')
    pwd = request.args.get('pwd')
    if name == 'lxy' and pwd == '123':
        return '{}的信息'.format(name)
    return redirect('/login/', code=301)  # 可以换成 return redirect(url_for('login'))


@app.route('/hello_world/')
def hello_world():
    return render_template('base.html')


@app.route('/demo/')
def demo():
    return render_template('detail.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login/')
def login():
    if request.args.get('name') == 'rocky':
        return 'ok'
    flash('用户名错误', category="username_error")
    flash('用户密码错误', "password_error")
    return 'error,设置了闪现'


@app.route('/get_flash/')
def get_flash():
    return '闪现的信息是{}'.format(get_flashed_messages(category_filter=['username_error']))


class UserInfo(db.Model):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)


class School(db.Model):
    __tablename__ = "school"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, comment="ID")
    name = db.Column(db.String(30), nullable=False, server_default='', comment="学校名称")
    area = db.Column(db.String(30), nullable=False, server_default='', comment="所属地区")
    score = db.Column(db.Integer, nullable=False, server_default='600', comment="录取分数线")

    def __repr__(self):
        return "<School(name:{})>".format(self.name)


if __name__ == '__main__':
    school_01 = School(name="北京大学", area="北京", score=658)  # 实例化模型类作为一条记录
    school_02 = School(name="清华大学", area="北京", score=667)
    school_03 = School(name="中山大学", area="广东", score=645)
    school_04 = School(name="复旦大学", area="上海", score=650)

    with app.app_context():
        db.create_all()  # 创建表

        # db.session.add(school_01)  # 把新创建的记录添加到数据库会话
        # db.session.add(school_02)
        # db.session.add(school_03)
        # db.session.add(school_04)
        #
        # db.session.commit()  # 提交数据库会话

        all_school = School.query.first()
        print(all_school)

        beijing_all = School.query.filter(School.area == "北京").all()
        beijing_first = School.query.filter(School.area == "北京").first()
        print(beijing_all)
        print(beijing_first)

        fudan_school = School.query.filter(School.name == '复旦大学').first()
        print(fudan_school)

        fudan_school = db.session.query(School).filter(School.name == '复旦大学').first()
        print(fudan_school)

        beida = School.query.filter(School.name == '北京大学').first()
        beida.score = 630
        db.session.commit()

        qinghua = School.query.filter(School.name == '清华大学').first()
        db.session.delete(qinghua)
        db.session.commit()

    app.run(debug=True)

