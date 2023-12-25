import os
import aiohttp
from aiogram import Bot, types, Dispatcher, executor
from aiogram.types import ParseMode

from requests_handlers import (add_user, add_film, add_request,
                               last_searched_films, get_film_counts)

from exceptions import ServiceError

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
SEARCH_ENGINE_ID = os.environ['SEARCH_ENGINE_ID']


bot = Bot(token=os.environ['BOT_TOKEN'])
dp = Dispatcher(bot)


async def find_movie_kinopoisk(query):
    url = 'https://api.kinopoisk.dev/v1.4/movie/search'
    params = {'page': 1, 'limit': 1, 'query': query}
    headers = {'accept': 'application/json', 'X-API-KEY': os.environ['KINOPOISK_API_KEY']}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            return data


async def find_random_movie_kinopoisk():
    url = 'https://api.kinopoisk.dev/v1.4/movie/random'
    headers = {'accept': 'application/json', 'X-API-KEY': os.environ['KINOPOISK_API_KEY']}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data


async def get_first_google_search_result(query: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': GOOGLE_API_KEY,
                'cx': SEARCH_ENGINE_ID,
                'q': query
            }
            async with session.get(url, params=params) as response:
                data = await response.json()
                return str(data['items'][1]['link'])

    except Exception as e:
        print(f"Error in Google Custom Search: {e}")

    return "No results found"


async def send_movie_with_response(response: dict, message: types.Message):
    response_text = (f"<b>Name:</b>\n{response['name']} ({response['year']})\n"
                     f"<b>Rating:</b>\nKinopoisk: <b>{response['rating']['kp']}</b>, "
                     f"IMDB: <b>{response['rating']['imdb']}</b>.\n"
                     f"<b>Description:</b>\n{response['description']}\n")

    await bot.send_photo(chat_id=message.chat.id,
                         photo=response['poster']['url'],
                         caption=response_text,
                         parse_mode=ParseMode.HTML)

    user = add_user(message)
    film = add_film(response)
    add_request(user, film, message.message_id)

    film_name = response['name']
    search_query = f"film {film_name}"
    first_link = await get_first_google_search_result(search_query)

    await bot.send_message(chat_id=message.chat.id, text=f"link: {first_link}")


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "🎬 <b>Welcome to Film Searcher Bot!</b> 🍿\n"
        "I'm here to help you discover information about movies.\n\n"
        "<b>How to Use:</b>\n"
        "Just send me the name of a movie, and I'll provide you with details about it!\n\n"
        "<b>Commands:</b>\n"
        "/start - Start interacting with the bot.\n"
        "/help - Display a list of available commands and usage instructions.\n"
        "/history - View the last films you've searched.\n"
        "/stats - Get statistics on the number of requests per film.\n\n"
        "<b>Example:</b>\n"
        "Send 'Venom' to learn more about the movie 'Venom'.\n\n"
        "🎥 Let's get started! Send me a movie name and enjoy the magic of cinema. 🍿"
    )

    await message.reply(welcome_text, parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    help_text = (
        "<b>Film Searcher Bot Commands:</b>\n"
        "/start - Start interacting with the bot.\n"
        "/help - Display this help message.\n"
        "/history - View the last films you've searched.\n"
        "/stats - Get statistics on the number of requests per film.\n"
        "<b>How to Use:</b>\n"
        "Simply send the name of a movie to get information about it!\n\n"
        "<b>Examples:</b>\n"
        "1. Send 'Venom' to search for information about the movie 'Venom'.\n"
        "2. Use /history to view your search history.\n"
        "3. Use /stats to get statistics on your search requests."
    )

    await message.reply(help_text, parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['random'])
async def send_random_movie(message: types.Message):
    try:
        response = await find_random_movie_kinopoisk()
        if not response:
            await message.reply("I haven't found anything 🫣")
            return
        await send_movie_with_response(response, message)
    except ServiceError:
        await message.reply("Kinopoisk API not working. Please try again later.")


@dp.message_handler(commands='history')
async def send_last_films(message: types.Message):
    films_num_limit = 10
    last_films = last_searched_films(user_id=message.from_user.id, num=films_num_limit)
    if len(last_films) == 0:
        await message.reply('You haven\'t searched yet', parse_mode=ParseMode.HTML)
        return
    max_films_history_num = min(films_num_limit, len(last_films))

    response_text = f"<b>Last {max_films_history_num} films:</b>\n"
    for film in last_films:
        response_text += f"{film.name} ({film.published_year})\n"

    await message.reply(response_text, parse_mode=ParseMode.HTML)


@dp.message_handler(commands='stats')
async def send_films_counts(message: types.Message):
    film_counts = get_film_counts(user_id=message.from_user.id)

    if len(film_counts) == 0:
        await message.reply('You haven\'t searched yet', parse_mode=ParseMode.HTML)
        return

    response_text = "<b>Number of your requests per film:</b>\n"
    for film_name, film_count in film_counts.items():
        response_text += f"{film_name}: {film_count}\n"

    await message.reply(response_text, parse_mode=ParseMode.HTML)


@dp.message_handler()
async def send_movie(message: types.Message) -> None:
    try:
        response = await find_movie_kinopoisk(message.text)
        if not response.get('docs', []):
            await message.reply("I haven\'t found anything🫣")
            return
        response = response['docs'][0]
        await send_movie_with_response(response, message)
    except ServiceError:
        await message.reply("Kinopoisk API not working. Please try again later.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
