# blueprint-maker

Generate blueprints from other blueprints.

## with-node-types

The `with-node-types` command generates a new blueprint from a list of provided node types.

It has the flags:
  - `-b`: This is the path to write the blueprint file.
  - `-n`: This is a node type to generate a node template for. You can provide this multiple times.

For example, if you run the command: `bm with-node-types -b examples/vpc-subnet.yaml -n cloudify.nodes.aws.ec2.Vpc -n cloudify.nodes.aws.ec2.Subnet`:

```yaml
tosca_definitions_version: cloudify_dsl_1_5

imports:

  - cloudify/types/types.yaml
  - plugin:cloudify-aws-plugin

inputs:

  vpc_resource_config_cidrblock:
    display_label: Vpc Resource Config Cidrblock
    type: string
  vpc_resource_config_kwargs:
    display_label: Vpc Resource Config Kwargs
    type: string
  subnet_resource_config_availabilityzone:
    display_label: Subnet Resource Config Availabilityzone
    type: string
  subnet_resource_config_cidrblock:
    display_label: Subnet Resource Config Cidrblock
    type: string
  subnet_resource_config_vpcid:
    display_label: Subnet Resource Config Vpcid
    type: string
  subnet_resource_config_kwargs:
    display_label: Subnet Resource Config Kwargs
    type: string
  subnet_use_available_zones:
    display_label: Subnet Use Available Zones
    type: boolean

node_templates:

  vpc:
    type: cloudify.nodes.aws.ec2.Vpc
    properties:
      resource_config:
        CidrBlock: { get_input : vpc_resource_config_cidrblock }
        kwargs: { get_input : vpc_resource_config_kwargs }
  subnet:
    type: cloudify.nodes.aws.ec2.Subnet
    properties:
      resource_config:
        AvailabilityZone: { get_input : subnet_resource_config_availabilityzone }
        CidrBlock: { get_input : subnet_resource_config_cidrblock }
        VpcId: { get_input : subnet_resource_config_vpcid }
        kwargs: { get_input : subnet_resource_config_kwargs }
      use_available_zones: { get_input : subnet_use_available_zones }
    relationships:
      - type: cloudify.relationships.depends_on
        target: vpc

```
Things to know:
 - A `cloudify.relationships.depends_on relationship will be inserted between every node and the previous node.
 - A For each node type property defined in the marketplace, a new input will be inserted into the inputs section.

## variants

The `variants` command takes an existing blueprint and creates variations of that blueprint.

For example, let's say that we have this blueprint:

```yaml
# examples/variant.yaml
tosca_definitions_version: cloudify_dsl_1_5

imports:
  - cloudify/types/types.yaml

node_templates:

  a:
    type: cloudify.nodes.Root

  b:
    type: cloudify.nodes.Root

  c:
    type: cloudify.nodes.Root
```

We can get variations of this blueprint by running: `bm variants -b examples/variant.yaml -m 5`.

This will create a maximum of 5 variations of the variant.yaml blueprint, by jumbling the order of the node templates.
If the total variants (`-t` or `--total-variants`) value exceeds the possible number of variations, then we will generate the maximum and print and error message explaining the discrepancy in what was requested and what was generated.

The new blueprints will be dropped in the same folder as the provided blueprint with names like `variant-1.yaml, variant-2.yaml` and so forth.

## rename nodes

The `rename-nodes` command takes and existing blueprint and renames all of the node templates to random stuff.

So for example, if you have a simple blueprint like `variant.yaml`, you can rename all of the nodes like this:

`bm rename-nodes -b examples/rename.yaml`

```yaml
#examples/rename.yaml
tosca_definitions_version: cloudify_dsl_1_5

imports:

  - cloudify/types/types.yaml

inputs:

  baz:
    type: string

node_templates:

  foo:
    type: cloudify.nodes.Roo
    relationships:
      - type: cloudify.relationships.connected_to
        target: baz

  bar:
    type: cloudify.nodes.Root

  baz:
    type: cloudify.nodes.Root

capabilities:

  cap1:
    value: { get_attribute: [ foo, quxx ] }

  cap2:
    value: { get_property: [ bar, qux ] }

  cap3:
    value: { get_input: baz }
```
Result:
```yaml
# examples/rename-viewer.yaml
tosca_definitions_version: cloudify_dsl_1_5

imports:

  - cloudify/types/types.yaml

inputs:

  baz:
    type: string

node_templates:

  yarn:
    type: cloudify.nodes.Root
  elevation:
    type: cloudify.nodes.Root
  pound:
    type: cloudify.nodes.Roo
    relationships:
      - type: cloudify.relationships.connected_to
        target: elevation
capabilities:
  cap1:
    value: {get_attribute: [pound, quxx]}
  cap2:
    value: {get_property: [yarn, qux]}
  cap3:
    value: {get_input: baz}


```