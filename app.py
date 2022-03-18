# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
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


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movies_ns.route('/')
class Movies(Resource):
    def get(self):
        all_movies = db.session.query(Movie).all()
        return jsonify(movies_schema.dump(all_movies))


@movies_ns.route('/<int:mid>')
class Movies(Resource):
    def get(self, mid):
        movie_ = Movie.query.get(mid)
        director_ = Director.query.filter(Director.id == movie_.director_id).one()
        genre_ = Genre.query.filter(Genre.id == movie_.genre_id).one()
        if movie_:
            return jsonify(movie_schema.dump(movie_), director_schema.dump(director_), genre_schema.dump(genre_))
        return "", 404


if __name__ == '__main__':
    app.run(debug=True)
