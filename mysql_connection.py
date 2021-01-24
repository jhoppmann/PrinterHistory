import mysql.connector
import mysql.connector.cursor
from logging import Logger


class Connector:

    def __init__(self, config: dict, log: 'Logger'):
        self.config = config
        self.log = log
        self.ensure_tables_exist()

    def save(self, file: str, time: str, topic: str, machine: str) -> None:
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor()
        _SQL = """insert into HISTORY
        (FILE, STATUS, MACHINE, PRINT_TIME)
        values
        (%s, %s, %s, %s)"""
        cursor.execute(_SQL, (file, topic, machine, time))
        conn.commit()
        cursor.close()
        conn.close()
        self.log.info('New database line logged')

    def ensure_tables_exist(self) -> None:
        history_table_statement = "CREATE TABLE IF NOT EXISTS `HISTORY` (" \
                                  "`ID` int NOT NULL AUTO_INCREMENT, " \
                                  "`DATE` timestamp default current_timestamp," \
                                  "`FILE` varchar(100) not null," \
                                  "`STATUS` varchar(40) not null," \
                                  "`MACHINE` varchar(30) not null," \
                                  "`PRINT_TIME` bigint not null," \
                                  "PRIMARY KEY (`ID`)" \
                                  ")"
        self.log.info('Setting up database connection...')
        conn = mysql.connector.connect(**self.config)
        self.log.info('Database connected')
        cursor = conn.cursor()
        cursor.execute(history_table_statement)
        conn.commit()
        cursor.close()
        conn.close()

    def load_data(self) -> dict:
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor(dictionary=True)
        _SQL = """SELECT * FROM HISTORY"""
        cursor.execute(_SQL)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
