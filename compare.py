#!/usr/bin/env python
"""
Garmin compare
"""

from os import path
from os import listdir
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
from plotly.subplots import make_subplots
import plotly.graph_objects as go


class Compare():
    "Compare Garmin workouts"

    def __init__(self, source):
        self.folder = source
        self.fields = ['heart_rate', 'cadence', 'watts', 'speed']
        self.colors = ['red', 'blue', 'green', 'purple', 'orange', 'yellow', 'teal', 'dimgrey']

    def run(self):
        data = self.__get_data()
        self.__generate_graphics(data)

    def __get_data(self):
        files = self.__get_files(self.folder)
        activities = {
            'files': [],
            'time': {},
            'distance': {},
            'heart_rate': {},
            'cadence': {},
            'watts': {},
            'speed': {}
        }
        for file in files:
            with open(path.join(self.folder, file), 'rb') as infile:
                soup = BeautifulSoup(infile.read(), 'lxml')
                activity = soup.trainingcenterdatabase.activities.activity
                # the date and time
                # file = self.__get_datetime(activity.id.get_text())
                activities['files'].append(file)
                activities['time'][file] = []
                activities['distance'][file] = []
                activities['heart_rate'][file] = []
                activities['cadence'][file] = []
                activities['watts'][file] = []
                activities['speed'][file] = []
                # trackpoints
                start_time = None
                trackpoints = activity.find_all('trackpoint')
                for trackpoint in trackpoints:
                    # calculate the time
                    activities['time'][file].append(
                        self.__get_activity_time(
                            start_time,
                            trackpoint.time.get_text()
                        )
                    )
                    # start time
                    if start_time is None:
                        start_time = trackpoint.time.get_text()
                     # add data
                    activities['distance'][file].append(
                        self.__get_distance(trackpoint)
                    )
                    activities['heart_rate'][file].append(
                        self.__get_heart_rate(trackpoint)
                    )
                    activities['cadence'][file].append(
                        self.__get_cadence(trackpoint)
                    )
                    activities['watts'][file].append(
                        self.__get_watts(trackpoint)
                    )
                    activities['speed'][file].append(
                        self.__get_speed(trackpoint)
                    )
        return activities

    def __generate_graphics(self, data):
        "Generate the graphics"
        figure = make_subplots(
            rows=len(self.fields),
            cols=1,
            vertical_spacing=0.05
        )
        row_num = 1
        colors = {}
        for field in self.fields:
            for file in sorted(data['files']):
                # the color
                show_legend = False
                if file not in colors:
                    colors[file] = self.colors.pop(0)
                    show_legend = True
                # add trace
                figure.add_trace(go.Scatter(
                    x=data['distance'][file],
                    y=data[field][file],
                    mode='lines',
                    line=dict(color=colors[file]),
                    legendgroup='{0}-groupe'.format(file),
                    name=file,
                    showlegend = show_legend
                ), row=row_num, col=1)
                figure.update_xaxes(title_text='distance', row=row_num, col=1)
                figure.update_yaxes(title_text=field.replace('_', ' '), row=row_num, col=1)
            row_num += 1
        figure.update_layout(
            title='Activities comparison',
            height=1920,
            width=1200
        )
        figure.show()
        
    def __old(self, title, dates, distance, chart):
        "Generate the graphics"
        figure = go.Figure()
        for date_time in sorted(dates):
            # distance
            figure.add_trace(go.Scatter(
                x=distance[date_time],
                y=chart[date_time],
                mode='lines',
                name=date_time
            ))
        figure.update_layout(
            title='{0} comparison'.format(title),
            xaxis_title='Distance',
            yaxis_title=title
        )
        figure.show()

    @staticmethod
    def __get_files(folder):
        "List files in a directory"
        return [f for f in listdir(folder) if path.isfile(path.join(folder, f))]

    @staticmethod
    def __get_datetime(string):
        "Get datetime object from string"
        date_time = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.000Z')
        return date_time.strftime('%Y-%m-%d')

    @staticmethod
    def __get_activity_time(time_start, time_end):
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
        return '{0:02d}:{1:02d}'.format(minutes, seconds)

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
    def __get_speed(trackpoint):
        "Get speed"
        speed_node = trackpoint.extensions.find('ns3:tpx').find('ns3:speed')
        if speed_node:
            return float(speed_node.get_text()) * 3.6
        return 0


def run():
    "Run the comparison"
    compare = Compare(get_path('source'))
    compare.run()

def get_path(file_path):
    "Get full path"
    project_path = path.dirname(path.realpath(__file__))
    return path.realpath(path.join(project_path, file_path))


if __name__ == '__main__':
    run()
