# Use the official Python image as a base
FROM python:3
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY alert-logger.py .

# Command to run the application with unbuffered output
CMD ["python", "-u", "alert-logger.py"]
