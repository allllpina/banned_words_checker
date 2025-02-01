import re


class TextProcessor:
    def __init__(self):
        # Скорочення
        self.contractions = {
            "n't": " not",
            "'d": " would",
            "'ll": " will",
            "'re": " are",
            "'ve": " have",
            "'s": " is",
            "'m": " am",
            "'t": " not"
        }

    def add_contraction(self, contraction: str, expanded: str) -> None:
        """Додає нове скорочення до словника."""
        self.contractions[contraction] = expanded

    def preprocess_text(self, text: str) -> str:
        """Обробляє текст за допомогою попередньої обробки."""
        # 1. Приведення до нижнього регістру
        text = text.strip().lower()

        # 2. Розширення скорочень
        for contraction, expanded in self.contractions.items():
            text = re.sub(r"\b" + re.escape(contraction) + r"\b", expanded, text)

        # 3. Видалення спецсимволів, тегів, чисел
        text = re.sub(r'<.*?>', '', text)  # Видалення HTML-тегів
        text = re.sub(r'[^a-z\s]', '', text)  # Видалення не букв та пробілів
        return text


