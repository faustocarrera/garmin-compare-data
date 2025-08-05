#!/usr/bin/env python
"""
Garmin compare
"""

import click
from garmin.utils import get_path
from garmin.compare import Compare

@click.command()
@click.option('--option', '-o', 'option', is_flag=False, default='lines', help='lines or histogram')
def cli(option):
    "Run the comparison"
    compare = Compare(get_path(__file__, 'source'))
    compare.run(option)


if __name__ == '__main__':
    cli()
