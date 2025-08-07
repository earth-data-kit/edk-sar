IMAGE_NAME="edk-sar-isce2"

CONTAINER_ID=$(docker ps -q --filter "ancestor=${IMAGE_NAME}")

if [ -z "$CONTAINER_ID" ]; then
  echo "No running container found with image: $IMAGE_NAME"
  exit 1
fi

docker exec -it "$CONTAINER_ID" /bin/bash
