import os
import time
from flask import render_template, request, jsonify
from app import app
from kubernetes import client


PERGOLA_UI_URL = os.environ.get("PERGOLA_UI_URL")
if PERGOLA_UI_URL:
    PERGOLA_UI_URL = PERGOLA_UI_URL.strip("/")

@app.route("/")
def homepage():
    ts_start = time.time()
    proc_start = time.process_time()

    k8s = client.NetworkingV1Api()
    ret = k8s.list_ingress_for_all_namespaces(watch=False, label_selector="pergola.cloud/project")

    data = {
        "ingresses" : []
    }

    for i in ret.items:
        annotations = i.metadata.annotations
        labels = i.metadata.labels

        ingress = {
            "project": {
                "name": None,
                "url": None
                },
            "stage": {
                "name": None,
                "url": None
                },
            "component": {
                "name": None
                },
            "provider": {
                "name": None,
                "auth": None,
                "urls": []
                }
        }

        if "pergola.cloud/project" in labels:
            project = labels["pergola.cloud/project"]
            ingress["project"]["name"] = project
            if PERGOLA_UI_URL:
                ingress["project"]["url"] = f"{PERGOLA_UI_URL}/pipeline/projects/{project}"

        if "pergola.cloud/stage" in labels:
            stage = labels["pergola.cloud/stage"]
            ingress["stage"]["name"] = stage
            if PERGOLA_UI_URL:
                ingress["stage"]["url"] = f"{ingress['project']['url']}/stages/{stage}"

        if "pergola.cloud/component" in labels:
            ingress["component"]["name"] = labels["pergola.cloud/component"]
        elif "pergola.cloud/part-of" in labels:
            ingress["component"]["name"] = labels["pergola.cloud/part-of"]

        if "pergola.cloud/ingress-provider-name" in annotations:
            ingress["provider"]["name"] = annotations["pergola.cloud/ingress-provider-name"]
        elif "kubernetes.io/ingress.class" in annotations:
            ingress_provider = annotations["kubernetes.io/ingress.class"]
            prefix = "pergola-"
            if ingress_provider.startswith(prefix):
                ingress_provider = ingress_provider[len(prefix):]
            ingress["provider"]["name"] = ingress_provider

        if "pergola.cloud/auth-provider-name" in annotations:
            ingress["provider"]["auth"] = annotations["pergola.cloud/auth-provider-name"]

        for r in i.spec.rules:
            host = r.host
            for p in r.http.paths:
                if p.path and p.path != "/":
                    ingress["provider"]["urls"].append(f"http://{host}{p.path}")
                else:
                    ingress["provider"]["urls"].append(f"http://{host}")

        data["ingresses"].append(ingress)

    data["total"] = len(data["ingresses"])
    data["time_elapsed_ms"] = (time.time() - ts_start) * 1000
    data["proc_elapsed_ms"] = (time.process_time() - proc_start) * 1000

    return render_template("index.html", data=data)
