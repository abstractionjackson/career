
import click
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from click import argument, command, group, option
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Float, String, Date, Integer
from sqlalchemy.orm import Session
from datetime import date

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
@employment.command()
def plot():
    fig, ax = plt.subplots()
    ax.set_xlabel('Employment Date')
    ax.set_ylabel('Compensation')
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    data = None
    stmt = employment_table.select()
    with engine.begin() as conn:
        res = conn.execute(stmt)
        data = res.all()
    labels = [row.employer for row in data]
    COLOR = 'tab:blue'
    lines = ax.hlines(
            [row.compensation for row in data],
            xmin = [row.start for row in data],
            xmax = [row.end or date.today() for row in data]
            )
    #.fill_between(x for x, y in segment), y1 = segment[0][1], y2 = 0)
    for i, segment in enumerate(lines.get_segments()):
        x, y = segment[0]
        x_offset = (segment[1][0] - x) / 2
        label = ax.text(
            x + x_offset,
            0,
            labels[i],
            verticalalignment='top',
            horizontalalignment='center',
            rotation=0
        )
        ax.fill_between([x for x, y in segment], y1 = segment[0][1], y2 = 0, color=COLOR)
    plt.show()
    pass
if __name__ == '__main__':
    employment()
