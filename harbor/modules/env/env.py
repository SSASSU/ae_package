import subprocess
import paramiko
import os 

from kubernetes import client, config

def get_k8s_node_ip(node_ips: list, master_ips: list):

    config.load_kube_config()

    #Get Node Info.
    v1 = client.CoreV1Api()
    node_info_list = v1.list_node().items

    #Get Internal Node IP
    for node in node_info_list:
 
        node_labels = node.metadata.labels
        addresses = node.status.addresses

        for addr in addresses:
            if addr.type == "InternalIP":
                node_ips.append(addr.address)
                #Get Master Node
                if "node-role.kubernetes.io/master" in node_labels:
                    master_ips.append(addr.address)

def ssl_config():

    command = 'openssl version'

    try:
        os.environ['LD_LIBRARY_PATH'] = "/usr/local/lib/"
        subprocess.run(command, shell=True, check=True)
        print("openssl checked!")

    except subprocess.CalledProcessError as e:
        print("error:", e)

def ssh_key_generator():

    key_file = "/root/.ssh/id_rsa"
    key_comment = ""
    
    try:
        #Old Key file Remove
        subprocess.run(["rm", "-rf", "/root/.ssh/id_rsa"], check=True)

        #ssh keygen 
        subprocess.run(
                ["ssh-keygen", "-t", "rsa", "-f", key_file, "-C", key_comment, "-N", ""],
                check=True
                )
    except subprocess.CalledProcessError as e:
        print(f"RSA key Generation Error: {e}")


def ssh_key_copy(node_ips: list, host_info: dict):

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        for node_ip in node_ips:
            ssh_client.connect(node_ip, username=host_info["account"]["id"], password=host_info["account"]["pass"])
            ssh_key_path = os.path.expanduser("~/.ssh/id_rsa.pub")
            ssh_key = open(ssh_key_path).read()
            ssh_client.exec_command(f"echo '{ssh_key}' > ~/.ssh/authorized_keys")
            ssh_client.close()
            print(f"{node_ip} : SSH Key Copied")

    except Exception as e:
        print(f"{node_ip} : SSH Key Copy Error: {str(e)}")


def harbor_add_host(master_ips: list, node_ips: list, host_info: dict):

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    harbor_host ="%s\tvision.harbor.core\n" %master_ips[0]
    harbor_host =harbor_host.encode('utf-8')

    try:
        for node_ip in node_ips:
            ssh_client.connect(node_ip, username=host_info["account"]["host_id"], password=host_info["account"]["host_pass"])

            with ssh_client.open_sftp().file("/etc/hosts", "r") as hosts_file:
                current_contents = hosts_file.read()

                if harbor_host in current_contents:
                    print(f"{node_ip}: {harbor_host} exist in /etc/hosts")

                else:
                    with ssh_client.open_sftp().file("/etc/hosts", "a") as hosts_file:
                        hosts_file.write("\n%s" %harbor_host.decode('utf-8'))
                        print(f"{node_ip}: /etc/hosts {harbor_host} added")
    
            ssh_client.close()

    except Exception as e:
        print(f"{node_ip} : /etc/hosts Configuration Error: {str(e)}")

