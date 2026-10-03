from ultralytics import YOLO
import config

def identify_element(img_filename=None):
    model = YOLO(config.COMPUTER_VISION_MODEL)
    results = model.predict(
        source=img_filename,
        classes=[24],
        conf=0.22,
        save=config.SAVE_VISION_PREDICTION,
        project=config.VISION_PREDICTION_FOLDER,
        name="predict",
        exist_ok=True
        )
    
    if len(results[0].boxes) == 0:
        print(f"No element detected. Filename: {img_filename}")
        return
    
    for box in results[0].boxes:
        class_id = int(box.cls.item())
        label_name = results.names[class_id]
        confidence_score = float(box.conf.item())
        print(f"Element identified: {label_name}. Filename: {img_filename}. Certainty: {confidence_score * 100:.2f}%")