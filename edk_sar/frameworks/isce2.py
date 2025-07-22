import subprocess
import docker

def init():
    docker_compose_path = "edk_sar/dockerfiles/docker-compose.yml"

    cmd = ["docker", "compose", "-f", docker_compose_path, "up", "--build", "-d"]

    # Build the Docker Compose services
    subprocess.run(
        cmd,
        check=True
    )

def get_container_id():
        cmd = ["docker", "ps", "-q", "-f", "name=edk-sar-isce2"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()

def run_cmd(cmd):
    container_id = get_container_id()
    client = docker.from_env()
    container = client.containers.get(container_id)

    exec_result = container.exec_run(cmd, stdout=True, stderr=True)
    return exec_result.output.decode()    