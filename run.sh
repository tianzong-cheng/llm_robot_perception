LLM_PERCEPTION_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export LLM_PERCEPTION_PATH
cd $LLM_PERCEPTION_PATH

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
xhost +  && docker run --gpus all --env NVIDIA_DISABLE_REQUIRE=1 -it --network=host --name foundationpose_cuda121  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined -v /home:/home -v /mnt:/mnt -v /tmp/.X11-unix:/tmp/.X11-unix -v /tmp:/tmp  --ipc=host -e DISPLAY=${DISPLAY} -e GIT_INDEX_FILE -e LLM_PERCEPTION_PATH="${LLM_PERCEPTION_PATH}" shingarey/foundationpose_custom_cuda121:latest python "${LLM_PERCEPTION_PATH}/FoundationPose/run_demo.py"
