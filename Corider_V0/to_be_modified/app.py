from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
api = Api(app)
client = MongoClient('mongodb://localhost:27017/')
db = client['users_db']
collection = db['users']

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('email')
parser.add_argument('password')

def abort_if_user_doesnt_exist(user_id):
    user = collection.find_one({'_id': ObjectId(user_id)})
    if user is None:
        abort(404, message="User {} doesn't exist".format(user_id))

class User(Resource):
    def get(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        user = collection.find_one({'_id': ObjectId(user_id)})
        user['_id'] = str(user['_id'])
        return user

    def post(self):
        args = parser.parse_args()
        user_data = {'name': args['name'], 'email': args['email'], 'password': args['password']}
        result = collection.insert_one(user_data)
        new_user_id = str(result.inserted_id)
        return {'message': 'User {} created'.format(new_user_id)}, 201

    def put(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        args = parser.parse_args()
        update_data = {k:v for k, v in args.items() if v is not None}
        collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        return {'message': 'User {} updated'.format(user_id)}

    def delete(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        collection.delete_one({'_id': ObjectId(user_id)})
        return {'message': 'User {} deleted'.format(user_id)}

class UserList(Resource):
    def get(self):
        users = []
        for user in collection.find():
            user['_id'] = str(user['_id'])
            users.append(user)
        return users

    def post(self):
        args = parser.parse_args()
        user_data = {'name': args['name'], 'email': args['email'], 'password': args['password']}
        result = collection.insert_one(user_data)
        new_user_id = str(result.inserted_id)
        return {'message': 'User {} created'.format(new_user_id)}, 201

api.add_resource(UserList, '/users')
api.add_resource(User, '/users/<user_id>')

if __name__ == '__main__':
    app.run(debug=True)
