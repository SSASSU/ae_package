import yaml
import kubernetes
import curses

from modules.env import env
from modules.certification import certification
from modules.harbor_install import harbor_install


with open("./config/config.yaml", "r") as config_file:
    config_data = yaml.load(config_file, Loader=yaml.FullLoader)

#config 

harbor_base_path = config_data["path_config"]["harbor_base"]

def running_check(stdscr):
    curses.curs_set(0) #cursor hide
    namespace_to_check = "harbor"  # namespace 
    timeout_seconds = 500  #timeout
    harbor_install.running_check(stdscr, namespace_to_check, timeout_seconds)

if __name__ == "__main__":

    # harbor env config
    env.config()
   
    # harbor cert. config 
    certification.config(harbor_base_path)

    # harbor helm install 
    harbor_install.create_namespace()
    harbor_install.apply_secret(harbor_base_path)
    harbor_install.helm_install(harbor_base_path)

    # k8s <-> running check 
    curses.wrapper(running_check)
    print("계속 진행")
