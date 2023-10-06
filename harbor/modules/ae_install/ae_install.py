import os
import subprocess

from kubernetes import client, config

#view apps, basic apps labeling
def update_node_label(k8s_nodes: dict):

    config.load_kube_config()

    v1 = client.CoreV1Api()

    master_node_name = ""

    label={} 
    label["processType"]="viewapps"

    for node_ip in k8s_nodes:
        if "master" == k8s_nodes[node_ip][1]:
            master_node_name = k8s_nodes[node_ip][0]
            break

    taint_patch = {
            "spec": {
                "taints": []
                }
            }
    
    label_patch = {
            "metadata": {
                "labels": label
                }
            }

    try:
        #taint remove patch
        result = v1.patch_node(master_node_name, taint_patch)
        print (f"{master_node_name}: Taint removed")
        #viewapps label patch
        result = v1.patch_node(master_node_name, label_patch)
        print (f"{master_node_name}: label added")

    except Exception as e:
        print(f"{master_node_name}: Patch Failed: {str(e)}")

def create_namespace():

    config.load_kube_config()

    # Create K8s Client
    v1 = client.CoreV1Api()

    # Create Namespace Object
    namespace = client.V1Namespace()
    namespace.metadata = client.V1ObjectMeta(name="viewapps")

    try:
        # Create Namespace
        v1.create_namespace(namespace)
        print(f"Namespace Created")
    except Exception as e:
        print(f"Namespace Create Error: {str(e)}")

def viewapps_helm_install(viewapps_path: str):

    create_namespace()

    try:
        # Build Helm install Command
        helm_install_cmd = [
            "helm",
            "install",
            "viewapps",
            viewapps_path,
            "-n",
            "viewapps"
        ]

        subprocess.run(helm_install_cmd, check=True)
        print(f"Helm Installed")
    except subprocess.CalledProcessError as e:
        print(f"Helm Install Error: {str(e)}")

