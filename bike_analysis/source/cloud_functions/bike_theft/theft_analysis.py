import os
import pymsteams

from typing import Dict
from google.cloud import bigquery


def analyze_bike_status(row_analysis:Dict, sus_lim:int = 7200, cus_lim:int = 5400)-> Dict[str, int]:
    """Takes in Series and then returns a boolean flag to send out messaging
        to warn Citibike Workers that stations need to be addressed.

    Args:
        row_analysis: Series of CitiBike stations ride table setup to track
            cumulative rides occurring at Stations in CitiBike network.
        sus_lim: Subscriber time limit.
        cus_lim: Customer time limit.

    Returns:
        data_pack: Dictionary containing messaging and data for insert into theft/ stolen table.
    """
    data_pack = {'start_station_name': '',
                 'start_station_id': '',
                 'end_station_name': '',
                 'end_station_id': '',
                 'usertype': '',
                 'bikeid': '',
                 'tripduration': ''
                 }

    if row_analysis['usertype'] == 'Customer' and row_analysis['tripduration'] >= cus_lim:
        for column, value in row_analysis.items():
            if column in data_pack.keys():
                data_pack[column] = value

    elif row_analysis['usertype'] == 'Subscriber' and row_analysis['tripduration'] >= sus_lim:
        for column, value in row_analysis.items():
            if column in data_pack.keys():
                data_pack[column] = value
    else:
        data_pack = {}

    return data_pack


def bq_insert_bike_theft(data_pack:Dict) -> None:
    """Inserts theft bike data into theft stolen bikes table.

    Args:
        Dictionary containing messaging and data for insert into theft/ stolen table
    """
    table_id = f"bigquery-public-data.new_york_citibike.theft_stolen_bikes"

    client = bigquery.Client()
    client.insert_rows_json(table_id, data_pack)


def alerting_bike_theft(data_pack:Dict) -> None:
    myTeamsMessage = pymsteams.connectorcard(os.get('msteams-webhook'))
    fill_message = {0:'full', 1:'empty'}
    myTeamsMessage.text(f"WARNING: {data_pack['start_station_name']} is {fill_message[data_pack['inventory_status']]} at {data_pack['starttime']}.")
    myTeamsMessage.send()


def run_main(trip_entry:Dict) -> None:
    data_pack = analyze_bike_status(trip_entry, sus_lim=7200, cus_lim=5400)

    if bool(data_pack):
        bq_insert_bike_theft(data_pack)
