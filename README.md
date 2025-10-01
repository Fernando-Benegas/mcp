# Traefik Hub MCP gateway



## Local cluster

How to deploy Traefik Hub and all the dependencies to test MCP gateway in a local kubernetes environment:

1. Install k3s
   
   ```shell
   curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE="644" INSTALL_K3S_EXEC="--disable traefik" sh -
   ```
2. Get a licencse key from preview environments and install the latest version of Traefik Hub

```shell
helm repo add --force-update traefik https://traefik.github.io/charts

# Install the Ingress Controller
kubectl create namespace traefik
kubectl create secret generic traefik-hub-license --namespace traefik --from-literal=token=
helm upgrade --install --namespace traefik traefik traefik/traefik \
  --set hub.token=traefik-hub-license \
  --set hub.apimanagement.enabled=true \
  --set hub.platformUrl=https://api-preview.hub.traefik.io/agent --set image.registry=europe-west9-docker.pkg.dev/traefiklabs --set image.repository=traefik-hub/traefik-hub --set image.tag=latest-v3 --set image.pullPolicy=Always
  ```

3. Deploy a local mcp server:

```shell

```   

### Prerequisites

- Install OCI dependencies:

```shell
sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
sudo apt update && sudo apt install python3 python3-pip python3-venv
```

- Install ``OCI-CLI``:  [Install oci-cli in linux](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm#InstallingCLI__linux_and_unix)

