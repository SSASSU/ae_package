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

def basicapps_db_init(config_path: str, user_info: dict, k8s_nodes: dict):

    config.load_kube_config()
    v1 = client.CoreV1Api()

    viewapps_db_ip: str=""
    master_ip: str=""

    viewapps_db_prefix = "maria-db-vsaiweb"

    pod_list =  v1.list_namespaced_pod(namespace='viewapps')

    service = v1.read_namespaced_service(name="vsai-bridge-app-service", namespace="default")
    cluster_ip = service.spec.cluster_ip

    #get context
    context = config.list_kube_config_contexts()[1]
    cluster_name = context['context']['cluster']

    for node_ip in k8s_nodes:
        if "master" == k8s_nodes[node_ip][1]:
            master_ip = node_ip

    for pod in pod_list.items:
        if pod.metadata.name.startswith(viewapps_db_prefix):
            viewapps_db_ip = pod.status.pod_ip

    #DB init
    db_config = {
        "host": viewapps_db_ip,
        "user": user_info["account"]["viewapps_db_id"],
        "password": user_info["account"]["viewapps_db_pass"]
    }
    conn = mysql.connector.connect(**db_config)

    try:
        cursor = conn.cursor()

        #cluster_info_query
        cluster_info_query = f"insert into aiworkflow.t_vai_cluster_info (cluster_id, cluster_name, bridge_scheme, bridge_host, bridge_port,  config_path, region, provider, current_size, max_size,  min_size, master_nodes, v_cpu, memory, storage,  v_gpu, gpu, kube_version, os, status,  reg_id, reg_dt, mod_id, mod_dt, del_yn,  master_ip, prometheus_url, prometheus_id, prometheus_pw) VALUES('CIL01', '{cluster_name}', 'http', '{cluster_ip}', '8490',  '/app/resources/kube_config', 'bundang', 'libvirt', 3, 10,  3, 1, 2, 8, 256,  2, 2, '1.17.0', 'ubuntu1804', 'created',  'vsadmin1', now(), 'vsadmin1', now(), 'N',  '{master_ip}', 'http://223.62.140.9:30477/grafana/d/node_summary/node-exporter-nodes?orgId=1&refresh=30s&token=', NULL, NULL)"


        cursor.execute(cluster_info_query)
        conn.commit()

        print(f"query executed: {cluster_info_query}")

    except mysql.connector.Error as e:
        print(f"Error: {e}")

