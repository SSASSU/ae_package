import yaml 

from modules.env import env
from modules.certification import certification

with open("./config/config.yaml", "r") as config_file:
    config_data = yaml.load(config_file, Loader=yaml.FullLoader)

#config 

harbor_base_path = config_data["path_config"]["harbor_base"]

if __name__ == "__main__":

    # harbor env config
    env.config()
   
    # harbor cert. config 
    certification.config(harbor_base_path)

    # harbor helm install 

    # k8s <-> running check 


