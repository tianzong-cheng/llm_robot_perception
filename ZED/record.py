import sys
import pyzed.sl as sl

work_folder = "/home/tianzong/Documents/workspace/perception/"

zed = sl.Camera()

# Open camera

init = sl.InitParameters()
init.camera_resolution = sl.RESOLUTION.VGA
init.camera_fps = 15
init.depth_mode = sl.DEPTH_MODE.ULTRA
init.coordinate_units = sl.UNIT.METER
init.depth_minimum_distance = 0

open_error = zed.open(init)
if open_error != sl.ERROR_CODE.SUCCESS:
    print("[ERROR] Camera: ", open_error)
    exit(1)

# Start recording

output_path = work_folder + "video/video.svo"
rec_para = sl.RecordingParameters()
rec_para.video_filename = output_path
rec_para.compression_mode = sl.SVO_COMPRESSION_MODE.LOSSLESS
rec_para.target_framerate = 15

record_error = zed.enable_recording(rec_para)
if record_error != sl.ERROR_CODE.SUCCESS:
    print("[ERROR] Recording: ", record_error)
    exit(1)

for i in range(30):
    print("Recording frame ", i)
    zed.grab()

# Disable recording
zed.disable_recording()
