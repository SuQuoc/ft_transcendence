FROM python:3.13.1-slim-bookworm

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		postgresql-client \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /game

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./entrypoint.sh ./entrypoint.sh
COPY ./game ./game
COPY ./pong ./pong
COPY ./manage.py ./manage.py

ENTRYPOINT ["./entrypoint.sh"]

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# FOR PROD --> CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "game.asgi:application"]
