from __future__ import print_function

import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'mydatabase'

TABLES = {}
TABLES['juzgado'] = (
    "CREATE TABLE `juzgado` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `page` int(11) NOT NULL,"
    "  `y` int(11) NOT NULL,"
    "  `text` varchar(255) NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

TABLES['headers'] = (
    "CREATE TABLE `headers` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `page` int(11) NOT NULL,"
    "  `y` int(11) NOT NULL,"
    "  `juzgado` varchar(255),"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

TABLES['contentofheaders'] = (
    "CREATE TABLE `contentofheaders` ("
    "  `id` int(11) NOT NULL,"
    "  `content` varchar(255) NOT NULL,"
    "  `x` int(11),"
    "  `record_x` int(11),"
    "  CONSTRAINT `contentofheaders_ibfk_1` FOREIGN KEY (`id`) "
    "     REFERENCES `headers` (`id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")

# TABLES['recordIndex'] = (
#     "CREATE TABLE `recordIndex` ("
#     "  `id` int(11),"
#     "  `page` int(11) NOT NULL,"
#     "  `y` int(11) NOT NULL,"
#     "  CONSTRAINT `recordIndex_ibfk_1` FOREIGN KEY (`id`) "
#     "     REFERENCES `headers` (`id`) ON DELETE CASCADE"
#     ") ENGINE=InnoDB")

TABLES['elements'] = (
    "CREATE TABLE `elements` ("
    "  `id` int(11),"
    "  `page` int(11) NOT NULL,"
    "  `x` int(11) NOT NULL,"
    "  `y` int(11) NOT NULL,"
    "  `text` varchar(255) NOT NULL,"
    "  CONSTRAINT `elements_ibfk_1` FOREIGN KEY (`id`) "
    "     REFERENCES `headers` (`id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")

cnx = mysql.connector.connect(user='root')
cursor = cnx.cursor()

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)
        
for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

cursor.close()
cnx.close()