import psycopg
from pgvector.psycopg import register_vector
from dotenv import load_dotenv

load_dotenv()
from config import settings 


def db_connect(DATABASE_URL) -> psycopg.Connection:
    
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    register_vector(conn)
    
    return conn


def init_db() -> None:
    
    try:
        BASE_SCHEMA_SQL = settings.base_schema_sql
    except Exception as e:
        logger.critical('%s',e)

    try:     
        DATABASE_URL = settings.database_url
    except Exception as e:
        print(f'db url error: {e}')
    
    with db_connect(DATABASE_URL) as conn:
        conn.execute(BASE_SCHEMA_SQL)

    return

