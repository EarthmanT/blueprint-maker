import os
import re
import sys
import yaml
from pathlib import Path

from blueprint_maker.logging import logger
from blueprint_maker.from_node_types.constants import (
    INSTRINSIC_FUNCTIONS
)


def split_lines(string):
  return re.split(r'\r?\n', string)


class CloudifySafeDumper(yaml.SafeDumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(CloudifySafeDumper, self).increase_indent(flow, False)

    def ignore_aliases(self, data):
        return True


def represent_intrinsic_functions(dumper, data):
    for fn in INSTRINSIC_FUNCTIONS:
        if fn in data:
            return dumper.org_represent_str(
                '{{ {fn}: {val} }}'.format(fn=fn, val=data[fn]))
    return dumper.represent_dict(data)


def repr_str(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar(
            u'tag:yaml.org,2002:str', data, style='>')
    return dumper.org_represent_str(data)

yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str
yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)
yaml.add_representer(
    dict, represent_intrinsic_functions, Dumper=yaml.SafeDumper)


def get_kwarg(kwargs, name, default=None):
    return kwargs.get(name, default)


def get_existing_file(kwargs, name, default=None):
    existing_file = kwargs.get(name, default)
    if existing_file:
        existing_file = Path(existing_file).resolve()
    if not existing_file or not os.path.exists(existing_file):
        logger.error(
            'File path is invalid or the file does not exist: {}'.format(
                existing_file))
        sys.exit(1)
    return existing_file


def get_new_file(kwargs, name, default=None):
    new_file = kwargs.get(name, default)
    if new_file:
        new_file = Path(new_file).resolve()
    else:
        logger.error('A new file path must be provided.')
        sys.exit(1)
    if os.path.exists(new_file):
        logger.error('Blueprint path already exists: {}'.format(
            new_file))
        sys.exit(1)
    return new_file


def remove_anchors(blueprint):
    python_dict = get_yaml(blueprint)
    create_new_cloudify_yaml(python_dict, blueprint)


def create_new_cloudify_yaml(python_dict, blueprint):
    yaml_obj = yaml.dump(
        python_dict,
        Dumper=CloudifySafeDumper,
        default_flow_style=False,
        sort_keys=False,
        width=float('inf')
    )
    lines = yaml_obj.split('\n')
    for line_no in range(0, len(lines)):
        for fn in INSTRINSIC_FUNCTIONS:
            if fn in lines[line_no]:
                lines[line_no] = lines[line_no].replace("'", '')
                break
    new_yaml = ''
    for line in lines:
        if line in ['imports:', 'inputs:', 'node_templates:']:
            new_yaml += '\n'
            new_yaml += '{}\n'.format(line)
            new_yaml += '\n'
        elif re.match(r'^[\s]{2}[a-zA-Z]', line):
            new_yaml += '\n'
            new_yaml += '{}\n'.format(line)
        else:
            new_yaml += '{}\n'.format(line)

    with open(blueprint, 'w') as outfile:
        outfile.write(new_yaml)


def get_yaml(filepath):
    with open(filepath, 'r') as stream:
        yaml_data = yaml.safe_load(stream)
        return yaml_data


def get_file_content(filepath):
    with open(filepath, 'r') as infile:
        return infile.read()


def put_file_content(filepath, content):
    with open(filepath, 'w') as outfile:
        outfile.write(content)

