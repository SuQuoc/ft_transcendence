FROM python:3.10-slim-buster

# Forces python to not buffer the output and print it directly 
ENV PYTHONBUFFERED=1

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