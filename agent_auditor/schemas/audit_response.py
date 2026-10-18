from pydantic import BaseModel, Field

class AuditResponse(BaseModel):
    image_properly_predicted: str | None = Field(description="Id of the robot sending the payload")
    feedback: str = Field(description="Element visually recognized")
    confidence: float | None = Field(description="Level of the risk associated")