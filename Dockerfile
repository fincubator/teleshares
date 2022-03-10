# Use an official Python runtime as a parent image
FROM python:3.7

RUN pip install pipenv

# Set the working directory to /teleshares
WORKDIR /teleshares

COPY Pipfile.lock /teleshares

RUN pipenv install --ignore-pipfile --keep-outdated

# Copy the current directory contents into the container at /teleshares
COPY . /teleshares

# Make port 80 available to the world outside this container
EXPOSE 8080
