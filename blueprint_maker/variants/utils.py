import os
import re
import sys
import itertools
from pathlib import Path

import click

from blueprint_maker.logging import logger
from blueprint_maker import utils as bm_utils

NT_REGEX = '(\nnode_templates:\n\s+|\n\ncapabilities:|\n\noutputs:|\n\npolicies:|\n\ngroups:|$)'
SEP_REGEX = '\n\n\s+'


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


def put_permutations(blueprint,
                     blueprint_content,
                     node_templates_section,
                     permutations):

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
        bm_utils.put_file_content(new_name, new_blueprint_content)