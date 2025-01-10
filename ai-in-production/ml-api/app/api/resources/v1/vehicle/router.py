# -----------------------------------------------------------
# API paragraph and field detection for ancestry document
# (C) 2021 Duy Nguyen, Ho Chi Minh, Viet Nam
# email duynguyenngoc@hotmail.com
# -----------------------------------------------------------

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Depends
from starlette.status import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
)
import uuid
import json
from mq_main import redis
from securities import token as token_helper
from helpers import time as time_helper
from settings import config
from api.entities.vehicle import MlTimeHandle, MlResult, MlStatusHandle, Vehicle, VehicleResponse
from api.resources.v1.object_detection.background import image_upload_background
from helpers.logging import logger
from helpers.storage import upload_file_bytes, create_path


router = APIRouter()


# @router.post("/upload_data")
# async def ml_process(
#     vehicle: Vehicle = Depends(),
#     file: UploadFile = File(...)):

@router.post("/upload_data")
async def ml_process(
    user_id: str = Form(...),
    cam_id: str = Form(...),
    time: str = Form(...),
    metadata: str = Form(...),
    file: UploadFile = File(...)):

    logger.info("/upload_data user_id - cam_id - time: %s %s %s", user_id, cam_id, time)
    logger.info("metadata: %s", metadata)

    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="file_type not support!")
    
    time_upload = time_helper.now_utc()
    task_id = str(uuid.uuid5(uuid.NAMESPACE_OID, config.ML_QUERY_NAME + "_"+ str(time_upload)))
    file_name = task_id + config.ML_IMAGE_TYPE
    dir_path = config.ML_STORAGE_UPLOAD_PATH + time_helper.str_yyyy_mm_dd(time_upload)    
    create_path(dir_path)
    file_path = dir_path + "/" +  file_name
    file_bytes = file.file.read()
    try:
        logger.info("File name: %s", file_name)
        upload_file_bytes(file_bytes, file_path)
        status = "SUCCESS"
        status_code=HTTP_200_OK
    except Exception as e:
        status_code=HTTP_500_INTERNAL_SERVER_ERROR
        status = "FAILED"
        error = str(e)
        logger.error("Error: %s", error)
    
    return VehicleResponse(status=status, time=time_upload, status_code=status_code, task_id=task_id)



