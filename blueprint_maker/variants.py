import os
import re
import sys
import itertools
from pathlib import Path

import click

from blueprint_maker.logging import logger

NT_REGEX = '(\nnode_templates:\n\s+|\n\ncapabilities:|\n\noutputs:|\n\npolicies:|\n\ngroups:|$)'
SEP_REGEX = '\n\n\s+'


def get_blueprint_content(filepath):
    with open(filepath, 'r') as infile:
        return infile.read()


def put_blueprint_content(filepath, content):
    with open(filepath, 'w') as outfile:
        outfile.write(content)


def get_node_templates_section(blueprint_content):
    return re.split(NT_REGEX, blueprint_content)[2:-2][0]


def get_node_templates(node_templates_section):
    node_templates_section = node_templates_section.strip()
    # TODO: We need to get a better separator.
    return re.split(SEP_REGEX, node_templates_section)


def get_permutations(node_templates, max_permutations=10):
    permutations = []
    current_permutations = 0
    for permutation in itertools.permutations(node_templates):
        permutations.append('\n\n  '.join(permutation))
        current_permutations += 1
        if current_permutations >= max_permutations:
            break
    return permutations


def put_permutations(blueprint, blueprint_content, node_templates_section, permutations):
    for n in range(0, len(permutations)):
        if n == 0:
            continue
        new_blueprint_content = blueprint_content.replace(
            node_templates_section, permutations[n])
        new_name = Path(
            os.path.join(
                blueprint.parent.as_posix(),
                blueprint.name.replace('.yaml', '-{}.yaml'.format(n))
            )
        ).resolve()
        put_blueprint_content(new_name, new_blueprint_content)


@click.command(name='create-variants',
               short_help='Create variants of a blueprint.')
@click.option('-b',
              '--blueprint',
              type=click.STRING,
              help='The path to blueprint YAML file.')
@click.option('-t',
              '--total-variants',
              type=click.INT,
              help='The number of variants to generate.')
def create_variants(*args, **kwargs):
    blueprint = kwargs.get('blueprint')
    # +1 because we are skipping the first which is a duplicate.
    total_variants = kwargs.get('total_variants', 5) + 1
    if blueprint:
        blueprint = Path(blueprint).resolve()
    if not os.path.exists(blueprint):
        logger.error('Incorrect blueprint path: {}'.format(blueprint))
        sys.exit(1)
    blueprint_content = get_blueprint_content(blueprint)
    node_templates_section = get_node_templates_section(blueprint_content)
    node_templates = get_node_templates(node_templates_section)
    permutations = get_permutations(node_templates, total_variants)
    logger.info('Generating {} variations of {}'.format(
        len(permutations) - 1, blueprint))
    if (total_variants - 1) - (len(permutations) - 1) > 0:
        logger.error(
            '{} variants were requested but {} were generated. '
            'This is the max number of permutations possible for '
            'the given node templates section.'.format(
                total_variants - 1,
                len(permutations) - 1
            )
        )
    put_permutations(blueprint,
                     blueprint_content,
                     node_templates_section,
                     permutations)
