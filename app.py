import os

from flask import Flask, flash, url_for, request, render_template, views, redirect, get_flashed_messages
from werkzeug.routing import BaseConverter
from functools import wraps


app = Flask(__name__)
app.config.update(TEMPLATES_AUTO_RELOAD=True)
app.secret_key = 'some_secret'


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


if __name__ == '__main__':
    app.run(debug=True)

