import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxManager:
    def __init__(self, url, token, org, bucket):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket

    def get_high_freq_data(self,mac_address, range_str="-1h", measurement="mqtt_msg_log"):
        """
        Fetches raw data. 
        Note: For very long periods, consider adding an aggregateWindow 
        here to prevent the UI from crashing.
        """
        client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        query_api = client.query_api()

        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {range_str})
          |> filter(fn: (r) => r["_measurement"] == "{measurement}")
          |> filter(fn: (r) => r["_field"] == "red" or r["_field"] == "green" or r["_field"] == "yellow" or r["_field"] == "count")
          |> filter(fn: (r) => r["mac"] == "{mac_address}")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> drop(columns: ["_start", "_stop", "_measurement","result", "table"])
          |> timeShift(duration: 8h)
        '''
        
        # Keep columns above should match your actual field names
        df = query_api.query_data_frame(query)
        client.close()
        
        if isinstance(df, list): # Handle multiple tables if returned
            df = pd.concat(df)
            
        return df