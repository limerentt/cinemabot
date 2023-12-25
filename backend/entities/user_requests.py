from datetime import datetime
from typing import NamedTuple


class UserRequest(NamedTuple):
    user_id: int
    film_id: int
    message_id: int
    request_dttm: datetime
