import re
import json
import yaml
import urllib.request

import click

from blueprint_maker.logging import logger
from blueprint_maker import utils as bm_utils
from blueprint_maker.from_node_types.constants import (
    BLUEPRINT_YAML_TEMPLATE
)



@click.command(name='from-node-types',
               short_help='Create variants of a blueprint.')
@click.option('-b',
              '--blueprint',
              type=click.STRING,
              help='The path to the new blueprint file to create.')
@click.option('-n',
              '--node-type',
              type=click.STRING,
              multiple=True,
              help='A node type to use in the blueprint.')
def create_from_node_types(*args, **kwargs):
    node_types = bm_utils.get_kwarg(kwargs, 'node_type', [])
    blueprint = bm_utils.get_new_file(kwargs, 'blueprint')
    previous_node_name = None
    for item in node_types:
        node_type_def = get(item)['items'][0]
        previous_node_name = generate_node_template_from_type(
            previous_node_name, node_type_def)
    bm_utils.create_new_cloudify_yaml(BLUEPRINT_YAML_TEMPLATE, blueprint)
    logger.info('Wrote new blueprint to {}'.format(blueprint))


def generate_node_template_from_type(previous_node_name, node_type_def):
        plugin_import = 'plugin:{}'.format(node_type_def['plugin_name'])
        if plugin_import not in BLUEPRINT_YAML_TEMPLATE['imports']:
            BLUEPRINT_YAML_TEMPLATE['imports'].append(plugin_import)
        node_name = node_type_def['name'].lower()
        cnt = 1
        while node_name in BLUEPRINT_YAML_TEMPLATE['node_templates']:
            node_name = '{}{}'.format(node_name, cnt)
            cnt += 1
        node_template = {
            node_name: fill_node_template(
                node_name,
                node_type_def['type'],
                node_type_def.get('properties'),
            )
        }
        if previous_node_name:
            node_template[node_name]['relationships'] = [
                {
                    'type': 'cloudify.relationships.depends_on',
                    'target': previous_node_name
                }
            ]
        BLUEPRINT_YAML_TEMPLATE['node_templates'].update(node_template)
        return node_name


def fill_node_template(node_name, node_type, properties):
    node_template = {
        'type': node_type
    }
    node_template_properties = {}
    for k, v in properties.items():
        new_value = create_property_value(node_name, k, v)
        if new_value:
            node_template_properties[k] = new_value
    if node_template_properties:
        node_template['properties'] = node_template_properties
    return node_template


def create_property_value(parent, child, schema):
    default = schema.pop('default', None)
    required = schema.pop('required', True)
    description = schema.pop('description', None)
    if default:
        return default
    new_value = {}
    schema_type = schema.get('type')
    if schema_type in ['string', 'boolean']:
        return create_get_input(
            '{}{}'.format(
                capitalize_components(parent),
                capitalize_components(child),
            ),
            schema
        )
    for k, v in schema.items():
        new_value[k] = create_get_input(
            '{}{}{}'.format(
                capitalize_components(parent),
                capitalize_components(child),
                capitalize_components(k),
            ),
        v)
    return new_value


def create_get_input(name, prop=None):
    new_name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    cnt = 1
    while new_name in BLUEPRINT_YAML_TEMPLATE['inputs']:
        new_name = '{}{}'.format(new_name, cnt)
        cnt += 1
    BLUEPRINT_YAML_TEMPLATE['inputs'].update(
        {
            new_name: {
                'display_label': re.sub(r"(\w)([A-Z])", r"\1 \2", name),
                'type': 'string' if not prop else prop.get('type', 'string')
            }
        }
    )
    return '{{ get_input : {new_name} }}'.format(new_name=new_name)


def capitalize_components(name):
    new = ''
    for component in name.split('_'):
        new += component.capitalize()
    return new


def get(node_type):
    url = 'https://marketplace.cloudify.co/node-types?type={node_type}&size=1'
    req = urllib.request.Request(url=url.format(node_type=node_type), method='GET')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))
