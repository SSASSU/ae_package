from kubernetes import client, config
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
        print(f"Namespace 생성되었습니다.")
    except Exception as e:
        print(f"Namespace 생성 중 오류 발생: {str(e)}")

def apply_secret(harbor_path: str):
    # Kubernetes 클러스터 설정 로드
    config.load_kube_config()  # 또는 config.load_incluster_config()를 사용하여 인클러스터 구성 로드

    # Kubernetes API 클라이언트 생성
    api_instance = client.CustomObjectsApi()

    # Secret을 적용할 namespace 및 파일 경로 설정
    namespace = "harbor"  # 적용할 namespace 이름으로 변경
    secret_file = harbor_path+"/secret.yaml"    # 적용할 Secret 이름으로 변경

    # Secret 적용 명령어 생성
    command = [
        "kubectl",
        "apply",
        "-f",
        secret_file,
        "-n",
        namespace,
    ]

    try:
        # kubectl 명령 실행
        os.system(" ".join(command))
        print(f"Secret'이(가) '{namespace}' 네임스페이스에 적용되었습니다.")
    except Exception as e:
        print(f"Secret 적용 중 오류 발생: {str(e)}")
