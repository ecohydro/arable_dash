from connection import conn
import arrow
from utilities import get_time, fmt_time
from pandas import DataFrame
import json

time_attrs = ['last_deploy', 'last_post', 'last_seen']
del_keys = ['flags']


class Device(object):

    def __init__(
            self,
            device_dict=None,
            device_id=None,
            name=None
    ):
        self.frame = self.__class__.__name__
        # The easiest way to build a device is with
        # a device dictionary.
        if not device_dict:
            if not device_id and not name:
                raise NameError()
            else:
                print(device_dict)
                device_dict = self._get_device_dict(
                    device_id=device_id,
                    name=name)
        self._set_device_attr(device_dict)

    def _get_device_dict(self, device_id=None, name=None):
        k = conn.devices(
            device_id, name)
        return k

    def _set_device_attr(self, k):
        for key in k:
            if key in time_attrs:
                setattr(self, key, get_time(k[key]))
            else:
                setattr(self, key, k[key])

    def plot_data(self, variable, n=1000):
        # return a dataframe that has the last N values of
        # a variable.
        pass

    def get_data(self, var_list=None):
        # Use the query function to get a result.
        df = DataFrame([])
        # Load the df.
        # Parse the time to datetime.
        # Now...
        if var_list:
            pass
            # Filter by var_list
        return df

    def query(
            self,
            end=arrow.utcnow().datetime,
            start=arrow.utcnow().shift(days=-1).datetime,
            order="time",
            measure='L0',
            ):
        args = {}
        # args['start'] = fmt_time(start)
        # args['end'] = fmt_time(end)
        args['devices'] = [self.name]
        args['measure'] = measure
        args['order'] = order
        return conn.query(**args)
