# HOW TO RUN

This repository is currently maintained by Tianzong Cheng.

## I. Environment

### i. ZED SDK

Install from [StereoLabs](https://www.stereolabs.com/developers/release). The AI module is not used in this project, so you can choose not to install it to save time.

### ii. ultralytics

Simply `pip install ultralytics`.

### iii. FoundationPose

#### Docker

If you are running this project on a 40-series GPU, use [this docker image](https://hub.docker.com/r/shingarey/foundationpose_custom_cuda121) (refer to [this](https://github.com/NVlabs/FoundationPose/issues/27)). Note that this is the default.

If you are running the project for the first time, you need to manually run `FoundationPose/build_all.sh` in the docker environment. This step isn't required later.

#### Data Prepare

Follow [FoundationPose README](https://github.com/NVlabs/FoundationPose?tab=readme-ov-file#data-prepare) and download weight files (demo data are not needed).

### iv. Misc

Download from [JBox](https://jbox.sjtu.edu.cn/l/n1b4yu) and extract it to the root folder: `assets/mesh` and `assets/cam_K.txt`.

## II. Run

Run `run.sh` under the root directory.

First, 30 frames will be captured to `video/` folder at 15 FPS and exported to `.png` format. Then, the `seg/draw_mask_cup.py` script will draw the mask of the mug. Finally, run FoundationPose.

You can change how many frames is recorded in `ZED/record.py`.

The output is under `FoundationPose/debug/ob_in_cam`, in the format of a homogeneous transformation matrix.
