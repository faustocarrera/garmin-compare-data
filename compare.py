#!/usr/bin/env python
"""
Garmin compare
"""

from os import path
from os import listdir
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime


class Compare():
    "Compare Garmin workouts"

    def __init__(self, folder):
        self.folder = folder

    def run(self):
        "Turn the lights on"
        files = self.__getfiles(self.folder)
        entries = {}
        for file in files:
            with open(path.join(self.folder, file), 'rb') as infile:
                entries[file] = {}
                entries[file]['points'] = {}
                soup = BeautifulSoup(infile.read(), 'lxml')
                activity = soup.trainingcenterdatabase.activities.activity
                # the date and time
                entries[file]['date'] = self.__get_datetime(activity.id.get_text())
                # trackpoints
                trackpoinst = activity.find_all('trackpoint')
                for trackpoint in trackpoinst:
                    time = self.__get_datetime(trackpoint.time.get_text())
                    distance = '{:.3f}'.format(float(trackpoint.distancemeters.get_text()))
                    heart_rate = int(trackpoint.heartratebpm.value.get_text())
                    cadence = int(trackpoint.cadence.get_text())
                    watts_node = trackpoint.extensions.find('ns3:tpx').find('ns3:watts')
                    if watts_node:
                        watts = int(watts_node.get_text())
                    else:
                        watts = 0
                    entries[file]['points'][time.strftime('%H:%M:%S')] = {
                        'distance': distance,
                        'heart_rate': heart_rate,
                        'cadence': cadence,
                        'watts': watts
                    }
        # make the calculations
        self.draw(entries)

    @staticmethod
    def draw(entries):
        "Draw comparative graphics"
        for file in entries:
            print(file)
            points = entries[file]
            date = points['date']
            for point in sorted(points['points']):
                data = points['points'][point]
                print(data['distance'], data['heart_rate'], data['cadence'], data['watts'])

    @staticmethod
    def __getfiles(folder):
        "List files in a directory"
        return [f for f in listdir(folder) if path.isfile(path.join(folder, f))]
    
    @staticmethod
    def __get_datetime(string):
        "Get datetime object from string"
        return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.000Z')

def run():
    compare = Compare(get_path('source'))
    compare.run()


def get_path(file_path):
    "Get full path"
    project_path = path.dirname(path.realpath(__file__))
    return path.realpath(path.join(project_path, file_path))


if __name__ == '__main__':
    run()
