#!/usr/bin/env python3
"""
PII(Personally Identifiable Information)
"""
import logging
import re
from typing import List
from os import getenv
import mysql.connector


PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """ returns the log message obfuscated """
    for obfuscated in fields:
        message = re.sub(rf'{obfuscated}=.*?{separator}',
                         rf'{obfuscated}={redaction}{separator}',
                         message)
    return message


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
    """
    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """ filter PII from log message """
        record.msg = filter_datum(self.fields, self.REDACTION,
                                  record.msg, self.SEPARATOR)
        return super().format(record)


def get_logger() -> logging.Logger:
    """ Create new logger object with specific config """
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Returns a connector to the database
    """
    username = getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    password = getenv('PERSONAL_DATA_DB_PASSWORD', '')
    host = getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    dbname = getenv('PERSONAL_DATA_DB_NAME', 'my_db')

    return mysql.connector.connection.MySQLConnection(
        user=username,
        password=password,
        host=host,
        database=dbname
    )


def main() -> None:
    """ Use of all above implementations """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    logger = get_logger()
    for row in cursor:
        message = (f"name={row[0]};email={row[1]};phone={row[2]};"
                   f"ssn={row[3]};password={row[4]};ip={row[5]};"
                   f"last_login={row[6]};user_agent={row[7]};")
        logger.info(message)
    cursor.close()
    db.close()


if __name__ == '__main__':
    main()
