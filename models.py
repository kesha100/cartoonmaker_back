from pydantic import BaseModel, Field
from typing import Optional


class JobConfig(BaseModel):
    input_width: Optional[int] = 1280
    input_height: Optional[int] = 720
    source_image_url: Optional[str] = None


class CreateJobRequest(BaseModel):
    prompt: str
    config: JobConfig = JobConfig()
    duration: int
    seed: int
    is_public: bool


class GetJobResultsRequest(BaseModel):
    job_id: str
