import unittest
import pandas as pd

from theft_analysis import analyze_bike_status

GLOBAL_DATA = {"tripduration":16930,
        "starttime":1465847845,
        "stoptime":1465864775,
        "start_station_id":259,
        "start_station_name":"South St & Whitehall St",
        "start_station_latitude":40.70122128,
        "start_station_longitude":-74.01234218,
        "end_station_id":3240,
        "end_station_name":"NYCBS Depot BAL - DYR",
        "end_station_latitude":0.0,
        "end_station_longitude":0.0,
        "bikeid":14826,
        "usertype":"Subscriber",
        "birth_year":"unknown",
        "gender":"unknown",
        "customer_plan":""
        }


class TestTheftAnalysis(unittest.TestCase):
    def test_dict_analysis(self):
        dict_result = analyze_bike_status(GLOBAL_DATA)

        self.assertEqual(len(dict_result), 7)

    def test_series_analysis(self):
        local_series = pd.Series(GLOBAL_DATA)
        pd_result = analyze_bike_status(local_series)

        self.assertEqual(len(pd_result), 7)

    def test_user_type(self):
        local_data = GLOBAL_DATA
        local_data['usertype'] = 'Annual'
        nu_result = analyze_bike_status(local_data)

        self.assertEqual(len(nu_result), 0)

if __name__ == '__main__':
    unittest.main()