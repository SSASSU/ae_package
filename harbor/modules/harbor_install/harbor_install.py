from kubernetes import client, config
import subprocess
import os

def create_namespace():
    # Kubernetes 클러스터 설정 로드
    config.load_kube_config()  # 또는 config.load_incluster_config()를 사용하여 인클러스터 구성 로드

    # Kubernetes API 클라이언트 생성
    v1 = client.CoreV1Api()

    # Namespace 오브젝트 생성
    namespace = client.V1Namespace()
    namespace.metadata = client.V1ObjectMeta(name="harbor")

    try:
        # Namespace 생성
        v1.create_namespace(namespace)
        print(f"Namespace Created")
    except Exception as e:
        print(f"Namespace Create Error: {str(e)}")

def apply_secret(harbor_path: str):
    # Kubernetes 클러스터 설정 로드
    config.load_kube_config()  # 또는 config.load_incluster_config()를 사용하여 인클러스터 구성 로드

    # Kubernetes API 클라이언트 생성
    api_instance = client.CustomObjectsApi()

    # Secret을 적용할 namespace 및 파일 경로 설정
    namespace = "harbor"  # 적용할 namespace 이름으로 변경
    secret_file = harbor_path+"/secret.yaml"    # 적용할 Secret 이름으로 변경

    # Secret 적용 명령어 생성
    secret_apply_cmd = [
        "kubectl",
        "apply",
        "-f",
        secret_file,
        "-n",
        namespace,
    ]

    try:
        # kubectl 명령 실행
        os.system(" ".join(secret_apply_cmd))
        print(f"Secret Applied at harbor namespace")
    except Exception as e:
        print(f"Secret Apply Error: {str(e)}")

def helm_install(harbor_path: str):
    try:
        # Helm 차트 설치 명령 실행
        repo_add_cmd = "helm repo add harbor https://helm.goharbor.io"
        helm_install_cmd = [
            "helm",
            "install",
            "harbor",
            "harbor/harbor",
            "-n",
            "harbor",
            "-f",
            harbor_path+"/values.yaml"
        ]
        subprocess.run(repo_add_cmd, shell=True, check=True)
        subprocess.run(helm_install_cmd, check=True)
        print(f"Helm Installed")
    except subprocess.CalledProcessError as e:
        print(f"Helm Install Error: {str(e)}")
