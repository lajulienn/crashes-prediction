FROM python:3.6
ADD ./app /code/app
ADD ./requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["python", "./app/app.py"]