import requests
import os 
import subprocess
from kubernetes import client, config

def create_projects(project_list: list, user_info: dict):

    url = "https://vision.harbor.core:30101/api/v2.0/projects"

    headers = {
        "Content-Type": "application/json",
    }
  
    auth = (user_info["account"]["harbor_id"], user_info["account"]["harbor_pass"])

    try:
        for project_name in project_list:
        
            data = {
                "project_name": project_name,
                "public": True,
                "storage_limit": -1,
            }

            response = requests.post(url, headers=headers, json=data, auth=auth, verify=False)

            if response.status_code >= 200 and response.status_code < 300:
                print("request : %s" %response.request.body)
                print("response : [%d] %s" %(response.status_code, response.text))
 
            else:
                print("response : [%s] %s" %(response.status_code, response.text))

    except Exception as e:
        print(f"Project Create API Failed: {str(e)}")

def upload_images(image_path: str):

    #Get File List 
    file_list: list=[]

    for root, dirs, files in os.walk(image_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_list.append(file_path)


    for image_file in file_list:
        image_load_cmd = "nerdctl load < %s" %(image_file)
        
        try:
            subprocess.run(image_load_cmd, shell=True, check=True)
            print("%s Loaded" %image_file)
        except subprocess.CalledProcessError as e:
            print(f"{image_file} Load Failed: {e}")

    images_cmd = "nerdctl images | grep vision.harbor.core:30101"
    output = subprocess.check_output(images_cmd, shell=True, universal_newlines=True)

    lines = output.strip().split('\n')
    image_list: list=[]

    for line in lines:
        columns = line.split()
  
        if len(columns) >= 2:
            repository = columns[0]
            tag = columns[1]
            image_list.append(f"{repository}:{tag}")

    for image in image_list:
        push_cmd = "nerdctl push %s" %image
        output = subprocess.check_output(push_cmd, shell=True, universal_newlines=True)

def webhook_config(user_info: dict):
    
    common_url = "https://vision.harbor.core:30101/api/v2.0/projects/common_template/webhook/policies"
    vision_url = "https://vision.harbor.core:30101/api/v2.0/projects/visionai_template/webhook/policies"

    headers = {
        "Content-Type": "application/json",
    }
    auth = (user_info["account"]["harbor_id"], user_info["account"]["harbor_pass"])

    try:
        common_data = get_webhook_data("common", "harbor/commonTemplate")
        vision_data = get_webhook_data("vision", "harbor/webhook")
 
        response = requests.post(common_url, headers=headers, json=common_data, auth=auth, verify=False)

        if response.status_code >= 200 and response.status_code < 300:
            print("request : %s" %response.request.body)
            print("response : [%d] %s" %(response.status_code, response.text))

        else:
            print("response : [%s] %s" %(response.status_code, response.text))

        response = requests.post(vision_url, headers=headers, json=vision_data, auth=auth, verify=False)

        if response.status_code >= 200 and response.status_code < 300:
            print("request : %s" %response.request.body)
            print("response : [%d] %s" %(response.status_code, response.text))

        else:
            print("response : [%s] %s" %(response.status_code, response.text)) 

    except Exception as e:

        print(f"Webhook Create API Failed: {str(e)}")


def get_webhook_data(webhook_name: str, webhook_path: str) -> str:

    config.load_kube_config()

    v1 = client.CoreV1Api()

    try:
        #Get the viewapps-workflow Service IP For Harbor Webhook
        service = v1.read_namespaced_service(name="vsai-workflow-app", namespace="viewapps")

        cluster_ip = service.spec.cluster_ip
        port = service.spec.ports[0].port

        data = {
            'enabled': True,
            'event_types': ["DELETE_ARTIFACT", "PULL_ARTIFACT", "PUSH_ARTIFACT"],
            'name': f'{webhook_name}',
            'targets': [{
                'address': f'http://{cluster_ip}:{port}/{webhook_path}',
                'skip_cert_verify': True,
                'type': 'http',
            }],
        }

        return data

    except client.rest.ApiException as e:
        print(f"Exception when calling CoreV1Api: {e}")
