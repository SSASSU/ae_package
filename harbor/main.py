import yaml
import kubernetes
import curses

from collections import OrderedDict
from typing import Dict
from modules.env import env
from modules.common import common
from modules.certification import certification
from modules.harbor_install import harbor_install
from modules.harbor_init import harbor_init
from modules.viewapps_install import viewapps_install
from modules.basicapps_install import basicapps_install

#Config file load 
with open("./config/config.yaml", "r") as config_file:
    config_data = yaml.load(config_file, Loader=yaml.FullLoader)

with open("./config/secret_config.yaml", "r") as config_file:
    user_info = yaml.load(config_file, Loader=yaml.FullLoader)

#Global 
k8s_nodes: Dict[str, tuple] =  OrderedDict()#{ ip, (node name, role) }

config_path = "./config"
harbor_base_path = config_data["path_config"]["harbor_base"]
harbor_image_path = config_data["path_config"]["image_path"]
viewapps_path = config_data["path_config"]["viewapps"] 
basicapps_path = config_data["path_config"]["basicapps"] 
project_list = config_data["project_list"]

def running_check(stdscr, namespace: str):

    curses.curs_set(0) 
    namespace_to_check = namespace
    timeout_seconds = 500
    common.running_check(stdscr, namespace_to_check, timeout_seconds)

if __name__ == "__main__":

    # SSL config(ARM openssl lib issue)
    env.ssl_config()
    # Get Node Info -> { ip, (node name, role) } 
    env.get_k8s_node_info(k8s_nodes)

    # ssh key copy
    env.ssh_key_generator()
    env.ssh_key_copy(k8s_nodes, user_info)

    # Harbor Host Config
    env.harbor_add_host(k8s_nodes, user_info)
    #Insecure Registry Config & Containerd restart

    env.insecure_regi_config(k8s_nodes, user_info)
    # Harbor Cert. Config 
    certification.config(harbor_base_path)

    # Harbor Helm Install & running check
    harbor_install.helm_install(harbor_base_path)
    curses.wrapper(running_check, "harbor")
    
    # Harbor Login 
    harbor_install.harbor_login(k8s_nodes, user_info)     

    # Harbor Init (project create, image upload)
    harbor_init.create_projects(project_list, user_info)
    harbor_init.upload_images(harbor_image_path)
 
    # Viewapps - Modify node metadata/annotation 
    viewapps_install.update_node_label(k8s_nodes)
    
    # Viewapps Helm Install & running check 
    viewapps_install.viewapps_helm_install(viewapps_path)
    curses.wrapper(running_check, "viewapps")
    viewapps_install.kube_config_copy()
    viewapps_install.workflow_add_host(k8s_nodes, user_info)
    
    # harbor webhook config
    harbor_init.webhook_config(user_info)

    # Viewapps DB init 
    viewapps_install.viewapps_db_init(config_path, user_info, k8s_nodes)

    # Basicapps - Modify node metadata/annotation
    basicapps_install.update_node_label(k8s_nodes)
    basicapps_install.basicapps_helm_install(basicapps_path)
    curses.wrapper(running_check, "default")
    basicapps_install.basicapps_db_init(config_path, user_info, k8s_nodes)

    



