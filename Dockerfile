FROM python:3.9

WORKDIR /home/lex/ysda_python/limerent/13.3.HW3/tasks/cinemabot

RUN apt-get update && apt-get install sqlite3 \
    && pip install --force-reinstall -v "aiogram==2.23.1"
COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
