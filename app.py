from flask import Flask, render_template, redirect, url_for, request, session, jsonify, send_from_directory
from bson.json_util import dumps,loads
from bson.objectid import ObjectId
from models.collection import User, Post, Admin, Comments, Albums
from models.helper import get_deactivate_userid_list, check_deactivate_post
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
    user_isdeactivated = check_deactivate_post(id)
    post_info = Post.find_one({"_id": ObjectId(id)})
    usr_id = str(post_info['author']['id'])

    if user_isdeactivated and 'admin_ids' not in session:
        if 'loggedin' in session :
            if usr_id != session['ids']:
                return 'post not found'
        else:
            return 'post not found'

        # if 'loggedin' in session:
        #     if usr_id == session['ids']:
        #         like_data = post_info['like']
        #         like = len(like_data)
        #         return render_template('detail.html',post_info = post_info, usr_id = usr_id, like = like)

        # print 'post not found'

    # print(post_info)
    # print(type(session['ids']))
    # print(usr_id)
    like_data = post_info['like']
    like = len(like_data)

    return render_template('detail.html',post_info = post_info, usr_id = usr_id, like = like)

@app.route('/user/<id>')
def user(id):
    print(id)
    post_list = []
    user_info = User.find_one({"_id": ObjectId(id)})
    # check if user is deactiate
    if user_info['isActive'] == False:
        if 'loggedin' in session:
            if session['ids'] == str(user_info['_id']):
                return render_template('user_deactivate.html',deactivate_status = 'user_valid')

        return render_template('user_deactivate.html',deactivate_status = 'guest')


    user_post = Post.find({"author.id": ObjectId(id)})
    print(user_info)
    for post in user_post:
        # print(post)
        post_list.append(post)
    post_number = len(post_list)
    post_list.reverse()
    return render_template('user.html',user_ids = str(user_info['_id']), user_info = user_info, user_post=post_list, post_number = post_number)

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

@app.route('/download/<path:filename>')
def download(filename):
    # print(filename)
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename= filename, as_attachment=True)

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
                session['isActive'] = valid_user['isActive']

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
    # del session['isActive']
    del session['id']
    del session['ids']
    return redirect('/')

@app.route('/update_user_status')
def update_user_status():
    if 'loggedin' in session:
        user_info = User.find_one(
            {'_id': ObjectId(session['ids'])},
            {'isActive': 1}
        )
        # print( not user_info['isActive'])

        # check khop user or admin moi cho update

        User.update_one(
            {'_id': ObjectId(session['ids'])},
            {'$set': {'isActive': not user_info['isActive']}}
        )

        return jsonify({
            'status': 'success',
            'message': 'update successfull ' + session['ids']
        })

    else:     
        return jsonify({
            "message": "No user found",
        })

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
            User.insert_one({'username':username,'password':password,'email':email, 'role':'user', 'isActive': True})
            return redirect('/login')

@app.route('/postdata/<type>')
def postdata(type):
    # get all deactivate user
    deactivate_users_list = get_deactivate_userid_list()
    # print(deactivate_users_list)

    # print(type)
    post_list = []
    if type == "All resources":
        post_list = list(Post.find({'author.id': {'$nin': deactivate_users_list}}))
        # print(post_list)
    elif type == "Photos":
        post_list = Post.find({"type":"photo", 'author.id': {'$nin': deactivate_users_list}})
    elif type == "Vectors":
        post_list = Post.find({"type":"vector", 'author.id': {'$nin': deactivate_users_list}})
    elif type == "PSD":
        post_list = Post.find({"type":"psd", 'author.id': {'$nin': deactivate_users_list}})
    return dumps({
        "message": "success",
        "post_list": post_list
    })

@app.route('/post_like/<post_id>/<viewer_name>')
def post_like(post_id, viewer_name):
    post_data = Post.find_one({'_id': ObjectId(post_id)})
    # print(post_data['like'])
    like_list = post_data['like']
    like_list.append(viewer_name)

    Post.update_one(
        {'_id': ObjectId(post_id)},
        {'$set':{'like': like_list}}
    )
    # return redirect(url_for('detail', id = post_id))
    return redirect('/detail/'+post_id)

@app.route('/post_dislike/<post_id>/<viewer_name>')
def post_dislike(post_id, viewer_name):
    post_data = Post.find_one({'_id': ObjectId(post_id)})
    # print(post_data['like'])
    like_list = post_data['like']
    like_list.remove(viewer_name)

    Post.update_one(
        {'_id': ObjectId(post_id)},
        {'$set':{'like': like_list}}
    )
    return redirect('/detail/'+post_id)

@app.route('/post_delete/<id>')
def post_delete(id):
    if 'loggedin' in session:
        post_data = Post.find_one({'_id': ObjectId(id)})
        author_id = str(post_data['author']['id'])
        # print(author_id)
        if author_id == session['ids']:
            try:
                Post.delete_one({'_id': ObjectId(id)})
                print('post delete')

                return redirect('/')
            except:
                return jsonify({
                    'message': 'post delete fail'
                })
        else:
            return ('', 204)
    else:
        return redirect('/login')

@app.route('/post_allow/<id>')
def post_allow(id):
    Post.update_one(
        {'_id': ObjectId(id)}, 
        {'$set': {'check': True}}
    )
    return redirect('/admin_page/checked')

@app.route('/post_ban/<id>')
def post_ban(id):
    Post.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'check': False}}
    )
    return redirect('/admin_page/waiting')

@app.route('/post_message',methods=['GET', 'POST'])
def post_message():
    if request.method == 'POST':
        newComment = Comments.insert_one({
            'author': session['ids'],
            'content': request.json['message']
        })
        # find post
        Post.find_one_and_update(
            {'_id': ObjectId(request.json['postId'])},
            {'$push': {'comments': str(newComment.inserted_id)}}
        )

        # Post.update(
        #     {},
        #     {'$unset': {'comments': 1}},
        #     False, True
        # )

    return jsonify({
        'status': 'sucssess',
        'comment': {
            'userid': session['ids'],
            'content': request.json['message'],
            'username': session['username'],
        }
    })

@app.route('/get_all_messages/<postId>')
def get_all_messages(postId):

    all_comments = []
    all_post_comment = Post.find_one({'_id': ObjectId(postId)}, {'comments': 1})
    print(all_post_comment)
    all_post_comment_id = all_post_comment['comments'][-5:]
    all_post_comment_id.reverse()
    print(all_post_comment_id)

    for comment_id in all_post_comment_id:
        comment = Comments.find_one({'_id': ObjectId(comment_id)})
        author = User.find_one({'_id':  ObjectId(comment['author'])})
        comment_checked = {
            'username': author['username'],
            'userid': comment['author'],
            'content': comment['content']
        }

        all_comments.append(comment_checked)
        # comment['username'] = author['username']
        # all_comments.append(comment)

    # print(all_comments)
    return jsonify({
        'status': 'success',
        'message': 'get all message successfull',
        'all_comments': dumps(all_comments)
    })

@app.route('/get_lazy_messages/<postId>', methods = ['GET', 'POST'])
def get_messages_lazy(postId):
    if request.method == 'POST':

        all_comments = []
        start_message_index = request.json['lazyIndex']    
            
        all_post_comment = Post.find_one({'_id': ObjectId(postId)}, {'comments': 1})
        reversed_post_comment_list = all_post_comment['comments'][::-1] #reverse array
        all_post_comment_id = reversed_post_comment_list[start_message_index : start_message_index + 5]
        print(all_post_comment_id)

        for comment_id in all_post_comment_id:
            comment = Comments.find_one({'_id': ObjectId(comment_id)})
            author = User.find_one({'_id':  ObjectId(comment['author'])})
            comment_checked = {
                'username': author['username'],
                'userid': comment['author'],
                'content': comment['content']
            }

            all_comments.append(comment_checked)
            # comment['username'] = author['username']
            # all_comments.append(comment)

        return jsonify({
            'status': 'success',
            'message': 'get all message successfull',
            'all_comments': dumps(all_comments)
        })
    else:
        return 'invalid method'

@app.route('/album/<userId>')
def album(userId):
    return render_template('album.html', user_ids = userId)

@app.route('/albums/<userId>')
def albums(userId):
    user_id = userId
    all_album = Albums.find({'userId._id': user_id })

    return jsonify({
        'status': 'success',
        'message': 'get all admin successful',
        'all_admin': dumps(all_album)
    })

@app.route('/album_create',methods=['GET', 'POST'])
def album_create():

    if 'loggedin' in session:
        if request.method == "POST":
            album_name = request.json['title']

            new_album = {
                'title': album_name,
                'thumbnail': '../static/image/no-resources.svg',
                'userId': {
                    '_id': session['ids'],
                    'username': session['username']
                },
                'postId': [],
            }

            created_album = Albums.insert_one(new_album)

            return jsonify({
                'status': 'success',
                'message': 'create album successful',
                'newAlbumID': dumps(created_album.inserted_id),
                'albumDetail': dumps(new_album) 
            })
        else:
            return 'Wrong request!'
    else:
        return 'you are not logged in'

@app.route('/album_delete',methods=['GET','POST'])
def album_delete():
    if 'loggedin' in session:
        if request.method == "POST":
            albumId = request.json['albumId']

            Albums.remove({
                '_id': ObjectId(albumId),
            })

            return jsonify({
                'status': 'success',
                'message': 'delete album successful',
            })
        else:
            return 'Wrong request!'
    else:
        return 'you are not logged in'
    

@app.route('/album_update',methods=['GET','POST'])
def album_update():
    if 'loggedin' in session:
        if request.method == "POST":
            album_name = request.json['title']
            album_id = request.json['albumId']

            Albums.update_one(
                {'_id': ObjectId(album_id)},
                {'$set':{'title': album_name}}
            )

            return jsonify({
                'status': 'success',
                'message': 'create album successful',
                'updatedId': album_id
            })
        else:
            return 'Wrong request!'
    else:
        return 'you are not logged in'


@app.route('/album_detail/<albumId>/<userId>')
def album_detail(albumId, userId):
    # album_data = Albums.find_one({'_id': ObjectId(albumId)})
    # print(album_data)

    return render_template('album_detail.html', user_id = userId)

    # return jsonify({
    #     'status': 'success',
    #     'message': 'get album data successful',
    #     'all_comments': dumps(album_data)
    # })

@app.route('/add_album_post',methods=['GET', 'POST'])
def add_album_post():
    if request.method == 'POST':
        album_id = request.json['albumId']
        post_id = request.json['postId']

        print(album_id)
        print(post_id)
        
        Albums.find_one_and_update(
            {'_id': ObjectId(album_id)},
            {'$push': {'postId': ObjectId(post_id)}}
        )

        return jsonify({
            'status': 'success',
            'message': 'add album post successful',
        })
    else:
        return 'wrong request!'

@app.route('/remove_album_post',methods=['GET', 'POST'])
def remove_album_post():
    if request.method == 'POST':
        album_id = request.json['albumId']
        post_id = request.json['postId']

        Albums.find_one_and_update(
            {'_id': ObjectId(album_id)},
            {'$pull': {'postId': ObjectId(post_id)}}
        )
        
        return jsonify({
            'status': 'success',
            'message': 'remove album post successful'
        })
    else:
        return 'wrong request'

@app.route('/get_album_detail/<albumId>')
def get_album_detail(albumId):
    album_info = Albums.find_one({'_id': ObjectId(albumId)}) 
    # print(album_info['postId'])
    post_list = Post.find({'_id': {'$in': album_info['postId']}})

    return jsonify({
        'status': 'success',
        'postList': dumps(post_list),
        'albumName': album_info['title'],
    })

@app.route('/get_album_suggest/<userId>')
def get_album_suggest(userId):
    all_suggest_post = Post.find({'author.id': ObjectId(userId)})

    return jsonify({
        'status': 'success',
        'suggestPost': dumps(all_suggest_post)
    })

@app.route('/admin_login',methods=['GET', 'POST'])
def admin_login():
    if request.method == "GET":
        if 'admin_logged' in session:
            return redirect('/admin_page/waiting')
        else:
            return render_template('admin_login.html')
    elif request.method == "POST":
        username = request.json['username']
        password = request.json['password']
        valid_user = Admin.find_one({'username': username})
        print(valid_user)
        if valid_user:
            if valid_user['password'] == password:
                session['admin_logged'] = True
                session['admin_name'] = username
                session['admin_ids'] = str(valid_user['_id'])
                session['is_admin'] = valid_user['isAdmin']

                print(session['admin_name'])
                print(session['admin_ids'])
                return jsonify({
                    "username": username,
                    "id": session['admin_ids'],
                })
            else:
                return jsonify({
                    "passwarn": 'wrong password',
                })
        else:
            return jsonify({
                "userwarn": 'admin not exist'
            })

@app.route('/admin_logout')
def admin_logout():
    del session['admin_logged'] 
    del session['admin_name']
    del session['admin_ids']
    del session['is_admin']
    return redirect('/admin_login')

@app.route('/admin_create', methods=['GET', 'POST'])
def admin_create():
    if request.method == "POST":
        admin_data = request.json
        # print(admin_data)
        admin_exist = Admin.find_one({'username': admin_data['username']})

        if admin_exist:
            
            return jsonify({
                'message': 'create admin fail, user existed',
                'status': 'fail'
            })
        else:
            new_admin = Admin.insert_one(admin_data)

            return jsonify({
                'message': 'create admin successful',
                'status': 'success',
                'adminId': dumps(new_admin.inserted_id)
            })
    else:
        return 'wrong request'

@app.route('/admin_update/<adminId>', methods=['GET', 'POST'])
def admin_update(adminId):
    if request.method == "POST":
        update_data = request.json
        print(update_data)
        if 'isAdmin' in update_data:
            return 'invalid updated'
        else:
            admin_updated = Admin.update_one(
                {'_id': ObjectId(adminId)},
                {'$set': {'password': update_data['password']}}
            )
            print(admin_updated)

        return jsonify({
            'message': 'update admin successful'
        })

    else:
        return 'wrong request'

@app.route('/update_admin_status/<adminId>', methods=['GET', 'POST'])
def update_admin_status(adminId):
    if request.method == "POST":
        if 'admin_ids' in session:
            admin_info = Admin.find_one({'_id': ObjectId(adminId)}, {'isActive': 1}) 
            print(admin_info['isActive'])
            Admin.update_one(
                {'_id': ObjectId(adminId)},
                {'$set': {'isActive': not admin_info['isActive']}}
            )

            return jsonify({
                'message': 'update admin status successful'
            })
            
        else:
            return 'request not allowed'
    else:
        return 'wrong request'
    
    

@app.route('/get_all_admin')
def get_all_admin():
    all_admin = list(Admin.find())
    print(all_admin)

    return jsonify({
        'message': 'get all admin successful',
        'allAdmin': dumps(all_admin)
    })


@app.route('/admin_page/<page>')
def admin_page(page):
    if 'admin_logged' in session:
        post_list = []
        posts = Post.find()
        # print(posts)
        for post in posts:
            post_list.append(post)
        post_list.reverse()
        print(post_list)

        if page == 'waiting':
            return render_template('admin_waiting_post.html', posts = post_list)
        elif page == 'checked':
            return render_template('admin_checked_post.html', posts = post_list)
        elif page == 'admin_manager':
            if session['is_admin'] == True:
                return render_template('admin_admin_manager.html')
            else:
                return 'You are not allowed'
        else:
            return 'page not found 404!' 
    else:
        return redirect('/admin_login')

    
if __name__ == '__main__':
  app.run(debug=False)
