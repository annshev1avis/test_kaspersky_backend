from collections import defaultdict
from dataclasses import dataclass, field
import re
from typing import BinaryIO

from pymorphy3 import MorphAnalyzer


@dataclass
class LemmaStats:
    """Статистика для одной словоформы (леммы).

    Атрибуты:
        total_count: Общее количество леммы во всём документе.
        line_counts: Количество леммы по строкам в формате {индекс строки: количество}.
    """
    total_count: int = 0
    line_counts: dict[int, int] = field(default_factory=lambda: defaultdict(int))


@dataclass
class AnalysisResult:
    """Результат анализа текстового файла.

    Атрибуты:
        total_lines: Общее количество строк в файле.
        lemma_stats: Словарь, где ключ — лемма, значение — её статистика.
    """
    total_lines: int = 0
    lemma_stats: dict[str, LemmaStats] = field(default_factory=lambda: defaultdict(LemmaStats))


WORD_RE = re.compile(r"[А-Яа-яЁёA-Za-z]+(?:-[А-Яа-яЁёA-Za-z]+)?")


def _extract_words(line: str) -> list[str]:
    """Извлекает слова из строки.

    Словом считается последовательность русских или английских букв,
    допускается один дефис внутри слова.
    """
    return WORD_RE.findall(line.lower())


class FileAnalyzer:
    """Анализирует текстовый файл и собирает статистику по леммам."""

    def __init__(self) -> None:
        self._morph = MorphAnalyzer()
        self._lemma_cache: dict[str, str] = {}
        
    def analyze(self, file: BinaryIO) -> AnalysisResult:
        """Анализирует файл построчно и собирает статистику:
        - общее количество вхождений каждой леммы
        - количество вхождений по строкам
        
        Для анализа слова приводятся к начальной форме.

        Returns:
            Объект AnalysisResult с общей статистикой.
        """
        result = AnalysisResult()
        
        for line_index, raw_line in enumerate(file):
            line = raw_line.decode("utf-8", errors="ignore")
            words = _extract_words(line)
            
            for word in words:
                lemma = self._get_lemma(word)
                result.lemma_stats[lemma].total_count += 1
                result.lemma_stats[lemma].line_counts[line_index] += 1
            
            result.total_lines += 1

        return result
    
    def _get_lemma(self, word: str) -> str:
        """Приводит слово к нормальной форме (лемме). Использует кэш.

        Returns:
            Нормальная форма слова.
        """
        cached_lemma = self._lemma_cache.get(word)
        if cached_lemma is not None:
            return cached_lemma
        
        lemma = self._morph.parse(word)[0].normal_form
        self._lemma_cache[word] = lemma
        return lemma
