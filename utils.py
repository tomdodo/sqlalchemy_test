from contextlib import contextmanager
from typing import List, Dict, Any
from datetime import datetime

from sqlalchemy import event, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

DATABASE_URI = "mysql://root:insecure@database:3306/performance_inserts"


engine = create_engine(DATABASE_URI, poolclass=NullPool)
get_session = sessionmaker(bind=engine)


@contextmanager
def record_queries():
    sql_queries: List[Dict[str, List[Any]]] = []

    def _spy_queries(
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ):
        sql_queries.append({"statement": statement, "parameters": list(parameters)})

    event.listen(engine, "before_cursor_execute", _spy_queries)
    yield sql_queries
    event.remove(engine, "before_cursor_execute", _spy_queries)


class TimeMeasurement(object):
    __slots__ = ("start_time", "end_time")

    def __init__(self):
        self.start_time = datetime.utcnow()
        self.end_time = None

    def stop(self):
        self.end_time = datetime.utcnow()

    @property
    def seconds(self) -> int:
        """
        Returns the duration of this measurement in milliseconds
        """
        return ((self.end_time or datetime.utcnow()) - self.start_time).total_seconds()


@contextmanager
def measure_time():
    measurement = TimeMeasurement()
    yield measurement
    measurement.stop()
