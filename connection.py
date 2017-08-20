from arable.client import ArableClient
import os

# Read the environmental variables in from .env:
if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

conn = ArableClient()
conn.connect(
    os.environ['USERNAME'],
    os.environ['PASSWORD'],
    os.environ['ORGNAME'])
