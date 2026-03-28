import asyncio
import os

from fastapi import APIRouter, UploadFile, HTTPException, File
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.report.service import create_report


router = APIRouter(tags=["report"])

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

MAX_CONCURRENT_REPORTS = 2

report_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REPORTS)


def _get_file_size(file: UploadFile) -> int:
    """
    Возвращает размер файла в байтах
    """

    file.file.seek(0, 2)  # переводит курсор в конец файла
    file_size = file.file.tell()
    file.file.seek(0)
    return file_size


def _remove_file(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)


@router.post("/public/report/export")
async def export_report(file: UploadFile = File(...)):
    """Принимает загруженный UTF-8 текстовый файл, составляет 
    частотную статистику по словоформам и возвращает XLSX-отчёт.

    Args:
        file: Входной текстовый файл в кодировке UTF-8.

    Returns:
        XLSX-файл с частотной статистикой по словоформам.

    Raises:
        HTTPException: Если файл пустой, слишком большой, имеет
        неподдерживаемую кодировку или произошла ошибка при обработке.
    """
    
    file_size = _get_file_size(file)
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Размер файла не должен превышать {MAX_FILE_SIZE_MB} МБ"
        )

    chunk = await file.read(1024)
    if not chunk:
        raise HTTPException(
            status_code=400,
            detail="Загруженный файл не должен быть пустым"
        )
    await file.seek(0)
    
    if report_semaphore.locked():
        raise HTTPException(
            status_code=503,
            detail="Сервер временно перегружен. Попробуйте снова через пару минут"
        )
    
    await report_semaphore.acquire()
    try:
        output_file_path = await run_in_threadpool(create_report, file.file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
        )
    finally:
        report_semaphore.release()
    
    return FileResponse(
        path=output_file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="report.xlsx",
        background=BackgroundTask(_remove_file, output_file_path)
    )
    
