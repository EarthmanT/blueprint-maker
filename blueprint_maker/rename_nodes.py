import os
import re
import sys
from pathlib import Path

import click

from blueprint_maker.logging import logger

@click.command(name='rename-nodes',
               short_help='Rename node templates from a blueprint.')
@click.option('-b',
              '--blueprint',
              type=click.STRING,
              help='The path to blueprint YAML file.')
def rename_nodes(*args, **kwargs):
