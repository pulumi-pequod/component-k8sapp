# component-k8sapp
Abstraction for K8s Deployment and Service.

# Inputs

* namespace: The namespace in which the service will be deployed.
* image: The image to deploy. This should be the full image reference including the registry and tag.
* allocate_ip_address: Whether to allocate an IP address for the service. This should be true or false.
* container_port: Container port to expose. This should be an integer.
* host_port (Optional): Host port to expose. This should be an integer. Defaults to the value given for container port.
* resources (Optional): Resource requirements for the container. Defaults to `cpu`: "100m", `memory`: "100Mi:.
* replicas (Optional): Number of replicas for the deployment. Defaults to 1.
* env_vars (Optional): Environment variables to pass to cluster. Defaults to none.

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
```
from pulumi_pequod_k8sapp import ServiceDeployment, ServiceDeploymentArgs

serviceDeployment = ServiceDeployment(
    "redis-leader",
    namespace=guestbook_ns_name,
    image="redis",
    container_port=6379, 
    allocate_ip_address=False,
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




