FROM python:3.12-slim-bookworm

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./project .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
