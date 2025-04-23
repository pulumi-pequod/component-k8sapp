from pulumi.provider.experimental import component_provider_host

from serviceDeployment import ServiceDeployment

if __name__ == "__main__":
    component_provider_host(name="k8sapp", components=[ServiceDeployment])
