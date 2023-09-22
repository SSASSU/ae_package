import yaml
import kubernetes
import curses

from modules.env import env
from modules.certification import certification
from modules.harbor_install import harbor_install

with open("./config/config.yaml", "r") as config_file:
    config_data = yaml.load(config_file, Loader=yaml.FullLoader)

with open("./config/secret_config.yaml", "r") as config_file:
    host_info = yaml.load(config_file, Loader=yaml.FullLoader)

#Global 

master_ips = []
node_ips = []
harbor_base_path = config_data["path_config"]["harbor_base"]


def running_check(stdscr):
    curses.curs_set(0) #cursor hide
    namespace_to_check = "harbor"  # namespace 
    timeout_seconds = 500  #timeout
    harbor_install.running_check(stdscr, namespace_to_check, timeout_seconds)

if __name__ == "__main__":

    # SSL config(ARM openssl lib issue)
    env.ssl_config()

    # Get Node Ip #List 
    env.get_k8s_node_ip(node_ips, master_ips)

    # ssh key copy
    env.ssh_key_generator()
    env.ssh_key_copy(node_ips, host_info)

    # Harbor Host Config
    env.harbor_add_host(master_ips, node_ips, host_info)
    exit(1)

    # Harbor Cert. Config 
    certification.config(harbor_base_path)

    # Harbor Helm Install 
    harbor_install.create_namespace()
    harbor_install.apply_secret(harbor_base_path)
    harbor_install.helm_install(harbor_base_path)

    # Kubernetes <-> Harbor Pods running check 
    curses.wrapper(running_check)
    print("계속 진행")
