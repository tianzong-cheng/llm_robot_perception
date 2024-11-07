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


mtx = np.array([
    [1.91938077e+03, 0.00000000e+00, 1.10501574e+03],
    [0.00000000e+00, 1.91971387e+03, 6.57137962e+02],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
])

dist = np.array([[-7.37720547e-02, 8.03354701e-02,
                2.05805953e-03, 7.28050570e-05, -3.02262430e-01]])


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
                objp, corners2, mtx, dist)
            R_target, _ = cv2.Rodrigues(rvec)
            R_target2cam.append(R_target)
            t_target2cam.append(tvec)

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

    R_cam2gripper, T_cam2gripper = cv2.calibrateHandEye(
        R_gripper2base,
        t_gripper2base,
        R_target2cam,
        t_target2cam,
        method=cv2.CALIB_HAND_EYE_TSAI
    )

    return R_cam2gripper, T_cam2gripper


if __name__ == "__main__":
    image_folder = './ZED'
    pos_file = './ZED/pos.txt'
    chessboard_size = (10, 7)
    square_size = 0.0297  # meters

    images, positions = load_images_and_positions(image_folder, pos_file)

    R_cam2gripper, T_cam2gripper = calibrate_hand_eye(
        images, positions, chessboard_size, square_size)

    print("Rotation Matrix:\n", R_cam2gripper.flatten())
    print("Translation Vector:\n", T_cam2gripper.flatten())

    # testing:
    target_points_base = []

    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0],
                           0:chessboard_size[1]].T.reshape(-1, 2) * square_size

    for img, pos in zip(images, positions):
        ret, corners = cv2.findChessboardCorners(img, chessboard_size, None)

        if ret:
            corners2 = cv2.cornerSubPix(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), corners, (11, 11), (-1, -1),
                                        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))

            success, rvec, tvec = cv2.solvePnP(objp, corners2, mtx, dist)
            target_point_in_cam = np.array(tvec).reshape(3, 1)
            target_point_in_gripper = R_cam2gripper @ target_point_in_cam + T_cam2gripper

            R_gripper2base = euler_to_rotation_matrix(pos[3:])
            t_gripper2base = pos[:3].reshape(3, 1)
            target_point_in_base = R_gripper2base @ target_point_in_gripper + t_gripper2base

            # print("Target point in base coordinates (calculated):",
            #       target_point_in_base.flatten())
            target_points_base.append(target_point_in_base.flatten())

    target_points_base = np.array(target_points_base)
    mean_point = np.mean(target_points_base, axis=0)
    errors = np.linalg.norm(target_points_base - mean_point, axis=1)
    rmse = np.sqrt(np.mean(errors ** 2))

    print("RMSE:", rmse)
