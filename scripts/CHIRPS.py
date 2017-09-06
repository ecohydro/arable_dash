from connection import conn
from Organization import Organization
import pandas as pd
import os

VARIABLES = {
    'L0': [
        'time',
        'device',
        'location',
        'lat', 'long',
        'dqs',
        'dsd0', 'dsd1', 'dsd2', 'dsd3', 'dsd4', 'dsd5', 'dsd6', 'dsd7', 'dsd8',
        'dsd9', 'dsd10', 'dsd11', 'dsd12', 'dsd13', 'dsd14', 'dsd15', 'dsd16',
        'dsd17', 'dsd18', 'dsd19', 'dsd20', 'dsd21', 'dsd22', 'dsd23', 'dsd24',
        'dsd25', 'dsd26', 'dsd27', 'dsd28', 'dsd29', 'dsd30', 'dsd31',
        'elev',
        'lw0', 'lw1', 'lw2', 'lw3',
        'orient_x', 'orient_y', 'orient_z',
        'p',
        'rain',
        'rh',
        'spec0', 'spec1', 'spec2', 'spec3', 'spec4', 'spec5', 'spec6', 'spec7',
        'spec8', 'spec9', 'spec10', 'spec11', 'spec12', 'spec13',
        'spec_tmp0', 'spec_tmp1',
        'sw0', 'sw1',
        'temp', 'rdqs'],
    'L1': [
        'time',
        'device',
        'location',
        'lat', 'long',
        'dqs',
        'B1dw', 'B1uw', 'B2dw', 'B2uw', 'B3dw', 'B3uw', 'B4dw', 'B4uw', 'B5dw',
        'B5uw', 'B6dw', 'B6uw', 'B7dw', 'B7uw',
        'LWdw', 'LWuw',
        'P',
        'PARdw', 'PARuw',
        'prate',
        'rain',
        'RH',
        'S_dw', 'S_uw', 'SWdw', 'SWuw',
        'Tabove',
        'Tair',
        'Tbelow']
    }

Org = Organization()
devices = [x for x in Org.devices_df['name']]

os.chdir('/Users/nkrell/Box Sync/pulsepod/ftpout')  # where files go

result = conn.query(
        devices=devices,
        order="-time",
        measure='L1',
        last=100000)
df = (pd.DataFrame(result['results'][0]['series'][0]['values'],
        columns=VARIABLES['L1'])
        .filter(items=['time', 'device', 'rain'])
        .fillna(0)
        .assign(
        time=lambda x: pd.to_datetime(x['time']))
      )

daily_rain = (df.set_index('time')
                .groupby([pd.TimeGrouper('D'), 'device'])
                .agg({'rain': 'sum'})
              )

# Fix name of file
df["day"] = df['time'].map(lambda x: x.day)
df["month"] = df['time'].map(lambda x: x.month)
df["year"] = df['time'].map(lambda x: x.year)
fname = "ZAMBIAPODS.%04d.%02d.%02d.csv" % \
        tuple(df[['year', 'month', 'day']].drop_duplicates().values[0])
print(fname)

# Put it in a new csv file!
daily_rain.to_csv(fname)
