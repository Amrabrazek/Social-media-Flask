from flask import render_template, redirect, url_for, flash, request, Blueprint, send_from_directory
from mainpro import  app, bcrypt, db
from mainpro.models import User, Post, Friendship
from mainpro.forms import PostForm, RegistrationForm, LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os

from datetime import date


@app.route('/register', methods=['GET','POST'])
def register():
    endpoint_title = "Register Page"
    form = RegistrationForm()
    if form.validate_on_submit():
        with app.app_context():
            profile_image=form.profile_image.data
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(
                first_name=form.first_name.data,
                middle_name=form.middle_name.data,
                last_name=form.last_name.data,
                birth_date=form.birth_date.data,

                profile_image_data = profile_image.read(),
                profile_image_filename = profile_image.filename,

                username=form.username.data,
                email=form.email.data,
                password=hashed_pw
            )
            db.session.add(new_user)
            db.session.commit()

        file = form.profile_image.data # First grab the file
        filename = secure_filename(file.filename)
        file.seek(0)
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],filename)) # Then save the file
            # Save the uploaded image
        # return redirect(url_for('home'))
        return redirect(url_for('login'))
    # else:
            # return "dsa"
    #     flash("Registration Unsuccessful","danger")
    return render_template('register.html', data={'title':endpoint_title,'form':form})


@app.route('/login', methods=['GET','POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    endpoint_title = "Login Page"
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(url_for(next_page))
            else:
                return redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Please check email and password.", "danger")
    return render_template('login.html', data={'title': endpoint_title, 'form': form})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


Navbar = ['home', 'profile', "friends" , 'logout']

# delete post
@app.route('/home/<post_id>', methods=['GET','POST'])
@login_required
def delete_Post(post_id):

    with app.app_context():

        post_to_delete = Post.query.filter(Post.id == post_id).first()
        print("===========================================")
        print(post_to_delete)
        db.session.delete(post_to_delete)
        db.session.commit()

    flash("Post deleted", "success")
    return redirect(url_for('home'))
    

# home page & add post & edit post
@app.route('/home', methods = ['GET', 'POST'])
@app.route('/', methods = ['GET', 'POST'])
@app.route('/edit/<post_id>', methods = ['GET', 'POST'])
@login_required
def home(post_id = ""):

    print("home")
    # edit post
    post_to_edit = ''
    if post_id :
        print("true")
        post_to_edit = Post.query.filter(Post.id == post_id).first()

        form = PostForm(obj=post_to_edit)
        
        if form.validate_on_submit():
            with app.app_context():
                form.populate_obj(post_to_edit)
                post_to_edit = Post.query.filter(Post.id == post_id).first()
                post_image = form.post_image.data

                post_to_edit.title = form.title.data
                post_to_edit.content = form.content.data
                post_to_edit.status = form.status.data
                post_to_edit.post_image_filename = post_image.filename
                db.session.commit()

            file = form.post_image.data # First grab the file
            filename = secure_filename(file.filename)
            file.seek(0)
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],filename)) # Then save the file

                
            flash("Post updated Successful", "success")
            return redirect(url_for('home'))


    # add post
    form = PostForm()
    if form.validate_on_submit():
        print("valid")
        with app.app_context():

            if form.post_image.data :
                post_imagex = form.post_image.data
                post_image_data = post_imagex.read()
                post_image_filename = post_imagex.filename
            else: 
                post_image_data = b''
                post_image_filename =""

            # profile_image_data = post_image.read()
            # print("----------------------------------------------------")
            # print (post_imagex)
            # print (post_imagex)

            new_post = Post(title=form.title.data,
                            content=form.content.data,
                            status=form.status.data,
                            user_id=current_user.id,
                            post_image_data = post_image_data,
                            post_image_filename = post_image_filename,
                            )
            db.session.add(new_post)
            db.session.commit()
        
        if form.post_image.data :
            file = form.post_image.data # First grab the file
            filename = secure_filename(file.filename)
            file.seek(0)
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],filename)) # Then save the file

        flash("Post added Successful", "success")
        return redirect(url_for('home'))
    

    friend_posts = []
    friendships = Friendship.query.filter((Friendship.user_id == current_user.id)).all()
    for friendship in friendships:
        # friend_id = friendship.friend_id if friendship.user_id == user_id else friendship.user_id
        friend_posts += User.query.get(friendship.friend_id).posts

    # print('00000000000000000000000000000000000')

    friends_posts  = list(filter(lambda post : post.status == 'Friends_only' , friend_posts ))
    
    posts_id = []

    for post in friends_posts:
        posts_id.append(post.id)

    # print(posts_id)
    # print(friends_posts)
    # for post in friend_posts:
    #     print(post.status)
    # print(friend_posts)

    posts_onlyme = db.session.query(
            Post,
            User
        )\
        .join( User, Post.user_id == User.id)\
        .filter(Post.user_id == current_user.id)\
        .order_by(Post.date.desc())\
        .all()
    
    # print('--------------------------------')
    # print(posts_onlyme)
    # posts_friends = db.session.query(
    #     Post,

    friendsandI_posts = db.session.query(
            Post,
            User
        )\
        .join( User, Post.user_id == User.id)\
        .filter(Post.id.in_(posts_id))\
        .order_by(Post.date.desc())\
        .all()
    
    # print('--------------------------------')
    # for post in friendsandI_posts:
    #     print(post.Post.id)
    # print(friendsandI_posts[2].user_id)

    posts_public = db.session.query(
            Post,
            User
        )\
        .join( User, Post.user_id == User.id)\
        .filter((Post.status == "Public") | (Post.user_id == current_user.id) | (Post.id.in_(posts_id)))\
        .order_by(Post.date.desc())\
        .all()

    endpoint_title = 'home'
    return render_template('home.html', data={ 'title':endpoint_title, 'Navbar':Navbar, 'form': form, "user": current_user,  "posts_onlyme": posts_onlyme, "posts_public":posts_public, "friends_only_posts":friendsandI_posts, "friends_only_posts_ids":posts_id, 'post_to_edit':post_to_edit })

    

# about page
@app.route('/about')
@login_required
def about():
    endpoint_title = 'about'
    return render_template('about.html', data={ 'title':endpoint_title, 'Navbar':Navbar})



@app.route('/profile')
@login_required
def profile():
        # image = current_user.image.decode('utf-8')
        # print(current_user.image)
        today = date.today()
        born = current_user.birth_date
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        endpoint_title = 'profile'
        
        return render_template('profile.html', data={ 'title':endpoint_title, 'Navbar':Navbar, 'user':current_user, 'age': age  })
