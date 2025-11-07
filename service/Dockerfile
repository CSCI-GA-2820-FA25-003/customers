# syntax=docker/dockerfile:1

FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files first to leverage Docker layer caching
COPY Pipfile Pipfile.lock ./

# Install pipenv and project dependencies
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

# Copy the service source code and entry file
COPY service/ ./service/
COPY wsgi.py ./

# Set environment variables
ENV FLASK_APP=service
ENV PORT=8080
EXPOSE 8080

# Run the Flask application
CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0", "--port=8080"]
