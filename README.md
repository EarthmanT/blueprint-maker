# blueprint-maker

Generate blueprints from other blueprints.

## create variants

The create variants tool takes an existing blueprint and creates node template order permutations of the same blueprint.

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

We can get variations of this blueprint by running: `blueprint-maker create-variants -b examples/variant.yaml -t 5`.

This will create 5 variations of the variant.yaml blueprint, by jumbling the order of the node templates.
If the total variants (`-t` or `--total-variants`) value exceeds the possible number of variations, then we will generate the maximum and print and error message explaining the discrepancy in what was requested and what was generated.

The new blueprints will be dropped in the same folder as the provided blueprint with names like `variant-1.yaml, variant-2.yaml` and so forth.
