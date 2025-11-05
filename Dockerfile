# Use official Python image
FROM python:3.11-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Collect static files for Nginx
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "pharma_city.wsgi:application", "--bind", "0.0.0.0:8000"]

