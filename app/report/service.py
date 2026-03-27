from fastapi import UploadFile

from app.report.analyzer import FileAnalyzer
from app.report.excel_exporter import ExcelExporter


def create_report(file: UploadFile) -> str:
    analyzer = FileAnalyzer()
    exporter = ExcelExporter()

    analysis_result = analyzer.analyze(file.file)
    output_file_path = exporter.export(analysis_result)
    return output_file_path
