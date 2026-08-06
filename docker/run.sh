CONTAINER_NAME="humble_container"
IMAGE_NAME="ros2_humble"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

xhost +SI:localuser:root >/dev/null

#Check if the container already exists (running or stopped)
if [ "$(docker ps -a -q -f name=^/${CONTAINER_NAME}$)" ]; then
	echo "Found existing container '${CONTAINER_NAME}'. Starting and attaching..."
	docker start "$CONTAINER_NAME"
	docker exec -it "$CONTAINER_NAME" bash
else
	echo "Container '${CONTAINER_NAME}' not found. Creating a new persistent one..."
	docker run -it \
		--name $CONTAINER_NAME \
		--hostname ros2_dev \
		--network host \
		--privileged \
		--ipc=host \
		-e DISPLAY=$DISPLAY \
		-e QT_X11_NO_MITSHM=1 \
		-v /tmp/.X11-unix:/tmp/.X11-unix:rw \
		-v "$PROJECT_ROOT/src:/root/od_gps_bot/src" \
		-w /root/od_gps_bot \
		$IMAGE_NAME
fi
		
