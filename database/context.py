from contextlib import contextmanager
from typing import Generator, Tuple
import sqlite3
from .connection import get_connection

@contextmanager
def db_context() -> Generator[Tuple[sqlite3.Connection, sqlite3.Cursor], None, None]:
    """データベース操作のためのコンテキストマネージャ。
    
    接続の取得、カーソルの作成、コミット/ロールバック、クローズを自動的に処理します。
    
    Yields:
        Tuple[sqlite3.Connection, sqlite3.Cursor]: データベース接続とカーソルのタプル
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield conn, cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()