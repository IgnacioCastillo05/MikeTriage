from fastapi import APIRouter
import logging
from app.core.data.kaggle_importer import import_kaggle_data, import_all_kaggle_data, get_kaggle_import_status

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/import")
async def import_kaggle():
    logger.info("Endpoint de importacion de Kaggle llamado")
    result = import_kaggle_data()
    return result

@router.post("/import-all")
async def import_all_kaggle():
    logger.info("Endpoint de importacion completa de Kaggle llamado")
    result = import_all_kaggle_data()
    return result

@router.get("/status")
async def kaggle_status():
    return get_kaggle_import_status()