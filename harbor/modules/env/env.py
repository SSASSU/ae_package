import subprocess
import os 

from kubernetes import client, config

def ssl_config():
    command = 'openssl version'

    try:
        os.environ['LD_LIBRARY_PATH'] = "/usr/local/lib/"
        subprocess.run(command, shell=True, check=True)
        print("openssl checked!")

    except subprocess.CalledProcessError as e:
        print("error:", e)


def ssh_key_copy():

    config.load_kube_config()

    #Get Node Info. 
    v1 = client.CoreV1Api()
    node_list = v1.list_node().items

    #Get Internal Node IP
    node_ips = []
    for node in node_list:
        addresses = node.status.addresses
        for addr in addresses:
            if addr.type == "InternalIP":
                node_ips.append(addr.address)

    print (node_ips)
