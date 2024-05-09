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
"""Check updates in Botocore package, generate new code and make commit."""
import datetime
from git import Repo
import hashlib
import json
import os
import shutil
from src.tools.constants import SERVICE_JSON_FILE_PATH, \
    BOTOCORE_SERVICE_JSON_FILE_PATH, \
    BOTOCORE_PACKAGE_PATH, \
    BOTOCORE_PACKAGE_URL
from src.tools.utils_codegen import UtilsCodeGen
from src.tools.shapes_codegen import ShapesCodeGen
from src.tools.resources_codegen import ResourcesCodeGen
from src.tools.codegen import generate_code

def clone_botocore_package():
    """
    Clone the Botocore package.
    
    Returns:
        None
    """
    if os.path.exists(BOTOCORE_PACKAGE_PATH):
        shutil.rmtree(BOTOCORE_PACKAGE_PATH)
    Repo.clone_from(BOTOCORE_PACKAGE_URL, BOTOCORE_PACKAGE_PATH)

def compare_file_contents(botocore_file, codegen_file):
    """
    Compare the service.json files in the Botocore package and the code gen package.

    Args:
        botocore_file (str): The file path to the service.json file in the Botocore package.
        codegen_file (str): The file path to the service.json file in the code gen package.

    Returns:
        bool: if the files have the same contents.
    """

    botocore_hash = calculate_hash(botocore_file)
    codegen_hash = calculate_hash(codegen_file)

    return botocore_hash == codegen_hash

def calculate_hash(file_path):
    """
    Calculate hash value with SHA-256 algorithm.

    Args:
        file_path (str): The file path.
    
    Returns:
        str: The hash value calculated by SHA-256.
    """

    # Read the file in binary mode
    with open(file_path, 'rb') as file:
        contents = file.read()

    # Calculate the hash value using SHA-256
    sha256 = hashlib.sha256()
    sha256.update(contents)
    return sha256.hexdigest()

def git_commit_and_push():
    """
    Create a new branch, then add, commit and push the changes.

    Returns:
        None
    """

    path = os.getcwd()
    repo = Repo(path)
    
    # Record current branch and checkout to the main branch
    current_branch = repo.active_branch

    # Checkout to a new branch
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    branch_name = f'botocore-sync-{timestamp}'
    new_branch = repo.create_head(branch_name)
    new_branch.checkout()

    # Add and commit files
    repo.git.add('-A')
    repo.git.commit('-m', 'Sync update from Botocore')

    # Push to remote
    remote = repo.remote()
    remote_ref = f"refs/heads/{branch_name}"
    remote.push(refspec=f"{remote_ref}:{remote_ref}")

    # Go back to the current branch
    current_branch.checkout()

if __name__ == "__main__":
    clone_botocore_package()

    if not compare_file_contents(BOTOCORE_SERVICE_JSON_FILE_PATH, SERVICE_JSON_FILE_PATH):
        # If the service.json file has been updated
        # TODO: Inject service JSON file path & run through with all the sagemaker service JSON files
        os.remove(SERVICE_JSON_FILE_PATH)
        shutil.copy(BOTOCORE_SERVICE_JSON_FILE_PATH, SERVICE_JSON_FILE_PATH)
        with open(SERVICE_JSON_FILE_PATH, 'r') as file:
            service_json = json.load(file)
        
        utils_code_gen = UtilsCodeGen()
        shapes_code_gen = ShapesCodeGen(service_json=service_json)
        resources_code_gen = ResourcesCodeGen(service_json=service_json)

        generate_code(utils_code_gen=utils_code_gen,
                      shapes_code_gen=shapes_code_gen,
                      resources_code_gen=resources_code_gen)
        git_commit_and_push()
