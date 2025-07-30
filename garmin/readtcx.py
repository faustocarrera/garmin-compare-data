#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Garmin read TCX files
"""

from os import path
from datetime import datetime
import warnings
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import pandas as pd
from .utils import get_files


class ReadTCX():
    "Read and parse Garmin TCX files"

    def __init__(self, source_path):
        self.source_path = source_path

    def parse(self):
        "Parse the TCX file"
        files = self.__get_files(self.source_path)
        activities = {}
        for file in files:
            with open(path.join(self.source_path, file), 'rb') as infile:
                warnings.filterwarnings(
                    'ignore', category=XMLParsedAsHTMLWarning)
                soup = BeautifulSoup(infile.read(), features='lxml')
                activity = soup.trainingcenterdatabase.activities.activity
                # create a dataframe for the activity
                df = pd.DataFrame(columns=[
                    'time',
                    'distance',
                    'heart_rate',
                    'cadence',
                    'watts',
                    'speed'
                ])
                # trackpoints
                start_time = None
                trackpoints = activity.find_all('trackpoint')
                for trackpoint in trackpoints:
                    data = [
                        self.__get_act_time(
                            start_time, trackpoint.time.get_text()
                        ),
                        self.__get_distance(trackpoint),
                        self.__get_heart_rate(trackpoint),
                        self.__get_cadence(trackpoint),
                        self.__get_watts(trackpoint),
                        self.__get_speed(trackpoint)
                    ]
                    df.loc[len(df)] = data
                    # start time
                    if start_time is None:
                        start_time = trackpoint.time.get_text()
                activities[file] = df
        return activities

    @staticmethod
    def __get_files(folder):
        files = []
        files_list = get_files(folder)
        for file in files_list:
            if file.endswith('.tcx'):
                files.append(file)
        return files

    @staticmethod
    def __get_act_time(time_start, time_end):
        "Get datetime object from string"
        if time_start is None:
            return 0
        # calculate delta
        time_format = '%Y-%m-%dT%H:%M:%S.000Z'
        start = datetime.strptime(time_start, time_format)
        end = datetime.strptime(time_end, time_format)
        delta = end - start
        minutes, seconds = divmod(delta.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def __get_distance(trackpoint):
        "Get distance"
        distance = float(trackpoint.distancemeters.get_text()) / 1000
        return f'{distance:.1f}k'

    @staticmethod
    def __get_heart_rate(trackpoint):
        "Get heart rate"
        if trackpoint.heartratebpm:
            return int(trackpoint.heartratebpm.value.get_text())
        return 0

    @staticmethod
    def __get_cadence(trackpoint):
        "Get cadence"
        if trackpoint.cadence:
            return int(trackpoint.cadence.get_text())
        return 0

    @staticmethod
    def __get_watts(trackpoint):
        "Get watts"
        watts_node = trackpoint.extensions.find('ns3:tpx').find('ns3:watts')
        if watts_node:
            return int(watts_node.get_text())
        return 0

    @staticmethod
    def __get_speed(trackpoint):
        "Get speed"
        speed_node = trackpoint.extensions.find('ns3:tpx').find('ns3:speed')
        if speed_node:
            return float(speed_node.get_text()) * 3.6
        return 0
