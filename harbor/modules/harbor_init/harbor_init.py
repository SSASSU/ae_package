import requests

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

            response = requests.post(url, headers=headers, json=data, auth=auth, verify=False)  # verify=False는 SSL 인증서 검증 무시

            if response.status_code >= 200 and response.status_code < 300:
                print("request : %s" %response.request.body)
                print("response : [%d] %s" %(response.status_code, response.text))
 
            else:
                print("response : [%s] %s" %(response.status_code, response.text))

    except Exception as e:
        print(f"Project Create API Failed: {str(e)}")
