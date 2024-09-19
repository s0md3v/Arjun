# Use a base image of Python
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the necessary files to the container
COPY ./ /app

# Install the dependencies and run setup.py
RUN python3 setup.py install

# Default command to run with argument "arjun"
ENTRYPOINT ["arjun"]
