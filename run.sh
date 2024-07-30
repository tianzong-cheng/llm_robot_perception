rm -rf video
mkdir video
mkdir video/rgb
mkdir video/depth
mkdir video/masks
cp assets/cam_K.txt video/

# Record
python3 ZED/record.py
python3 ZED/svo_export.py --mode 4 --input_svo_file ./video/video.svo2 --output_path_dir ./video/

# Draw mask
python3 seg/draw_mask_cup.py

# Run FoundationPose
docker rm -f foundationpose_cuda121
CATGRASP_DIR=$(pwd)/../
xhost +  && docker run --gpus all --env NVIDIA_DISABLE_REQUIRE=1 -it --network=host --name foundationpose_cuda121  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined -v /home/tianzong:/home/tianzong -v /mnt:/mnt -v /tmp/.X11-unix:/tmp/.X11-unix -v /tmp:/tmp  --ipc=host -e DISPLAY=${DISPLAY} -e GIT_INDEX_FILE foundationpose_cuda121:latest python /home/tianzong/Documents/workspace/perception/FoundationPose/run_demo.py
