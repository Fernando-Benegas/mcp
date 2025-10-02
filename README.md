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

### Using an external MCP server

In this example, we will use Notion MCP

1. Deploy the externalService and [ingressroute](https://github.com/Fernando-Benegas/mcp/blob/main/k8s/external-mcp.yaml):

```shell
kubectl apply -f https://raw.githubusercontent.com/Fernando-Benegas/mcp/blob/main/k8s/external-mcp.yaml
```


TO BE TESTED

### Client and Middleware setup

TBC


## OKE cluster

### Deploy Redis for distributed features

```bash
helm upgrade --install redis bitnami/redis --namespace redis --values tools/redis/values.yaml --create-namespace
```

## Deploy Hub

### Create namespace

```bash
kubectl create ns traefik
```

### Create Hub token secret

```bash
kubectl create secret generic hub-license --from-literal=token="${HUB_TOKEN}" -n traefik
```

### deploy Traefik

```bash
helm upgrade --install traefik traefik/traefik --create-namespace --namespace traefik --values hub/hub-values.yaml --devel
```

### Add Hub dashboard ingress if needed

```bash
envsubst < hub/dashboard.yaml | kubectl apply -f -
```

### Deploy observability stack

```bash
kubectl create ns observability
```

#### Deploy Otel collector

##### install collector

```bash
helm upgrade --install otel-collector open-telemetry/opentelemetry-collector -n observability --values tools/observability/otel-collector/values.yaml 
```

#### Deploy loki

```bash
helm upgrade --install loki grafana/loki -n observability --values tools/observability/loki/values.yaml
```

#### Deploy Jaeger

```bash
kubectl apply -f tools/observability/jaeger
```

#### Deploy Prometheus stack

```bash
helm upgrade --install promtail grafana/promtail -n observability --values tools/observability/promtail/values.yaml
kubectl create configmap grafana-traefik-dashboards --from-file=tools/observability/prometheus-stack/traefik.json -o yaml --dry-run=client -n observability | kubectl apply -f - && kubectl label -n observability cm grafana-traefik-dashboards grafana_dashboard=true
helm upgrade -i prometheus-stack prometheus-community/kube-prometheus-stack -f tools/observability/prometheus-stack/values.yaml -n observability
envsubst < tools/observability/prometheus-stack/ingress.yaml | kubectl apply -f -
```

## deploy external mcp

```bash
for i in $(find mcp/ext -type f -follow -print); do
  envsubst < $i | kubectl apply -f -
done
```

## deploy internal mcp

```bash
for i in $(find mcp/int -type f -follow -print); do
  envsubst < $i | kubectl apply -f -
done
```

## build mcp server

```bash
docker buildx build -t newa/simple-mcp-server:v1.0. --platform linux/amd64 -f mcp/docker/dockerfile . --push
```
