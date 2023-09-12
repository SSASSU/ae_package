#/bin/bash
export LD_LIBRARY_PATH="/usr/local/lib"

curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh 

chmod +x get_helm.sh

./get_helm.sh

rm -rf ./get_helm.sh
