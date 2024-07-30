# HOW TO RUN

This repository is currently maintained by Tianzong Cheng.

## I. Docker Environment for FoundationPose

If you are running this project on a 40-series GPU, use [this docker image](https://hub.docker.com/r/shingarey/foundationpose_custom_cuda121) (refer to [this](https://github.com/NVlabs/FoundationPose/issues/27)). Note that this is the default.

If you are running the project for the first time, you need to manually run `FoundationPose/build_all.sh` in the docker environment. This step isn't required later.

## II. Modify the Work Folder

The work folder variables in `ZED/record.py`, `seg/draw_mask_cup.py`, `FoundationPose/run_demo.py` need to be changed to the root directory of this project before running.

In `run.sh`, you also need to change the volume mount directory: `-v /home/tianzong:/home/tianzong` and the `run_demo.py` path: `python /home/tianzong/Documents/workspace/perception/FoundationPose/run_demo.py`.

## III. Run

Run `run.sh` under the root directory.

First, 30 frames will be captured to `video/` folder at 15 FPS and exported to `.png` format. Then, the `seg/draw_mask_cup.py` script will draw the mask of the mug. Finally, run FoundationPose.

You can change how many frames is recorded in `ZED/record.py`.
