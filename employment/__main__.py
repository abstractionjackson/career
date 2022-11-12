
import click
from click import argument, command, group, option
from sqlalchemy import create_engine, MetaData, text, insert, select
from sqlalchemy import Table, Column, Float, String, Date, Integer
from sqlalchemy.orm import Session

engine = create_engine('sqlite+pysqlite:///career.db', future=True)
metadata_obj = MetaData()
employment_table = Table(
        "employment",
        metadata_obj,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('start', Date),
        Column('end', Date),
        Column('employer', String, unique=False),
        Column('role', String, unique=False),
        Column('compensation', Float, unique=False)
        )
@group()
def employment():
    metadata_obj.create_all(engine)
    pass
@employment.command('drop_db')
def drop_db():
    metadata_obj.drop_all(engine)
    pass
@employment.command()
@argument('start', type=click.DateTime())
@argument('employer')
@argument('role')
@argument('compensation', type=click.FLOAT)
@option('-e', '--end', type=click.DateTime())
def create(**kwargs):
    print(f'CREATE {kwargs["role"]} at {kwargs["employer"]} for ${kwargs["compensation"]} from {kwargs["start"]} to {kwargs["end"]}')
    stmt = employment_table.insert(kwargs)
    with engine.begin() as conn:
        conn.execute(stmt)
@employment.command()
@option('--id', type=click.INT)
@option('-e', '--employer')
@option('-r', '--role')
def get(id, employer, role):
    stmt = employment_table.select()
    if id is not None:
        stmt = stmt.where(employment_table.c.id == id)
    elif employer is not None and role is not None:
        stmt = stmt.where(
                employment_table.c.employer == employer
                and employment_table.c.role == role)
    with engine.begin() as conn:
        res = conn.execute(stmt)
        if id is not None:
            print(res.one())
        elif employer is not None and role is not None:
            print(res.one())
        else:
            print(res.all())
@employment.command()
@argument('id', type=click.INT)
def delete(id):
    stmt = employment_table.delete().where(employment_table.c.id == id)
    with engine.begin() as conn:
        conn.execute(stmt)

if __name__ == '__main__':
    employment()
