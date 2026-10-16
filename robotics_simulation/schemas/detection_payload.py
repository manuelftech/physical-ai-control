from pydantic import BaseModel, Field

class DetectionPayload(BaseModel):
    process_id: str | None = Field(description="Id of the vision detection process")
    element_type: str | None = Field(description="Element visually recognized")
    alert_level: str | None = Field(description="Level of the risk associated")
    prediction_confidence: float | None = Field(description="Compuer Vision model confidence")
    prediction_timestamp: int | None = Field(description="Time of visual recognition")
    image_url: str | None = Field(description="Path of the Bucket where the predicted image is stored")