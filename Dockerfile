# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app (root of our project in container)
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the local directory into /app
COPY . .

# Set PYTHONPATH to /app
ENV PYTHONPATH=/app

# Default port (can be overridden by cloud provider)
ENV PORT=5001

# Run the application using gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT web_app:app
