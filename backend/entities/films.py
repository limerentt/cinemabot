from datetime import datetime
from typing import NamedTuple


class Film(NamedTuple):
    id: int
    name: str
    published_year: int
    description: str
    genre: str
    imdb_rating: float
    kinopoisk_rating: float
