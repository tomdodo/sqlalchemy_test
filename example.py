import json
import logging

import sys
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Enum, event
from sqlalchemy.orm import sessionmaker, relationship, backref, subqueryload, joinedload
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base

from config import USER, PASSWORD

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
LOG = logging.getLogger(__name__)


DATABASE_URI = 'mysql://{username}:{password}@127.0.0.1:3306/lightning_sqlalchemy?charset=utf8&use_unicode=1'

engine = create_engine(DATABASE_URI.format(username=USER, password=PASSWORD), poolclass=NullPool)
db = sessionmaker(bind=engine)()

Base = declarative_base()

# lazy loading options
# lazy='select'
# lazy='joined'
# lazy='subquery'
# lazy='selectin'
# lazy='raise'
# lazy='noload'
# lazy='dynamic'


class Company(Base):
    __tablename__ = 'Company'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)


class Email(Base):
    __tablename__ = 'Email'
    id = Column('id', Integer, primary_key=True)
    type = Column('type', Enum('home', 'work', 'other'), nullable=False)
    email = Column('email')
    user_id = Column('user_id', Integer, ForeignKey('User.id'))


class PhoneNumber(Base):
    __tablename__ = 'PhoneNumber'
    id = Column('id', Integer, primary_key=True)
    type = Column('type', Enum('home', 'work', 'other'), nullable=False)
    phone_number = Column('phone_number')
    user_id = Column('user_id', Integer, ForeignKey('User.id'))


class User(Base):
    __tablename__ = 'User'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    company_id = Column('company_id', Integer, ForeignKey(Company.id))

    company = relationship(Company, backref='users')  # lazy='joined'
    emails = relationship(Email)
    phone_numbers = relationship(PhoneNumber, lazy='dynamic')


def monitor_queries(fn):
    def decorated(*args, **kwargs):
        queries = []
        def spy_select_statements(
                conn, cursor, statement, parameters, context, executemany):
            actual_query = statement % parameters
            queries.append(actual_query)

        event.listen(
            db.connection().engine,
            'before_cursor_execute', spy_select_statements)
        # commit necessary otherwise the listener does not activate
        db.commit()

        fn_result = fn(*args, **kwargs)

        LOG.debug('--- EMITTED QUERIES for function call %s(%s, %s) --' % (fn.__name__, args, kwargs))
        for index, query in enumerate(queries):
            query_lines = query.split('\n')
            LOG.debug('%s. %s' % (index, query_lines[0]))
            for query_line in query_lines[1:]:
                LOG.debug('   %s' % query_line)
        sys.stdout.flush()
        sys.stderr.flush()
        return fn_result

    return decorated


@monitor_queries
def get_user_companies():
    users = db.query(User)
    out = []
    for user in users:
        out.append({
            'name': user.name,
            'company_name': user.company.name
        })
    return out


@monitor_queries
def get_user_emails():
    # .options(subqueryload(User.emails))
    # .options(joinedload(User.emails))
    users = db.query(User)
    out = []
    for user in users:
        out.append({
            'name': user.name,
            'emails': [
                {'type': email.type, 'email': email.email}
                for email in user.emails
            ]
        })
    return out


@monitor_queries
def get_user_phones(phone_type=None):
    # .options(subqueryload(User.phone_numbers))
    users = db.query(User)
    out = []
    for user in users:
        phone_numbers = user.phone_numbers
        if phone_type:
            phone_numbers = phone_numbers.filter(
                PhoneNumber.type == phone_type)
        out.append({
            'name': user.name,
            'phones': [
                {
                    'type': phone_number.type,
                    'phone_number': phone_number.phone_number
                } for phone_number in phone_numbers
            ]
        })
    return out


def dump_results(data):
    sys.stdout.flush()
    sys.stderr.flush()
    print(json.dumps(data, indent=4))
    sys.stdout.flush()

# Test comment to create a PR
