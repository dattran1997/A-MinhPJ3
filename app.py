from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from bson.json_util import dumps,loads
from bson.objectid import ObjectId
from models.collection import User, Post
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)

app.secret_key ='this is secret!'

UPLOAD_FOLDER = "static/image"
ALLOWED_EXTENSIONS = set(['txt','jpg','png','jpeg','gif','pdf'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    check_1 = '.' in filename
    check_2 = filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    if check_1 and check_2:
        return True
    else:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detail/<id>')
def detail(id):
    # print(id)
    post_info = Post.find_one({"_id": ObjectId(id)})
    # print(post_info)
    return render_template('detail.html',post_info = post_info)

@app.route('/user/<id>')
def user(id):
    print(id)
    post_list = []
    user_info = User.find_one({"_id": ObjectId(id)})
    user_post = Post.find({"author.id": ObjectId(id)})
    # print(user_info)
    for post in user_post:
        # print(post)
        post_list.append(post)
    post_number = len(post_list)
    post_list.reverse()
    return render_template('user.html', user_info = user_info, user_post=post_list, post_number = post_number)

@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == "GET":
        if 'loggedin' in session:
            return render_template('upload.html')
        else:
            return redirect('/login')
    elif request.method == "POST":
        form = request.form
        title = form['title']
        type = form['type']
        link = form['link']
        file = request.files['file']
        file_name = file.filename
        user_info = User.find_one(loads(session['id']))

        user_data ={
            "id": user_info['_id'],
            "username": user_info['username'],
            "email": user_info['email']
        }

        print(user_data)
        if file and allowed_file(file_name):
            file_name = secure_filename(file_name)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
        Post.insert_one({'title': title, 'type': type, 'link': link, 'thumbnail': file_name, 'like': [], 'check':False, "author": user_data})
        return redirect("/")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "GET":
        if 'loggedin' in session:
            return redirect('/')
        else:
            return render_template('login.html')
    elif request.method == "POST":
        username = request.json['username']
        password = request.json['password']
        valid_user = User.find_one({'username': username})
        print(valid_user)
        if valid_user:
            if valid_user['password'] == password:
                session['loggedin'] = True
                session['username'] = username
                session['id'] = dumps(valid_user['_id'])
                session['ids'] = str(valid_user['_id'])

                print(session['id'])
                print(session['ids'])
                return jsonify({
                    "username": username,
                    "id": session['id'],
                })
            else:
                return jsonify({
                    "passwarn": 'wrong password',
                })
        else:
            return jsonify({
                "userwarn": 'user not exist'
            })

@app.route('/logout')
def logout():
    del session['loggedin']
    del session['username']
    del session['id']
    del session['ids']
    return redirect('/')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == "GET":
        return render_template('register.html',name_warn = "")
    elif request.method == "POST":
        form = request.form
        username = form['username']
        password = form['password']
        email = form['email']
        user_exist = User.find_one({'username':username})
        if user_exist:
            return render_template('register.html',name_warn = 'user exitst')
        else:
            User.insert_one({'username':username,'password':password,'email':email, 'role':'user'})
            return redirect('/login')

@app.route('/postdata/<type>')
def postdata(type):
    print(type)
    post_list = []
    if type == "All resources":
        post_list = Post.find()
    elif type == "Photos":
        post_list = Post.find({"type":"photo"})
    elif type == "Vectors":
        post_list = Post.find({"type":"vector"})
    elif type == "PSD":
        post_list = Post.find({"type":"psd"})
    return dumps({
        "message": "success",
        "post_list": post_list
    })

if __name__ == '__main__':
  app.run(debug=True)
