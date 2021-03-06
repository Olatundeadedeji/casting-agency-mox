import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movies, Actors
from auth import AuthError, requires_auth, get_token_auth_header


def create_app(test_config=None):
    # create and configure the app.
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # After_request decorator setup for GET, POST, PATCH, DELETE & OPTIONS.
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorisation, true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # Index page endpoint.
    @app.route('/')
    def welcome():
        return 'Home of Casting Agency', 200

 #----------------------------------------------------------------------------#
 # Movies Endpoints.
 #----------------------------------------------------------------------------#
    # Movies endpoint to handle the GET requests.
    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def retrieve_movies(jwt):
        # Query to retrieve all movies.
        movies = Movies.query.order_by(Movies.id).all()

        # Return results on success
        try:
            return jsonify({
                'success': True,
                'movies': [movie.format() for movie in movies]
            }), 200
        except:
            abort(404)

    # Movies endpoint to handle the POST requests.
    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def add_movie(jwt):

        # get response data
        data = request.get_json()
        title = data.get('title', None)
        release_date = data.get('release_date', None)

        # Insert new movie details into database.
        try:
            movie = Movies(title=title, release_date=release_date)
            movie.insert()
            return jsonify({
                'success': True,
                'movie': movie.format()
            }), 201
        except:
            abort(500)

    # Movies endpoint to hand the PATCH requests.
    @app.route('/movies/<id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(jwt, id):

        data = request.get_json()
        title = data.get('title', None)
        release_date = data.get('release_date', None)

        movie = Movies.query.get(id)

        # Return a 404 error if no movie.
        if movie is None:
            abort(404)

        # Return a 400 error if there is no title or release date.
        if title is None or release_date is None:
            abort(400)

        movie.title = title
        movie.release_date = release_date

        # Try to update movie details in the DB.
        try:
            movie.update()
            return jsonify({
                'success': True,
                'movie': [movie.format()]
            }), 200
        except:
            abort(404)

    # Movies endpoint to hand the DELETE requests.
    @app.route('/movies/<int:id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(jwt, id):

        movie = Movies.query.get(id)

        # Return a 404 error if no movie.
        if movie is None:
            abort(404)

        try:
            movie.delete()
            return jsonify({
                'success': True,
                'delete': movie.id
            }), 200
        except:
            abort(404)
#----------------------------------------------------------------------------#
#  Actors endpoints.
#----------------------------------------------------------------------------#
    # Actors endpoint to handle the GET requests.

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def retrieve_actors(jwt):

        # Query to retrieve all actors.
        actors = Actors.query.order_by(Actors.id).all()

        # Return results on success
        try:
            return jsonify({
                'success': True,
                'actors': [actor.format() for actor in actors]
            }), 200
        except:
            abort(404)

    # Actors endpoint to handle the POST requests.
    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def add_actor(jwt):

        # get response data
        data = request.get_json()
        name = data.get('name', None)
        age = data.get('age', None)
        gender = data.get('gender', None)

        # Insert new actor details into database.
        try:
            actor = Actors(name=name, age=age, gender=gender)
            actor.insert()
            return jsonify({
                'success': True,
                'actor': actor.format()
            }), 201
        except:
            abort(500)


    # Actor endpoint to hand the PATCH requests.
    @app.route('/actors/<id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actor(jwt, id):

        data = request.get_json()
        name = data.get('name', None)
        age = data.get('age', None)
        gender = data.get('gender', None)

        actor = Actors.query.get(id)

        # Return a 404 error if no actor.
        if actor is None:
            abort(404)

        # Return a 400 error if there is no name, age or gender.
        if name is None or age is None or gender is None:
            abort(400)

        actor.name = name
        actor.age = age
        actor.gender = gender

        # Try to update actor details in the database.
        try:
            actor.update()
            return jsonify({
                'success': True,
                'actor': [actor.format()]
            }), 200
        except:
            abort(404)

    # Actors endpoint to hand the DELETE requests.
    @app.route('/actors/<int:id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(jwt, id):

        actor = Actors.query.get(id)

        # Return a 404 error if no movie.
        if actor is None:
            abort(404)

        try:
            actor.delete()
            return jsonify({
                'success': True,
                'delete': actor.id
            }), 200
        except:
            abort(404)

    # Error Handling
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error
        }), error.status_code

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
