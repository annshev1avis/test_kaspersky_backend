from fastapi import APIRouter, UploadFile, HTTPException, File
from fastapi.responses import FileResponse

from app.report.service import create_report


router = APIRouter(tags=["report"])

@router.post("/public/report/export")
async def export_report(file: UploadFile = File(...)):
    """Принимает загруженный UTF-8 текстовый файл, составляет 
    частотную статистику по словоформам и возвращает XLSX-отчёт.

    Args:
        file: Входной текстовый файл в кодировке UTF-8.

    Returns:
        XLSX-файл с частотной статистикой по словоформам.

    Raises:
        HTTPException: Если файл пустой, имеет неподдерживаемую кодировку
        или произошла ошибка при обработке.
    """

    chunk = await file.read(1024)
    if not chunk:
        raise HTTPException(
            status_code=400,
            detail="Загруженный файл не должен быть пустым"
        )
    await file.seek(0)
    
    try:
        output_file_path = create_report(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
        )
    
    return FileResponse(
        path=output_file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="report.xlsx"
    )
    
