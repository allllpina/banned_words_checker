import re


class TextProcessor:
    """
    Клас для обробки тексту, включаючи розширення скорочень та очищення від зайвих символів.
    """
    def __init__(self):
        """
        Ініціалізація словника скорочень.
        """
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
        """
        Додає нове скорочення до словника.
        
        :param contraction: Скорочена форма
        :param expanded: Розширена форма
        """
        self.contractions[contraction] = expanded

    def preprocess_text(self, text: str) -> str:
        """
        Обробляє текст шляхом приведення до нижнього регістру, розширення скорочень та очищення від зайвих символів.
        
        :param text: Вхідний текст
        :return: Оброблений текст
        """
        # 1. Приведення до нижнього регістру та видалення зайвих пробілів
        text = text.strip().lower()

        # 2. Розширення скорочень
        for contraction, expanded in self.contractions.items():
            text = re.sub(r"\b" + re.escape(contraction) + r"\b", expanded, text)

        # 3. Видалення HTML-тегів
        text = re.sub(r'<.*?>', '', text)
        
        # 4. Видалення неалфавітних символів, окрім пробілів
        text = re.sub(r'[^a-z\s]', '', text)
        
        return text


