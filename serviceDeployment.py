from typing import Optional, Sequence, TypedDict

import pulumi
from pulumi import ResourceOptions, ComponentResource, Output
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import (
    ContainerArgs,
    ContainerPortArgs,
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
    ports: Optional[pulumi.Input[Sequence[int]]]
    """Ports to expose on the service. This should be a list of integers"""
    allocate_ip_address: pulumi.Input[bool]
    """Whether to allocate an IP address for the service. This should be true or false"""

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
        resources = args.get("resources", 
                             ResourceRequirementsArgs(requests={
                                "cpu": "100m",
                                "memory": "100Mi"}))
        replicas = args.get("replicas", 1)
        ports = args.get("ports", [])
        container_ports_config=[ContainerPortArgs(container_port=p) for p in ports] if ports else None,
        service_ports_config=[ServicePortArgs(port=p, target_port=p) for p in ports] if ports else None,
        allocate_ip_address = args.get("allocate_ip_address", False)

        # Labels used for the deployment and service.
        labels = {"app": name}

        # Container config
        container = ContainerArgs(
            name=name,
            image=image,
            resources=resources, 
            ports=container_ports_config,
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
                    spec=PodSpecArgs(containers=[container]),
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self))
        
        # Service
        service = Service(
            name,
            metadata=ObjectMetaArgs(
                name=name,
                namespace=namespace,
                labels=self.deployment.metadata.apply(lambda m: m.labels),
            ),
            spec=ServiceSpecArgs(
                ports=service_ports_config,
                selector=self.deployment.spec.apply(lambda s: s.template.metadata.labels),
                type=("LoadBalancer") if allocate_ip_address else None,
            ),
            opts=pulumi.ResourceOptions(parent=self))

        # Return IP address if applicable
        if allocate_ip_address:
            ingress=self.service.status.apply(lambda s: s.load_balancer.ingress[0])
            self.ip_address = ingress.apply(lambda i: i.ip or i.hostname or "")
            
        self.register_outputs({})
