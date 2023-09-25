from flask import request, session, jsonify, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        new_user = User(
            username = data.get('username'),
            bio = data.get('bio'),
            image_url = data.get('image_url'),
        )
        
        new_user.password_hash = data.get('password')
        
        db.session.add(new_user)
        
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return make_response({"message": "422 (Unprocessable Entity)"}, 422)
        
        session['user_id'] = new_user.id
        user_dict = new_user.to_dict()

        return make_response(jsonify(user_dict), 201)


class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return make_response(jsonify(user.to_dict()), 200)
        else:
            return make_response({"message": "401 (Unauthorized)"}, 401)

class Login(Resource):
    def post(self):
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter(User.username == username).first()
        
        if user:
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 200
        else:
            return make_response({"message": "401 (Unauthorized)"}, 401)

class Logout(Resource):
    def delete(self):
        if session['user_id'] == None:
            return make_response({"message": "401 (Unauthorized)"}, 401)
        else:
            session['user_id'] = None
            return make_response({"message": "204 (No Content)"}, 204)

class RecipeIndex(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()    
        if user:
            recipes = []
            for recipe in user.recipes:
                recipes.append(recipe.to_dict())
            return recipes, 200
        else:
            return make_response({"message": "401 (Unauthorized)"}, 401)
    
    def post(self):
        data = request.get_json()
        user = User.query.filter(User.id == session.get('user_id')).first()

        if user:
            recipe = Recipe(
                title = data['title'],
                instructions =data['instructions'],
                minutes_to_complete = data['minutes_to_complete'],
                user = user
            )
            
            db.session.add(recipe)
            
            try:
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                return make_response({"message": "422 (Unprocessable Entity)"}, 422)
            
            return make_response(jsonify(recipe.to_dict()), 201)
        else:
            return make_response({"message": "401 (Unauthorized)"}, 401)

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)