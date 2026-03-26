from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse

from app.report.service import create_report


router = APIRouter(tags=["report"])

@router.post("/public/report/export")
def export_report(file: UploadFile):
    output_file_path = create_report(file)
    
    return FileResponse(
        path=output_file_path,
        filename="report.xlsx"
    )
    
