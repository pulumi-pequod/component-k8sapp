# component-k8sapp
Abstraction for K8s Deployment and Service.

# Usage
## Specify Package in `Pulumi.yaml`

Add the following to your `Pulumi.yaml` file:
Note: If no version is specified, the latest version will be used.

```
packages:
  k8sapp: https://github.com/pulumi-pequod/component-k8sapp[@vX.Y.Z]
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
    cpu="0.25",
    mem="2Gi",
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
        "cloud.google.com/gke-accelerator": "nvidia-l4",
    },
    resources={
        "requests": {
            "cpu": "4",
            "memory": "16Gi",
            "nvidia.com/gpu": "1",
        },
        "limits": {
            "nvidia.com/gpu": "1",
        },
    },
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




