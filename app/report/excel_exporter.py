from pathlib import Path
from openpyxl import Workbook
from tempfile import NamedTemporaryFile

from app.report.analyzer import AnalysisResult


class ExcelExporter:
    """Формирует Excel-файл с частотной статистикой по леммам"""
    
    HEADER = [
        "Словоформа",
        "Количество во всём документе",
        "Количество по строкам",
    ]
    
    def export(self, analysis_result: AnalysisResult) -> str:
        """Экспортирует результат анализа в xlsx-файл.

        Args:
            analysis_result: Результат анализа текстового файла.

        Returns:
            Путь к созданному xlsx-файлу.
        """
        
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Отчет"
        
        worksheet.append(self.HEADER)
        
        for lemma in sorted(analysis_result.lemma_stats):
            stats = analysis_result.lemma_stats[lemma]
            
            worksheet.append(
                [
                    lemma,
                    stats.total_count,
                    self._line_counts_to_str(
                        stats.line_counts,
                        analysis_result.total_lines
                    ),
                ]
            )
        
        with NamedTemporaryFile(suffix=".xlsx") as temp_file:
            output_path = Path(temp_file.name)
            
        workbook.save(output_path)
        return str(output_path)
        
    def _line_counts_to_str(self, line_counts: dict[int, int], total_lines=int):
        """Собирает строку со статистикой по строкам.
        Например: '0,11,32,0,0,3'.

        Args:
            line_counts: Количество вхождений леммы по индексам строк.
            total_lines: Общее количество строк в документе.

        Returns:
            Строка со статистикой по всем строкам документа.
        """
        
        counts_with_zeros = [
            str(line_counts.get(line_index, 0))
            for line_index in range(total_lines)
        ]
        return ",".join(counts_with_zeros)
