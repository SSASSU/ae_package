import os
from kubernetes import client, config

#view apps, basic apps labeling
def update_node_label(k8s_nodes: dict):

    # Kubernetes 설정 로드
    config.load_kube_config()

    # Kubernetes API 클라이언트 생성
    v1 = client.CoreV1Api()

    # 추가할 레이블 및 값 정의
    master_node_name = ""

    label={} 
    label["ProcessType"]="viewapps"

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
