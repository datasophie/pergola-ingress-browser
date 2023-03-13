# Pergola Ingress Browser
Retrieves and lists all [Ingresses](https://docs.pergola.cloud/docs/reference/project-manifest#ingresses) configured on Pergola, per Project/Stage/Component, including their network and auth configurations, if available.

## Deployment to Pergola

* Create a new [Project](https://docs.pergola.cloud/docs/reference/projects) pointing to this Git repo
* Trigger a new Build
* Create a new [Stage](https://docs.pergola.cloud/docs/reference/stages)
* Let your Pergola admin know that you need special permissions for the [Identity defined in pergola.yaml](pergola.yaml#L11)
  * You can also skip this step and deploy first
  * See [required permissions](#required-permissions-at-runtime) below
* (optional) Add a new Configuration to Stage:
  * If you want the app to automatically create links to Pergola UI, add this entry to the config:
  * PERGOLA_UI_URL: <url of your Pergola UI installation, e.g. https://console.pergola.mycompany.com>
* Deploy

### Required permissions at runtime
This app defines an [Identity](https://docs.pergola.cloud/docs/reference/project-manifest#identity) which requires access to K8s resources at runtime with at least following permissions:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ingress-browser
rules:
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list"]
```
This `ClusterRole` needs to be setup by a Pergola admin.

As soon as the Stage exists a Pergola admin can link the Pergola Identity to the ClusterRole above.
Here is a template for the binding:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ingress-browser
roleRef:
  kind: ClusterRole
  name: ingress-browser
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: ServiceAccount
  name: ingress-browser # as defined in pergola.yaml
  namespace: # of project/stage
```

This can be done before or after deployment. As long as this role binding is not in place, the app will report "permission denied".

## Running the app locally (for dev/debugging)
*Note:* You need a local `~/.kube/config` with at least the permission to get and list Ingresses on Kubernetes (see [required permissions](#required-permissions-at-runtime) above).

### With Python
Requires Python >= 3.8

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

### With Docker
```bash
docker compose build
docker compose up
```
