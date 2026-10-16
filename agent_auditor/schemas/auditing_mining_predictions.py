from pydantic import BaseModel, Field

class AuditingMiningPredictions(BaseModel):
    process_id: str | None = Field(description="Id of the vision detection process")
    audit_timestamp: int | None = Field(description="Time of image auditing")
    verification_status: str | None = Field(description="Message of validation of the prediction")
    agent_fedback: str | None = Field(description="Feedback of the AI Agent regarding the predicted image")
    image_url: str | None = Field(description="Path of the Bucket where the predicted image is stored")