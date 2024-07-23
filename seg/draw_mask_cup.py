from ultralytics import YOLO
import cv2
import torch
from pathlib import Path
import numpy as np
import shutil

work_folder = "/home/tianzong/Documents/workspace/perception/"

model = YOLO(work_folder + "assets/yolov8l-seg.pt")

input_image_path = Path(work_folder + "video/rgb/000000.png")
print("[INFO] Processing image:", input_image_path)
input_image = cv2.imread(input_image_path)
input_height, input_width = input_image.shape[:2]

# Run inference on the image
results = model(input_image_path)

output_dir = Path(work_folder + "seg/output/")
output_dir.mkdir(parents=True, exist_ok=True)

# Copy the original image to the output folder
shutil.copy(input_image_path, output_dir / "original_image.jpg")

# Get the class names
seg_classes = list(results[0].names.values())

# Find the index of the "cup" class
cup_class_index = seg_classes.index("cup") if "cup" in seg_classes else None

if cup_class_index is None:
    print("No 'cup' class found in the model's classes.")
else:
    for result in results:
        masks = result.masks.data
        boxes = result.boxes.data
        clss = boxes[:, 5]

        # MASK OF ALL INSTANCES OF THE CUP CLASS
        cup_indices = torch.where(clss == cup_class_index)
        cup_masks = masks[cup_indices]
        cup_mask = torch.any(cup_masks, dim=0).int() * 255

        if cup_masks is not None:
            # Resize the cup mask to the original image size
            cup_mask_resized = cv2.resize(
                cup_mask.cpu().numpy(),
                (input_width, input_height),
                interpolation=cv2.INTER_NEAREST,
            )

            # MASK FOR EACH INSTANCE OF THE CUP CLASS
            for i, cup_index in enumerate(cup_indices[0].cpu().numpy()):
                single_cup_mask = masks[torch.tensor([cup_index])]
                single_cup_mask = torch.any(single_cup_mask, dim=0).int() * 255
                single_cup_mask_resized = cv2.resize(
                    single_cup_mask.cpu().numpy(),
                    (input_width, input_height),
                    interpolation=cv2.INTER_NEAREST,
                )
                cv2.imwrite(str(f"./output/cup_{i}.jpg"), single_cup_mask_resized)

                # Create a masked version of the input image for each cup
                single_cup_mask_resized = single_cup_mask_resized.astype(np.uint8)
                single_masked_image = cv2.bitwise_and(
                    input_image, input_image, mask=single_cup_mask_resized
                )
                cv2.imwrite(str(f"./output/masked_cup_{i}.jpg"), single_masked_image)
