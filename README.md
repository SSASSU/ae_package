# ae_package
This is a project created to make "ae" installation easy.

## Requirements
"ae_package" operates on a Kubernetes cluster with a minimum requirement of one master node and two worker nodes. The supported operating system is Ubuntu 20.04, compatible with both ARM and x86 architectures.

| item      | version          | note |
|-----------|--------------|------|
| ubuntu | 20.04 | |
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

#### - ae_package configuration 
[Container image file list in ./ae_package/harbor/images]

✅ openjdk.tar

✅ vsai-bridge-app.tar

✅ vsai-message-app.tar

✅ vsai-metric-pusher.tar

✅ vsai-view-app.tar

✅ vsai-workflow-app.tar

[Config File List in ./ae_package/harbor/config]

✅ ai_data.sql

✅ cp_data.sql

✅ mec_core.sql

✅ mec_vision_ai.sql

✅ config.yaml

✅ containerd_config.toml

✅ secret_config.yaml

✅ secret_config.yaml_template


You should fill in the appropriate content in the "secret_config.yaml_template" and then rename it to "secret_config.yaml".

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

#### - If your system is x86-based, make the following changes to the Harbor's `values.yaml` file.
```
# cd /root/ae_package/harbor/harbor_values
# mv values_x86.yaml values.yaml
```

#### - ae_package install 
```
# cd /root/ae_package/harbor
# python main.py
```