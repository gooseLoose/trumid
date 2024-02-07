import unittest
import pandas as pd

from inventory_notification import analyze_station_inv


class TestInventoryAnalysis(unittest.TestCase):
    def test_open_inventory(self):
        data = {'start_station_name': "South St & Whitehall St",
               'start_station_id': 259,
               'starttime': 1465847845,
               'inventory_count': 10
               }
        dict_result = analyze_station_inv(data, data['start_station_id'])

        self.assertEqual(len(dict_result), 0)

    def test_full_inventory(self):
        data = {'start_station_name': "South St & Whitehall St",
               'start_station_id': 259,
               'starttime': 1465847845,
               'inventory_count': 30
               }
        dict_result = analyze_station_inv(data, data['start_station_id'])

        self.assertEqual(len(dict_result), 5)
        self.assertEqual(dict_result['inventory_status'], 0)

    def test_empty_inventory(self):
        data = {'start_station_name': "South St & Whitehall St",
               'start_station_id': 259,
               'starttime': 1465847845,
               'inventory_count': 1
               }
        dict_result = analyze_station_inv(data, data['start_station_id'])

        self.assertEqual(len(dict_result), 5)
        self.assertEqual(dict_result['inventory_status'], 1)

if __name__ == '__main__':
    unittest.main()