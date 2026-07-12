# Use the official Playwright Python image (Jammy Ubuntu base)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files into the working directory
COPY . .

# Expose port 10000 for the dummy health check server
EXPOSE 10000

# Command to run app.py
CMD ["python", "app.py"]
