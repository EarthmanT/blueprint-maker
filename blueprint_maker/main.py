########
# Copyright (c) 2014-2022 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click

from blueprint_maker.variants import command as variants
from blueprint_maker.rename_nodes import command as rename_nodes
from blueprint_maker.from_node_types import command as from_node_types

CLICK_CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'])


@click.group(name='blueprint-maker', context_settings=CLICK_CONTEXT_SETTINGS)
def init():
    pass


def blueprint_maker():
    init()


def _register_commands():
    init.add_command(variants.create_variants)
    init.add_command(rename_nodes.create_by_renaming_nodes)
    init.add_command(from_node_types.create_from_node_types)


_register_commands()


if __name__ == "__main__":
    blueprint_maker()
