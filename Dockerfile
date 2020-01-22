FROM python:3.7.5-slim

# Set to ensure logs are output promptly
ENV PYTHONUNBUFFERED=1

# Add build deps for python packages
# libpq-dev is required to install psycopg2-binary
RUN apt-get update && apt-get install -y libpq-dev && apt-get clean

# Create python user to avoid having to run celery as root
RUN useradd -m python && \
  mkdir /app && \
  chown python:python -R /app
WORKDIR /app
USER python
ENV PATH=/opt/bin:/home/python/.local/bin:$PATH

# Get latest pip
RUN pip install --user --upgrade pip

# Install poetry
RUN pip install --user poetry==0.12.17

# Copy the dependency files first
ADD poetry.lock /app
ADD pyproject.toml /app

# Install dependencies, dev not required for application runtime
RUN poetry install --no-dev

# Add the application
ADD . .

# Run flask on port 5000
EXPOSE 5000


# Set the entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
