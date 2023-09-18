import yaml
import kubernetes

from modules.env import env
from modules.certification import certification
from modules.harbor_install import harbor_install


with open("./config/config.yaml", "r") as config_file:
    config_data = yaml.load(config_file, Loader=yaml.FullLoader)

#config 

harbor_base_path = config_data["path_config"]["harbor_base"]

if __name__ == "__main__":

    # harbor env config
    env.config()
   
    # harbor cert. config 
    #certification.config(harbor_base_path)

    # harbor helm install 
    harbor_install.create_namespace()
    harbor_install.apply_secret(harbor_base_path)
    #3. helm chart install 


    # k8s <-> running check 


