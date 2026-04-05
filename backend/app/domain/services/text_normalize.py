def normalize_description(text: str) -> str:
    return " ".join(text.split()).lower() if text else ""
