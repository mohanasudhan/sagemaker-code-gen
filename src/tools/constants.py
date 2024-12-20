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

CLASS_METHODS = set(["create", "add", "start", "register", "import", "list", "get"])
OBJECT_METHODS = set(
    ["refresh", "delete", "update", "stop", "deregister", "wait", "wait_for_status"]
)

TERMINAL_STATES = set(
    ["Completed", "Stopped", "Deleted", "Failed", "Succeeded", "Cancelled"]
)

CONFIGURABLE_ATTRIBUTE_SUBSTRINGS = [
    "kms",
    "s3",
    "subnet",
    "tags",
    "role",
    "security_group",
]

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
    "blob": "Any",
}

SHAPE_DAG_FILE_PATH = os.getcwd() + "/src/code_injection/shape_dag.py"
PYTHON_TYPES_TO_BASIC_JSON_TYPES = {
    "str": "string",
    "int": "integer",
    "bool": "boolean",
    "float": "double",
    "datetime.datetime": "timestamp",
}

LICENCES_STRING = """
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
"""

BASIC_IMPORTS_STRING = """
import logging
"""

LOGGER_STRING = """
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""

# TODO: The file name should be injected, we should update it to be more generic
SERVICE_JSON_FILE_PATH = os.getcwd() + "/sample/sagemaker/2017-07-24/service-2.json"
RUNTIME_SERVICE_JSON_FILE_PATH = (
    os.getcwd() + "/sample/sagemaker-runtime/2017-05-13/service-2.json"
)

GENERATED_CLASSES_LOCATION = os.getcwd() + "/src/generated"
UTILS_CODEGEN_FILE_NAME = "utils.py"
INTELLIGENT_DEFAULTS_HELPER_CODEGEN_FILE_NAME = "intelligent_defaults_helper.py"

RESOURCES_CODEGEN_FILE_NAME = "resources.py"

SHAPES_CODEGEN_FILE_NAME = "shapes.py"

CONFIG_SCHEMA_FILE_NAME = "config_schema.py"
