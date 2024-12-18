from typing import Dict

from pydantic import BaseModel, Field, ConfigDict, model_validator, model_serializer


class StatusCodeMsg(BaseModel):
    status_code: int = Field(..., description='Status code')
    description: str = Field(..., description="Descriptions of status message")
    message: str = Field(..., description="Messages of the status message")

    @model_serializer
    def ser_model(self) -> dict:
        return {"description": f'{self.description}',
                "content": {"application/json": {"example": {"status": f"{self.message}"}}}}

    def get_status_msg(self):
        return {'status': f'{self.message}'}
