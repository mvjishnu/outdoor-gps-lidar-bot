#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="odgps_container"
IMAGE_NAME="ros2_humble"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

DISPLAY_VALUE="${DISPLAY:-}"
WAYLAND_NAME=""
WAYLAND_SOCKET=""
if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
	if [[ "$WAYLAND_DISPLAY" = /* ]]; then
		WAYLAND_SOCKET="$WAYLAND_DISPLAY"
		WAYLAND_NAME="$(basename "$WAYLAND_SOCKET")"
	else
		WAYLAND_NAME="$WAYLAND_DISPLAY"
		WAYLAND_SOCKET="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/$WAYLAND_DISPLAY"
	fi
	[[ -S "$WAYLAND_SOCKET" ]] || WAYLAND_SOCKET=""
fi

DISPLAY_KIND=""
if [[ -n "$DISPLAY_VALUE" ]]; then
	DISPLAY_NUMBER="${DISPLAY_VALUE##*:}"
	DISPLAY_NUMBER="${DISPLAY_NUMBER%%.*}"
	if [[ -S "/tmp/.X11-unix/X${DISPLAY_NUMBER}" ]]; then
		DISPLAY_KIND=x11
	fi
fi
if [[ -z "$DISPLAY_KIND" && -n "$WAYLAND_SOCKET" ]]; then
	DISPLAY_KIND=wayland
	WAYLAND_NAME="${WAYLAND_NAME:-wayland-0}"
	DISPLAY_VALUE=""
fi
if [[ -z "$DISPLAY_KIND" ]]; then
	echo "No usable X11/XWayland or Wayland display was found. Start the launcher from a desktop session." >&2
	exit 1
fi

NVIDIA_ARGS=()
NVIDIA_ENV=()
if command -v nvidia-smi >/dev/null 2>&1 && docker info --format '{{json .Runtimes}}' 2>/dev/null | grep -q '"nvidia"'; then
	NVIDIA_ARGS+=(--gpus all)
	NVIDIA_ENV+=( -e NVIDIA_VISIBLE_DEVICES=all
		-e NVIDIA_DRIVER_CAPABILITIES=graphics,compute,utility,video
		-e __NV_PRIME_RENDER_OFFLOAD=1
		-e __GLX_VENDOR_LIBRARY_NAME=nvidia
		-e __VK_LAYER_NV_optimus=NVIDIA_only )
fi
if [[ -d /dev/dri ]]; then
	SOFTWARE_GL=0
else
	SOFTWARE_GL=1
fi

if [[ "$DISPLAY_KIND" == x11 ]]; then
	# Grant only this local root client access to the current X server.
	xhost +SI:localuser:root >/dev/null 2>&1 || true
fi

if ! docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
	mkdir -p "$PROJECT_ROOT/build" "$PROJECT_ROOT/install" "$PROJECT_ROOT/log"
	RUN_ARGS=(docker run -d
		--name "$CONTAINER_NAME"
		--hostname ros2_dev
		--network host
		--ipc=host
		--privileged
		"${NVIDIA_ARGS[@]}"
		--tmpfs /run/user/0:uid=0,gid=0,mode=0700
		-e "DISPLAY=$DISPLAY_VALUE"
		-e QT_QPA_PLATFORM='wayland;xcb'
		-e QT_X11_NO_MITSHM=1
		-e XDG_RUNTIME_DIR=/run/user/0
		-e LIBGL_ALWAYS_SOFTWARE="$SOFTWARE_GL"
		-e GZ_IP=127.0.0.1
		-e IGN_IP=127.0.0.1
		-e GZ_PARTITION=outdoor_gps
		-e IGN_PARTITION=outdoor_gps
		-v "$PROJECT_ROOT/src:/root/od_gps_bot/src"
		-v "$PROJECT_ROOT/build:/root/od_gps_bot/build"
		-v "$PROJECT_ROOT/install:/root/od_gps_bot/install"
		-v "$PROJECT_ROOT/log:/root/od_gps_bot/log"
		-w /root/od_gps_bot)
	if [[ "$DISPLAY_KIND" == x11 ]]; then
		RUN_ARGS+=( -v /tmp/.X11-unix:/tmp/.X11-unix:rw )
	else
		RUN_ARGS+=( -e "WAYLAND_DISPLAY=$WAYLAND_NAME"
			-v "$WAYLAND_SOCKET:/run/user/0/$WAYLAND_NAME:rw" )
	fi
	if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
		echo "Building the ROS 2/Gazebo image on first use..."
		docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
	fi
	"${RUN_ARGS[@]}" "${NVIDIA_ENV[@]}" "$IMAGE_NAME" sleep infinity
else
	if [[ "$DISPLAY_KIND" == wayland ]] && ! docker inspect "$CONTAINER_NAME" --format '{{range .Mounts}}{{if eq .Destination "/run/user/0/'"$WAYLAND_NAME"'"}}present{{end}}{{end}}' 2>/dev/null | grep -q present; then
		echo "The existing container was not created with this Wayland socket. Stop and remove '$CONTAINER_NAME', then rerun this launcher to recreate it for native Wayland." >&2
		exit 1
	fi
fi

docker start "$CONTAINER_NAME" >/dev/null
docker exec "$CONTAINER_NAME" install -d -m 0700 /run/user/0
if [[ "$DISPLAY_KIND" == x11 ]]; then
	DISPLAY_ENV=(-e "DISPLAY=$DISPLAY_VALUE")
else
	DISPLAY_ENV=(-e DISPLAY= -e "WAYLAND_DISPLAY=$WAYLAND_NAME")
fi

if ! docker exec "$CONTAINER_NAME" test -f /root/od_gps_bot/install/setup.bash; then
	echo "Building the outdoor GPS/LiDAR ROS 2 workspace..."
	docker exec "$CONTAINER_NAME" bash -lc \
		'source /opt/ros/humble/setup.bash && cd /root/od_gps_bot && colcon build --symlink-install'
fi

exec docker exec -it \
	"${DISPLAY_ENV[@]}" \
	-e 'QT_QPA_PLATFORM=wayland;xcb' \
	-e QT_X11_NO_MITSHM=1 \
	-e XDG_RUNTIME_DIR=/run/user/0 \
	-e "LIBGL_ALWAYS_SOFTWARE=$SOFTWARE_GL" \
	-e GZ_IP=127.0.0.1 -e IGN_IP=127.0.0.1 \
	-e GZ_PARTITION=outdoor_gps -e IGN_PARTITION=outdoor_gps \
	"${NVIDIA_ENV[@]}" \
	"$CONTAINER_NAME" bash
