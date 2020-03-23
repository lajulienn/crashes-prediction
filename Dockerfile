FROM python:3.6
RUN apt-get -qqy update && \
    apt-get install -y gdal-bin python-gdal python3-gdal libgdal-dev
ADD ./app /code/app
ADD ./requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "./app/main.py"]
