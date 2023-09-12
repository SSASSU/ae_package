import subprocess

def config(harbor_path: str):
    ca_create_cmd = 'openssl genrsa -out %s/ca.key 4096' % harbor_path
    key_create_cmd = 'openssl genrsa -out %s/vision.harbor.core.key 4096' % harbor_path
    csr_create_cmd = f'openssl req -sha512 -new \ -subj "/C=KR/ST=Seoul/L=Seoul/O=SKT/OU=IT/CN=vision.harbor.core" -key {harbor_path}/vision.harbor.core.key -out {harbor_path}/vision.harbor.core.csr'

    try:
        #ca create
        subprocess.run(ca_create_cmd, shell=True, check=True)
        #ca verify
        verify_key(harbor_path, "ca.key")

        #server certi. create
        subprocess.run(key_create_cmd, shell=True, check=True)
        #server key verify
        verify_key(harbor_path, "vision.harbor.core.key")

    except subprocess.CalledProcessError as e:
        print("error:", e)

def verify_key(harbor_path: str, file_name: str): 
    key_file = '%s/%s' %(harbor_path, file_name)
    
    try:
        command = 'openssl rsa -in %s -check -noout' % key_file
        subprocess.run(command, shell=True, check=True)
        print("%s is Valid" %file_name)
    except subprocess.CalledProcessError as e:
        print("%s is Invalid", e %file_name)


