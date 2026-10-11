from ultralytics import YOLO
import config
import os

def identify_element(img_filename=None):
    model = YOLO(config.COMPUTER_VISION_MODEL)
    results = model.predict(
        img_filename, 
        conf=0.25,
        imgsz=640, 
        save=config.SAVE_VISION_PREDICTION,
        project=config.VISION_PREDICTION_FOLDER,
        name="predict",
        exist_ok=True
        )
    
    rock_found = False
    truck_found = False
    ACCEPTED_CONFIDENCE = 0.90

    for box in results[0].boxes:
        name = model.names[int(box.cls)]
        confidence = float(box.conf)
        
        if name == "rock" and confidence > ACCEPTED_CONFIDENCE:
            rock_found = True
        elif name == "truck" and confidence > ACCEPTED_CONFIDENCE:
            truck_found = True

    if rock_found and truck_found:
        print("Rock found near Truck")
    else:
        print("No rocks near trucks")