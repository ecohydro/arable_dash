from arable.client import ArableClient

a = ArableClient()
a.connect('nkrell@ucsb.edu', 'map2528', 'ucsb')

from datetime import datetime, timedelta
from pandas import DataFrame
import pandas as pd
from io import StringIO

def write_csv(f, data):
    with open(f, 'ab') as csvfile:
        csvfile.write(data)
        csvfile.close()

# download new pod data
result = a.query(format='csv', devices=['A000472'], measure='L0')
write_csv('zm_472.csv', result)

# batch download old pod data
starttime_str = raw_input("enter time:")  #example 2016:10:18:00:00:00
arr = starttime_str.split(':')
starttime = datetime(int(arr[0]), int(arr[1]),int(arr[2]),int(arr[3]),int(arr[4]),int(arr[5]))

for i in range(30): #range input is 12 hrs * No.days; e.g. 84 = 1 week of data
    tmp_end_time = starttime + timedelta(hours=2)
    print(starttime, tmp_end_time)
    startdate_fmt = starttime.strftime("%Y-%m-%dT%H:%M:%SZ")
    enddate_fmt = tmp_end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    result = a.query(format='csv',
                     devices=[ # '1d28d33a-c923-4965-a7bb-5881d222c9a8', #b23
                               # '54322099-e76d-4636-afd2-0861e2113a16', #b24
                               # 'ec3a9f9d-264d-442d-bea8-c17c361366e9', #b11
                               # 'ccb7247d-4e2e-443d-b783-e516d03a358c', #b39
                               # 'ca2d8769-ccf5-47d5-8aed-741ca6ae94cd', #b01
                               # '12173122-6d64-4804-966a-374326fdaf3d', #b13
                               # '50ba7a2e-a1aa-4033-86a7-0700605dc702', #b28
                               # 'cee6972b-135f-45b0-be4b-7c23002676ba', #b32
                               # 'e78581f0-2693-47ad-9899-0048450ccaa7', #b34
                               # 'a993a1cd-9fe9-4932-870d-29c6b5df1214', #b30
                               # '9b849362-b06d-4317-96f5-f266c1ada8d6', #b21
                               # 'a044ad4f-fd7c-4aa4-bffc-9158ccbad3a1',#b27
                                'a1309866-13f8-4dbe-b661-8c9f787ac745'], #b13
                    order="time",
                    start=startdate_fmt, #first rain occured...?
                    end=enddate_fmt,
                    measure='L0')
    starttime = tmp_end_time
    write_csv('zm_pds_b16.csv', result)
