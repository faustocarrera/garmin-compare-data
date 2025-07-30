#!/usr/bin/env python
"""
Garmin compare
"""



from datetime import datetime
import warnings
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
from plotly.subplots import make_subplots
import plotly.graph_objects as go


class Compare():
    "Compare Garmin workouts"

    def __init__(self, source):
        self.folder = source
        self.fields = ['heart_rate', 'cadence', 'watts', 'speed', 'time']
        self.colors = ['red', 'blue', 'green', 'purple',
                       'orange', 'yellow', 'teal', 'dimgrey']

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
                warnings.filterwarnings(
                    'ignore', category=XMLParsedAsHTMLWarning)
                soup = BeautifulSoup(infile.read(), features='lxml')
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
        ref = 'distance'
        row_num = 1
        col_num = 1
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
                    x=data[ref][file],
                    y=data[field][file],
                    mode='lines',
                    line=dict(color=colors[file]),
                    legendgroup='{0}-groupe'.format(file),
                    name=file,
                    showlegend=show_legend
                ), row=row_num, col=col_num)
                figure.update_xaxes(title_text=ref, row=row_num, col=col_num)
                figure.update_yaxes(title_text=field.replace(
                    '_', ' '), row=row_num, col=col_num)
            row_num += 1
        figure.update_layout(
            title='Activities comparison',
            height=1920,
            width=1200
        )
        figure.show()

    @staticmethod
    def __get_files(folder):
        "List files in a directory"
        return [f for f in listdir(folder) if path.isfile(path.join(folder, f))]

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
        return '{0:02d}:{1:02d}:{2:02d}'.format(hours, minutes, seconds)

    @staticmethod
    def __get_distance(trackpoint):
        "Get distance"
        distance = float(trackpoint.distancemeters.get_text()) / 1000
        return '{:.1f}k'.format(distance)

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