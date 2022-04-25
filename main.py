from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar
from functools import wraps

#Basic setup
app = Flask(__name__)
app.secret_key = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLES
#User Table(In the relationship table, this is parent for BlogPost, Comment)
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), unique=True, nullable=False)
    #之後要拿、修改BlogPost的資料要透過這個
    posts = relationship("BlogPost", back_populates="author")
    #之後要拿、修改Comment的資料要透過這個
    comments = relationship("Comment", back_populates="commentor")
# db.create_all()

#POST Table(In the relationship, this is child for User, parent for Comment)
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    #查詢的時候要透過author_id這欄獲得的值來連接user的id，他是User的child
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    #之後要拿、修改User的資料要透過這個
    author = relationship("User", back_populates="posts")
    #之後要拿、修改Comment的資料要透過這個
    comments = relationship("Comment", back_populates="post")
# db.create_all()

#Comment Table
class Comment(UserMixin,db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    #查詢的時候要透過commentor_id這欄獲得的值來連接user的id，他是User的child
    commentor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    #查詢的時候要透過post_id這欄獲得的值來連接post的id，他是BlogPost的child
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    #之後要拿、修改User, BlogPost的資料要透過這個
    commentor = relationship("User", back_populates="comments")
    post = relationship("BlogPost", back_populates="comments")

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, current_user=current_user)

@app.route('/register', methods=["GET","POST"])
def register():
    registed_form = RegisterForm()
    if registed_form.validate_on_submit():
        registed_name = registed_form.name.data
        registed_password = registed_form.password.data
        registed_email  = registed_form.email.data
        checking_for_email = User.query.filter_by(email=registed_email).first()
        if checking_for_email == None:
            converted_password = generate_password_hash(registed_password,method="pbkdf2:sha256", salt_length=8)
            new_user = User(name=registed_name, password=converted_password, email=registed_email)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("get_all_posts"))
        else:
            flash("You have already signed with that email, login instead!")
            return redirect(url_for("login"))
    return render_template("register.html", form = registed_form)

@app.route('/login', methods=["GET","POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        login_email = login_form.email.data
        login_password = login_form.password.data
        user = User.query.filter_by(email=login_email).first()
        if user == None:
            flash("The email does not exist, please try again.")
            return render_template("login.html", form = login_form)
        else:
            correct_password = user.password
            if check_password_hash(correct_password, login_password):
                login_user(user)
                return redirect(url_for("get_all_posts"))
            else:
                flash("Wrong password, please try again")
                return render_template("login.html", form=login_form)
    return render_template("login.html", form = login_form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

@app.route("/post/<int:post_id>", methods=["GET","POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    #可以直接把current_user傳進來，沒有登入則為空值
    comment_form = CommentForm()
    all_comments = db.session.query(Comment).all()
    gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment")
            return redirect(url_for("login"))
        else:
            comment_text = comment_form.comment.data
            new_comment = Comment(text=comment_text, commentor_id=current_user.id, post_id=post_id)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("show_post", post_id=post_id))
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form, comment_list=all_comments, gravatar=gravatar)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

#Make a decorator to wrap certain functions
def admin_only(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            #觸發錯誤403
            return abort(403)
        else:
            #確認user是admin, id=1的話就照常執行傳入的function
            return function(*args, **kwargs)
    return decorated_function

@app.route("/new-post", methods=["GET","POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y"),
            author_id = current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)

@app.route("/edit-post/<int:post_id>", methods=["GET","POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))


    return render_template("make-post.html", form=edit_form)

@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

if __name__ == "__main__":
    app.run(debug=True)
