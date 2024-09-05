FROM python:3.12-slim-bookworm


WORKDIR /user_management


# Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc \
                        libpq-dev \
                        postgresql-client \
    && apt-get clean

# Copy project files
COPY ./scripts/entrypoint.sh ./scripts/entrypoint.sh
COPY ./api ./api
COPY ./user_management ./user_management
COPY ./manage.py ./manage.py

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./scripts/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
