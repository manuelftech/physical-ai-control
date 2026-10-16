import os
import glob
import shutil
import structlog
logger = structlog.get_logger()

def get_latest_predicted_image(folder):
    # Returns path of the latest image predicted by Yolo
    images = os.path.join(folder)
    if images:
        image_path = max(glob.glob(images, "*.jpg"), key=os.path.getmtime)
        logger.info("Image found. Path: %s", image_path)
        return image_path
    else:
        logger.info("No images found in folder %s", folder)

def remove_folder(folder):
    # Deletes the specified folder
    if os.path.exists(folder):
        shutil.rmtree(folder)
        logger.info("Folder %s deleted", folder)
    else:
        logger.info("Folder %s does not exist", folder)