FROM python:3.10
ENV PYTHONUNBUFFERED 1

# create root directory for the project in the container
RUN mkdir /application
# Set the working directory to /application
WORKDIR /application
# Copy the current directory contents into the container at /application
ADD . /application/
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt