# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""Constants used in the code_generator modules."""
import os

CLASS_METHODS = set(['create', 'add', 'start', 'register', 'import', 'list', 'get'])
OBJECT_METHODS = set(['refresh', 'delete', 'update', 'stop', 'deregister', 'wait', 'wait_for_status'])

BASIC_JSON_TYPES_TO_PYTHON_TYPES = {
    "string": "str",
    "integer": "int",
    "boolean": "bool",
    "long": "int",
    "float": "float",
    "map": "dict",
    "double": "float",
    "list": "list",
    "timestamp": "datetime.datetime",
}

SHAPE_DAG_FILE_PATH = os.getcwd() + 'src/code_injection/shape_dag.py'

LICENCES_STRING = '''
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
'''

# TODO: The file name should be injected, we should update it to be more generic
SERVICE_JSON_FILE_PATH = os.getcwd() + '/sample/sagemaker/2017-07-24/service-2.json'

GENERATED_CLASSES_LOCATION = os.getcwd() + '/src/generated'

UTILS_CODEGEN_FILE_NAME = 'utils.py'

RESOURCES_CODEGEN_FILE_NAME = 'resources.py'

SHAPES_CODEGEN_FILE_NAME = 'shapes.py'