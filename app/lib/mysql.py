import os
import logging
from threading import Lock
from typing import List, Optional, Tuple, Callable
from mysql.connector import connection as dbConnection
from mysql.connector.cursor import MySQLCursor, MySQLCursorPrepared, MySQLCursorDict
from mysql.connector.errors import Error as DBError, InterfaceError, InternalError, Warning as DBWarning

logger = logging.getLogger("MYSQL")

class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        
        return cls._instances[cls]

class Query():
    def __init__(self, query: str, params: tuple = (), usePrepared: bool = False) -> None:
        self.query = query
        self.params = params
        self.usePrepared = usePrepared


class MySQL(object, metaclass=SingletonMeta):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)

            _user = os.getenv('MYSQL_USER')
            _password = os.getenv('MYSQL_PASSWORD')
            _host = os.getenv('MYSQL_HOST')

            try:
                logger.info('new instance of database. trying to connect...')
                connection = dbConnection.MySQLConnection(
                    user=_user, 
                    password=_password, 
                    host=_host, 
                    raise_on_warnings=True, 
                    autocommit=False,
                    charset='utf8',
                    use_unicode=True,
                    time_zone='-03:00'
                )
            
            except DBError as err:
                logger.error('cannot connect to database: {}'.format(err.msg))
                MySQL._instance = None

                raise

            MySQL._instance.connection = connection
            logger.info('connected to database')

        return cls._instance

    def __init__(self):
        self.connection: dbConnection.MySQLConnection = self._instance.connection

    def execute(self, query: str, params: tuple = (), usePrepared: bool = False, autoCommit: bool = True) -> Tuple[list, Optional[int]]:
        c_class = MySQLCursorDict
        if usePrepared and params != ():
            c_class = MySQLCursorPrepared

        cursor = self.connection.cursor(cursor_class=c_class)

        try:
            result, column_names, last_inserted_id = execute(cursor, query, params)

        except:
            self.connection.rollback()
            raise
        
        else:
            if autoCommit:
                self.connection.commit()

        finally:
            cursor.close()

        response = []
        for row in result:
            if c_class == MySQLCursorPrepared:
                r = dict(zip(column_names, row))
                for key in r:
                    try:
                        r[key] = r[key].decode()
                    except (UnicodeDecodeError, AttributeError):
                        pass
                    
                response.append(r)
            else:
                response.append(row)

        return response, last_inserted_id

    def rollback(self):
        try:
            self.connection.rollback()
        except (DBError, InternalError, InterfaceError) as err:
            logger.debug('error trying to rollback transaction: {}'.format(err.msg))
            raise

    def commit(self):
        try:
            self.connection.commit()
        
        except (DBError, InternalError, InterfaceError) as err:
            logger.debug('error trying to commit transaction: {}'.format(err.msg))
            raise

    # Only for insert, update or delete queries
    def executeTransactionQueries(self, queries: List[Query], do_after_each: Callable = None) -> None:
        for query in queries:
            c_class = MySQLCursorDict
            if query.usePrepared and query.params != ():
                c_class = MySQLCursorPrepared

            cursor = self.connection.cursor(cursor_class=c_class)

            try:
                execute(cursor, query.query, query.params)

            except:
                self.connection.rollback()
                raise

            finally:
                if do_after_each is not None:
                    do_after_each(query)
                
                cursor.close()

        try:
            self.connection.commit()
        
        except (DBError, InternalError, InterfaceError) as err:
            logger.debug('error trying to commit all transaction queries: {}'.format(err.msg))
            raise
    
    def query(self, query: str, params: tuple = (), usePrepared: bool = False) -> Query:
        q = Query(query, params, usePrepared)

        return q

    def __del__(self):
        logger.info('closing database connection and cursor')

        self.connection.close()


def execute(cursor: MySQLCursor, query: str, params: tuple) -> Tuple[list, tuple, Optional[int]]:
    try:
        cursor.execute(query, params, multi=False)
    
    except DBWarning as warn:
        logger.warning(warn.msg)
    
    except DBError as err:
        logger.debug('error executing query "{}" with args "{}": {}'.format(query, params, err.msg))
        raise

    column_names = cursor.column_names
    last_inserted_id = cursor.lastrowid

    try:
        result = cursor.fetchall()
    except InterfaceError as err:
        if err.msg == "No result set to fetch from" or err.msg == "No result set to fetch from.":
            return [], (), last_inserted_id
        
        raise
    
    return result, column_names, None

"""
class MySQL(metaclass=SingletonMeta):
    connection: dbConnection.MySQLConnection = None

    def __init__(self) -> None:
        _user = os.getenv('MYSQL_USER')
        _password = os.getenv('MYSQL_PASSWORD')
        _host = os.getenv('MYSQL_HOST')

        try:
            logger.info('new instance of database. trying to connect...')
            self.connection = dbConnection.MySQLConnection(user=_user, password=_password, host=_host, raise_on_warnings=True)
        
        except DBError as err:
            logger.error('cannot connect to database: {}'.format(err.msg))
            self.connection = None

            raise

        logger.info('connected to database')

    def execute(self, query: str, params: tuple = (), usePrepared: bool = False) -> list:
        c_class = MySQLCursorDict
        if usePrepared and params != ():
            c_class = MySQLCursorPrepared

        cursor = self.connection.cursor(cursor_class=c_class)

        try:
            result, column_names = execute(cursor, query, params)

        except:
            raise

        finally:
            cursor.close()

        response = []
        for row in result:
            if c_class == MySQLCursorPrepared:
                response.append(dict(zip(column_names, row)))
            else:
                response.append(row)

        return response

    def __del__(self):
        logger.info('closing database connection')

        self.connection.close()
"""
