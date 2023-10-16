from kubernetes import client, config
from kubernetes.client.rest import ApiException

import paramiko
import subprocess
import os
import curses
import time

def create_namespace():

    config.load_kube_config()  

    # Create K8s Client
    v1 = client.CoreV1Api()

    # Create Namespace Object
    namespace = client.V1Namespace()
    namespace.metadata = client.V1ObjectMeta(name="harbor")

    try:
        # Create Namespace 
        v1.create_namespace(namespace)
        print(f"Namespace Created")
    except Exception as e:
        print(f"Namespace Create Error: {str(e)}")

def apply_secret(harbor_path: str):

    config.load_kube_config()

    api_instance = client.CustomObjectsApi()

    namespace = "harbor"
    secret_file = harbor_path+"/secret.yaml"

    secret_apply_cmd = [
        "kubectl",
        "apply",
        "-f",
        secret_file,
        "-n",
        namespace,
    ]

    try:
        # Excute kubectl command 
        os.system(" ".join(secret_apply_cmd))
        print(f"Secret Applied at harbor namespace")
    except Exception as e:
        print(f"Secret Apply Error: {str(e)}")

def helm_install(harbor_path: str):

    create_namespace()

    apply_secret(harbor_path)

    try:
        # Build Helm install Command
        repo_add_cmd = "helm repo add harbor https://helm.goharbor.io"
        helm_install_cmd = [
            "helm",
            "install",
            "harbor",
            "harbor/harbor",
            "-n",
            "harbor",
            "-f",
            harbor_path+"/values.yaml"
        ]
        subprocess.run(repo_add_cmd, shell=True, check=True)
        subprocess.run(helm_install_cmd, check=True)
        print(f"Helm Installed")
    except subprocess.CalledProcessError as e:
        print(f"Helm Install Error: {str(e)}")

def harbor_login(k8s_nodes: dict, user_info: dict):

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    nerdctl_login_cmd = "nerdctl login vision.harbor.core:30101 -u %s -p %s" %(user_info["account"]["harbor_id"], user_info["account"]["harbor_pass"])
 
    try:
        for node_ip in k8s_nodes:

            ssh_client.connect(node_ip, username=user_info["account"]["host_id"], password=user_info["account"]["host_pass"])

            stdin, stdout, stderr = ssh_client.exec_command(nerdctl_login_cmd)
   
            print(f"{node_ip}: {stdout.read().decode()}")

            ssh_client.close()

    except Exception as e:
        print(f"{node_ip} : Harbor Login Error: {str(e)}")
