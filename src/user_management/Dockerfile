FROM python:3.13.1-slim-bookworm


WORKDIR /user_management


# Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc \
                        libpq-dev \
                        postgresql-client \
    && apt-get clean

# Copy project files
COPY ./scripts/entrypoint.sh ./scripts/entrypoint.sh
COPY ./user_management ./user_management
COPY ./api ./api
COPY ./friends ./friends
COPY ./utils_jwt.py ./utils_jwt.py
COPY ./manage.py ./manage.py

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./scripts/entrypoint.sh"]
