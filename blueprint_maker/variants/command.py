import click
import subprocess

from blueprint_maker.logging import logger
from blueprint_maker import utils as bm_utils
from blueprint_maker.variants import utils as v_utils

@click.command(name='variants',
               short_help='Create variants of a blueprint.')
@click.option('-b',
              '--blueprint',
              type=click.STRING,
              help='The path to blueprint YAML file.')
@click.option('-m',
              '--max-variants',
              type=click.INT,
              help='The max number of variants to generate.')
@click.option('-o',
              '--output-directory',
              type=click.STRING,
              help='The directory where we will put the new files.')
def create_variants(*args, **kwargs):
    # +1 because we are skipping the first which is a duplicate.
    max_variants = bm_utils.get_kwarg(kwargs, 'max_variants', 5) + 1
    blueprint = bm_utils.get_existing_file(kwargs, 'blueprint')
    subprocess.run(['cfy-lint', '-b', blueprint.as_posix(), '-af'])
    output_directory = bm_utils.get_existing_file(kwargs, 'output_directory')
    bm_utils.remove_anchors(blueprint)
    blueprint_content = bm_utils.get_file_content(blueprint)
    node_templates_section = v_utils.get_node_templates_section(blueprint_content)
    node_templates = v_utils.get_node_templates(node_templates_section)
    permutations = v_utils.get_permutations(node_templates, max_variants)
    logger.info('Generating {} variations of {}'.format(
        len(permutations) - 1, blueprint))
    if (max_variants - 1) - (len(permutations) - 1) > 0:
        logger.error(
            '{} variants were requested but {} were generated. '
            'This is the max number of permutations possible for '
            'the given node templates section.'.format(
                max_variants - 1,
                len(permutations) - 1
            )
        )
    new_filename_base = v_utils.get_newfilename_base(blueprint, output_directory)
    v_utils.put_permutations(new_filename_base,
                             blueprint_content,
                             node_templates_section,
                             permutations)
