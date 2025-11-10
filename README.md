# component-k8sapp
Abstraction for K8s Deployment and Service.

# Inputs

* namespace: The namespace in which the service will be deployed.
* image: The image to deploy. This should be the full image reference including the registry and tag.
* allocate_ip_address: Whether to allocate an IP address for the service. This should be true or false.
* container_port: Container port to expose. This should be an integer.
* host_port (Optional): Host port to expose. This should be an integer. Defaults to the value given for container port.
* cpu (Optional): CPU resource request. Units: millicores (e.g., '100m') or cores (e.g., '1', '0.5'). Defaults to "100m".
* mem (Optional): Memory resource request. Units: bytes with optional suffixes (e.g., '128Mi', '1Gi', '512M'). Defaults to "100Mi".
* resources (Optional): Full resource requirements for the container (requests and limits). If provided, this overrides cpu/mem parameters. Use this for advanced scenarios like GPU resources.
* replicas (Optional): Number of replicas for the deployment. Defaults to 1.
* env_vars (Optional): Environment variables to pass to cluster. Defaults to none.
* node_selector (Optional): Node selector constraints for pod scheduling.
* tolerations (Optional): Tolerations for pod scheduling. For GKE Autopilot, use to tolerate balloon pod resize operations.

# Outputs

* ip_address: If `allocate_ip_address` is set to `true`, the component returns the IP address/DNS name for the service.

# Usage
## Specify Package in `Pulumi.yaml`

Add the following to your `Pulumi.yaml` file:
Note: If no version is specified, the latest version will be used.

```
packages:
  k8sapp: https://github.com/pulumi-pequod/component-k8sapp[@v1.0.1]
``` 

## Use SDK in Program

### Python

**Basic usage:**
```python
from pulumi_pequod_k8sapp import ServiceDeployment

serviceDeployment = ServiceDeployment(
    "redis-leader",
    namespace=guestbook_ns_name,
    image="redis",
    container_port=6379, 
    allocate_ip_address=False,
    opts=pulumi.ResourceOptions(provider=k8s_provider))
```

**With GPU resources (e.g., for GKE Autopilot):**
```python
import pulumi_kubernetes as k8s
from pulumi_pequod_k8sapp import ServiceDeployment

gpu_service = ServiceDeployment(
    "gpu-workload",
    namespace=namespace,
    image="my-gpu-image",
    container_port=8080,
    allocate_ip_address=True,
    node_selector={
        "cloud.google.com/gke-accelerator": "nvidia-a100-80gb",
    },
    tolerations=[
        k8s.core.v1.TolerationArgs(
            key="node.gke.io/balloon-pod-resize",
            operator="Exists",
            effect="NoSchedule",
        )
    ],
    resources=k8s.core.v1.ResourceRequirementsArgs(
        requests={"cpu": "4", "memory": "16Gi", "nvidia.com/gpu": "1"},
        limits={"nvidia.com/gpu": "1"},
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider))
```

### Typescript
```
import { ServiceDeployment } from "@pulumi-pequod/k8sapp";

const frontend = new ServiceDeployment("frontend", {
    replicas: 3,
    image: "pulumi/guestbook-php-redis",
    namespace: guestbookNsName,
    containerPort: 80,
    allocateIpAddress: true,
}, { provider: k8sProvider });
```

### Dotnet
```
using PulumiPequod.K8sapp;

var deployment = new ServiceDeployment("stack-settings", {
  Namespace = "myns",
  Iimage = "myimage",
  ContainerPort = 80
});
```

### YAML
```
  redis-replica:
    type: k8sapp:ServiceDeployment
    properties:
      namespace: ${guestbook-yaml-ns.metadata.name}
      image: pulumi/guestbook-redis-replica
      containerPort: 6379
      allocateIpAddress: false
    options:
      provider: ${k8sProvider}
```




