from connection import conn
from pandas import DataFrame
from Device import Device
import arrow


class Organization(object):

    def __init__(self):
        self.Devices = []

        # Drop flag columns for now.
        device_list = conn.devices()
        for device in device_list:
            self.Devices.append(Device(device_dict=device))
        self.devices_df = DataFrame(device_list).drop(['flags'], axis=1)
        # Strip location info out and make the location column format ok
        self.devices_df['location'] = [
            c.get('name', 'None') for c in self.devices_df.location
        ]
        # use arrow to make last seen times human readable:
        self.devices_df['last_seen'] = self.devices_df['last_seen'].apply(
            lambda x: arrow.get(x).humanize())
        self.devices_df['last_deploy'] = self.devices_df['last_deploy'].apply(
            lambda x: arrow.get(x).humanize())
        self.devices_df['last_post'] = self.devices_df['last_post'].apply(
            lambda x: arrow.get(x).humanize())
        self.device_dict = self.devices_df.to_dict()
        self.device_ids = [x for x in self.device_dict['id'].values()]

    def device(self, name):
        return self.Devices[
            [i for i, x in enumerate(self.Devices) if x.name == name][0]
        ]
