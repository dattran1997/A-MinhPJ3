from models.collection import User, Post
from bson.objectid import ObjectId
from bson.json_util import dumps,loads
import sys

### common task

def get_deactivate_userid_list():
    deactivate_users_list = []
    try:
        deactivate_users = list(User.find({'isActive': False}, {'_id': 1}))
        for user in deactivate_users:
            deactivate_users_list.append(user['_id'])
    except:
        print('error:', sys.exc_info()[0])
    finally:
        return deactivate_users_list


def check_deactivate_post(id):
    deactivate_users_list = get_deactivate_userid_list()

    try:
        deactivate_post = Post.find_one({'_id': ObjectId(id), 'author.id': {'$in': deactivate_users_list}})
        print(deactivate_post)
        if deactivate_post :
            return True
        else:
            return False
    except:
        print('error:', sys.exc_info()[0])
    
    
    






### populate

def update_user_isactive_field():
    try:
        User.update_many(
            {},
            {"$set": {"isActive": True}}
        )
        print('update user status success')
    except ValueError:
        print(ValueError)
 # update_user_isactive_field()