# Traefik Hub MCP gateway test

The purpose of this guide is to deploy a mcp server in a local k8s cluster and OKE to test MCP gateway:

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

3. Deploy a local [mcp server](https://github.com/Fernando-Benegas/mcp/blob/main/k8s/mcp-server.yaml):

```shell
kubectl apply -f https://raw.githubusercontent.com/Fernando-Benegas/mcp/refs/heads/main/k8s/mcp-server.yaml
```   

4. Test the mcp server using two terminals:
 
  - Terminal 1
     
```shell
   curl -N http://localhost/mcp?stream=messages
```
  - Terminal 2
     
```shell
curl -X POST -H "Content-Type: application/json" -d '{"user":"k8s-tester","text":"Hello again!"}'  http://localhost/mcp
```

   Expected output in terminal 1:

```
id: 0
data: {"text":"Hello again!","user":"k8s-tester"}
event: message
```


