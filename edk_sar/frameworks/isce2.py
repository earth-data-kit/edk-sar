import subprocess
import docker
import logging

logger = logging.getLogger(__name__)


def init(env_path):
    docker_compose_path = "edk_sar/dockerfiles/docker-compose.yml"

    cmd = [
        "docker",
        "compose",
        "-f",
        docker_compose_path,
        "--env-file",
        env_path,
        "up",
        "--build",
        "-d",
    ]

    # Build the Docker Compose services
    subprocess.run(cmd, check=True)


def get_container_id():
    cmd = ["docker", "ps", "-q", "-f", "name=edk-sar-isce2"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def run_cmd(cmd):
    logger.info(f"Running command: {cmd}")
    container_id = get_container_id()
    client = docker.from_env()
    container = client.containers.get(container_id)

    # Stream output as it is produced
    exec_result = container.exec_run(cmd, stdout=True, stderr=True, stream=True)
    for chunk in exec_result.output:
        print (chunk.decode().rstrip())
