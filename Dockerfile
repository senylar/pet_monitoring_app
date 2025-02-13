FROM python:3.12
LABEL authors="gggg"

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Verify Flask installation
RUN python -m pip show flask

# Expose the port for the Flask application
EXPOSE 5000

# Set the command to run the application
CMD ["python", "stub_server/stub_server.py"]