from io import BytesIO

import pytest

from app.report.analyzer import FileAnalyzer


@pytest.fixture
def analyzer():
    return FileAnalyzer()


def test_total_lines(analyzer):
    content = "дом кот\nдом\nпечка".encode("utf-8")
    file = BytesIO(content)
    
    result = analyzer.analyze(file)
    
    assert result.total_lines == 3


def test_total_counts(analyzer):
    content = "дом кот\nдом".encode("utf-8")
    file = BytesIO(content)
    
    result = analyzer.analyze(file)
    
    assert result.lemma_stats["дом"].total_count == 2
    assert result.lemma_stats["кот"].total_count == 1
    

def test_line_counts(analyzer):
    content = "дом кот\nдом\nбабочка".encode("utf-8")
    file = BytesIO(content)
    
    result = analyzer.analyze(file)
    
    assert result.lemma_stats["дом"].line_counts == {0: 1, 1:1}
    assert result.lemma_stats["кот"].line_counts == {0: 1}
    assert result.lemma_stats["бабочка"].line_counts == {2: 1}


def test_russian_lemmatization(analyzer):
    content = "житель жителем\nжители\nжителе жителями".encode("utf-8")
    file_obj = BytesIO(content)

    result = analyzer.analyze(file_obj)

    assert result.lemma_stats["житель"].total_count == 5


def test_hyphen_word(analyzer):
    content = "дом-домик дом\n".encode("utf-8")
    file_obj = BytesIO(content)

    result = analyzer.analyze(file_obj)

    assert "дом-домик" in result.lemma_stats


def test_empty_file(analyzer):
    file_obj = BytesIO(b"")

    result = analyzer.analyze(file_obj)

    assert result.total_lines == 0
    assert result.lemma_stats == {}


def test_invalid_bytes_are_ignored(analyzer):
    content = b"\xff\xfe dom\n"
    file_obj = BytesIO(content)

    result = analyzer.analyze(file_obj)

    assert "dom" in result.lemma_stats


def test_multiple_lines_sparse_counts(analyzer):
    content = b"dom\n\n\ndom\n"
    file_obj = BytesIO(content)

    result = analyzer.analyze(file_obj)
    stats = result.lemma_stats

    assert stats["dom"].total_count == 2
    assert stats["dom"].line_counts[0] == 1
    assert stats["dom"].line_counts[3] == 1
    