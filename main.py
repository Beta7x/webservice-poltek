# In this semester you have to use JSON format in every request body.
from flask import Flask
from flask_restx import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

user_params = reqparse.RequestParser()
user_params.add_argument('name', type=str, help='Your username', location='json', required=True)
user_params.add_argument('email', type=str, help='Your Email Address', location='json', required=True)
user_params.add_argument('educations', type=list, help='Education History', location='json', action='append', required=True)

@api.route('/hello')
class User(Resource):
    def get(self):
        return {'message':'Hello world!'}
    
    @api.expect(user_params)
    def post(self):
        args = user_params.parse_args()
        name = args['name']
        email = args['email']
        educations = args['educations']
        educations = educations[0]
        
        return {
            'name': name,
            'email': email,
            'educations': educations,
        }, 201
    
    def put(self):
        return {'message':'Hello wordl using PUT method'}, 200
    
    def delete(self):
        return {'message':'Hello wordl using DELETE method'}, 200

if __name__ == '__main__':
    app.run(ssl_context='adhoc', debug=True)
