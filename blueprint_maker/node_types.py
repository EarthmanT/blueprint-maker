import os
import re
import sys
import json
import yaml
import urllib.request
from pathlib import Path

import click
from blueprint_maker.logging import logger



BLUEPRINT_YAML_TEMPLATE = {
    'tosca_definitions_version': 'cloudify_dsl_1_5',
    'imports': [
        'cloudify/types/types.yaml',
    ],
    'inputs': {},
    'node_templates': {}
}

CONCAT = 'concat'
GET_SYS = 'get_sys'
GET_INPUT = 'get_input'
GET_SECRET = 'get_secret'
GET_PROPERTY = 'get_property'
GET_ATTRIBUTE = 'get_attribute'
GET_CAPABILITY = 'get_capability'
GET_ENVIRONMENT_CAPABILITY = 'get_environment_capability'
INSTRINSIC_FUNCTIONS = [
    CONCAT,
    GET_SYS,
    GET_INPUT,
    GET_SECRET,
    GET_PROPERTY,
    GET_ATTRIBUTE,
    GET_CAPABILITY,
    GET_ENVIRONMENT_CAPABILITY
]

class CloudifySafeDumper(yaml.SafeDumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(CloudifySafeDumper, self).increase_indent(flow, False)


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
def create_with_node_types(*args, **kwargs):
    blueprint = kwargs.get('blueprint')
    # +1 because we are skipping the first which is a duplicate.
    node_types = kwargs.get('node_type', [])
    if blueprint:
        blueprint = Path(blueprint).resolve()
    else:
        logger.error('A blueprint must be provided.')
        sys.exit(1)
    if os.path.exists(blueprint):
        logger.error('Blueprint path already exists: {}'.format(blueprint))
        sys.exit(1)

    previous_node_name = None
    for item in node_types:
        node_type_def = get(item)['items'][0]
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
        previous_node_name = node_name
    yaml_obj = yaml.dump(
        BLUEPRINT_YAML_TEMPLATE,
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
        else:
            new_yaml += '{}\n'.format(line)

    with open(blueprint, 'w') as outfile:
        outfile.write(new_yaml)
    logger.info('Wrote new blueprint to {}'.format(blueprint))


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
