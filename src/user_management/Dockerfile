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
COPY ./api ./api
COPY ./user_management ./user_management
COPY ./manage.py ./manage.py

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./scripts/entrypoint.sh"]

# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "user_management.asgi:application"] # NOTE: FE might not update the small profile pic
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# [aguilmea] for deployment testing
#CMD ["python", "manage.py", "check", "--deploy"]