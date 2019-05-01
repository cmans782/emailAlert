"""flaskblog."""

from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cff7026348d9bbff68576cb2b73fadd1'

posts = [
    {
        'author': 'Taylor Lentz',
        'title': 'blog post 1',
        'content': 'first post content',
        'date_posted': 'April 3, 2019'
    },
    {
        'author': 'Blake Kratz',
        'title': 'blog post 2',
        'content': 'second post content',
        'date_posted': 'April 20, 2020'
    }
]


@app.route("/")
def home():
    return render_template('home.html', posts=posts)

@app.route("/newPackage")
def newPackage():
    return render_template('newPackage.html', title='New_Package')

@app.route("/employee")
def employee():
    return render_template('employee.html', title='Employee')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('Account created for {}!'.format(form.username.data), 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)
