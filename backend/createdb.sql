create table films(
    film_id integer primary key,
    film_name text,
    published_year int,
    description text,
    genre varchar(255),
    imdb_rating real,
    kinopoisk_rating real
);

create table users(
    user_id integer primary key,
    user_name varchar(255)
);

create table user_requests(
    request_id integer primary key,
    user_id integer,
    film_id integer,
    message_id integer,
    request_dttm TIMESTAMP default current_timestamp,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(film_id) REFERENCES films(film_id)
);