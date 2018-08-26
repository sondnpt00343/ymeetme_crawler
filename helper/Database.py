import os
import configparser
import mysql.connector
from mysql.connector import errorcode

cursor = None
connection = None

class Database:
    config = None
    filename = 'config'

    # connection = Database(config)
    def __init__(self, filename='config/database'):
        config = configparser.ConfigParser()
        config.read(filename)

        self.filename = filename
        self.config = {
            'host': os.getenv('DB_HOST', config.get('database', 'host')),
            'port': os.getenv('DB_PORT', config.get('database', 'port')),
            'user': os.getenv('DB_USERNAME', config.get('database', 'user')),
            'password': os.getenv('DB_PASSWORD', config.get('database', 'password')),
            'database': os.getenv('DB_NAME', config.get('database', 'database')),
            'raise_on_warnings': True,
            'use_pure': False,
            'use_unicode': True,
            'charset': 'utf8'
        }

    def connect(self):
        global connection

        try:
            if connection is not None:
                return connection
            else:
                connection = mysql.connector.connect(**self.config)
                return connection
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def cursor(self):
        global cursor

        if cursor is not None:
            return cursor
        else:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            return cursor
