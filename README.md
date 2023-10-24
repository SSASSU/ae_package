# ae_package
This is a project created to make "ae" installation easy.

## Requirements
"ae_package" operates on a Kubernetes cluster with a minimum requirement of one master node and two worker nodes. The supported operating system is Ubuntu 20.04, compatible with both ARM and x86 architectures.

| item      | version          | note |
|-----------|--------------|------|
| kubernetes  | v1.23.13 |    |
| containerd| v1.6.6   |   |
| mysql-client |  8.0 |  |
| python | 3.9 | |
| helm | v3.13.1 | |

## Installation

#### - ae_package clone
```
# cd
# git clone https://github.com/SSASSU/ae_package.git
```

#### - helm3 install
```
# cd /root/ae_package/harbor/scripts
# ./helm3_installer.sh
```

#### - python & python Package install 
```
# apt update
# apt install -y python3.9
# cp /bin/python3.9 /bin/python
# cd /root/ae_package/harbor/scripts
# ./python_package_installer.sh
```

#### - mysql-client install
```
# apt install -y mysql-client-8.0
```

#### - ae_package install 
```
# cd /root/ae_package/harbor
# python main.py
```