from io import BytesIO
from fastapi.testclient import TestClient
from openpyxl import load_workbook

from app.main import app


client = TestClient(app)


def read_xlsx_response(content: bytes):
    workbook = load_workbook(BytesIO(content))
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    return rows
    
    
def test_export_report_returns_xlsx_file():
    file_content = "Житель жил в доме\nЖителем гордились\n"
    response = client.post(
        "/public/report/export",
        files={"file": ("input.txt", file_content.encode("utf-8"), "text/plain")}
    )
    
    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment; filename=\"report.xlsx\"" in response.headers["content-disposition"]
    

def test_export_report_contains_expected_statistics():
    file_content = "Житель жил\nЖителем гордились\n"
    response = client.post(
        "/public/report/export",
        files={"file": ("input.txt", file_content.encode("utf-8"), "text/plain")},
    )

    assert response.status_code == 200

    rows = read_xlsx_response(response.content)

    assert rows[0] == ("Словоформа", "Количество во всём документе", "Количество по строкам")

    data_rows = rows[1:]
    data = {row[0]: row[1:] for row in data_rows}

    assert "житель" in data
    assert data["житель"] == (2, "1,1")


def test_export_report_returns_400_for_empty_file():
    response = client.post(
        "/public/report/export",
        files={"file": ("empty.txt", b"", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Загруженный файл не должен быть пустым"}


def test_export_report_returns_400_for_non_utf8_file():
    file_content_cp1251 = "Привет".encode("cp1251")

    response = client.post(
        "/public/report/export",
        files={"file": ("input.txt", file_content_cp1251, "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Должен быть передан текстовый файл в кодировке utf-8"}