import subprocess
import paramiko
import os 

from kubernetes import client, config

def get_k8s_node_info(k8s_nodes: dict):

    config.load_kube_config()

    v1 = client.CoreV1Api()
    node_info_list = v1.list_node().items

    for node in node_info_list:
 
        node_labels = node.metadata.labels
        addresses = node.status.addresses
        host_name: str
        ip: str

        for addr in addresses:
            if addr.type == "InternalIP":
                ip = addr.address

            if addr.type == "Hostname":
                host_name = addr.address

        if "node-role.kubernetes.io/master" in node_labels:
            k8s_nodes[ip] = (host_name, "master")
        else:
            k8s_nodes[ip] = (host_name, "worker")       

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


def ssh_key_copy(k8s_nodes: dict, user_info: dict):

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        for node_ip in k8s_nodes:
            ssh_client.connect(node_ip, username=user_info["account"]["id"], password=user_info["account"]["pass"])
            ssh_key_path = os.path.expanduser("~/.ssh/id_rsa.pub")
            ssh_key = open(ssh_key_path).read()
            ssh_client.exec_command(f"echo '{ssh_key}' > ~/.ssh/authorized_keys")
            ssh_client.close()
            print(f"{node_ip} : SSH Key Copied")

    except Exception as e:
        print(f"{node_ip} : SSH Key Copy Error: {str(e)}")


def harbor_add_host(k8s_nodes: dict, user_info: dict):

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    
    harbor_host ="%s\tvision.harbor.core\n" %list(k8s_nodes.keys())[0]
    harbor_host =harbor_host.encode('utf-8')

    try:
        for node_ip in k8s_nodes:
            ssh_client.connect(node_ip, username=user_info["account"]["host_id"], password=user_info["account"]["host_pass"])

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

def insecure_regi_config(k8s_nodes: dict, user_info: dict):

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #containerd restart command 
    containerd_restart_cmd = "service containerd restart"

    try:
        for node_ip in k8s_nodes:
            ssh_client.connect(node_ip, username=user_info["account"]["host_id"], password=user_info["account"]["host_pass"])

            sftp = ssh_client.open_sftp()
            sftp.put("./config/containerd_config.toml", "/etc/containerd/config.toml")
            print (f"{node_ip}: config.toml Copied")

            sftp.close()

            stdin, stdout, stderr = ssh_client.exec_command(containerd_restart_cmd) 
            print (f"{node_ip}: Containerd service restart: {containerd_restart_cmd}")

            ssh_client.close()

    except Exception as e:
        print(f"{node_ip} : Containerd Insecure Registry Config Error: {str(e)}")

