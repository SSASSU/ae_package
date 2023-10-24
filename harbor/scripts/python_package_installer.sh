#/bin/bash

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python ./get-pip.py
python -m pip install --ignore-installed PyYAML
python -m pip install -r ../requirements.txt  
python -m pip install --upgrade requests

