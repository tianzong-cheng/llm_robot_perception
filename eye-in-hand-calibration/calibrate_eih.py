import numpy as np
import cv2
import os


def load_images_and_positions(image_folder, pos_file):
    images = []
    positions = []

    with open(pos_file, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            pos = list(map(float, parts[:6]))  # Get first six values as pose
            positions.append(pos)

            image_name = f"Explorer_HD2K_SN30856488_{parts[6]}.png"
            img_path = os.path.join(image_folder, image_name)
            if os.path.exists(img_path):
                img = cv2.imread(img_path)

                # Keep only the left half of the image
                height, width = img.shape[:2]
                left_img = img[:, :width // 2]

                images.append(left_img)
            else:
                print(f"Warning: Image {image_name} not found!")

    return images, np.array(positions)


def euler_to_rotation_matrix(angles):
    angles_rad = np.radians(angles)

    roll, pitch, yaw = angles_rad

    R_x = np.array([[1, 0, 0],
                    [0, np.cos(roll), -np.sin(roll)],
                    [0, np.sin(roll), np.cos(roll)]])

    R_y = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                    [0, 1, 0],
                    [-np.sin(pitch), 0, np.cos(pitch)]])

    R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                    [np.sin(yaw), np.cos(yaw), 0],
                    [0, 0, 1]])

    R = R_z @ R_y @ R_x
    return R


camera_K = np.array([[478.5675, 0, 336.3325],
                     [0, 478.8125, 188.4455],
                     [0, 0, 1]])


def calibrate_hand_eye(images, positions, chessboard_size, square_size):
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0],
                           0:chessboard_size[1]].T.reshape(-1, 2) * square_size

    R_gripper2base = []
    t_gripper2base = []
    R_target2cam = []
    t_target2cam = []
    R_target = np.zeros((3, 1))

    for img, pos in zip(images, positions):
        ret, corners = cv2.findChessboardCorners(img, chessboard_size, None)

        if ret:
            # Refine corner positions
            corners2 = cv2.cornerSubPix(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), corners, (11, 11), (-1, -1),
                                        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))

            # cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)
            # cv2.imshow('img', img)
            # cv2.waitKey(0)

            success, rvec, tvec = cv2.solvePnP(
                objp, corners2, camera_K, None)
            cv2.Rodrigues(rvec, R_target)
            R_target2cam.append(R_target)
            t_target2cam.append(tvec)
            print(tvec)

            # Convert Euler angles to rotation matrix
            rotation_matrix = euler_to_rotation_matrix(pos[3:])
            R_gripper2base.append(rotation_matrix)
            t_gripper2base.append(pos[:3])
        else:
            print("Warning: Chessboard not found in image!")

    # Convert lists to numpy arrays
    R_gripper2base = np.array(R_gripper2base)
    t_gripper2base = np.array(t_gripper2base)
    R_target2cam = np.array(R_target2cam)
    t_target2cam = np.array(t_target2cam)

    R_gripper, T_gripper = cv2.calibrateHandEye(
        R_gripper2base,
        t_gripper2base,
        R_target2cam,
        t_target2cam,
        method=cv2.CALIB_HAND_EYE_TSAI
    )

    return R_gripper, T_gripper


if __name__ == "__main__":
    image_folder = './ZED'
    pos_file = './ZED/pos.txt'
    chessboard_size = (10, 7)
    square_size = 0.03  # meters

    images, positions = load_images_and_positions(image_folder, pos_file)

    R_gripper, T_gripper = calibrate_hand_eye(
        images, positions, chessboard_size, square_size)

    print("Rotation Matrix:\n", R_gripper)
    print("Translation Vector:\n", T_gripper)
