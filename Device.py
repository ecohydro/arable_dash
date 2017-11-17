from connection import conn
import arrow
from utilities import get_time, fmt_time
from pandas import DataFrame
from pandas.compat import StringIO
import pandas as pd

time_attrs = ['last_deploy', 'last_post', 'last_seen']
del_keys = ['flags']

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


class Device(object):

    def __init__(
            self,
            device_dict=None,
            device_id=None,  # (e.g. '58dd4a9eb4e1e85e885103ac')
            name=None  # (e.g. 'A000360')
    ):
        self.frame = self.__class__.__name__
        # The easiest way to initialize a new device is with
        # a device dictionary passed as an argument.
        # That is how the Organization object initializes objects.
        if not device_dict:
            # If there is no device_dict passed, then use either
            # the device_id argument (e.g. '58dd4a9eb4e1e85e885103ac')
            # or the name argument (e.g. 'A000360').
            if not device_id and not name:
                raise NameError()
            else:
                # _get_device_dict will extract the device_dict:
                device_dict = self._get_device_dict(
                    device_id=device_id,
                    name=name)
        # Set the properties of this device.
        self._set_device_attr(device_dict)
        self.variables = VARIABLES

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

    def _get_device_variables(self, measure='L1'):
        result = self.query(measure=measure)
        return result['results'][0]['series'][0]['columns']

    def get_data(self, var_list=[], measure='L1', output_fmt='csv', **kwargs):
        """Returns a dataframe of Mark data.
            :param var_list: optional; list of variables to include
            :param measure: optional; "L1" (default) or "L0".
        """
        # Use the query function to get a result.
        result = self.query(measure=measure, **kwargs)
        # Prepend time to the var_list (all dataframes return "time")
        var_list.insert(0, 'time')
        if output_fmt is 'json':
            try:
                data = result['results'][0]['series'][0]['values']
                df = DataFrame(data, columns=self.variables[measure])
                # If no list is passed, only "time" is in var_list:
                if len(var_list) > 1:
                    # Filter to include only items in the var_list
                    df = (df.filter(items=var_list)
                            .assign(
                                time=lambda x: pd.to_datetime(x['time']))
                            .set_index('time')
                            .dropna()
                          )
                    # Convert datetimes to Plotly timestamp format for plotting
                    # df['time'] = [x.strftime("%Y-%m-%d %H:%M:%S.%f") for x in df['time']]  # NOQA
                return df
            except KeyError:
                return DataFrame([], columns=var_list)
        elif output_fmt is 'csv':
                try:
                    df = pd.read_csv(StringIO(result))
                    df = (df.filter(items=var_list)
                            .assign(
                                time=lambda x: pd.to_datetime(x['time']))
                            .set_index('time')
                            .dropna()
                          )
                    return df
                except KeyError:
                    return DataFrame([], columns=var_list)

    def query(
            self,
            end=arrow.utcnow().datetime,
            start=arrow.utcnow().shift(days=-1).datetime,
            order="time",
            measure='L1',
            output_format='csv',   # Added to deal with error in Arable client.
            limit=1000
            ):
        """Query API for this device.
            :param end: optional; default is now (datetime obj in UTC)
            :param start: optional; default is 1 day before now
            (datetime obj in UTC)
            :param order: optional; "time" (time ascending) or "-time" (time
            descending)
            :param measure: optional; "L1" (default) or "L0".
            :param output_format: optional; "csv" (default)
            :param limit: optional; default is 1000
        """
        args = {}
        args['start'] = fmt_time(start)
        args['end'] = fmt_time(end)
        args['devices'] = [self.name]
        args['measure'] = measure
        args['order'] = order
        args['limit'] = limit
        args['format'] = output_format
        return conn.query(**args)
