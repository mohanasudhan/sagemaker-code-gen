
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

import logging

import datetime
import boto3
import time
from pprint import pprint
from pydantic import BaseModel, validate_call
from typing import List, Dict, Optional, Literal
from boto3.session import Session
from .utils import SageMakerClient, Unassigned
from .shapes import *

from src.code_injection.codec import transform


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Base(BaseModel):
    @classmethod
    def _serialize(cls, data: Dict) -> Dict:
        result = {{}}
        for attr, value in data.items():
            if isinstance(value, Unassigned):
                continue
            
            if isinstance(value, List):
                result[attr] = cls._serialize_list(value)
            elif isinstance(value, Dict):
                result[attr] = cls._serialize_dict(value)
            elif hasattr(value, 'serialize'):
                result[attr] = value.serialize()
            else:
                result[attr] = value
        return result
    
    @classmethod
    def _serialize_list(value: List):
        return [v.serialize() if hasattr(v, 'serialize') else v for v in value]
    
    @classmethod
    def _serialize_dict(value: Dict):
        return {{k: v.serialize() if hasattr(v, 'serialize') else v for k, v in value.items()}}

class Action(Base):
    action_name: Optional[str] = Unassigned()
    action_arn: Optional[str] = Unassigned()
    source: Optional[ActionSource] = Unassigned()
    action_type: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    properties: Optional[Dict[str, str]] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    lineage_group_arn: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        action_name: str,
        source: ActionSource,
        action_type: str,
        description: Optional[str] = Unassigned(),
        status: Optional[str] = Unassigned(),
        properties: Optional[Dict[str, str]] = Unassigned(),
        metadata_properties: Optional[MetadataProperties] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating action resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ActionName': action_name,
            'Source': source,
            'ActionType': action_type,
            'Description': description,
            'Status': status,
            'Properties': properties,
            'MetadataProperties': metadata_properties,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_action(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(action_name=action_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        action_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ActionName': action_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_action(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeActionResponse')
        action = cls(**transformed_response)
        return action
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ActionName': self.action_name,
        }
        client = SageMakerClient().client
        response = client.describe_action(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeActionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ActionName': self.action_name,
        }
        self.client.delete_action(**operation_input_args)


class Algorithm(Base):
    algorithm_name: str
    algorithm_arn: str
    creation_time: datetime.datetime
    training_specification: TrainingSpecification
    algorithm_status: str
    algorithm_status_details: AlgorithmStatusDetails
    algorithm_description: Optional[str] = Unassigned()
    inference_specification: Optional[InferenceSpecification] = Unassigned()
    validation_specification: Optional[AlgorithmValidationSpecification] = Unassigned()
    product_id: Optional[str] = Unassigned()
    certify_for_marketplace: Optional[bool] = Unassigned()
    
    @classmethod
    def create(
        cls,
        algorithm_name: str,
        training_specification: TrainingSpecification,
        algorithm_description: Optional[str] = Unassigned(),
        inference_specification: Optional[InferenceSpecification] = Unassigned(),
        validation_specification: Optional[AlgorithmValidationSpecification] = Unassigned(),
        certify_for_marketplace: Optional[bool] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating algorithm resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'AlgorithmName': algorithm_name,
            'AlgorithmDescription': algorithm_description,
            'TrainingSpecification': training_specification,
            'InferenceSpecification': inference_specification,
            'ValidationSpecification': validation_specification,
            'CertifyForMarketplace': certify_for_marketplace,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_algorithm(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(algorithm_name=algorithm_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        algorithm_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'AlgorithmName': algorithm_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_algorithm(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeAlgorithmOutput')
        algorithm = cls(**transformed_response)
        return algorithm
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'AlgorithmName': self.algorithm_name,
        }
        client = SageMakerClient().client
        response = client.describe_algorithm(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeAlgorithmOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'AlgorithmName': self.algorithm_name,
        }
        self.client.delete_algorithm(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Pending', 'InProgress', 'Completed', 'Failed', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.algorithm_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class App(Base):
    app_arn: Optional[str] = Unassigned()
    app_type: Optional[str] = Unassigned()
    app_name: Optional[str] = Unassigned()
    domain_id: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    space_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    last_health_check_timestamp: Optional[datetime.datetime] = Unassigned()
    last_user_activity_timestamp: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    resource_spec: Optional[ResourceSpec] = Unassigned()
    
    @classmethod
    def create(
        cls,
        domain_id: str,
        app_type: str,
        app_name: str,
        user_profile_name: Optional[str] = Unassigned(),
        space_name: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        resource_spec: Optional[ResourceSpec] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating app resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'DomainId': domain_id,
            'UserProfileName': user_profile_name,
            'SpaceName': space_name,
            'AppType': app_type,
            'AppName': app_name,
            'Tags': tags,
            'ResourceSpec': resource_spec,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_app(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(domain_id=domain_id, app_type=app_type, app_name=app_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        domain_id: str,
        app_type: str,
        app_name: str,
        user_profile_name: Optional[str] = Unassigned(),
        space_name: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'DomainId': domain_id,
            'UserProfileName': user_profile_name,
            'SpaceName': space_name,
            'AppType': app_type,
            'AppName': app_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_app(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeAppResponse')
        app = cls(**transformed_response)
        return app
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'UserProfileName': self.user_profile_name,
            'SpaceName': self.space_name,
            'AppType': self.app_type,
            'AppName': self.app_name,
        }
        client = SageMakerClient().client
        response = client.describe_app(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeAppResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'UserProfileName': self.user_profile_name,
            'SpaceName': self.space_name,
            'AppType': self.app_type,
            'AppName': self.app_name,
        }
        self.client.delete_app(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Deleted', 'Deleting', 'Failed', 'InService', 'Pending'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class AppImageConfig(Base):
    app_image_config_arn: Optional[str] = Unassigned()
    app_image_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    kernel_gateway_image_config: Optional[KernelGatewayImageConfig] = Unassigned()
    jupyter_lab_app_image_config: Optional[JupyterLabAppImageConfig] = Unassigned()
    
    @classmethod
    def create(
        cls,
        app_image_config_name: str,
        tags: Optional[List[Tag]] = Unassigned(),
        kernel_gateway_image_config: Optional[KernelGatewayImageConfig] = Unassigned(),
        jupyter_lab_app_image_config: Optional[JupyterLabAppImageConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating app_image_config resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'AppImageConfigName': app_image_config_name,
            'Tags': tags,
            'KernelGatewayImageConfig': kernel_gateway_image_config,
            'JupyterLabAppImageConfig': jupyter_lab_app_image_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_app_image_config(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(app_image_config_name=app_image_config_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        app_image_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'AppImageConfigName': app_image_config_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_app_image_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeAppImageConfigResponse')
        app_image_config = cls(**transformed_response)
        return app_image_config
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'AppImageConfigName': self.app_image_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_app_image_config(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeAppImageConfigResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'AppImageConfigName': self.app_image_config_name,
        }
        self.client.delete_app_image_config(**operation_input_args)


class Artifact(Base):
    artifact_name: Optional[str] = Unassigned()
    artifact_arn: Optional[str] = Unassigned()
    source: Optional[ArtifactSource] = Unassigned()
    artifact_type: Optional[str] = Unassigned()
    properties: Optional[Dict[str, str]] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    lineage_group_arn: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        source: ArtifactSource,
        artifact_type: str,
        artifact_name: Optional[str] = Unassigned(),
        properties: Optional[Dict[str, str]] = Unassigned(),
        metadata_properties: Optional[MetadataProperties] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating artifact resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ArtifactName': artifact_name,
            'Source': source,
            'ArtifactType': artifact_type,
            'Properties': properties,
            'MetadataProperties': metadata_properties,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_artifact(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(artifact_arn=response['ArtifactArn'], session=session, region=region)
    
    @classmethod
    def get(
        cls,
        artifact_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ArtifactArn': artifact_arn,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_artifact(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeArtifactResponse')
        artifact = cls(**transformed_response)
        return artifact
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ArtifactArn': self.artifact_arn,
        }
        client = SageMakerClient().client
        response = client.describe_artifact(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeArtifactResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ArtifactArn': self.artifact_arn,
            'Source': self.source,
        }
        self.client.delete_artifact(**operation_input_args)


class AutoMLJob(Base):
    auto_m_l_job_name: str
    auto_m_l_job_arn: str
    input_data_config: List[AutoMLChannel]
    output_data_config: AutoMLOutputDataConfig
    role_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    auto_m_l_job_status: str
    auto_m_l_job_secondary_status: str
    auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned()
    problem_type: Optional[str] = Unassigned()
    auto_m_l_job_config: Optional[AutoMLJobConfig] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    partial_failure_reasons: Optional[List[AutoMLPartialFailureReason]] = Unassigned()
    best_candidate: Optional[AutoMLCandidate] = Unassigned()
    generate_candidate_definitions_only: Optional[bool] = Unassigned()
    auto_m_l_job_artifacts: Optional[AutoMLJobArtifacts] = Unassigned()
    resolved_attributes: Optional[ResolvedAttributes] = Unassigned()
    model_deploy_config: Optional[ModelDeployConfig] = Unassigned()
    model_deploy_result: Optional[ModelDeployResult] = Unassigned()
    
    @classmethod
    def create(
        cls,
        auto_m_l_job_name: str,
        input_data_config: List[AutoMLChannel],
        output_data_config: AutoMLOutputDataConfig,
        role_arn: str,
        problem_type: Optional[str] = Unassigned(),
        auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned(),
        auto_m_l_job_config: Optional[AutoMLJobConfig] = Unassigned(),
        generate_candidate_definitions_only: Optional[bool] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        model_deploy_config: Optional[ModelDeployConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating auto_m_l_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'AutoMLJobName': auto_m_l_job_name,
            'InputDataConfig': input_data_config,
            'OutputDataConfig': output_data_config,
            'ProblemType': problem_type,
            'AutoMLJobObjective': auto_m_l_job_objective,
            'AutoMLJobConfig': auto_m_l_job_config,
            'RoleArn': role_arn,
            'GenerateCandidateDefinitionsOnly': generate_candidate_definitions_only,
            'Tags': tags,
            'ModelDeployConfig': model_deploy_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_auto_m_l_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(auto_m_l_job_name=auto_m_l_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        auto_m_l_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'AutoMLJobName': auto_m_l_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_auto_m_l_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeAutoMLJobResponse')
        auto_m_l_job = cls(**transformed_response)
        return auto_m_l_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'AutoMLJobName': self.auto_m_l_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_auto_m_l_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeAutoMLJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'AutoMLJobName': self.auto_m_l_job_name,
        }
        self.client.stop_auto_m_l_job(**operation_input_args)
    
    @validate_call
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.auto_m_l_job_status
    
            if current_status in terminal_states:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class AutoMLJobV2(Base):
    auto_m_l_job_name: str
    auto_m_l_job_arn: str
    auto_m_l_job_input_data_config: List[AutoMLJobChannel]
    output_data_config: AutoMLOutputDataConfig
    role_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    auto_m_l_job_status: str
    auto_m_l_job_secondary_status: str
    auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned()
    auto_m_l_problem_type_config: Optional[AutoMLProblemTypeConfig] = Unassigned()
    auto_m_l_problem_type_config_name: Optional[str] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    partial_failure_reasons: Optional[List[AutoMLPartialFailureReason]] = Unassigned()
    best_candidate: Optional[AutoMLCandidate] = Unassigned()
    auto_m_l_job_artifacts: Optional[AutoMLJobArtifacts] = Unassigned()
    resolved_attributes: Optional[AutoMLResolvedAttributes] = Unassigned()
    model_deploy_config: Optional[ModelDeployConfig] = Unassigned()
    model_deploy_result: Optional[ModelDeployResult] = Unassigned()
    data_split_config: Optional[AutoMLDataSplitConfig] = Unassigned()
    security_config: Optional[AutoMLSecurityConfig] = Unassigned()
    
    @classmethod
    def create(
        cls,
        auto_m_l_job_name: str,
        auto_m_l_job_input_data_config: List[AutoMLJobChannel],
        output_data_config: AutoMLOutputDataConfig,
        auto_m_l_problem_type_config: AutoMLProblemTypeConfig,
        role_arn: str,
        tags: Optional[List[Tag]] = Unassigned(),
        security_config: Optional[AutoMLSecurityConfig] = Unassigned(),
        auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned(),
        model_deploy_config: Optional[ModelDeployConfig] = Unassigned(),
        data_split_config: Optional[AutoMLDataSplitConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating auto_m_l_job_v2 resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'AutoMLJobName': auto_m_l_job_name,
            'AutoMLJobInputDataConfig': auto_m_l_job_input_data_config,
            'OutputDataConfig': output_data_config,
            'AutoMLProblemTypeConfig': auto_m_l_problem_type_config,
            'RoleArn': role_arn,
            'Tags': tags,
            'SecurityConfig': security_config,
            'AutoMLJobObjective': auto_m_l_job_objective,
            'ModelDeployConfig': model_deploy_config,
            'DataSplitConfig': data_split_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_auto_m_l_job_v2(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(auto_m_l_job_name=auto_m_l_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        auto_m_l_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'AutoMLJobName': auto_m_l_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_auto_m_l_job_v2(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeAutoMLJobV2Response')
        auto_m_l_job_v2 = cls(**transformed_response)
        return auto_m_l_job_v2
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'AutoMLJobName': self.auto_m_l_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_auto_m_l_job_v2(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeAutoMLJobV2Response', self)
        return self
    
    @validate_call
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.auto_m_l_job_status
    
            if current_status in terminal_states:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class Cluster(Base):
    cluster_arn: str
    cluster_status: str
    instance_groups: List[ClusterInstanceGroupDetails]
    cluster_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_message: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    
    @classmethod
    def create(
        cls,
        cluster_name: str,
        instance_groups: List[ClusterInstanceGroupSpecification],
        vpc_config: Optional[VpcConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating cluster resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ClusterName': cluster_name,
            'InstanceGroups': instance_groups,
            'VpcConfig': vpc_config,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_cluster(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(cluster_name=cluster_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        cluster_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ClusterName': cluster_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_cluster(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeClusterResponse')
        cluster = cls(**transformed_response)
        return cluster
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ClusterName': self.cluster_name,
        }
        client = SageMakerClient().client
        response = client.describe_cluster(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeClusterResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ClusterName': self.cluster_name,
        }
        self.client.delete_cluster(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Creating', 'Deleting', 'Failed', 'InService', 'RollingBack', 'SystemUpdating', 'Updating'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.cluster_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class CodeRepository(Base):
    code_repository_name: str
    code_repository_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    git_config: Optional[GitConfig] = Unassigned()
    
    @classmethod
    def create(
        cls,
        code_repository_name: str,
        git_config: GitConfig,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating code_repository resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'CodeRepositoryName': code_repository_name,
            'GitConfig': git_config,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_code_repository(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(code_repository_name=code_repository_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        code_repository_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'CodeRepositoryName': code_repository_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_code_repository(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeCodeRepositoryOutput')
        code_repository = cls(**transformed_response)
        return code_repository
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'CodeRepositoryName': self.code_repository_name,
        }
        client = SageMakerClient().client
        response = client.describe_code_repository(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeCodeRepositoryOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'CodeRepositoryName': self.code_repository_name,
        }
        self.client.delete_code_repository(**operation_input_args)


class CompilationJob(Base):
    compilation_job_name: str
    compilation_job_arn: str
    compilation_job_status: str
    stopping_condition: StoppingCondition
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    failure_reason: str
    model_artifacts: ModelArtifacts
    role_arn: str
    input_config: InputConfig
    output_config: OutputConfig
    compilation_start_time: Optional[datetime.datetime] = Unassigned()
    compilation_end_time: Optional[datetime.datetime] = Unassigned()
    inference_image: Optional[str] = Unassigned()
    model_package_version_arn: Optional[str] = Unassigned()
    model_digests: Optional[ModelDigests] = Unassigned()
    vpc_config: Optional[NeoVpcConfig] = Unassigned()
    derived_information: Optional[DerivedInformation] = Unassigned()
    
    @classmethod
    def create(
        cls,
        compilation_job_name: str,
        role_arn: str,
        output_config: OutputConfig,
        stopping_condition: StoppingCondition,
        model_package_version_arn: Optional[str] = Unassigned(),
        input_config: Optional[InputConfig] = Unassigned(),
        vpc_config: Optional[NeoVpcConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating compilation_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'CompilationJobName': compilation_job_name,
            'RoleArn': role_arn,
            'ModelPackageVersionArn': model_package_version_arn,
            'InputConfig': input_config,
            'OutputConfig': output_config,
            'VpcConfig': vpc_config,
            'StoppingCondition': stopping_condition,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_compilation_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(compilation_job_name=compilation_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        compilation_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'CompilationJobName': compilation_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_compilation_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeCompilationJobResponse')
        compilation_job = cls(**transformed_response)
        return compilation_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'CompilationJobName': self.compilation_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_compilation_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeCompilationJobResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'CompilationJobName': self.compilation_job_name,
        }
        self.client.delete_compilation_job(**operation_input_args)
    
    def stop(self) -> None:
    
        operation_input_args = {
            'CompilationJobName': self.compilation_job_name,
        }
        self.client.stop_compilation_job(**operation_input_args)
    
    @validate_call
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        terminal_states = ['COMPLETED', 'FAILED', 'STOPPED']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.compilation_job_status
    
            if current_status in terminal_states:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class Context(Base):
    context_name: Optional[str] = Unassigned()
    context_arn: Optional[str] = Unassigned()
    source: Optional[ContextSource] = Unassigned()
    context_type: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    properties: Optional[Dict[str, str]] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    lineage_group_arn: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        context_name: str,
        source: ContextSource,
        context_type: str,
        description: Optional[str] = Unassigned(),
        properties: Optional[Dict[str, str]] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating context resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ContextName': context_name,
            'Source': source,
            'ContextType': context_type,
            'Description': description,
            'Properties': properties,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_context(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(context_name=context_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        context_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ContextName': context_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_context(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeContextResponse')
        context = cls(**transformed_response)
        return context
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ContextName': self.context_name,
        }
        client = SageMakerClient().client
        response = client.describe_context(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeContextResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ContextName': self.context_name,
        }
        self.client.delete_context(**operation_input_args)


class DataQualityJobDefinition(Base):
    job_definition_arn: str
    job_definition_name: str
    creation_time: datetime.datetime
    data_quality_app_specification: DataQualityAppSpecification
    data_quality_job_input: DataQualityJobInput
    data_quality_job_output_config: MonitoringOutputConfig
    job_resources: MonitoringResources
    role_arn: str
    data_quality_baseline_config: Optional[DataQualityBaselineConfig] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    @classmethod
    def create(
        cls,
        job_definition_name: str,
        data_quality_app_specification: DataQualityAppSpecification,
        data_quality_job_input: DataQualityJobInput,
        data_quality_job_output_config: MonitoringOutputConfig,
        job_resources: MonitoringResources,
        role_arn: str,
        data_quality_baseline_config: Optional[DataQualityBaselineConfig] = Unassigned(),
        network_config: Optional[MonitoringNetworkConfig] = Unassigned(),
        stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating data_quality_job_definition resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
            'DataQualityBaselineConfig': data_quality_baseline_config,
            'DataQualityAppSpecification': data_quality_app_specification,
            'DataQualityJobInput': data_quality_job_input,
            'DataQualityJobOutputConfig': data_quality_job_output_config,
            'JobResources': job_resources,
            'NetworkConfig': network_config,
            'RoleArn': role_arn,
            'StoppingCondition': stopping_condition,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_data_quality_job_definition(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(job_definition_name=job_definition_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_data_quality_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeDataQualityJobDefinitionResponse')
        data_quality_job_definition = cls(**transformed_response)
        return data_quality_job_definition
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_data_quality_job_definition(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeDataQualityJobDefinitionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_data_quality_job_definition(**operation_input_args)


class DeviceFleet(Base):
    device_fleet_name: str
    device_fleet_arn: str
    output_config: EdgeOutputConfig
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    description: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    iot_role_alias: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        device_fleet_name: str,
        output_config: EdgeOutputConfig,
        role_arn: Optional[str] = Unassigned(),
        description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        enable_iot_role_alias: Optional[bool] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating device_fleet resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'DeviceFleetName': device_fleet_name,
            'RoleArn': role_arn,
            'Description': description,
            'OutputConfig': output_config,
            'Tags': tags,
            'EnableIotRoleAlias': enable_iot_role_alias,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_device_fleet(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(device_fleet_name=device_fleet_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        device_fleet_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'DeviceFleetName': device_fleet_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_device_fleet(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeDeviceFleetResponse')
        device_fleet = cls(**transformed_response)
        return device_fleet
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'DeviceFleetName': self.device_fleet_name,
        }
        client = SageMakerClient().client
        response = client.describe_device_fleet(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeDeviceFleetResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DeviceFleetName': self.device_fleet_name,
        }
        self.client.delete_device_fleet(**operation_input_args)


class Domain(Base):
    domain_arn: Optional[str] = Unassigned()
    domain_id: Optional[str] = Unassigned()
    domain_name: Optional[str] = Unassigned()
    home_efs_file_system_id: Optional[str] = Unassigned()
    single_sign_on_managed_application_instance_id: Optional[str] = Unassigned()
    single_sign_on_application_arn: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    security_group_id_for_domain_boundary: Optional[str] = Unassigned()
    auth_mode: Optional[str] = Unassigned()
    default_user_settings: Optional[UserSettings] = Unassigned()
    domain_settings: Optional[DomainSettings] = Unassigned()
    app_network_access_type: Optional[str] = Unassigned()
    home_efs_file_system_kms_key_id: Optional[str] = Unassigned()
    subnet_ids: Optional[List[str]] = Unassigned()
    url: Optional[str] = Unassigned()
    vpc_id: Optional[str] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    app_security_group_management: Optional[str] = Unassigned()
    default_space_settings: Optional[DefaultSpaceSettings] = Unassigned()
    
    @classmethod
    def create(
        cls,
        domain_name: str,
        auth_mode: str,
        default_user_settings: UserSettings,
        subnet_ids: List[str],
        vpc_id: str,
        domain_settings: Optional[DomainSettings] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        app_network_access_type: Optional[str] = Unassigned(),
        home_efs_file_system_kms_key_id: Optional[str] = Unassigned(),
        kms_key_id: Optional[str] = Unassigned(),
        app_security_group_management: Optional[str] = Unassigned(),
        default_space_settings: Optional[DefaultSpaceSettings] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating domain resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'DomainName': domain_name,
            'AuthMode': auth_mode,
            'DefaultUserSettings': default_user_settings,
            'DomainSettings': domain_settings,
            'SubnetIds': subnet_ids,
            'VpcId': vpc_id,
            'Tags': tags,
            'AppNetworkAccessType': app_network_access_type,
            'HomeEfsFileSystemKmsKeyId': home_efs_file_system_kms_key_id,
            'KmsKeyId': kms_key_id,
            'AppSecurityGroupManagement': app_security_group_management,
            'DefaultSpaceSettings': default_space_settings,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_domain(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(domain_id=response['DomainId'], session=session, region=region)
    
    @classmethod
    def get(
        cls,
        domain_id: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'DomainId': domain_id,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_domain(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeDomainResponse')
        domain = cls(**transformed_response)
        return domain
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'DomainId': self.domain_id,
        }
        client = SageMakerClient().client
        response = client.describe_domain(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeDomainResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'RetentionPolicy': self.retention_policy,
        }
        self.client.delete_domain(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Deleting', 'Failed', 'InService', 'Pending', 'Updating', 'Update_Failed', 'Delete_Failed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class EdgeDeploymentPlan(Base):
    edge_deployment_plan_arn: str
    edge_deployment_plan_name: str
    model_configs: List[EdgeDeploymentModelConfig]
    device_fleet_name: str
    stages: List[DeploymentStageStatusSummary]
    edge_deployment_success: Optional[int] = Unassigned()
    edge_deployment_pending: Optional[int] = Unassigned()
    edge_deployment_failed: Optional[int] = Unassigned()
    next_token: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    
    @classmethod
    def create(
        cls,
        edge_deployment_plan_name: str,
        model_configs: List[EdgeDeploymentModelConfig],
        device_fleet_name: str,
        stages: Optional[List[DeploymentStage]] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating edge_deployment_plan resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'EdgeDeploymentPlanName': edge_deployment_plan_name,
            'ModelConfigs': model_configs,
            'DeviceFleetName': device_fleet_name,
            'Stages': stages,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_edge_deployment_plan(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(edge_deployment_plan_name=edge_deployment_plan_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        edge_deployment_plan_name: str,
        next_token: Optional[str] = Unassigned(),
        max_results: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'EdgeDeploymentPlanName': edge_deployment_plan_name,
            'NextToken': next_token,
            'MaxResults': max_results,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_edge_deployment_plan(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeEdgeDeploymentPlanResponse')
        edge_deployment_plan = cls(**transformed_response)
        return edge_deployment_plan
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'EdgeDeploymentPlanName': self.edge_deployment_plan_name,
            'NextToken': self.next_token,
            'MaxResults': self.max_results,
        }
        client = SageMakerClient().client
        response = client.describe_edge_deployment_plan(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeEdgeDeploymentPlanResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'EdgeDeploymentPlanName': self.edge_deployment_plan_name,
        }
        self.client.delete_edge_deployment_plan(**operation_input_args)


class EdgePackagingJob(Base):
    edge_packaging_job_arn: str
    edge_packaging_job_name: str
    edge_packaging_job_status: str
    compilation_job_name: Optional[str] = Unassigned()
    model_name: Optional[str] = Unassigned()
    model_version: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    output_config: Optional[EdgeOutputConfig] = Unassigned()
    resource_key: Optional[str] = Unassigned()
    edge_packaging_job_status_message: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    model_artifact: Optional[str] = Unassigned()
    model_signature: Optional[str] = Unassigned()
    preset_deployment_output: Optional[EdgePresetDeploymentOutput] = Unassigned()
    
    @classmethod
    def create(
        cls,
        edge_packaging_job_name: str,
        compilation_job_name: str,
        model_name: str,
        model_version: str,
        role_arn: str,
        output_config: EdgeOutputConfig,
        resource_key: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating edge_packaging_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'EdgePackagingJobName': edge_packaging_job_name,
            'CompilationJobName': compilation_job_name,
            'ModelName': model_name,
            'ModelVersion': model_version,
            'RoleArn': role_arn,
            'OutputConfig': output_config,
            'ResourceKey': resource_key,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_edge_packaging_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(edge_packaging_job_name=edge_packaging_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        edge_packaging_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'EdgePackagingJobName': edge_packaging_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_edge_packaging_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeEdgePackagingJobResponse')
        edge_packaging_job = cls(**transformed_response)
        return edge_packaging_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'EdgePackagingJobName': self.edge_packaging_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_edge_packaging_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeEdgePackagingJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'EdgePackagingJobName': self.edge_packaging_job_name,
        }
        self.client.stop_edge_packaging_job(**operation_input_args)
    
    @validate_call
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        terminal_states = ['COMPLETED', 'FAILED', 'STOPPED']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.edge_packaging_job_status
    
            if current_status in terminal_states:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class Endpoint(Base):
    endpoint_name: str
    endpoint_arn: str
    endpoint_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    endpoint_config_name: Optional[str] = Unassigned()
    production_variants: Optional[List[ProductionVariantSummary]] = Unassigned()
    data_capture_config: Optional[DataCaptureConfigSummary] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    last_deployment_config: Optional[DeploymentConfig] = Unassigned()
    async_inference_config: Optional[AsyncInferenceConfig] = Unassigned()
    pending_deployment_summary: Optional[PendingDeploymentSummary] = Unassigned()
    explainer_config: Optional[ExplainerConfig] = Unassigned()
    shadow_production_variants: Optional[List[ProductionVariantSummary]] = Unassigned()
    
    @classmethod
    def create(
        cls,
        endpoint_name: str,
        endpoint_config_name: str,
        deployment_config: Optional[DeploymentConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating endpoint resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'EndpointName': endpoint_name,
            'EndpointConfigName': endpoint_config_name,
            'DeploymentConfig': deployment_config,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_endpoint(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(endpoint_name=endpoint_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        endpoint_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'EndpointName': endpoint_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_endpoint(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeEndpointOutput')
        endpoint = cls(**transformed_response)
        return endpoint
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'EndpointName': self.endpoint_name,
        }
        client = SageMakerClient().client
        response = client.describe_endpoint(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeEndpointOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'EndpointName': self.endpoint_name,
        }
        self.client.delete_endpoint(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['OutOfService', 'Creating', 'Updating', 'SystemUpdating', 'RollingBack', 'InService', 'Deleting', 'Failed', 'UpdateRollbackFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.endpoint_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class EndpointConfig(Base):
    endpoint_config_name: str
    endpoint_config_arn: str
    production_variants: List[ProductionVariant]
    creation_time: datetime.datetime
    data_capture_config: Optional[DataCaptureConfig] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    async_inference_config: Optional[AsyncInferenceConfig] = Unassigned()
    explainer_config: Optional[ExplainerConfig] = Unassigned()
    shadow_production_variants: Optional[List[ProductionVariant]] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    
    @classmethod
    def create(
        cls,
        endpoint_config_name: str,
        production_variants: List[ProductionVariant],
        data_capture_config: Optional[DataCaptureConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        kms_key_id: Optional[str] = Unassigned(),
        async_inference_config: Optional[AsyncInferenceConfig] = Unassigned(),
        explainer_config: Optional[ExplainerConfig] = Unassigned(),
        shadow_production_variants: Optional[List[ProductionVariant]] = Unassigned(),
        execution_role_arn: Optional[str] = Unassigned(),
        vpc_config: Optional[VpcConfig] = Unassigned(),
        enable_network_isolation: Optional[bool] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating endpoint_config resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'EndpointConfigName': endpoint_config_name,
            'ProductionVariants': production_variants,
            'DataCaptureConfig': data_capture_config,
            'Tags': tags,
            'KmsKeyId': kms_key_id,
            'AsyncInferenceConfig': async_inference_config,
            'ExplainerConfig': explainer_config,
            'ShadowProductionVariants': shadow_production_variants,
            'ExecutionRoleArn': execution_role_arn,
            'VpcConfig': vpc_config,
            'EnableNetworkIsolation': enable_network_isolation,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_endpoint_config(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(endpoint_config_name=endpoint_config_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        endpoint_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'EndpointConfigName': endpoint_config_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_endpoint_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeEndpointConfigOutput')
        endpoint_config = cls(**transformed_response)
        return endpoint_config
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'EndpointConfigName': self.endpoint_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_endpoint_config(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeEndpointConfigOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'EndpointConfigName': self.endpoint_config_name,
        }
        self.client.delete_endpoint_config(**operation_input_args)


class Experiment(Base):
    experiment_name: Optional[str] = Unassigned()
    experiment_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    source: Optional[ExperimentSource] = Unassigned()
    description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    
    @classmethod
    def create(
        cls,
        experiment_name: str,
        display_name: Optional[str] = Unassigned(),
        description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating experiment resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ExperimentName': experiment_name,
            'DisplayName': display_name,
            'Description': description,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_experiment(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(experiment_name=experiment_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        experiment_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ExperimentName': experiment_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_experiment(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeExperimentResponse')
        experiment = cls(**transformed_response)
        return experiment
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ExperimentName': self.experiment_name,
        }
        client = SageMakerClient().client
        response = client.describe_experiment(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeExperimentResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ExperimentName': self.experiment_name,
        }
        self.client.delete_experiment(**operation_input_args)


class FeatureGroup(Base):
    feature_group_arn: str
    feature_group_name: str
    record_identifier_feature_name: str
    event_time_feature_name: str
    feature_definitions: List[FeatureDefinition]
    creation_time: datetime.datetime
    next_token: str
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    online_store_config: Optional[OnlineStoreConfig] = Unassigned()
    offline_store_config: Optional[OfflineStoreConfig] = Unassigned()
    throughput_config: Optional[ThroughputConfigDescription] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    feature_group_status: Optional[str] = Unassigned()
    offline_store_status: Optional[OfflineStoreStatus] = Unassigned()
    last_update_status: Optional[LastUpdateStatus] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    online_store_total_size_bytes: Optional[int] = Unassigned()
    
    @classmethod
    def create(
        cls,
        feature_group_name: str,
        record_identifier_feature_name: str,
        event_time_feature_name: str,
        feature_definitions: List[FeatureDefinition],
        online_store_config: Optional[OnlineStoreConfig] = Unassigned(),
        offline_store_config: Optional[OfflineStoreConfig] = Unassigned(),
        throughput_config: Optional[ThroughputConfig] = Unassigned(),
        role_arn: Optional[str] = Unassigned(),
        description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating feature_group resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'FeatureGroupName': feature_group_name,
            'RecordIdentifierFeatureName': record_identifier_feature_name,
            'EventTimeFeatureName': event_time_feature_name,
            'FeatureDefinitions': feature_definitions,
            'OnlineStoreConfig': online_store_config,
            'OfflineStoreConfig': offline_store_config,
            'ThroughputConfig': throughput_config,
            'RoleArn': role_arn,
            'Description': description,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_feature_group(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(feature_group_name=feature_group_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        feature_group_name: str,
        next_token: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'FeatureGroupName': feature_group_name,
            'NextToken': next_token,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_feature_group(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeFeatureGroupResponse')
        feature_group = cls(**transformed_response)
        return feature_group
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'FeatureGroupName': self.feature_group_name,
            'NextToken': self.next_token,
        }
        client = SageMakerClient().client
        response = client.describe_feature_group(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeFeatureGroupResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'FeatureGroupName': self.feature_group_name,
        }
        self.client.delete_feature_group(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Creating', 'Created', 'CreateFailed', 'Deleting', 'DeleteFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.feature_group_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class FlowDefinition(Base):
    flow_definition_arn: str
    flow_definition_name: str
    flow_definition_status: str
    creation_time: datetime.datetime
    output_config: FlowDefinitionOutputConfig
    role_arn: str
    human_loop_request_source: Optional[HumanLoopRequestSource] = Unassigned()
    human_loop_activation_config: Optional[HumanLoopActivationConfig] = Unassigned()
    human_loop_config: Optional[HumanLoopConfig] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        flow_definition_name: str,
        output_config: FlowDefinitionOutputConfig,
        role_arn: str,
        human_loop_request_source: Optional[HumanLoopRequestSource] = Unassigned(),
        human_loop_activation_config: Optional[HumanLoopActivationConfig] = Unassigned(),
        human_loop_config: Optional[HumanLoopConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating flow_definition resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'FlowDefinitionName': flow_definition_name,
            'HumanLoopRequestSource': human_loop_request_source,
            'HumanLoopActivationConfig': human_loop_activation_config,
            'HumanLoopConfig': human_loop_config,
            'OutputConfig': output_config,
            'RoleArn': role_arn,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_flow_definition(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(flow_definition_name=flow_definition_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        flow_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'FlowDefinitionName': flow_definition_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_flow_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeFlowDefinitionResponse')
        flow_definition = cls(**transformed_response)
        return flow_definition
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'FlowDefinitionName': self.flow_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_flow_definition(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeFlowDefinitionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'FlowDefinitionName': self.flow_definition_name,
        }
        self.client.delete_flow_definition(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Initializing', 'Active', 'Failed', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.flow_definition_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class Hub(Base):
    hub_name: str
    hub_arn: str
    hub_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    hub_display_name: Optional[str] = Unassigned()
    hub_description: Optional[str] = Unassigned()
    hub_search_keywords: Optional[List[str]] = Unassigned()
    s3_storage_config: Optional[HubS3StorageConfig] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        hub_name: str,
        hub_description: str,
        hub_display_name: Optional[str] = Unassigned(),
        hub_search_keywords: Optional[List[str]] = Unassigned(),
        s3_storage_config: Optional[HubS3StorageConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating hub resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'HubName': hub_name,
            'HubDescription': hub_description,
            'HubDisplayName': hub_display_name,
            'HubSearchKeywords': hub_search_keywords,
            'S3StorageConfig': s3_storage_config,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_hub(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(hub_name=hub_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        hub_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'HubName': hub_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_hub(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeHubResponse')
        hub = cls(**transformed_response)
        return hub
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'HubName': self.hub_name,
        }
        client = SageMakerClient().client
        response = client.describe_hub(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeHubResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'HubName': self.hub_name,
        }
        self.client.delete_hub(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['InService', 'Creating', 'Updating', 'Deleting', 'CreateFailed', 'UpdateFailed', 'DeleteFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.hub_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class HubContent(Base):
    hub_content_name: str
    hub_content_arn: str
    hub_content_version: str
    hub_content_type: str
    document_schema_version: str
    hub_name: str
    hub_arn: str
    hub_content_document: str
    hub_content_status: str
    creation_time: datetime.datetime
    hub_content_display_name: Optional[str] = Unassigned()
    hub_content_description: Optional[str] = Unassigned()
    hub_content_markdown: Optional[str] = Unassigned()
    hub_content_search_keywords: Optional[List[str]] = Unassigned()
    hub_content_dependencies: Optional[List[HubContentDependency]] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    
    @classmethod
    def get(
        cls,
        hub_name: str,
        hub_content_type: str,
        hub_content_name: str,
        hub_content_version: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'HubName': hub_name,
            'HubContentType': hub_content_type,
            'HubContentName': hub_content_name,
            'HubContentVersion': hub_content_version,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_hub_content(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeHubContentResponse')
        hub_content = cls(**transformed_response)
        return hub_content
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'HubName': self.hub_name,
            'HubContentType': self.hub_content_type,
            'HubContentName': self.hub_content_name,
            'HubContentVersion': self.hub_content_version,
        }
        client = SageMakerClient().client
        response = client.describe_hub_content(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeHubContentResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'HubName': self.hub_name,
            'HubContentType': self.hub_content_type,
            'HubContentName': self.hub_content_name,
            'HubContentVersion': self.hub_content_version,
        }
        self.client.delete_hub_content(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Available', 'Importing', 'Deleting', 'ImportFailed', 'DeleteFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.hub_content_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class HumanTaskUi(Base):
    human_task_ui_arn: str
    human_task_ui_name: str
    creation_time: datetime.datetime
    ui_template: UiTemplateInfo
    human_task_ui_status: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        human_task_ui_name: str,
        ui_template: UiTemplate,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating human_task_ui resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'HumanTaskUiName': human_task_ui_name,
            'UiTemplate': ui_template,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_human_task_ui(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(human_task_ui_name=human_task_ui_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        human_task_ui_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'HumanTaskUiName': human_task_ui_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_human_task_ui(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeHumanTaskUiResponse')
        human_task_ui = cls(**transformed_response)
        return human_task_ui
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'HumanTaskUiName': self.human_task_ui_name,
        }
        client = SageMakerClient().client
        response = client.describe_human_task_ui(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeHumanTaskUiResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'HumanTaskUiName': self.human_task_ui_name,
        }
        self.client.delete_human_task_ui(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Active', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.human_task_ui_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class HyperParameterTuningJob(Base):
    hyper_parameter_tuning_job_name: str
    hyper_parameter_tuning_job_arn: str
    hyper_parameter_tuning_job_config: HyperParameterTuningJobConfig
    hyper_parameter_tuning_job_status: str
    creation_time: datetime.datetime
    training_job_status_counters: TrainingJobStatusCounters
    objective_status_counters: ObjectiveStatusCounters
    training_job_definition: Optional[HyperParameterTrainingJobDefinition] = Unassigned()
    training_job_definitions: Optional[List[HyperParameterTrainingJobDefinition]] = Unassigned()
    hyper_parameter_tuning_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    best_training_job: Optional[HyperParameterTrainingJobSummary] = Unassigned()
    overall_best_training_job: Optional[HyperParameterTrainingJobSummary] = Unassigned()
    warm_start_config: Optional[HyperParameterTuningJobWarmStartConfig] = Unassigned()
    autotune: Optional[Autotune] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    tuning_job_completion_details: Optional[HyperParameterTuningJobCompletionDetails] = Unassigned()
    consumed_resources: Optional[HyperParameterTuningJobConsumedResources] = Unassigned()
    
    @classmethod
    def create(
        cls,
        hyper_parameter_tuning_job_name: str,
        hyper_parameter_tuning_job_config: HyperParameterTuningJobConfig,
        training_job_definition: Optional[HyperParameterTrainingJobDefinition] = Unassigned(),
        training_job_definitions: Optional[List[HyperParameterTrainingJobDefinition]] = Unassigned(),
        warm_start_config: Optional[HyperParameterTuningJobWarmStartConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        autotune: Optional[Autotune] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating hyper_parameter_tuning_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'HyperParameterTuningJobName': hyper_parameter_tuning_job_name,
            'HyperParameterTuningJobConfig': hyper_parameter_tuning_job_config,
            'TrainingJobDefinition': training_job_definition,
            'TrainingJobDefinitions': training_job_definitions,
            'WarmStartConfig': warm_start_config,
            'Tags': tags,
            'Autotune': autotune,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_hyper_parameter_tuning_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(hyper_parameter_tuning_job_name=hyper_parameter_tuning_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        hyper_parameter_tuning_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'HyperParameterTuningJobName': hyper_parameter_tuning_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_hyper_parameter_tuning_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeHyperParameterTuningJobResponse')
        hyper_parameter_tuning_job = cls(**transformed_response)
        return hyper_parameter_tuning_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'HyperParameterTuningJobName': self.hyper_parameter_tuning_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_hyper_parameter_tuning_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeHyperParameterTuningJobResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'HyperParameterTuningJobName': self.hyper_parameter_tuning_job_name,
        }
        self.client.delete_hyper_parameter_tuning_job(**operation_input_args)
    
    def stop(self) -> None:
    
        operation_input_args = {
            'HyperParameterTuningJobName': self.hyper_parameter_tuning_job_name,
        }
        self.client.stop_hyper_parameter_tuning_job(**operation_input_args)
    
    @validate_call
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        terminal_states = ['Completed', 'Failed', 'Stopped', 'DeleteFailed']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.hyper_parameter_tuning_job_status
    
            if current_status in terminal_states:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class Image(Base):
    creation_time: Optional[datetime.datetime] = Unassigned()
    description: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    image_arn: Optional[str] = Unassigned()
    image_name: Optional[str] = Unassigned()
    image_status: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        image_name: str,
        role_arn: str,
        description: Optional[str] = Unassigned(),
        display_name: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating image resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'Description': description,
            'DisplayName': display_name,
            'ImageName': image_name,
            'RoleArn': role_arn,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_image(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(image_name=image_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        image_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ImageName': image_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_image(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeImageResponse')
        image = cls(**transformed_response)
        return image
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ImageName': self.image_name,
        }
        client = SageMakerClient().client
        response = client.describe_image(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeImageResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ImageName': self.image_name,
        }
        self.client.delete_image(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['CREATING', 'CREATED', 'CREATE_FAILED', 'UPDATING', 'UPDATE_FAILED', 'DELETING', 'DELETE_FAILED'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.image_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class ImageVersion(Base):
    base_image: Optional[str] = Unassigned()
    container_image: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    image_arn: Optional[str] = Unassigned()
    image_version_arn: Optional[str] = Unassigned()
    image_version_status: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    version: Optional[int] = Unassigned()
    vendor_guidance: Optional[str] = Unassigned()
    job_type: Optional[str] = Unassigned()
    m_l_framework: Optional[str] = Unassigned()
    programming_lang: Optional[str] = Unassigned()
    processor: Optional[str] = Unassigned()
    horovod: Optional[bool] = Unassigned()
    release_notes: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        base_image: str,
        client_token: str,
        image_name: str,
        aliases: Optional[List[str]] = Unassigned(),
        vendor_guidance: Optional[str] = Unassigned(),
        job_type: Optional[str] = Unassigned(),
        m_l_framework: Optional[str] = Unassigned(),
        programming_lang: Optional[str] = Unassigned(),
        processor: Optional[str] = Unassigned(),
        horovod: Optional[bool] = Unassigned(),
        release_notes: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating image_version resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'BaseImage': base_image,
            'ClientToken': client_token,
            'ImageName': image_name,
            'Aliases': aliases,
            'VendorGuidance': vendor_guidance,
            'JobType': job_type,
            'MLFramework': m_l_framework,
            'ProgrammingLang': programming_lang,
            'Processor': processor,
            'Horovod': horovod,
            'ReleaseNotes': release_notes,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_image_version(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(image_name=image_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        image_name: str,
        version: Optional[int] = Unassigned(),
        alias: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ImageName': image_name,
            'Version': version,
            'Alias': alias,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_image_version(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeImageVersionResponse')
        image_version = cls(**transformed_response)
        return image_version
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ImageName': self.image_name,
            'Version': self.version,
            'Alias': self.alias,
        }
        client = SageMakerClient().client
        response = client.describe_image_version(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeImageVersionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ImageName': self.image_name,
            'Version': self.version,
            'Alias': self.alias,
        }
        self.client.delete_image_version(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['CREATING', 'CREATED', 'CREATE_FAILED', 'DELETING', 'DELETE_FAILED'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.image_version_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class InferenceComponent(Base):
    inference_component_name: str
    inference_component_arn: str
    endpoint_name: str
    endpoint_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    variant_name: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    specification: Optional[InferenceComponentSpecificationSummary] = Unassigned()
    runtime_config: Optional[InferenceComponentRuntimeConfigSummary] = Unassigned()
    inference_component_status: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        inference_component_name: str,
        endpoint_name: str,
        variant_name: str,
        specification: InferenceComponentSpecification,
        runtime_config: InferenceComponentRuntimeConfig,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating inference_component resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'InferenceComponentName': inference_component_name,
            'EndpointName': endpoint_name,
            'VariantName': variant_name,
            'Specification': specification,
            'RuntimeConfig': runtime_config,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_inference_component(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(inference_component_name=inference_component_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        inference_component_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'InferenceComponentName': inference_component_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_inference_component(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeInferenceComponentOutput')
        inference_component = cls(**transformed_response)
        return inference_component
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'InferenceComponentName': self.inference_component_name,
        }
        client = SageMakerClient().client
        response = client.describe_inference_component(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeInferenceComponentOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'InferenceComponentName': self.inference_component_name,
        }
        self.client.delete_inference_component(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['InService', 'Creating', 'Updating', 'Failed', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.inference_component_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class InferenceExperiment(Base):
    arn: str
    name: str
    type: str
    status: str
    endpoint_metadata: EndpointMetadata
    model_variants: List[ModelVariantConfigSummary]
    schedule: Optional[InferenceExperimentSchedule] = Unassigned()
    status_reason: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    completion_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    data_storage_config: Optional[InferenceExperimentDataStorageConfig] = Unassigned()
    shadow_mode_config: Optional[ShadowModeConfig] = Unassigned()
    kms_key: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        name: str,
        type: str,
        role_arn: str,
        endpoint_name: str,
        model_variants: List[ModelVariantConfig],
        shadow_mode_config: ShadowModeConfig,
        schedule: Optional[InferenceExperimentSchedule] = Unassigned(),
        description: Optional[str] = Unassigned(),
        data_storage_config: Optional[InferenceExperimentDataStorageConfig] = Unassigned(),
        kms_key: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating inference_experiment resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'Name': name,
            'Type': type,
            'Schedule': schedule,
            'Description': description,
            'RoleArn': role_arn,
            'EndpointName': endpoint_name,
            'ModelVariants': model_variants,
            'DataStorageConfig': data_storage_config,
            'ShadowModeConfig': shadow_mode_config,
            'KmsKey': kms_key,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_inference_experiment(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(name=name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'Name': name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_inference_experiment(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeInferenceExperimentResponse')
        inference_experiment = cls(**transformed_response)
        return inference_experiment
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'Name': self.name,
        }
        client = SageMakerClient().client
        response = client.describe_inference_experiment(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeInferenceExperimentResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'Name': self.name,
        }
        self.client.delete_inference_experiment(**operation_input_args)
    
    def stop(self) -> None:
    
        operation_input_args = {
            'Name': self.name,
            'ModelVariantActions': self.model_variant_actions,
            'DesiredModelVariants': self.desired_model_variants,
            'DesiredState': self.desired_state,
            'Reason': self.reason,
        }
        self.client.stop_inference_experiment(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Creating', 'Created', 'Updating', 'Running', 'Starting', 'Stopping', 'Completed', 'Cancelled'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class InferenceRecommendationsJob(Base):
    job_name: str
    job_type: str
    job_arn: str
    role_arn: str
    status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    input_config: RecommendationJobInputConfig
    job_description: Optional[str] = Unassigned()
    completion_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    stopping_conditions: Optional[RecommendationJobStoppingConditions] = Unassigned()
    inference_recommendations: Optional[List[InferenceRecommendation]] = Unassigned()
    endpoint_performances: Optional[List[EndpointPerformance]] = Unassigned()
    
    @classmethod
    def create(
        cls,
        job_name: str,
        job_type: str,
        role_arn: str,
        input_config: RecommendationJobInputConfig,
        job_description: Optional[str] = Unassigned(),
        stopping_conditions: Optional[RecommendationJobStoppingConditions] = Unassigned(),
        output_config: Optional[RecommendationJobOutputConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating inference_recommendations_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'JobName': job_name,
            'JobType': job_type,
            'RoleArn': role_arn,
            'InputConfig': input_config,
            'JobDescription': job_description,
            'StoppingConditions': stopping_conditions,
            'OutputConfig': output_config,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_inference_recommendations_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(job_name=job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'JobName': job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_inference_recommendations_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeInferenceRecommendationsJobResponse')
        inference_recommendations_job = cls(**transformed_response)
        return inference_recommendations_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'JobName': self.job_name,
        }
        client = SageMakerClient().client
        response = client.describe_inference_recommendations_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeInferenceRecommendationsJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'JobName': self.job_name,
        }
        self.client.stop_inference_recommendations_job(**operation_input_args)
    
    @validate_call
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        terminal_states = ['COMPLETED', 'FAILED', 'STOPPED', 'DELETED']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if current_status in terminal_states:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class LabelingJob(Base):
    labeling_job_status: str
    label_counters: LabelCounters
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    job_reference_code: str
    labeling_job_name: str
    labeling_job_arn: str
    input_config: LabelingJobInputConfig
    output_config: LabelingJobOutputConfig
    role_arn: str
    human_task_config: HumanTaskConfig
    failure_reason: Optional[str] = Unassigned()
    label_attribute_name: Optional[str] = Unassigned()
    label_category_config_s3_uri: Optional[str] = Unassigned()
    stopping_conditions: Optional[LabelingJobStoppingConditions] = Unassigned()
    labeling_job_algorithms_config: Optional[LabelingJobAlgorithmsConfig] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()
    labeling_job_output: Optional[LabelingJobOutput] = Unassigned()
    
    @classmethod
    def create(
        cls,
        labeling_job_name: str,
        label_attribute_name: str,
        input_config: LabelingJobInputConfig,
        output_config: LabelingJobOutputConfig,
        role_arn: str,
        human_task_config: HumanTaskConfig,
        label_category_config_s3_uri: Optional[str] = Unassigned(),
        stopping_conditions: Optional[LabelingJobStoppingConditions] = Unassigned(),
        labeling_job_algorithms_config: Optional[LabelingJobAlgorithmsConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating labeling_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'LabelingJobName': labeling_job_name,
            'LabelAttributeName': label_attribute_name,
            'InputConfig': input_config,
            'OutputConfig': output_config,
            'RoleArn': role_arn,
            'LabelCategoryConfigS3Uri': label_category_config_s3_uri,
            'StoppingConditions': stopping_conditions,
            'LabelingJobAlgorithmsConfig': labeling_job_algorithms_config,
            'HumanTaskConfig': human_task_config,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_labeling_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(labeling_job_name=labeling_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        labeling_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'LabelingJobName': labeling_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_labeling_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeLabelingJobResponse')
        labeling_job = cls(**transformed_response)
        return labeling_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'LabelingJobName': self.labeling_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_labeling_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeLabelingJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'LabelingJobName': self.labeling_job_name,
        }
        self.client.stop_labeling_job(**operation_input_args)
    
    @validate_call
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.labeling_job_status
    
            if current_status in terminal_states:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class Model(Base):
    model_name: str
    creation_time: datetime.datetime
    model_arn: str
    primary_container: Optional[ContainerDefinition] = Unassigned()
    containers: Optional[List[ContainerDefinition]] = Unassigned()
    inference_execution_config: Optional[InferenceExecutionConfig] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    deployment_recommendation: Optional[DeploymentRecommendation] = Unassigned()
    
    @classmethod
    def create(
        cls,
        model_name: str,
        primary_container: Optional[ContainerDefinition] = Unassigned(),
        containers: Optional[List[ContainerDefinition]] = Unassigned(),
        inference_execution_config: Optional[InferenceExecutionConfig] = Unassigned(),
        execution_role_arn: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        vpc_config: Optional[VpcConfig] = Unassigned(),
        enable_network_isolation: Optional[bool] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating model resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ModelName': model_name,
            'PrimaryContainer': primary_container,
            'Containers': containers,
            'InferenceExecutionConfig': inference_execution_config,
            'ExecutionRoleArn': execution_role_arn,
            'Tags': tags,
            'VpcConfig': vpc_config,
            'EnableNetworkIsolation': enable_network_isolation,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(model_name=model_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        model_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ModelName': model_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelOutput')
        model = cls(**transformed_response)
        return model
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ModelName': self.model_name,
        }
        client = SageMakerClient().client
        response = client.describe_model(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelName': self.model_name,
        }
        self.client.delete_model(**operation_input_args)


class ModelBiasJobDefinition(Base):
    job_definition_arn: str
    job_definition_name: str
    creation_time: datetime.datetime
    model_bias_app_specification: ModelBiasAppSpecification
    model_bias_job_input: ModelBiasJobInput
    model_bias_job_output_config: MonitoringOutputConfig
    job_resources: MonitoringResources
    role_arn: str
    model_bias_baseline_config: Optional[ModelBiasBaselineConfig] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    @classmethod
    def create(
        cls,
        job_definition_name: str,
        model_bias_app_specification: ModelBiasAppSpecification,
        model_bias_job_input: ModelBiasJobInput,
        model_bias_job_output_config: MonitoringOutputConfig,
        job_resources: MonitoringResources,
        role_arn: str,
        model_bias_baseline_config: Optional[ModelBiasBaselineConfig] = Unassigned(),
        network_config: Optional[MonitoringNetworkConfig] = Unassigned(),
        stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating model_bias_job_definition resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
            'ModelBiasBaselineConfig': model_bias_baseline_config,
            'ModelBiasAppSpecification': model_bias_app_specification,
            'ModelBiasJobInput': model_bias_job_input,
            'ModelBiasJobOutputConfig': model_bias_job_output_config,
            'JobResources': job_resources,
            'NetworkConfig': network_config,
            'RoleArn': role_arn,
            'StoppingCondition': stopping_condition,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_bias_job_definition(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(job_definition_name=job_definition_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_bias_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelBiasJobDefinitionResponse')
        model_bias_job_definition = cls(**transformed_response)
        return model_bias_job_definition
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_bias_job_definition(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelBiasJobDefinitionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_model_bias_job_definition(**operation_input_args)


class ModelCard(Base):
    model_card_arn: str
    model_card_name: str
    model_card_version: int
    content: str
    model_card_status: str
    creation_time: datetime.datetime
    created_by: UserContext
    security_config: Optional[ModelCardSecurityConfig] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    model_card_processing_status: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        model_card_name: str,
        content: str,
        model_card_status: str,
        security_config: Optional[ModelCardSecurityConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating model_card resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ModelCardName': model_card_name,
            'SecurityConfig': security_config,
            'Content': content,
            'ModelCardStatus': model_card_status,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_card(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(model_card_name=model_card_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        model_card_name: str,
        model_card_version: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ModelCardName': model_card_name,
            'ModelCardVersion': model_card_version,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_card(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelCardResponse')
        model_card = cls(**transformed_response)
        return model_card
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ModelCardName': self.model_card_name,
            'ModelCardVersion': self.model_card_version,
        }
        client = SageMakerClient().client
        response = client.describe_model_card(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelCardResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelCardName': self.model_card_name,
        }
        self.client.delete_model_card(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Draft', 'PendingReview', 'Approved', 'Archived'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.model_card_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class ModelCardExportJob(Base):
    model_card_export_job_name: str
    model_card_export_job_arn: str
    status: str
    model_card_name: str
    model_card_version: int
    output_config: ModelCardExportOutputConfig
    created_at: datetime.datetime
    last_modified_at: datetime.datetime
    failure_reason: Optional[str] = Unassigned()
    export_artifacts: Optional[ModelCardExportArtifacts] = Unassigned()
    
    @classmethod
    def create(
        cls,
        model_card_name: str,
        model_card_export_job_name: str,
        output_config: ModelCardExportOutputConfig,
        model_card_version: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating model_card_export_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ModelCardName': model_card_name,
            'ModelCardVersion': model_card_version,
            'ModelCardExportJobName': model_card_export_job_name,
            'OutputConfig': output_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_card_export_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(model_card_export_job_arn=response['ModelCardExportJobArn'], session=session, region=region)
    
    @classmethod
    def get(
        cls,
        model_card_export_job_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ModelCardExportJobArn': model_card_export_job_arn,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_card_export_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelCardExportJobResponse')
        model_card_export_job = cls(**transformed_response)
        return model_card_export_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ModelCardExportJobArn': self.model_card_export_job_arn,
        }
        client = SageMakerClient().client
        response = client.describe_model_card_export_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelCardExportJobResponse', self)
        return self
    
    @validate_call
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        terminal_states = ['Completed', 'Failed']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if current_status in terminal_states:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class ModelExplainabilityJobDefinition(Base):
    job_definition_arn: str
    job_definition_name: str
    creation_time: datetime.datetime
    model_explainability_app_specification: ModelExplainabilityAppSpecification
    model_explainability_job_input: ModelExplainabilityJobInput
    model_explainability_job_output_config: MonitoringOutputConfig
    job_resources: MonitoringResources
    role_arn: str
    model_explainability_baseline_config: Optional[ModelExplainabilityBaselineConfig] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    @classmethod
    def create(
        cls,
        job_definition_name: str,
        model_explainability_app_specification: ModelExplainabilityAppSpecification,
        model_explainability_job_input: ModelExplainabilityJobInput,
        model_explainability_job_output_config: MonitoringOutputConfig,
        job_resources: MonitoringResources,
        role_arn: str,
        model_explainability_baseline_config: Optional[ModelExplainabilityBaselineConfig] = Unassigned(),
        network_config: Optional[MonitoringNetworkConfig] = Unassigned(),
        stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating model_explainability_job_definition resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
            'ModelExplainabilityBaselineConfig': model_explainability_baseline_config,
            'ModelExplainabilityAppSpecification': model_explainability_app_specification,
            'ModelExplainabilityJobInput': model_explainability_job_input,
            'ModelExplainabilityJobOutputConfig': model_explainability_job_output_config,
            'JobResources': job_resources,
            'NetworkConfig': network_config,
            'RoleArn': role_arn,
            'StoppingCondition': stopping_condition,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_explainability_job_definition(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(job_definition_name=job_definition_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_explainability_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelExplainabilityJobDefinitionResponse')
        model_explainability_job_definition = cls(**transformed_response)
        return model_explainability_job_definition
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_explainability_job_definition(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelExplainabilityJobDefinitionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_model_explainability_job_definition(**operation_input_args)


class ModelPackage(Base):
    model_package_name: str
    model_package_arn: str
    creation_time: datetime.datetime
    model_package_status: str
    model_package_status_details: ModelPackageStatusDetails
    model_package_group_name: Optional[str] = Unassigned()
    model_package_version: Optional[int] = Unassigned()
    model_package_description: Optional[str] = Unassigned()
    inference_specification: Optional[InferenceSpecification] = Unassigned()
    source_algorithm_specification: Optional[SourceAlgorithmSpecification] = Unassigned()
    validation_specification: Optional[ModelPackageValidationSpecification] = Unassigned()
    certify_for_marketplace: Optional[bool] = Unassigned()
    model_approval_status: Optional[str] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    model_metrics: Optional[ModelMetrics] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    approval_description: Optional[str] = Unassigned()
    domain: Optional[str] = Unassigned()
    task: Optional[str] = Unassigned()
    sample_payload_url: Optional[str] = Unassigned()
    customer_metadata_properties: Optional[Dict[str, str]] = Unassigned()
    drift_check_baselines: Optional[DriftCheckBaselines] = Unassigned()
    additional_inference_specifications: Optional[List[AdditionalInferenceSpecificationDefinition]] = Unassigned()
    skip_model_validation: Optional[str] = Unassigned()
    source_uri: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        model_package_name: Optional[str] = Unassigned(),
        model_package_group_name: Optional[str] = Unassigned(),
        model_package_description: Optional[str] = Unassigned(),
        inference_specification: Optional[InferenceSpecification] = Unassigned(),
        validation_specification: Optional[ModelPackageValidationSpecification] = Unassigned(),
        source_algorithm_specification: Optional[SourceAlgorithmSpecification] = Unassigned(),
        certify_for_marketplace: Optional[bool] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        model_approval_status: Optional[str] = Unassigned(),
        metadata_properties: Optional[MetadataProperties] = Unassigned(),
        model_metrics: Optional[ModelMetrics] = Unassigned(),
        client_token: Optional[str] = Unassigned(),
        domain: Optional[str] = Unassigned(),
        task: Optional[str] = Unassigned(),
        sample_payload_url: Optional[str] = Unassigned(),
        customer_metadata_properties: Optional[Dict[str, str]] = Unassigned(),
        drift_check_baselines: Optional[DriftCheckBaselines] = Unassigned(),
        additional_inference_specifications: Optional[List[AdditionalInferenceSpecificationDefinition]] = Unassigned(),
        skip_model_validation: Optional[str] = Unassigned(),
        source_uri: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating model_package resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ModelPackageName': model_package_name,
            'ModelPackageGroupName': model_package_group_name,
            'ModelPackageDescription': model_package_description,
            'InferenceSpecification': inference_specification,
            'ValidationSpecification': validation_specification,
            'SourceAlgorithmSpecification': source_algorithm_specification,
            'CertifyForMarketplace': certify_for_marketplace,
            'Tags': tags,
            'ModelApprovalStatus': model_approval_status,
            'MetadataProperties': metadata_properties,
            'ModelMetrics': model_metrics,
            'ClientToken': client_token,
            'Domain': domain,
            'Task': task,
            'SamplePayloadUrl': sample_payload_url,
            'CustomerMetadataProperties': customer_metadata_properties,
            'DriftCheckBaselines': drift_check_baselines,
            'AdditionalInferenceSpecifications': additional_inference_specifications,
            'SkipModelValidation': skip_model_validation,
            'SourceUri': source_uri,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_package(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(model_package_name=response['ModelPackageName'], session=session, region=region)
    
    @classmethod
    def get(
        cls,
        model_package_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ModelPackageName': model_package_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_package(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelPackageOutput')
        model_package = cls(**transformed_response)
        return model_package
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ModelPackageName': self.model_package_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_package(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelPackageOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelPackageName': self.model_package_name,
        }
        self.client.delete_model_package(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Pending', 'InProgress', 'Completed', 'Failed', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.model_package_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class ModelPackageGroup(Base):
    model_package_group_name: str
    model_package_group_arn: str
    creation_time: datetime.datetime
    created_by: UserContext
    model_package_group_status: str
    model_package_group_description: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        model_package_group_name: str,
        model_package_group_description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating model_package_group resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ModelPackageGroupName': model_package_group_name,
            'ModelPackageGroupDescription': model_package_group_description,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_package_group(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(model_package_group_name=model_package_group_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        model_package_group_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ModelPackageGroupName': model_package_group_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_package_group(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelPackageGroupOutput')
        model_package_group = cls(**transformed_response)
        return model_package_group
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ModelPackageGroupName': self.model_package_group_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_package_group(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelPackageGroupOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelPackageGroupName': self.model_package_group_name,
        }
        self.client.delete_model_package_group(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Pending', 'InProgress', 'Completed', 'Failed', 'Deleting', 'DeleteFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.model_package_group_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class ModelQualityJobDefinition(Base):
    job_definition_arn: str
    job_definition_name: str
    creation_time: datetime.datetime
    model_quality_app_specification: ModelQualityAppSpecification
    model_quality_job_input: ModelQualityJobInput
    model_quality_job_output_config: MonitoringOutputConfig
    job_resources: MonitoringResources
    role_arn: str
    model_quality_baseline_config: Optional[ModelQualityBaselineConfig] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    @classmethod
    def create(
        cls,
        job_definition_name: str,
        model_quality_app_specification: ModelQualityAppSpecification,
        model_quality_job_input: ModelQualityJobInput,
        model_quality_job_output_config: MonitoringOutputConfig,
        job_resources: MonitoringResources,
        role_arn: str,
        model_quality_baseline_config: Optional[ModelQualityBaselineConfig] = Unassigned(),
        network_config: Optional[MonitoringNetworkConfig] = Unassigned(),
        stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating model_quality_job_definition resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
            'ModelQualityBaselineConfig': model_quality_baseline_config,
            'ModelQualityAppSpecification': model_quality_app_specification,
            'ModelQualityJobInput': model_quality_job_input,
            'ModelQualityJobOutputConfig': model_quality_job_output_config,
            'JobResources': job_resources,
            'NetworkConfig': network_config,
            'RoleArn': role_arn,
            'StoppingCondition': stopping_condition,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_quality_job_definition(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(job_definition_name=job_definition_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_quality_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelQualityJobDefinitionResponse')
        model_quality_job_definition = cls(**transformed_response)
        return model_quality_job_definition
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_quality_job_definition(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelQualityJobDefinitionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_model_quality_job_definition(**operation_input_args)


class MonitoringSchedule(Base):
    monitoring_schedule_arn: str
    monitoring_schedule_name: str
    monitoring_schedule_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    monitoring_schedule_config: MonitoringScheduleConfig
    monitoring_type: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    endpoint_name: Optional[str] = Unassigned()
    last_monitoring_execution_summary: Optional[MonitoringExecutionSummary] = Unassigned()
    
    @classmethod
    def create(
        cls,
        monitoring_schedule_name: str,
        monitoring_schedule_config: MonitoringScheduleConfig,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating monitoring_schedule resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'MonitoringScheduleName': monitoring_schedule_name,
            'MonitoringScheduleConfig': monitoring_schedule_config,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_monitoring_schedule(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(monitoring_schedule_name=monitoring_schedule_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        monitoring_schedule_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'MonitoringScheduleName': monitoring_schedule_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_monitoring_schedule(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeMonitoringScheduleResponse')
        monitoring_schedule = cls(**transformed_response)
        return monitoring_schedule
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'MonitoringScheduleName': self.monitoring_schedule_name,
        }
        client = SageMakerClient().client
        response = client.describe_monitoring_schedule(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeMonitoringScheduleResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'MonitoringScheduleName': self.monitoring_schedule_name,
        }
        self.client.delete_monitoring_schedule(**operation_input_args)
    
    def stop(self) -> None:
    
        operation_input_args = {
            'MonitoringScheduleName': self.monitoring_schedule_name,
        }
        self.client.stop_monitoring_schedule(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Pending', 'Failed', 'Scheduled', 'Stopped'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.monitoring_schedule_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class NotebookInstance(Base):
    notebook_instance_arn: Optional[str] = Unassigned()
    notebook_instance_name: Optional[str] = Unassigned()
    notebook_instance_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    url: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    subnet_id: Optional[str] = Unassigned()
    security_groups: Optional[List[str]] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    network_interface_id: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    notebook_instance_lifecycle_config_name: Optional[str] = Unassigned()
    direct_internet_access: Optional[str] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    accelerator_types: Optional[List[str]] = Unassigned()
    default_code_repository: Optional[str] = Unassigned()
    additional_code_repositories: Optional[List[str]] = Unassigned()
    root_access: Optional[str] = Unassigned()
    platform_identifier: Optional[str] = Unassigned()
    instance_metadata_service_configuration: Optional[InstanceMetadataServiceConfiguration] = Unassigned()
    
    @classmethod
    def create(
        cls,
        notebook_instance_name: str,
        instance_type: str,
        role_arn: str,
        subnet_id: Optional[str] = Unassigned(),
        security_group_ids: Optional[List[str]] = Unassigned(),
        kms_key_id: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        lifecycle_config_name: Optional[str] = Unassigned(),
        direct_internet_access: Optional[str] = Unassigned(),
        volume_size_in_g_b: Optional[int] = Unassigned(),
        accelerator_types: Optional[List[str]] = Unassigned(),
        default_code_repository: Optional[str] = Unassigned(),
        additional_code_repositories: Optional[List[str]] = Unassigned(),
        root_access: Optional[str] = Unassigned(),
        platform_identifier: Optional[str] = Unassigned(),
        instance_metadata_service_configuration: Optional[InstanceMetadataServiceConfiguration] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating notebook_instance resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'NotebookInstanceName': notebook_instance_name,
            'InstanceType': instance_type,
            'SubnetId': subnet_id,
            'SecurityGroupIds': security_group_ids,
            'RoleArn': role_arn,
            'KmsKeyId': kms_key_id,
            'Tags': tags,
            'LifecycleConfigName': lifecycle_config_name,
            'DirectInternetAccess': direct_internet_access,
            'VolumeSizeInGB': volume_size_in_g_b,
            'AcceleratorTypes': accelerator_types,
            'DefaultCodeRepository': default_code_repository,
            'AdditionalCodeRepositories': additional_code_repositories,
            'RootAccess': root_access,
            'PlatformIdentifier': platform_identifier,
            'InstanceMetadataServiceConfiguration': instance_metadata_service_configuration,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_notebook_instance(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(notebook_instance_name=notebook_instance_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        notebook_instance_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'NotebookInstanceName': notebook_instance_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_notebook_instance(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeNotebookInstanceOutput')
        notebook_instance = cls(**transformed_response)
        return notebook_instance
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'NotebookInstanceName': self.notebook_instance_name,
        }
        client = SageMakerClient().client
        response = client.describe_notebook_instance(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeNotebookInstanceOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'NotebookInstanceName': self.notebook_instance_name,
        }
        self.client.delete_notebook_instance(**operation_input_args)
    
    def stop(self) -> None:
    
        operation_input_args = {
            'NotebookInstanceName': self.notebook_instance_name,
        }
        self.client.stop_notebook_instance(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Pending', 'InService', 'Stopping', 'Stopped', 'Failed', 'Deleting', 'Updating'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.notebook_instance_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class NotebookInstanceLifecycleConfig(Base):
    notebook_instance_lifecycle_config_arn: Optional[str] = Unassigned()
    notebook_instance_lifecycle_config_name: Optional[str] = Unassigned()
    on_create: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned()
    on_start: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    
    @classmethod
    def create(
        cls,
        notebook_instance_lifecycle_config_name: str,
        on_create: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned(),
        on_start: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating notebook_instance_lifecycle_config resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': notebook_instance_lifecycle_config_name,
            'OnCreate': on_create,
            'OnStart': on_start,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_notebook_instance_lifecycle_config(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(notebook_instance_lifecycle_config_name=notebook_instance_lifecycle_config_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        notebook_instance_lifecycle_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': notebook_instance_lifecycle_config_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_notebook_instance_lifecycle_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeNotebookInstanceLifecycleConfigOutput')
        notebook_instance_lifecycle_config = cls(**transformed_response)
        return notebook_instance_lifecycle_config
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': self.notebook_instance_lifecycle_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_notebook_instance_lifecycle_config(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeNotebookInstanceLifecycleConfigOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': self.notebook_instance_lifecycle_config_name,
        }
        self.client.delete_notebook_instance_lifecycle_config(**operation_input_args)


class Pipeline(Base):
    pipeline_arn: Optional[str] = Unassigned()
    pipeline_name: Optional[str] = Unassigned()
    pipeline_display_name: Optional[str] = Unassigned()
    pipeline_definition: Optional[str] = Unassigned()
    pipeline_description: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    pipeline_status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_run_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    parallelism_configuration: Optional[ParallelismConfiguration] = Unassigned()
    
    @classmethod
    def create(
        cls,
        pipeline_name: str,
        client_request_token: str,
        role_arn: str,
        pipeline_display_name: Optional[str] = Unassigned(),
        pipeline_definition: Optional[str] = Unassigned(),
        pipeline_definition_s3_location: Optional[PipelineDefinitionS3Location] = Unassigned(),
        pipeline_description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        parallelism_configuration: Optional[ParallelismConfiguration] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating pipeline resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'PipelineName': pipeline_name,
            'PipelineDisplayName': pipeline_display_name,
            'PipelineDefinition': pipeline_definition,
            'PipelineDefinitionS3Location': pipeline_definition_s3_location,
            'PipelineDescription': pipeline_description,
            'ClientRequestToken': client_request_token,
            'RoleArn': role_arn,
            'Tags': tags,
            'ParallelismConfiguration': parallelism_configuration,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_pipeline(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(pipeline_name=pipeline_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        pipeline_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'PipelineName': pipeline_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_pipeline(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribePipelineResponse')
        pipeline = cls(**transformed_response)
        return pipeline
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'PipelineName': self.pipeline_name,
        }
        client = SageMakerClient().client
        response = client.describe_pipeline(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribePipelineResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'PipelineName': self.pipeline_name,
            'ClientRequestToken': self.client_request_token,
        }
        self.client.delete_pipeline(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Active', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.pipeline_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class PipelineExecution(Base):
    pipeline_arn: Optional[str] = Unassigned()
    pipeline_execution_arn: Optional[str] = Unassigned()
    pipeline_execution_display_name: Optional[str] = Unassigned()
    pipeline_execution_status: Optional[str] = Unassigned()
    pipeline_execution_description: Optional[str] = Unassigned()
    pipeline_experiment_config: Optional[PipelineExperimentConfig] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    parallelism_configuration: Optional[ParallelismConfiguration] = Unassigned()
    selective_execution_config: Optional[SelectiveExecutionConfig] = Unassigned()
    
    @classmethod
    def get(
        cls,
        pipeline_execution_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'PipelineExecutionArn': pipeline_execution_arn,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_pipeline_execution(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribePipelineExecutionResponse')
        pipeline_execution = cls(**transformed_response)
        return pipeline_execution
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'PipelineExecutionArn': self.pipeline_execution_arn,
        }
        client = SageMakerClient().client
        response = client.describe_pipeline_execution(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribePipelineExecutionResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'PipelineExecutionArn': self.pipeline_execution_arn,
            'ClientRequestToken': self.client_request_token,
        }
        self.client.stop_pipeline_execution(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Executing', 'Stopping', 'Stopped', 'Failed', 'Succeeded'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.pipeline_execution_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class ProcessingJob(Base):
    processing_job_name: str
    processing_resources: ProcessingResources
    app_specification: AppSpecification
    processing_job_arn: str
    processing_job_status: str
    creation_time: datetime.datetime
    processing_inputs: Optional[List[ProcessingInput]] = Unassigned()
    processing_output_config: Optional[ProcessingOutputConfig] = Unassigned()
    stopping_condition: Optional[ProcessingStoppingCondition] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    network_config: Optional[NetworkConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    experiment_config: Optional[ExperimentConfig] = Unassigned()
    exit_message: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    processing_end_time: Optional[datetime.datetime] = Unassigned()
    processing_start_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    monitoring_schedule_arn: Optional[str] = Unassigned()
    auto_m_l_job_arn: Optional[str] = Unassigned()
    training_job_arn: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        processing_job_name: str,
        processing_resources: ProcessingResources,
        app_specification: AppSpecification,
        role_arn: str,
        processing_inputs: Optional[List[ProcessingInput]] = Unassigned(),
        processing_output_config: Optional[ProcessingOutputConfig] = Unassigned(),
        stopping_condition: Optional[ProcessingStoppingCondition] = Unassigned(),
        environment: Optional[Dict[str, str]] = Unassigned(),
        network_config: Optional[NetworkConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        experiment_config: Optional[ExperimentConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating processing_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ProcessingInputs': processing_inputs,
            'ProcessingOutputConfig': processing_output_config,
            'ProcessingJobName': processing_job_name,
            'ProcessingResources': processing_resources,
            'StoppingCondition': stopping_condition,
            'AppSpecification': app_specification,
            'Environment': environment,
            'NetworkConfig': network_config,
            'RoleArn': role_arn,
            'Tags': tags,
            'ExperimentConfig': experiment_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_processing_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(processing_job_name=processing_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        processing_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ProcessingJobName': processing_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_processing_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeProcessingJobResponse')
        processing_job = cls(**transformed_response)
        return processing_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ProcessingJobName': self.processing_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_processing_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeProcessingJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'ProcessingJobName': self.processing_job_name,
        }
        self.client.stop_processing_job(**operation_input_args)
    
    @validate_call
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.processing_job_status
    
            if current_status in terminal_states:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class Project(Base):
    project_arn: str
    project_name: str
    project_id: str
    service_catalog_provisioning_details: ServiceCatalogProvisioningDetails
    project_status: str
    creation_time: datetime.datetime
    project_description: Optional[str] = Unassigned()
    service_catalog_provisioned_product_details: Optional[ServiceCatalogProvisionedProductDetails] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    
    @classmethod
    def create(
        cls,
        project_name: str,
        service_catalog_provisioning_details: ServiceCatalogProvisioningDetails,
        project_description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating project resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'ProjectName': project_name,
            'ProjectDescription': project_description,
            'ServiceCatalogProvisioningDetails': service_catalog_provisioning_details,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_project(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(project_name=project_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        project_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'ProjectName': project_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_project(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeProjectOutput')
        project = cls(**transformed_response)
        return project
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ProjectName': self.project_name,
        }
        client = SageMakerClient().client
        response = client.describe_project(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeProjectOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ProjectName': self.project_name,
        }
        self.client.delete_project(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Pending', 'CreateInProgress', 'CreateCompleted', 'CreateFailed', 'DeleteInProgress', 'DeleteFailed', 'DeleteCompleted', 'UpdateInProgress', 'UpdateCompleted', 'UpdateFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.project_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class Space(Base):
    domain_id: Optional[str] = Unassigned()
    space_arn: Optional[str] = Unassigned()
    space_name: Optional[str] = Unassigned()
    home_efs_file_system_uid: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    space_settings: Optional[SpaceSettings] = Unassigned()
    ownership_settings: Optional[OwnershipSettings] = Unassigned()
    space_sharing_settings: Optional[SpaceSharingSettings] = Unassigned()
    space_display_name: Optional[str] = Unassigned()
    url: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        domain_id: str,
        space_name: str,
        tags: Optional[List[Tag]] = Unassigned(),
        space_settings: Optional[SpaceSettings] = Unassigned(),
        ownership_settings: Optional[OwnershipSettings] = Unassigned(),
        space_sharing_settings: Optional[SpaceSharingSettings] = Unassigned(),
        space_display_name: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating space resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'DomainId': domain_id,
            'SpaceName': space_name,
            'Tags': tags,
            'SpaceSettings': space_settings,
            'OwnershipSettings': ownership_settings,
            'SpaceSharingSettings': space_sharing_settings,
            'SpaceDisplayName': space_display_name,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_space(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(domain_id=domain_id, space_name=space_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        domain_id: str,
        space_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'DomainId': domain_id,
            'SpaceName': space_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_space(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeSpaceResponse')
        space = cls(**transformed_response)
        return space
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'SpaceName': self.space_name,
        }
        client = SageMakerClient().client
        response = client.describe_space(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeSpaceResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'SpaceName': self.space_name,
        }
        self.client.delete_space(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Deleting', 'Failed', 'InService', 'Pending', 'Updating', 'Update_Failed', 'Delete_Failed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class StudioLifecycleConfig(Base):
    studio_lifecycle_config_arn: Optional[str] = Unassigned()
    studio_lifecycle_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    studio_lifecycle_config_content: Optional[str] = Unassigned()
    studio_lifecycle_config_app_type: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        studio_lifecycle_config_name: str,
        studio_lifecycle_config_content: str,
        studio_lifecycle_config_app_type: str,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating studio_lifecycle_config resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'StudioLifecycleConfigName': studio_lifecycle_config_name,
            'StudioLifecycleConfigContent': studio_lifecycle_config_content,
            'StudioLifecycleConfigAppType': studio_lifecycle_config_app_type,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_studio_lifecycle_config(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(studio_lifecycle_config_name=studio_lifecycle_config_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        studio_lifecycle_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'StudioLifecycleConfigName': studio_lifecycle_config_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_studio_lifecycle_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeStudioLifecycleConfigResponse')
        studio_lifecycle_config = cls(**transformed_response)
        return studio_lifecycle_config
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'StudioLifecycleConfigName': self.studio_lifecycle_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_studio_lifecycle_config(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeStudioLifecycleConfigResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'StudioLifecycleConfigName': self.studio_lifecycle_config_name,
        }
        self.client.delete_studio_lifecycle_config(**operation_input_args)


class TrainingJob(Base):
    training_job_name: str
    training_job_arn: str
    model_artifacts: ModelArtifacts
    training_job_status: str
    secondary_status: str
    algorithm_specification: AlgorithmSpecification
    resource_config: ResourceConfig
    stopping_condition: StoppingCondition
    creation_time: datetime.datetime
    tuning_job_arn: Optional[str] = Unassigned()
    labeling_job_arn: Optional[str] = Unassigned()
    auto_m_l_job_arn: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    hyper_parameters: Optional[Dict[str, str]] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    input_data_config: Optional[List[Channel]] = Unassigned()
    output_data_config: Optional[OutputDataConfig] = Unassigned()
    warm_pool_status: Optional[WarmPoolStatus] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    training_start_time: Optional[datetime.datetime] = Unassigned()
    training_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    secondary_status_transitions: Optional[List[SecondaryStatusTransition]] = Unassigned()
    final_metric_data_list: Optional[List[MetricData]] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    enable_inter_container_traffic_encryption: Optional[bool] = Unassigned()
    enable_managed_spot_training: Optional[bool] = Unassigned()
    checkpoint_config: Optional[CheckpointConfig] = Unassigned()
    training_time_in_seconds: Optional[int] = Unassigned()
    billable_time_in_seconds: Optional[int] = Unassigned()
    debug_hook_config: Optional[DebugHookConfig] = Unassigned()
    experiment_config: Optional[ExperimentConfig] = Unassigned()
    debug_rule_configurations: Optional[List[DebugRuleConfiguration]] = Unassigned()
    tensor_board_output_config: Optional[TensorBoardOutputConfig] = Unassigned()
    debug_rule_evaluation_statuses: Optional[List[DebugRuleEvaluationStatus]] = Unassigned()
    profiler_config: Optional[ProfilerConfig] = Unassigned()
    profiler_rule_configurations: Optional[List[ProfilerRuleConfiguration]] = Unassigned()
    profiler_rule_evaluation_statuses: Optional[List[ProfilerRuleEvaluationStatus]] = Unassigned()
    profiling_status: Optional[str] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    retry_strategy: Optional[RetryStrategy] = Unassigned()
    remote_debug_config: Optional[RemoteDebugConfig] = Unassigned()
    infra_check_config: Optional[InfraCheckConfig] = Unassigned()
    
    @classmethod
    def create(
        cls,
        training_job_name: str,
        algorithm_specification: AlgorithmSpecification,
        role_arn: str,
        output_data_config: OutputDataConfig,
        resource_config: ResourceConfig,
        stopping_condition: StoppingCondition,
        hyper_parameters: Optional[Dict[str, str]] = Unassigned(),
        input_data_config: Optional[List[Channel]] = Unassigned(),
        vpc_config: Optional[VpcConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        enable_network_isolation: Optional[bool] = Unassigned(),
        enable_inter_container_traffic_encryption: Optional[bool] = Unassigned(),
        enable_managed_spot_training: Optional[bool] = Unassigned(),
        checkpoint_config: Optional[CheckpointConfig] = Unassigned(),
        debug_hook_config: Optional[DebugHookConfig] = Unassigned(),
        debug_rule_configurations: Optional[List[DebugRuleConfiguration]] = Unassigned(),
        tensor_board_output_config: Optional[TensorBoardOutputConfig] = Unassigned(),
        experiment_config: Optional[ExperimentConfig] = Unassigned(),
        profiler_config: Optional[ProfilerConfig] = Unassigned(),
        profiler_rule_configurations: Optional[List[ProfilerRuleConfiguration]] = Unassigned(),
        environment: Optional[Dict[str, str]] = Unassigned(),
        retry_strategy: Optional[RetryStrategy] = Unassigned(),
        remote_debug_config: Optional[RemoteDebugConfig] = Unassigned(),
        infra_check_config: Optional[InfraCheckConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating training_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'TrainingJobName': training_job_name,
            'HyperParameters': hyper_parameters,
            'AlgorithmSpecification': algorithm_specification,
            'RoleArn': role_arn,
            'InputDataConfig': input_data_config,
            'OutputDataConfig': output_data_config,
            'ResourceConfig': resource_config,
            'VpcConfig': vpc_config,
            'StoppingCondition': stopping_condition,
            'Tags': tags,
            'EnableNetworkIsolation': enable_network_isolation,
            'EnableInterContainerTrafficEncryption': enable_inter_container_traffic_encryption,
            'EnableManagedSpotTraining': enable_managed_spot_training,
            'CheckpointConfig': checkpoint_config,
            'DebugHookConfig': debug_hook_config,
            'DebugRuleConfigurations': debug_rule_configurations,
            'TensorBoardOutputConfig': tensor_board_output_config,
            'ExperimentConfig': experiment_config,
            'ProfilerConfig': profiler_config,
            'ProfilerRuleConfigurations': profiler_rule_configurations,
            'Environment': environment,
            'RetryStrategy': retry_strategy,
            'RemoteDebugConfig': remote_debug_config,
            'InfraCheckConfig': infra_check_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_training_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(training_job_name=training_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        training_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'TrainingJobName': training_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_training_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeTrainingJobResponse')
        training_job = cls(**transformed_response)
        return training_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'TrainingJobName': self.training_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_training_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeTrainingJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'TrainingJobName': self.training_job_name,
        }
        self.client.stop_training_job(**operation_input_args)
    
    @validate_call
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.training_job_status
    
            if current_status in terminal_states:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class TransformJob(Base):
    transform_job_name: str
    transform_job_arn: str
    transform_job_status: str
    model_name: str
    transform_input: TransformInput
    transform_resources: TransformResources
    creation_time: datetime.datetime
    failure_reason: Optional[str] = Unassigned()
    max_concurrent_transforms: Optional[int] = Unassigned()
    model_client_config: Optional[ModelClientConfig] = Unassigned()
    max_payload_in_m_b: Optional[int] = Unassigned()
    batch_strategy: Optional[str] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    transform_output: Optional[TransformOutput] = Unassigned()
    data_capture_config: Optional[BatchDataCaptureConfig] = Unassigned()
    transform_start_time: Optional[datetime.datetime] = Unassigned()
    transform_end_time: Optional[datetime.datetime] = Unassigned()
    labeling_job_arn: Optional[str] = Unassigned()
    auto_m_l_job_arn: Optional[str] = Unassigned()
    data_processing: Optional[DataProcessing] = Unassigned()
    experiment_config: Optional[ExperimentConfig] = Unassigned()
    
    @classmethod
    def create(
        cls,
        transform_job_name: str,
        model_name: str,
        transform_input: TransformInput,
        transform_output: TransformOutput,
        transform_resources: TransformResources,
        max_concurrent_transforms: Optional[int] = Unassigned(),
        model_client_config: Optional[ModelClientConfig] = Unassigned(),
        max_payload_in_m_b: Optional[int] = Unassigned(),
        batch_strategy: Optional[str] = Unassigned(),
        environment: Optional[Dict[str, str]] = Unassigned(),
        data_capture_config: Optional[BatchDataCaptureConfig] = Unassigned(),
        data_processing: Optional[DataProcessing] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        experiment_config: Optional[ExperimentConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating transform_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'TransformJobName': transform_job_name,
            'ModelName': model_name,
            'MaxConcurrentTransforms': max_concurrent_transforms,
            'ModelClientConfig': model_client_config,
            'MaxPayloadInMB': max_payload_in_m_b,
            'BatchStrategy': batch_strategy,
            'Environment': environment,
            'TransformInput': transform_input,
            'TransformOutput': transform_output,
            'DataCaptureConfig': data_capture_config,
            'TransformResources': transform_resources,
            'DataProcessing': data_processing,
            'Tags': tags,
            'ExperimentConfig': experiment_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_transform_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(transform_job_name=transform_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        transform_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'TransformJobName': transform_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_transform_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeTransformJobResponse')
        transform_job = cls(**transformed_response)
        return transform_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'TransformJobName': self.transform_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_transform_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeTransformJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'TransformJobName': self.transform_job_name,
        }
        self.client.stop_transform_job(**operation_input_args)
    
    @validate_call
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.transform_job_status
    
            if current_status in terminal_states:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class Trial(Base):
    trial_name: Optional[str] = Unassigned()
    trial_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    experiment_name: Optional[str] = Unassigned()
    source: Optional[TrialSource] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    
    @classmethod
    def create(
        cls,
        trial_name: str,
        experiment_name: str,
        display_name: Optional[str] = Unassigned(),
        metadata_properties: Optional[MetadataProperties] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating trial resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'TrialName': trial_name,
            'DisplayName': display_name,
            'ExperimentName': experiment_name,
            'MetadataProperties': metadata_properties,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_trial(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(trial_name=trial_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        trial_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'TrialName': trial_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_trial(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeTrialResponse')
        trial = cls(**transformed_response)
        return trial
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'TrialName': self.trial_name,
        }
        client = SageMakerClient().client
        response = client.describe_trial(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeTrialResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'TrialName': self.trial_name,
        }
        self.client.delete_trial(**operation_input_args)


class TrialComponent(Base):
    trial_component_name: Optional[str] = Unassigned()
    trial_component_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    source: Optional[TrialComponentSource] = Unassigned()
    status: Optional[TrialComponentStatus] = Unassigned()
    start_time: Optional[datetime.datetime] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    parameters: Optional[Dict[str, TrialComponentParameterValue]] = Unassigned()
    input_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned()
    output_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    metrics: Optional[List[TrialComponentMetricSummary]] = Unassigned()
    lineage_group_arn: Optional[str] = Unassigned()
    sources: Optional[List[TrialComponentSource]] = Unassigned()
    
    @classmethod
    def create(
        cls,
        trial_component_name: str,
        display_name: Optional[str] = Unassigned(),
        status: Optional[TrialComponentStatus] = Unassigned(),
        start_time: Optional[datetime.datetime] = Unassigned(),
        end_time: Optional[datetime.datetime] = Unassigned(),
        parameters: Optional[Dict[str, TrialComponentParameterValue]] = Unassigned(),
        input_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned(),
        output_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned(),
        metadata_properties: Optional[MetadataProperties] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating trial_component resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'TrialComponentName': trial_component_name,
            'DisplayName': display_name,
            'Status': status,
            'StartTime': start_time,
            'EndTime': end_time,
            'Parameters': parameters,
            'InputArtifacts': input_artifacts,
            'OutputArtifacts': output_artifacts,
            'MetadataProperties': metadata_properties,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_trial_component(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(trial_component_name=trial_component_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        trial_component_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'TrialComponentName': trial_component_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_trial_component(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeTrialComponentResponse')
        trial_component = cls(**transformed_response)
        return trial_component
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'TrialComponentName': self.trial_component_name,
        }
        client = SageMakerClient().client
        response = client.describe_trial_component(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeTrialComponentResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'TrialComponentName': self.trial_component_name,
        }
        self.client.delete_trial_component(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['InProgress', 'Completed', 'Failed', 'Stopping', 'Stopped'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status.primary_status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class UserProfile(Base):
    domain_id: Optional[str] = Unassigned()
    user_profile_arn: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    home_efs_file_system_uid: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    single_sign_on_user_identifier: Optional[str] = Unassigned()
    single_sign_on_user_value: Optional[str] = Unassigned()
    user_settings: Optional[UserSettings] = Unassigned()
    
    @classmethod
    def create(
        cls,
        domain_id: str,
        user_profile_name: str,
        single_sign_on_user_identifier: Optional[str] = Unassigned(),
        single_sign_on_user_value: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        user_settings: Optional[UserSettings] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating user_profile resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'DomainId': domain_id,
            'UserProfileName': user_profile_name,
            'SingleSignOnUserIdentifier': single_sign_on_user_identifier,
            'SingleSignOnUserValue': single_sign_on_user_value,
            'Tags': tags,
            'UserSettings': user_settings,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_user_profile(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(domain_id=domain_id, user_profile_name=user_profile_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        domain_id: str,
        user_profile_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'DomainId': domain_id,
            'UserProfileName': user_profile_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_user_profile(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeUserProfileResponse')
        user_profile = cls(**transformed_response)
        return user_profile
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'UserProfileName': self.user_profile_name,
        }
        client = SageMakerClient().client
        response = client.describe_user_profile(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeUserProfileResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'UserProfileName': self.user_profile_name,
        }
        self.client.delete_user_profile(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Deleting', 'Failed', 'InService', 'Pending', 'Updating', 'Update_Failed', 'Delete_Failed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class Workforce(Base):
    workforce: Workforce
    
    @classmethod
    def create(
        cls,
        workforce_name: str,
        cognito_config: Optional[CognitoConfig] = Unassigned(),
        oidc_config: Optional[OidcConfig] = Unassigned(),
        source_ip_config: Optional[SourceIpConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        workforce_vpc_config: Optional[WorkforceVpcConfigRequest] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating workforce resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'CognitoConfig': cognito_config,
            'OidcConfig': oidc_config,
            'SourceIpConfig': source_ip_config,
            'WorkforceName': workforce_name,
            'Tags': tags,
            'WorkforceVpcConfig': workforce_vpc_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_workforce(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(workforce_name=workforce_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        workforce_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'WorkforceName': workforce_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_workforce(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeWorkforceResponse')
        workforce = cls(**transformed_response)
        return workforce
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'WorkforceName': self.workforce_name,
        }
        client = SageMakerClient().client
        response = client.describe_workforce(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeWorkforceResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'WorkforceName': self.workforce_name,
        }
        self.client.delete_workforce(**operation_input_args)
    
    @validate_call
    def wait_for_status(
        self,
        status: Literal['Initializing', 'Updating', 'Deleting', 'Failed', 'Active'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional[object]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.workforce.status
    
            if status == current_status:
                return
    
            # TODO: Raise some generated TimeOutError
            if timeout is not None and time.time() - start_time >= timeout:
                raise Exception("Timeout exceeded. Final resource state - " + current_status)
    
            time.sleep(poll)


class Workteam(Base):
    workteam: Workteam
    
    @classmethod
    def create(
        cls,
        workteam_name: str,
        member_definitions: List[MemberDefinition],
        description: str,
        workforce_name: Optional[str] = Unassigned(),
        notification_configuration: Optional[NotificationConfiguration] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        logger.debug(f"Creating workteam resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker')
    
        operation_input_args = {
            'WorkteamName': workteam_name,
            'WorkforceName': workforce_name,
            'MemberDefinitions': member_definitions,
            'Description': description,
            'NotificationConfiguration': notification_configuration,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_workteam(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(workteam_name=workteam_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        workteam_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        operation_input_args = {
            'WorkteamName': workteam_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_workteam(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeWorkteamResponse')
        workteam = cls(**transformed_response)
        return workteam
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'WorkteamName': self.workteam_name,
        }
        client = SageMakerClient().client
        response = client.describe_workteam(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeWorkteamResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'WorkteamName': self.workteam_name,
        }
        self.client.delete_workteam(**operation_input_args)


