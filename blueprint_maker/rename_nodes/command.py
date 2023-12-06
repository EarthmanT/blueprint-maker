import sys
import json

import click
from wonderwords import RandomWord

from blueprint_maker.logging import logger
from blueprint_maker import utils as bm_utils
from blueprint_maker.from_node_types.constants import (
    GET_PROPERTY,
    GET_ATTRIBUTE, # TODO: Figure out why this isn't working.
    INSTRINSIC_FUNCTIONS,
)

NODE_TEMPLATE_FNS = [GET_PROPERTY, GET_ATTRIBUTE]
RANDOMWORDS = RandomWord()


@click.command(name='rename-nodes',
               short_help='Create a new blueprint by renaming the nodes in another blueprint.')
@click.option('-b',
              '--blueprint',
              type=click.STRING,
              help='The path to blueprint YAML file.')
def create_by_renaming_nodes(*args, **kwargs):
    # +1 because we are skipping the first which is a duplicate.
    blueprint = bm_utils.get_existing_file(kwargs, 'blueprint')
    blueprint_content = bm_utils.get_file_content(blueprint)
    blueprint_yaml = bm_utils.get_yaml(blueprint)
    for node_name in get_sorted_node_template_names(blueprint_yaml):
        new_node_name = RANDOMWORDS.word()
        blueprint_content = recurse_data(
            blueprint_yaml,
            node_name,
            new_node_name)
        node_template = blueprint_yaml['node_templates'].pop(node_name)
        blueprint_yaml['node_templates'][new_node_name] = node_template
    new_blueprint_file = blueprint.as_posix().replace(
        '.yaml',
        '-{}.yaml'.format(RANDOMWORDS.word()))
    bm_utils.put_file_content(new_blueprint_file, '')
    blueprint_content = bm_utils.create_new_cloudify_yaml(
        blueprint_yaml, new_blueprint_file)
    logger.info('Wrote new blueprint to {}'.format(new_blueprint_file))


def get_sorted_node_template_names(blueprint_yaml):
    node_templates = blueprint_yaml.get('node_templates', {})
    return sorted(node_templates.keys())

def recurse_data(data, old, new):
    if isinstance(data, str):
            try:
                data = json.loads(data.replace("'", '"'))
            except json.JSONDecodeError:
                pass
            else:
                if GET_ATTRIBUTE in data or GET_PROPERTY in data:
                    data = recurse_data(data, old, new)
    if isinstance(data, list):
        for n in range(0, len(data)):
            data[n] = recurse_data(data[n], old, new)
    elif isinstance(data, dict):
        for k, v in list(data.items()):
            if k in INSTRINSIC_FUNCTIONS:
                if k in NODE_TEMPLATE_FNS:
                    if not isinstance(v, list) or len(v) < 2:
                        logger.error(
                            'The fn {} is followed by {}, '
                            'which is not a valid arg.'.format(k, v))
                        sys.exit(1)
                    elif v[0] == old:
                        v[0] = new
                        data[k] = v
                data = str(data)
            elif k == 'relationships' and isinstance(v, list):
                for n in range(0, len(v)):
                    if v[n]['target'] == old:
                        v[n]['target'] = new
                data[k] = recurse_data(v, old, new)
            else:
                data[k] = recurse_data(v, old, new)
    return data
