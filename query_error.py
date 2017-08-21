# This is sample code that is used to generate API error messages related to
# Issue #2 on the apiclient repository.
from arable.client import ArableClient
import os
import datetime

# Read the environmental variables in from .env:
if os.path.exists('.env'):
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

# Setup the connection using our credentials.
# (Let me know if you need them)

conn = ArableClient()
conn.connect(
    os.environ['USERNAME'],
    os.environ['PASSWORD'],
    os.environ['ORGNAME'])

# Let's just grab the first device in our org list:
d = conn.devices()[0]

# Extract the deployment time for this device
deploy_time = datetime.datetime.strptime(
    d['last_deploy'], "%Y-%m-%dT%H:%M:%S.%f")

# Let's set a start date to be 4 days prior to the last deploy:
ok_earlier_time = deploy_time - datetime.timedelta(days=4)

# This query works:
conn.query(
    devices=[d['name']],
    start=ok_earlier_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    measure='L1')

# What if we try to start the query 7 days before the last deploy?
bad_earlier_time = deploy_time - datetime.timedelta(days=7)

# This query fails with a 400 Bad Message
conn.query(
    devices=[d['name']],
    start=bad_earlier_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    measure='L1')
