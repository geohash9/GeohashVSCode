# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED True

# Set the working directory in the container
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy the requirements file into the container at /app
COPY . ./

# Install any dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Define the command to run your Flask application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 timeout 0 main:app
