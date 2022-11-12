
from click import argument, command, group, option

@command()
def hello():
    print('Hello, World!')

@group()
def employment():
    pass

@employment.command()
@argument('start')
@argument('employer')
@argument('role')
@argument('compensation')
@option('-e', '--end')
def create(employer, role, compensation, start, end=None):
    print(f'CREATE {role} at {employer} for ${compensation} from {start} to {end}')

if __name__ == '__main__':
    employment()
