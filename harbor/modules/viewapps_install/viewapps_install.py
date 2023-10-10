import os
import subprocess
import mysql.connector

from kubernetes import client, config

#view apps, basic apps labeling
def update_node_label(k8s_nodes: dict):

    config.load_kube_config()

    v1 = client.CoreV1Api()

    master_node_name: str

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

def viewapps_db_init(config_path: str, user_info: dict):

    #DB port forward 
    db_port_forword()

    config.load_kube_config()
    v1 = client.CoreV1Api()

    viewapps_db_prefix = "maria-db-vsaiweb"

    pod_list =  v1.list_namespaced_pod(namespace='viewapps')
    viewapps_db_ip: str

    for pod in pod_list.items:
        if pod.metadata.name.startswith(viewapps_db_prefix):
            viewapps_db_ip = pod.status.pod_ip

    #DB init
    db_config = {
        "host": viewapps_db_ip,
        "user": user_info["account"]["viewapps_db_id"],
        "password": user_info["account"]["viewapps_db_pass"]
    }

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        #CP DB Create
        cp_create_query = "create database if not exists `cp`"
        cursor.execute(cp_create_query)
        print(f"query executed: {cp_create_query}")

        #mysql privileges
        use_mysql_db_query = "use mysql"
        cursor.execute(use_mysql_db_query)
        print(f"query executed: {use_mysql_db_query}")

        grant_query = "grant all privileges on cp.* to aiworkflowuser"
        cursor.execute(grant_query)
        print(f"query executed: {grant_query}")

        flush_query = "flush privileges"
        cursor.execute(flush_query)
        print(f"query executed: {flush_query}")

    except mysql.connector.Error as e:
        print(f"Error: {e}")

    #DB Schema Import
    db_schema_import(config_path, viewapps_db_ip, user_info["account"]["viewapps_db_pass"])

def db_port_forword():

    port_forward_cmd = "nohup kubectl -n viewapps port-forward --address 0.0.0.0 svc/maria-db-vsaiweb 3306:3306 >/dev/null 2>&1 &"

    try:
        subprocess.Popen(port_forward_cmd, shell=True)
        print(f"Port Forward: {port_forward_cmd}")

    except Exception as e:
        print(f"Error: {e}")

def kube_config_copy():

    config.load_kube_config()
    v1 = client.CoreV1Api()

    workflow_prefix = "vsai-workflow-app"

    pod_list =  v1.list_namespaced_pod(namespace='viewapps')
    workflow_pod_name: str

    for pod in pod_list.items:
        if pod.metadata.name.startswith(workflow_prefix):
            workflow_pod_name = pod.metadata.name

    src_path="/root/.kube/config"
    dest_path="/app/resources/kube_config"
    copy_cmd = f"kubectl cp {src_path} viewapps/{workflow_pod_name}:{dest_path}"
    
    try:
        subprocess.run(copy_cmd, shell=True, check=True)
        print(f"File '{src_path}' copied to '{workflow_pod_name}:{dest_path}' successfully.")

    except:
        print(f"kubectl cp Error: {e}")

def db_schema_import(config_path: str, db_ip: str, db_pass: str):

    mec_vision_ai_cmd = f"mysql -h {db_ip} -u root -p{db_pass} aiworkflow < {config_path}/mec_vision_ai.sql"
    mec_core_cmd = f"mysql -h {db_ip} -u root -p{db_pass} cp < {config_path}/mec_core.sql"
   
    try:
        subprocess.Popen(mec_vision_ai_cmd, shell=True)
        print(f"mec_vision_ai.sql import: {mec_vision_ai_cmd}")
        subprocess.Popen(mec_core_cmd, shell=True)
        print(f"mec_core.sql import: {mec_core_cmd}")
        exit(1)
    except Exception as e:
        print(f"sql Import Error: {e}")
