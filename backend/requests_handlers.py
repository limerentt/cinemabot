import datetime
from aiogram import types

import db

from entities.users import User
from entities.films import Film
from entities.user_requests import UserRequest


def add_user(message: types.Message) -> User:
    user = User(id=message.from_user.id,
                name=message.from_user.username)

    if db.is_user_registered(message.from_user.id):
        return user

    db.insert("users", {
        "user_id": message.from_user.id,
        "user_name": message.from_user.username
    })
    return user


def add_film(response: dict) -> Film:
    film = Film(id=int(response['id']),
                name=response['name'],
                published_year=int(response['year']),
                description=response['description'],
                genre=response['genres'][0]['name'],
                imdb_rating=float(response['rating']['imdb']),
                kinopoisk_rating=float(response['rating']['kp']))

    if db.was_film_searched(int(response['id'])):
        return film

    db.insert("films", {
        "film_id": int(response['id']),
        "film_name": response['name'],
        "published_year": int(response['year']),
        "description": response['description'],
        "genre": response['genres'][0]['name'],
        "imdb_rating": float(response['rating']['imdb']),
        "kinopoisk_rating": float(response['rating']['kp'])
    })
    return film


def add_request(user: User, film: Film, message_id: int) -> UserRequest:
    request_dttm = datetime.datetime.now()
    db.insert("user_requests", {
        "user_id": user.id,
        "film_id": film.id,
        "message_id": message_id
    })

    return UserRequest(user_id=user.id,
                       film_id=film.id,
                       message_id=message_id,
                       request_dttm=request_dttm)


def last_searched_films(user_id: int, num: int) -> list[Film]:
    cursor = db.get_cursor()
    cursor.execute(
        f"select films.* "
        f"from user_requests req left join films "
        f"using(film_id) "
        f"where req.user_id = {user_id} "
        f"order by req.request_dttm desc limit {num}")
    rows = cursor.fetchall()
    last_films = [Film(*row) for row in rows]
    return last_films


def get_film_counts(user_id: int) -> dict:
    cursor = db.get_cursor()
    cursor.execute(
        f"select films.film_name, count(req.message_id) as film_count "
        f"from user_requests req join films "
        f"using(film_id) "
        f"where req.user_id = {user_id} "
        f"group by films.film_name")
    rows = cursor.fetchall()
    film_counts = dict(rows)
    return film_counts
