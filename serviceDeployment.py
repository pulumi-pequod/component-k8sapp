from typing import Optional, Sequence, TypedDict

import pulumi
from pulumi import ResourceOptions, ComponentResource, Output
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import (
    ContainerArgs,
    ContainerPortArgs,
    EnvVarArgs,
    PodSpecArgs,
    PodTemplateSpecArgs,
    ResourceRequirementsArgs,
    Service,
    ServicePortArgs,
    ServiceSpecArgs,
)
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs

class ServiceDeploymentArgs(TypedDict):

    namespace: pulumi.Input[str]
    """The namespace in which the service will be deployed"""
    image: pulumi.Input[str]
    """The image to deploy. This should be the full image reference including the registry and tag"""
    resources: Optional[ResourceRequirementsArgs]
    """Resource requirements for the container"""
    replicas: Optional[pulumi.Input[int]]
    """Number of replicas for the deployment"""
    container_port: pulumi.Input[int]
    """Container port to expose. This should be an integer"""
    host_port: Optional[pulumi.Input[int]]
    """Host port to expose. This should be an integer"""
    allocate_ip_address: pulumi.Input[bool]
    """Whether to allocate an IP address for the service. This should be true or false"""
    env_vars: Optional[pulumi.Input[list[dict[str, pulumi.Input[str]]]]]
    cpu: Optional[pulumi.Input[str]]
    """CPU resource request. Units: millicores (e.g., '100m') or cores (e.g., '1', '0.5')"""
    mem: Optional[pulumi.Input[str]]
    """Memory resource request. Units: bytes with optional suffixes (e.g., '128Mi', '1Gi', '512M')"""
    node_selector: Optional[pulumi.Input[dict[str, pulumi.Input[str]]]]
    """Node selector constraints for pod scheduling. For GKE Autopilot GPU selection, use: 
    {'cloud.google.com/gke-accelerator': 'GPU_TYPE', 'cloud.google.com/gke-accelerator-count': 'GPU_COUNT'}"""

class ServiceDeployment(ComponentResource):
    """
    Deploys a Kubernetes service and deployment.
    """
    ip_address: Output[str]
    """The IP address of the service. This is only available if allocate_ip_address is set to true."""

    def __init__(self, name: str, args: ServiceDeploymentArgs, opts: ResourceOptions = None):

        super().__init__('k8sapp:index:ServiceDeployment', name, {}, opts)

        # Collect the inputs and set defaults if needed.
        namespace = args.get("namespace")
        image = args.get("image")
        cpu = args.get("cpu", "100m")
        mem = args.get("mem", "100Mi")
        node_selector = args.get("node_selector")
        
        # Handle resources: if user provides resources, use it directly.
        # Otherwise, build default resources from cpu/mem parameters.
        # This allows users to specify full resource requirements including GPU limits.
        resources = args.get("resources")
        if resources is None:
            resources = ResourceRequirementsArgs(
                requests={"cpu": cpu, "memory": mem}
            )
        replicas = args.get("replicas", 1)
        container_port = args.get("container_port", None)
        host_port = args.get("host_port", container_port)
        allocate_ip_address = args.get("allocate_ip_address", False)
        env_vars = args.get("env_vars") 
        if env_vars:
            env_vars.append({"name":"GET_HOSTS_FROM", "value": "dns"})
        else:
            env_vars = [{"name":"GET_HOSTS_FROM", "value": "dns"}]

        # Labels used for the deployment and service.
        labels = {"app": name}

        # Build the env vars
        env_var_args = []
        for env_var in env_vars:
            env_var_args.append(EnvVarArgs(
                name=env_var["name"],
                value=env_var["value"]
            ))

        # Container config
        container = ContainerArgs(
            name=name,
            image=image,
            resources=resources, 
            ports=[ContainerPortArgs(
                container_port=container_port,
            )],
            env=env_var_args,
        )

        # Deployment
        deployment = Deployment(
            name,
            metadata=ObjectMetaArgs(
                namespace=namespace
            ),
            spec=DeploymentSpecArgs(
                selector=LabelSelectorArgs(match_labels=labels),
                replicas=replicas,
                template=PodTemplateSpecArgs(
                    metadata=ObjectMetaArgs(labels=labels),
                    spec=PodSpecArgs(
                        containers=[container],
                        node_selector=node_selector,
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self))
        
        # Service
        service = Service(
            name,
            metadata=ObjectMetaArgs(
                name=name,
                namespace=namespace,
                labels=deployment.metadata.apply(lambda m: m.labels),
            ),
            spec=ServiceSpecArgs(
                ports=[ServicePortArgs(
                    port=host_port,
                    target_port=container_port,
                )],
                selector=deployment.spec.apply(lambda s: s.template.metadata.labels),
                type=("LoadBalancer") if allocate_ip_address else None,
            ),
            opts=pulumi.ResourceOptions(parent=self))

        # Return IP address if applicable
        if allocate_ip_address:
            ingress=service.status.apply(lambda s: s.load_balancer.ingress[0])
            self.ip_address = ingress.apply(lambda i: i.ip or i.hostname or "")
            
        self.register_outputs({})
