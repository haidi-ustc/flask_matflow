# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV FLASK_RUN_HOST 0.0.0.0

# Create and set the working directory
WORKDIR /flask_matflow

RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main" > /etc/apt/sources.list \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main" >> /etc/apt/sources.list \
   && apt-get update && apt-get upgrade -y \
   && apt-get install -y --no-install-recommends gcc libpq-dev \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*
# Install Python dependencies
COPY requirements.txt /flask_matflow/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy only necessary files to container (modify this as per your needs)
COPY ../ /flask_matflow/


# Specify the command to run on container start
CMD ["python", "manage.py"]

