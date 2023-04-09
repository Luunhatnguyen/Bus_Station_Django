FROM python:3.10

# Update APT
RUN apt-get update

# Make work directory
RUN mkdir /app
WORKDIR /app

# Install required packaged for Dijango projects
COPY ./AppApis/app/requirements.txt ./AppApis/app/requirements.txt
RUN pip install -r ./AppApis/app/requirements.txt

# Clone source code
COPY . .

# Expose Dijango Server Port
EXPOSE 8000

# Start webserver
CMD ["python", "AppApis/app/manage.py", "runserver", "0.0.0.0:8000"]