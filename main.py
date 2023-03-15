# In this semester you have to use JSON format in every request body.
from flask import Flask
from flask_restx import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt

app = Flask(__name__)
api = Api(app)

"""
Begin Database
"""
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:toor@localhost:3306/flask_webservice"
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Users(db.Model):
    id      = db.Column(db.Integer(), primary_key = True)
    email   = db.Column(db.String(32), unique=True, nullable=False)
    name    = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(32), nullable=False)
"""
End Database
"""

user_params = reqparse.RequestParser()
user_params.add_argument('name', type=str, help='Your username', location='json', required=True)
user_params.add_argument('email', type=str, help='Your Email Address', location='json', required=True)
user_params.add_argument('educations', type=list, help='Education History', location='json', action='append', required=True)

registration_params = reqparse.RequestParser()
registration_params.add_argument('name', type=str, help='Your name', location='json', required=True)
registration_params.add_argument('email', type=str, help='Your Email address', location='json', required=True)
registration_params.add_argument('password', type=str, help='Your Password', location='json', required=True)
registration_params.add_argument('re_password', type=str, help='Retype Password', location='json', required=True)

auth_params = reqparse.RequestParser()
auth_params.add_argument('email', type=str, help='Your Email address', location='json', required=True)
auth_params.add_argument('password', type=str, help='Your Password', location='json', required=True)

AUDIENCE_MOBILE = "myMobileApp"
ISSUER = "myFlaskWebService"
SECRET_KEY = "d2lkaWVzCg=="

# Registration Service
@api.route('/signup')
class Registration(Resource):
    @api.expect(registration_params)
    def post(self):
        args = registration_params.parse_args()
        email = args['email']
        name = args['name']
        password = args['password']
        re_password = args['re_password']
        
        if password != re_password:
            return {
                "message": "Password insn't same!"
            }, 400
        
        user = db.session.execute(db.select(Users).filter_by(email=email)).first()
        if user:
            return {
                "message": "This email has been used!"
            }, 409
            
        user = Users()
        user.email = email
        user.name = name
        user.password = generate_password_hash(password)
        
        db.session.add(user)
        db.session.commit()
        
        return {
            "message": "User successfully created!"
        }, 201

@api.route('/signin')
class Login(Resource):
    @api.expect(auth_params)
    def post(self):
        args = auth_params.parse_args()
        email = args['email']
        password = args['password']
        
        if not email or not password:
            return {
                "message": "Please type email and password"
            }, 400
        
        user = db.session.execute(db.select(Users).filter_by(email=email)).first()
        if not user:
            return {
                "message": "Wrong email or password!"
            }, 400
        else:
            user = user[0]
            
        if check_password_hash(user.password, password):
            payload = {
                "user_id": user.id,
                "email": user.email,
                "aud": AUDIENCE_MOBILE,
                "iss": ISSUER,
                "iat": datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=2)
            }
            token = jwt.encode(payload, SECRET_KEY)
            return token
        else:
            return {
                "message": "Wrong email or password"
            }
        
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
