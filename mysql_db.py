import os
from dotenv import load_dotenv
import mysql.connector
import logging.config

# Загружаем настройки логирования из файла конфигурации
logging.config.fileConfig("logging.conf")

# Загружаем переменные окружения из файла .env
load_dotenv()

# Подключаемся к базе данных MySQL
try:
    mysqlDatabase = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        database=os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USERNAME"),
        password=os.getenv("MYSQL_PASSWORD"),
        auth_plugin=os.getenv("MYSQL_AUTH_PLUGIN"),
    )
    logging.info("connection to MySQL is OK")
except mysql.connector.Error as err:
    logging.error(f"error: {err}")


# Возвращаем объект подключения
def get_connection():
    return mysqlDatabase
