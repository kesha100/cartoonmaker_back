# import json
#
# from fastapi import FastAPI, Body, HTTPException
# import uvicorn
# from pydantic import BaseModel
# from typing import Optional
# import aiohttp
# from starlette.middleware.cors import CORSMiddleware
# from models import JobConfig, CreateJobRequest, GetJobResultsRequest
# app = FastAPI()
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # Replace with your frontend URL in production
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE"],
#     allow_headers=["*"],
# )
#
#
# # Replace with your actual RapidAPI key
# X_RAPIDAPI_KEY = "90029b4b14msh4e362fd29217a94p1bf3d7jsna1c470832032"
#
# async def make_api_request(url: str, data: Optional[dict] = None):
#     headers = {
#         "x-rapidapi-host": "haiper-ai-api-unofficial.p.rapidapi.com",
#         "Content-Type": "application/json",
#         "x-rapidapi-key": X_RAPIDAPI_KEY,
#     }
#     async with aiohttp.ClientSession() as session:
#         try:
#             if data:
#                 async with session.post(url, json=data, headers=headers, verify_ssl=False) as response:
#                     response.raise_for_status()
#                     if response.content_type == 'application/json':
#                         return await response.json()
#                     else:
#                         return {"status": "error", "message": "Unexpected response format", "content": await response.text()}
#             else:
#                 async with session.get(url, headers=headers, verify_ssl=False) as response:
#                     response.raise_for_status()
#                     if response.content_type == 'application/json':
#                         return await response.json()
#                     else:
#                         content = await response.text()
#                         try:
#                             parsed_content = json.loads(json.loads(content)['content'])
#                             return parsed_content
#                         except json.JSONDecodeError as e:
#                             return {"status": "error", "message": f"Error parsing content: {e}", "content": content}
#         except aiohttp.ClientResponseError as e:
#             return {"status": "error", "message": f"Error from API: {e.status} - {e}"}
# @app.post("/create-job")
# async def create_job(job_data: CreateJobRequest):
#     try:
#         response = await make_api_request(
#             url="https://haiper-ai-api-unofficial.p.rapidapi.com/v1/haiper/generate",
#             data=job_data.dict(),
#         )
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error creating job: {e}")
#
#
# @app.post("/get-job-results")
# async def get_job_results(job_data: GetJobResultsRequest):
#     try:
#         response = await make_api_request(
#             url="https://haiper-ai-api-unofficial.p.rapidapi.com/v1/haiper/job-results",
#             data={"job_id": job_data.job_id},
#         )
#
#         # Check if the response indicates the job is still processing
#         if response["status"] == "success" and response["value"]["status"] == "processing":
#             return response  # Return the processing response
#
#         # Otherwise, return the final result
#         return response
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error getting job results: {e}")
#
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

import json
from fastapi import FastAPI, HTTPException, Request
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
import aiohttp
from starlette.middleware.cors import CORSMiddleware
from models import JobConfig, CreateJobRequest, GetJobResultsRequest

app = FastAPI()



# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust as needed for your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Replace with your actual RapidAPI key
X_RAPIDAPI_KEY = "90029b4b14msh4e362fd29217a94p1bf3d7jsna1c470832032"


async def make_api_request(url: str, data: Optional[dict] = None):
    headers = {
        "x-rapidapi-host": "haiper-ai-api-unofficial.p.rapidapi.com",
        "Content-Type": "application/json",
        "x-rapidapi-key": X_RAPIDAPI_KEY,
    }
    async with aiohttp.ClientSession() as session:
        try:
            if data:
                async with session.post(url, json=data, headers=headers, verify_ssl=False) as response:
                    response.raise_for_status()
                    print("here u")
                    if response.content_type == 'application/json':
                        return await response.json()
                    else:
                        return {"status": "error", "message": "Unexpected response format",
                                "content": await response.text()}
            else:
                async with session.get(url, headers=headers, verify_ssl=False) as response:
                    response.raise_for_status()
                    if response.content_type == 'application/json':
                        return await response.json()
                    else:
                        content = await response.text()
                        try:
                            parsed_content = json.loads(json.loads(content)['content'])
                            return parsed_content
                        except json.JSONDecodeError as e:
                            return {"status": "error", "message": f"Error parsing content: {e}", "content": content}
        except aiohttp.ClientResponseError as e:
            return {"status": "error", "message": f"Error from API: {e.status} - {e}"}


def slice_prompts(input_text: str) -> List[str]:
    """
    Slices input text into prompts.
    Each prompt is expected to be formatted as "prompt X: text".
    Returns a list of prompts.
    """
    prompts = []
    parts = input_text.split(".")
    for part in parts:
        if part.strip():  # Ensure non-empty lines
            prompt_text = part.strip()
            prompts.append(prompt_text)
    return prompts


# Endpoint to create jobs from prompts
@app.post("/create-job")
async def create_jobs_from_prompts(request: Request, input_json: CreateJobRequest):
    try:
        print("here")
        prompts = slice_prompts(input_text=input_json.prompt)
        print("here-ee")
        job_ids = []
        for prompt in prompts:
            job_data = CreateJobRequest(prompt=prompt, config=JobConfig(), duration=4, seed=123, is_public=True)
            response = await make_api_request(
                url="https://haiper-ai-api-unofficial.p.rapidapi.com/v1/haiper/generate",
                data=job_data.dict(),
            )
            job_ids.append(response)

        return job_ids

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating jobs from prompts: {e}")


# Endpoint to get job results
@app.post("/get-job-results")
async def get_job_results(job_data: GetJobResultsRequest):
    try:
        response = await make_api_request(
            url="https://haiper-ai-api-unofficial.p.rapidapi.com/v1/haiper/job-results",
            data={"job_id": job_data.job_id},
        )

        # Check if the response indicates the job is still processing
        if response["status"] == "success" and response["value"]["status"] == "processing":
            return response  # Return the processing response

        # Otherwise, return the  final result
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting job results: {e}")


# Run FastAPI application with uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
