FROM python:3.10-slim-buster


WORKDIR /user_management


# Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc \
                        libpq-dev \
                        postgresql-client \
    && apt-get clean

COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project files
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
