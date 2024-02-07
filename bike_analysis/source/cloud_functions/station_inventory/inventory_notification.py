import os
import pymsteams

from typing import Dict
from google.cloud import bigquery


def analyze_station_inv(row_analysis:Dict, out_inv:int=0 , over_inv:int=30):
    """Takes in Series and then returns a boolean flag to send out messaging
        to warn Citibike Workers that stations need to be addressed.

    Args:
        row_analysis: Series of CitiBike stations ride table setup to track
            cumulative rides occurring at Stations in CitiBike network.
        out_inv: Inventory indicator of station reaching empty.
        over_inv: Inventory indicator of station reaching overfilled.

    Returns:
        notification: message
    """
    data_pack = {'start_station_name': '',
                 'start_station_id': '',
                 'starttime': '',
                 'inventory_status': '',
                 'inventory_count': ''
                 }

    if row_analysis['inventory_count'] == out_inv:
        for column, value in row_analysis.items():
            if column in data_pack.keys():
                data_pack[column] = value
        data_pack['inventory_status'] = 1

    elif row_analysis['inventory_count'] == over_inv:
        for column, value in row_analysis.items():
            if column in data_pack.keys():
                data_pack[column] = value
        data_pack['inventory_status'] = 0

    else:
        data_pack = {}

    return data_pack


def bq_insert_station_inv(data_pack:Dict) -> None:
    """Inserts station fill data into table tracking times when stations have
        either been filled or emptied. 

    Args:
        Dictionary containing messaging and data for insert into theft/ stolen table
    """
    table_id = f"bigquery-public-data.new_york_citibike.station_fill_monitoring"

    client = bigquery.Client()
    client.insert_rows_json(table_id, data_pack)


def alerting_inventory_fill(data_pack:Dict) -> None:
    myTeamsMessage = pymsteams.connectorcard(os.get('msteams-webhook'))
    fill_message = {0:'full', 1:'empty'}
    myTeamsMessage.text(f"WARNING: {data_pack['start_station_name']} is {fill_message[data_pack['inventory_status']]} at {data_pack['starttime']}.")
    myTeamsMessage.send()


def run_main(trip_entry:Dict) -> None:

    data_pack = analyze_station_inv(trip_entry, out_inv=1 , over_inv=30)

    if bool(data_pack):
        bq_insert_station_inv(data_pack)
        alerting_inventory_fill(data_pack)