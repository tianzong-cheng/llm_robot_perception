docker rm -f foundationpose_cuda121
CATGRASP_DIR=$(pwd)/../
xhost +  && docker run --gpus all --env NVIDIA_DISABLE_REQUIRE=1 -it --network=host --name foundationpose_cuda121  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined -v /home/tianzong:/home/tianzong -v /mnt:/mnt -v /tmp/.X11-unix:/tmp/.X11-unix -v /tmp:/tmp  --ipc=host -e DISPLAY=${DISPLAY} -e GIT_INDEX_FILE shingarey/foundationpose_custom_cuda121:latest bash
