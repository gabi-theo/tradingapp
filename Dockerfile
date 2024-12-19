# Base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the run_migrations.sh script from the scripts folder in the project root
COPY ./scripts/run_migrations.sh /app/

# Ensure the entrypoint script is executable
RUN chmod +x /app/run_migrations.sh

# Expose the port Django will run on
EXPOSE 8000