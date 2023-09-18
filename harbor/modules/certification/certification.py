import subprocess
import yaml

def config(harbor_path: str):
    ca_create_cmd = 'openssl genrsa -out %s/ca.key 4096' % harbor_path
    cacrt_create_cmd = f'openssl req -x509 -new -nodes -sha512 -days 3650 -subj "/C=KR/ST=Seoul/L=Seoul/O=SKT/OU=IT/CN=vision.harbor.core" -key {harbor_path}/ca.key -out {harbor_path}/ca.crt'

    key_create_cmd = 'openssl genrsa -out %s/vision.harbor.core.key 4096' % harbor_path
    csr_create_cmd = f'openssl req -sha512 -new -subj "/C=KR/ST=Seoul/L=Seoul/O=SKT/OU=IT/CN=vision.harbor.core" -key {harbor_path}/vision.harbor.core.key -out {harbor_path}/vision.harbor.core.csr'
    crt_create_cmd = f'openssl x509 -req -sha512 -days 3650 -extfile {harbor_path}/v3.ext -CA {harbor_path}/ca.crt -CAkey {harbor_path}/ca.key -CAcreateserial  -in {harbor_path}/vision.harbor.core.csr  -out {harbor_path}/vision.harbor.core.crt'

    try:
        #ca create
        subprocess.run(ca_create_cmd, shell=True, check=True)
        #ca verify
        verify_key(harbor_path, "ca.key")

        #ca.crt create
        subprocess.run(cacrt_create_cmd, shell=True, check=True)

        #server certi. create
        subprocess.run(key_create_cmd, shell=True, check=True)
        #server key verify
        verify_key(harbor_path, "vision.harbor.core.key")

        #csr file create
        subprocess.run(csr_create_cmd, shell=True, check=True)
        
        #crt file create
        subprocess.run(crt_create_cmd, shell=True, check=True)

        #create secret yaml
        create_secret(harbor_path)

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

def key_encoder(harbor_path: str, fil_name: str) -> str:

    key_file = '%s/%s' %(harbor_path, file_name)

    try:
        encoding_cmd = 'cat %s | base64 -w 0' % key_file
        subprocess.run(encoding_cmd, shell=True, check=True)
       
    except subprocess.CalledProcessError as e:
        print("test", e)

def create_secret(harbor_path: str):

    crt_cmd = 'cat %s/vision.harbor.core.crt | base64 -w 0' % harbor_path
    crt_completed = subprocess.run(crt_cmd, shell=True, check=True, stdout=subprocess.PIPE)
    tls_crt_base64 = crt_completed.stdout.decode('utf-8')

    
    key_cmd = 'cat %s/vision.harbor.core.key | base64 -w 0' % harbor_path
    key_completed = subprocess.run(key_cmd, shell=True, check=True, stdout=subprocess.PIPE)
    tls_key_base64 = key_completed.stdout.decode('utf-8')

    data = {
    'apiVersion': 'v1',
    'data': {
        'tls.crt': tls_crt_base64,
        'tls.key': tls_key_base64,
    },
    'kind': 'Secret',
    'metadata': { 
     'name': 'harbor-tls',
     'namespace': 'harbor',
     },
    'type': 'kubernetes.io/tls'
    }

    with open(harbor_path+"/secret.yaml", "w") as yaml_file:
        yaml.dump(data, yaml_file, default_style='')    
