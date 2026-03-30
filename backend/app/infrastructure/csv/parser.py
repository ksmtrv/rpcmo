import chardet
import csv
import io
from typing import Any

from app.core.errors import ValidationError


def detect_encoding(content: bytes) -> str:
    result = chardet.detect(content)
    return result.get("encoding", "utf-8") or "utf-8"


def detect_delimiter(first_line: str) -> str:
    for delim in [";", ",", "\t", "|"]:
        if delim in first_line:
            return delim
    return ";"


def parse_csv_rows(
    content: bytes,
    encoding: str | None = None,
    delimiter: str | None = None,
) -> tuple[list[str], list[dict[str, Any]], str, str]:
    enc = encoding or detect_encoding(content)
    try:
        text = content.decode(enc)
    except UnicodeDecodeError:
        enc = "utf-8"
        text = content.decode(enc, errors="replace")

    lines = text.strip().split("\n")
    if not lines:
        raise ValidationError("CSV файл пуст")

    delim = delimiter or detect_delimiter(lines[0])
    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    headers = reader.fieldnames or []
    rows = list(reader)
    return headers, rows, enc, delim


def map_row_to_transaction_data(row: dict[str, Any], column_map: dict[str, str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for target, source in column_map.items():
        if source and source in row:
            result[target] = row[source]
    return result
