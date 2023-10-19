import time

from kubernetes import client, config
from kubernetes.client.rest import ApiException

def running_check(stdscr, namespace, timeout_seconds=300):

    config.load_kube_config()

    v1 = client.CoreV1Api()

    start_time = time.time()
    end_time = start_time + timeout_seconds

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Namespace: {namespace}")
        stdscr.addstr(1, 0, "Pods:")

        if time.time() > end_time:
            stdscr.addstr(2, 0, f"The pods did not transition to the Running state for {timeout_seconds} seconds.")
            break

        try:
            pods = v1.list_namespaced_pod(namespace)
        except ApiException as e:
            stdscr.addstr(2, 0, f"An error occurred while fetching the list of pods: {e}")
            break

        row = 3
        all_running = True

        for pod in pods.items:
            if pod.status.phase != "Running":
                all_running = False
                stdscr.addstr(row, 2, f"- {pod.metadata.name}, Phase: {pod.status.phase}\n")
            else:
                stdscr.addstr(row, 2, f"- {pod.metadata.name}, Phase: {pod.status.phase}\n")
            row += 1

        if all_running:
            stdscr.addstr(row, 0, f"\nAll pods are in Running state. Continuing in 30 seconds.")
            stdscr.refresh()
            time.sleep(30)
            break

        elapsed_time = int(time.time() - start_time)
        stdscr.addstr(row + 1, 0, f"Elapsed time: {elapsed_time} seconds")

        stdscr.refresh()
        time.sleep(1)  # loop restart every 1sec

