#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Garmin compare
"""

from .readtcx import ReadTCX
from plotly.subplots import make_subplots
import plotly.graph_objects as go


class Compare():
    "Compare two or more Garmin activity files"

    def __init__(self, source_path):
        self.source_path = source_path
        self.read_tcx = ReadTCX(source_path)
        self.fields = ['heart_rate', 'cadence', 'watts', 'speed', 'time']
        self.colors = ['red', 'blue', 'green', 'purple',
                       'orange', 'yellow', 'teal', 'dimgrey']

    def run(self, option):
        "Generate the graphics for the comparison"
        garmin_data = self.read_tcx.parse()
        ref = 'distance'
        row_num = 1
        col_num = 1
        colors = {}
        figure = make_subplots(
            rows=len(self.fields),
            cols=1,
            vertical_spacing=0.05
        )
        for field in self.fields:
            for file, df in garmin_data.items():
                # the color
                show_legend = False
                if file not in colors:
                    colors[file] = self.colors.pop(0)
                    show_legend = True
                if option == 'histogram':
                    figure.add_trace(go.Histogram(
                        x=df[field],
                        legendgroup=f"{file}-groupe",
                        name=file,
                        showlegend=show_legend,
                        opacity=0.75
                    ), row=row_num, col=col_num)
                else:
                    # add trace
                    figure.add_trace(go.Scatter(
                        x=df[ref],
                        y=df[field],
                        mode='lines',
                        line=dict(color=colors[file]),
                        legendgroup=f"{file}-groupe",
                        name=file,
                        showlegend=show_legend
                    ), row=row_num, col=col_num)
                figure.update_xaxes(
                    title_text=ref,
                    row=row_num,
                    col=col_num
                )
                figure.update_yaxes(
                    title_text=field.replace('_', ' '),
                    row=row_num,
                    col=col_num
                )
            row_num += 1
        if option == 'histogram':
            figure.update_layout(
                title='Activities comparison',
                height=1920,
                width=1200,
                barmode='overlay'
            )
            figure.update_traces(opacity=0.75)
        else:
            figure.update_layout(
                title='Activities comparison',
                height=1920,
                width=1200
            )
        figure.show()
