FROM python:3.8.5-slim

# Add build deps for python packages
# libpq-dev is required to install psycopg2-binary
# curl is used to install poetry
RUN apt-get update && \
    apt-get install -y curl libpq-dev && \
    apt-get clean

# Set the working directory to /app
WORKDIR /app

# Create python user to avoid having to run as root
RUN useradd -m python && \
    chown python:python -R /app
# Set the user
USER python

# Set the poetry version
ARG POETRY_VERSION=1.0.10
# Set to ensure logs are output promptly
ENV PYTHONUNBUFFERED=1
# Update the path
ENV PATH=/home/python/.poetry/bin:/home/python/.local/bin:$PATH

# Install vendored poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

# Add poetry stuff
ADD pyproject.toml .
ADD poetry.lock .

# Install all the dependencies and cleanup
RUN poetry config virtualenvs.create false && \
    poetry run pip install --user -U pip && \
    poetry install --no-dev && \
    "yes" | poetry cache clear --all pypi

# Add everything
ADD . .

# Set the entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
