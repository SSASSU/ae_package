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

    # Secret 적용 명령어 생성
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

def running_check(stdscr, namespace, timeout_seconds=300):

    config.load_kube_config()  

    v1 = client.CoreV1Api()

    start_time = time.time()
    end_time = start_time + timeout_seconds

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Namespace: {namespace}")
        stdscr.addstr(1, 0, "Pods:")

        if time.time() > end_time:
            stdscr.addstr(2, 0, f"The pods did not transition to the Running state for {timeout_seconds} seconds.")
            break

        try:
            pods = v1.list_namespaced_pod(namespace)
        except ApiException as e:
            stdscr.addstr(2, 0, f"An error occurred while fetching the list of pods: {e}")
            break

        row = 3
        all_running = True

        for pod in pods.items:
            if pod.status.phase != "Running":
                all_running = False
                stdscr.addstr(row, 2, f"- {pod.metadata.name}, Phase: {pod.status.phase}\n")
            else:
                stdscr.addstr(row, 2, f"- {pod.metadata.name}, Phase: {pod.status.phase}\n")
            row += 1

        if all_running:
            stdscr.addstr(row, 0, f"\nAll pods are in Running state. Continuing in 5 seconds.")
            stdscr.refresh()
            time.sleep(5)
            break

        elapsed_time = int(time.time() - start_time)
        stdscr.addstr(row + 1, 0, f"Elapsed time: {elapsed_time} seconds")

        stdscr.refresh()
        time.sleep(1)  # loop restart every 1sec


def harbor_login(node_ips: list, user_info: dict):

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    nerdctl_login_cmd = "nerdctl login vision.harbor.core:30101 -u %s -p %s" %(user_info["account"]["harbor_id"], user_info["account"]["harbor_pass"])
 
    try:
        for node_ip in node_ips:

            ssh_client.connect(node_ip, username=user_info["account"]["host_id"], password=user_info["account"]["host_pass"])

            stdin, stdout, stderr = ssh_client.exec_command(nerdctl_login_cmd)
   
            print(f"{node_ip}: {stdout.read().decode()}")

            ssh_client.close()

    except Exception as e:
        print(f"{node_ip} : Harbor Login Error: {str(e)}")


