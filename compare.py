#!/usr/bin/env python
"""
Garmin compare
"""

from os import path
from os import listdir
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import click


class Compare():
    "Compare Garmin workouts"

    def __init__(self, folder):
        self.folder = folder
        self.figure = go.Figure()

    def run(self, chart):
        "Turn the lights on"
        files = self.__get_files(self.folder)
        activities = {
            'dates': [],
            'time': {},
            'distance': {},
            'heart_rate': {},
            'cadence': {},
            'watts': {}
        }
        for file in files:
            with open(path.join(self.folder, file), 'rb') as infile:
                soup = BeautifulSoup(infile.read(), 'lxml')
                activity = soup.trainingcenterdatabase.activities.activity
                # the id, date and time
                date_time = self.__get_datetime(activity.id.get_text())
                activities['dates'].append(date_time)
                activities['distance'][date_time] = []
                activities['heart_rate'][date_time] = []
                activities['cadence'][date_time] = []
                activities['watts'][date_time] = []
                # trackpoints
                counter = 0
                trackpoints = activity.find_all('trackpoint')
                for trackpoint in trackpoints:
                    # add data
                    activities['distance'][date_time].append(
                        self.__get_distance(trackpoint)
                    )
                    activities['heart_rate'][date_time].append(
                        self.__get_heart_rate(trackpoint)
                    )
                    activities['cadence'][date_time].append(
                        self.__get_cadence(trackpoint)
                    )
                    activities['watts'][date_time].append(
                        self.__get_watts(trackpoint)
                    )
                    counter += 1
        # make the calculations
        self.__draw_heart_rate(activities, chart)

    def __draw_heart_rate(self, activities, chart):
        "Draw comparative graphics"
        for date_time in sorted(activities['dates']):
            # distance
            self.figure.add_trace(go.Scatter(
                x=activities['distance'][date_time],
                y=activities[chart][date_time],
                mode='lines',
                name=('{0} {1}'.format(chart, date_time)).replace('_', ' ').capitalize()
            ))
        self.figure.update_layout(
            title=chart.replace('_', ' ').capitalize() + ' comparison',
            xaxis_title='Distance',
            yaxis_title=chart.replace('_', ' ').capitalize()
        )
        self.figure.show()

    @staticmethod
    def __get_distance(trackpoint):
        "Get distance"
        return '{:.3f}'.format(float(trackpoint.distancemeters.get_text()))

    @staticmethod
    def __get_heart_rate(trackpoint):
        "Get heart rate"
        return int(trackpoint.heartratebpm.value.get_text())

    @staticmethod
    def __get_cadence(trackpoint):
        "Get cadence"
        return int(trackpoint.cadence.get_text())

    @staticmethod
    def __get_watts(trackpoint):
        "Get watts"
        watts_node = trackpoint.extensions.find('ns3:tpx').find('ns3:watts')
        if watts_node:
            return int(watts_node.get_text())
        return 0

    @staticmethod
    def __get_files(folder):
        "List files in a directory"
        return [f for f in listdir(folder) if path.isfile(path.join(folder, f))]

    @staticmethod
    def __get_datetime(string):
        "Get datetime object from string"
        date_time = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.000Z')
        return date_time.strftime('%Y-%m-%d')


@click.command()
@click.option(
    '--chart',
    '-c',
    type=click.Choice(['heart_rate', 'cadence', 'watts'], case_sensitive=True),
    default='heart_rate',
    help='Chart to export'
)
def run(chart):
    "Run the comparison"
    compare = Compare(get_path('source'))
    compare.run(chart)


def get_path(file_path):
    "Get full path"
    project_path = path.dirname(path.realpath(__file__))
    return path.realpath(path.join(project_path, file_path))


if __name__ == '__main__':
    run()
