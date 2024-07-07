FROM python:3.10-slim

WORKDIR /home/cambridge_spark_am2_practice

# Install Poetry
RUN pip install poetry

# Copy the necessary files
COPY . /home/cambridge_spark_am2_practice

# Install the project dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Expose port 80
EXPOSE 80

# Start the application
CMD poetry run uvicorn main:app --host 0.0.0.0 --port 80