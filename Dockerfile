FROM python:3.12.4
# set work directory
WORKDIR /usr/src/app/
# copy project
COPY . /usr/src/app/
# install dependencies
RUN pip install --user telebot
# run app
CMD ["python", "cmd/main.py"]