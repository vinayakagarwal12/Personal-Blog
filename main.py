from flask import Flask, render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug import secure_filename
from datetime import datetime
import os
import math


app=Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER']="//home//rohit2411//PycharmProjects//flask1//static"
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL='True',
    MAIL_USERNAME='rohitgarg2555',
    MAIL_PASSWORD='abc')
mail=Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://phpmyadmin:'put password here'@localhost/rg'

db = SQLAlchemy(app)

class Contacts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12),nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(12), nullable=False)

class Posts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21),nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/2)
    page=request.args.get('page')
    if (not str(page).isdigit()):
        page=1
    page=int(page)
    posts=posts[(page-1)*2:(page-1)*2+2]
    #logic of pagination
    #First
    if (page==1):
      prev="#"
      next="/?page="+ str(page+1)
    elif(page==last):
      next = "#"
      prev = "/?page=" + str(page - 1)
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)
    return render_template('index.html',posts=posts,prev=prev,next=next)

@app.route("/post/<string:post_slug>",methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',post=post)

@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user'] == "rohit"):
        if request.method=='POST':
            box_title=request.form.get('title')
            tlin = request.form.get('tlin')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date=datetime.now()

            if (sno=='0'):
                post=Posts(title=box_title,slug=slug,content=content,img_file=img_file,date=date,tagline=tlin)
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug = slug
                post.content = content
                post.tagline = tlin
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/'+sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',post=post,sno=sno)

@app.route("/uploader",methods=['GET','POST'])
def uploader():
    if ('user' in session and session['user'] == "rohit"):
      if(request.method=='POST'):
          f=request.files['file1']
          f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
          return "Uploaded Succesfully"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if ('user' in session and session['user'] == "rohit"):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/dashboard",methods=['GET','POST'])
def dashboard():
    if ('user' in session and session['user']=="rohit"):
        posts = Posts.query.all()
        return render_template('dashboard.html',posts=posts)
    if request.method=='POST':
        username=request.form.get('uname')
        userpass=request.form.get('pass')
        if(username=="rohit" and userpass=="rohit"):
            #set the session variable
          session['user']=username
          posts=Posts.query.all()
          return render_template('dashboard.html',posts=posts)
        #redirect to admin panel
    return render_template('login.html')

@app.route("/contact",methods=['GET','POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to databse'''
        name=request.form.get('name')
        email = request.form.get('email')
        phone=request.form.get('phone')
        message= request.form.get('message')
        entry= Contacts(name=name,phone_num=phone,msg=message,date=datetime.now(),email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' +name,
                          sender=email,
                          recipients=["rohitgarg2555@gmail.com"],
                          body=message+"\n"+phone)
    return render_template('contact.html')
app.debug=True
app.run(port=4944)
