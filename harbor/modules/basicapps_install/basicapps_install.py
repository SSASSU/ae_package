import os
import subprocess
import mysql.connector

from kubernetes import client, config

#Basicapps labeling
def update_node_label(k8s_nodes: dict):

    config.load_kube_config()

    v1 = client.CoreV1Api()

    worker_node_name: str

    label={} 
    label["processType"]="basicapps"

    #Set the label of the last worker node to "basicapps"
    last_node_ip=next(reversed(k8s_nodes))

    if "master" != k8s_nodes[last_node_ip][1]:
        worker_node_name = k8s_nodes[last_node_ip][0]
    else:
        print(f"Couldn't find the worker node")
        exit(1)

    label_patch = {
            "metadata": {
                "labels": label
                }
            }

    try:
        #viewapps label patch
        result = v1.patch_node(worker_node_name, label_patch)
        print (f"{worker_node_name}: label added")

    except Exception as e:
        print(f"{worker_node_name}: Patch Failed: {str(e)}")

def basicapps_helm_install(basicapps_path: str):

    try:
        # Build Helm install Command
        helm_install_cmd = [
            "helm",
            "install",
            "basicapps",
            basicapps_path
        ]

        subprocess.run(helm_install_cmd, check=True)
        print(f"Basicapps Helm Installed")
    except subprocess.CalledProcessError as e:
        print(f"Basicapps Helm Install Error: {str(e)}")

