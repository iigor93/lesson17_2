# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from create_data import data, create_data_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)

api = Api(app)
movies_ns = api.namespace('/movies')
directors_ns = api.namespace('/directors')
genres_ns = api.namespace('/genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


create_data_db(data, db, Movie, Director, Genre)


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movies_ns.route('/')
class MoviesAll(Resource):
    def get(self):
        director_id = request.values.get('director_id')
        genre_id = request.values.get('genre_id')
        if director_id is None and genre_id is None:
            all_movies = db.session.query(Movie).all()
        elif director_id is not None and genre_id is None:
            all_movies = db.session.query(Movie).filter(Movie.director_id == director_id)
        elif director_id is None and genre_id is not None:
            all_movies = db.session.query(Movie).filter(Movie.genre_id == genre_id)
        else:
            all_movies = db.session.query(Movie).filter(Movie.director_id == director_id, Movie.genre_id == genre_id)
        return jsonify(movies_schema.dump(all_movies))

    def post(self):
        new_item_reqeust = request.json
        all_items = db.session.query(Movie).all()
        all_items_id = []
        for item_ in all_items:
            all_items_id.append(item_.id)
        if new_item_reqeust.get('id') in all_items_id:
            return f'Item with id {new_item_reqeust.get("id")} already exists'
        new_item = Movie(**new_item_reqeust)
        db.session.add(new_item)
        db.session.commit()
        db.session.close()
        return "", 201


@movies_ns.route('/<int:mid>/')
class Movies(Resource):
    def get(self, mid):
        movie_ = Movie.query.get(mid)
        if movie_:
            director_ = Director.query.filter(Director.id == movie_.director_id).one()
            genre_ = Genre.query.filter(Genre.id == movie_.genre_id).one()
            return jsonify(movie_schema.dump(movie_), director_schema.dump(director_), genre_schema.dump(genre_))
        return "", 404

    def delete(self, mid):
        movie_ = Movie.query.get(mid)
        if movie_:
            db.session.delete(movie_)
            db.session.commit()
            db.session.close()
            return "", 204
        return "", 404

    def put(self, mid):
        item_ = Movie.query.get(mid)
        if item_:
            new_item_reqeust = request.json
            item_.title = new_item_reqeust.get('title')
            item_.description = new_item_reqeust.get('description')
            item_.trailer = new_item_reqeust.get('trailer')
            item_.year = new_item_reqeust.get('year')
            item_.rating = new_item_reqeust.get('rating')
            item_.genre_id = new_item_reqeust.get('genre_id')
            item_.director_id = new_item_reqeust.get('director_id')
            db.session.add(item_)
            db.session.commit()
            db.session.close()
            return "", 201
        return "", 404


@directors_ns.route('/')
class DirectorsAll(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return jsonify(directors_schema.dump(all_directors))
    def post(self):
        new_item_reqeust = request.json
        all_items = db.session.query(Director).all()
        all_items_id = []
        for item_ in all_items:
            all_items_id.append(item_.id)
        if new_item_reqeust.get('id') in all_items_id:
            return f'Item with id {new_item_reqeust.get("id")} already exists'
        new_item = Director(**new_item_reqeust)
        db.session.add(new_item)
        db.session.commit()
        db.session.close()
        return "", 201


@directors_ns.route('/<int:mid>/')
class Directors(Resource):
    def get(self, mid):
        director_ = Director.query.get(mid)
        if director_:
            return jsonify(director_schema.dump(director_))
        return "", 404

    def delete(self, mid):
        director_ = Director.query.get(mid)
        if director_:
            db.session.delete(director_)
            db.session.commit()
            db.session.close()
            return "", 204
        return "", 404

    def put(self, mid):
        item_ = Director.query.get(mid)
        if item_:
            new_item_reqeust = request.json
            item_.name = new_item_reqeust.get('name')
            db.session.add(item_)
            db.session.commit()
            db.session.close()
            return "", 201
        return "", 404


@genres_ns.route('/')
class GenreAll(Resource):
    def get(self):
        all_genre = db.session.query(Genre).all()
        return jsonify(genres_schema.dump(all_genre))
    def post(self):
        new_item_reqeust = request.json
        all_items = db.session.query(Genre).all()
        all_items_id = []
        for item_ in all_items:
            all_items_id.append(item_.id)
        if new_item_reqeust.get('id') in all_items_id:
            return f'Item with id {new_item_reqeust.get("id")} already exists'
        new_item = Genre(**new_item_reqeust)
        db.session.add(new_item)
        db.session.commit()
        db.session.close()
        return "", 201


@genres_ns.route('/<int:mid>/')
class Genres(Resource):
    def get(self, mid):
        genre_ = Genre.query.get(mid)
        if genre_:
            return jsonify(genre_schema.dump(genre_))
        return "", 404

    def delete(self, mid):
        genre_ = Genre.query.get(mid)
        if genre_:
            db.session.delete(genre_)
            db.session.commit()
            db.session.close()
            return "", 204
        return "", 404

    def put(self, mid):
        item_ = Genre.query.get(mid)
        if item_:
            new_item_reqeust = request.json
            item_.name = new_item_reqeust.get('name')
            db.session.add(item_)
            db.session.commit()
            db.session.close()
            return "", 201
        return "", 404


if __name__ == '__main__':
    app.run()
