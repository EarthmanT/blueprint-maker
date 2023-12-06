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
GET_ATTRIBUTE_LIST = 'get_attribute_list'
GET_ENVIRONMENT_CAPABILITY = 'get_environment_capability'
INSTRINSIC_FUNCTIONS = [
    CONCAT,
    GET_SYS,
    GET_INPUT,
    GET_SECRET,
    GET_PROPERTY,
    GET_ATTRIBUTE,
    GET_CAPABILITY,
    GET_ATTRIBUTE_LIST,
    GET_ENVIRONMENT_CAPABILITY
]
