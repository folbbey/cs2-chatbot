"""Database connection management for PostgreSQL."""
import os
import psycopg2
from psycopg2 import pool
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Connection pool
_connection_pool: Optional[pool.SimpleConnectionPool] = None


def get_db_config():
    """Get database configuration from environment variables."""
    return {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', '5432')),
        'database': os.getenv('POSTGRES_DB', 'fishing_bot'),
        'user': os.getenv('POSTGRES_USER', 'bot_user'),
        'password': os.getenv('POSTGRES_PASSWORD', 'bot_password')
    }


def initialize_pool(minconn=1, maxconn=10):
    """Initialize the connection pool."""
    global _connection_pool
    if _connection_pool is None:
        config = get_db_config()
        logger.info(f"Initializing connection pool to {config['host']}:{config['port']}/{config['database']}")
        _connection_pool = pool.SimpleConnectionPool(
            minconn,
            maxconn,
            **config
        )
        logger.info("Connection pool initialized successfully")


def get_connection():
    """Get a connection from the pool."""
    if _connection_pool is None:
        initialize_pool()
    return _connection_pool.getconn()


def return_connection(conn):
    """Return a connection to the pool."""
    if _connection_pool is not None:
        _connection_pool.putconn(conn)


def close_pool():
    """Close all connections in the pool."""
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None
        logger.info("Connection pool closed")


class DatabaseConnection:
    """Context manager for database connections."""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        
        if self.cursor:
            self.cursor.close()
        
        if self.conn:
            return_connection(self.conn)
