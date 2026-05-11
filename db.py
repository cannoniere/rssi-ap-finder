import psycopg
from pgvector.psycopg import register_vector
import logging
import log
from dotenv import load_dotenv

load_dotenv()
from config import settings 

def db_connect(DATABASE_URL) -> psycopg.Connection:
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    register_vector(conn)
    return conn

def init_db(log_queue) -> None:
    logger = log.configure_queue_logger(__name__, log_queue)
    print('1')    
    try:
        BASE_SCHEMA_SQL = settings.base_schema_sql
    except Exception as e:
        logger.critical('%s',e)
    print('2')    

    try:     
        DATABASE_URL = settings.database_url
        print(settings)
        print(DATABASE_URL)
    except Exception as e:
        logger.critical('%s',e)
    print('3')    
    print(DATABASE_URL)
    print(BASE_SCHEMA_SQL)
    
    with db_connect(DATABASE_URL) as conn:
        conn.execute(BASE_SCHEMA_SQL)
#        for stmt in MIGRATIONS_SQL:
#            conn.execute(stmt)
