import asyncio
from googletrans import Translator
from .text_processor import TextProcessor


class TextScanner:
    """
    Клас для сканування тексту на наявність заборонених слів.
    Використовує Google Translate для перекладу тексту та TextProcessor для його обробки.
    """
    def __init__(self, banned_words_file):
        """
        Ініціалізація об'єкта TextScanner.
        Завантажує список заборонених слів, ініціалізує перекладач та текстовий процесор.
        """
        try:
            self.banned_words = self._load_banned_words(banned_words_file)  # Завантаження списку заборонених слів
            self.translator = Translator()  # Ініціалізація перекладача
            self.txt_processor = TextProcessor()  # Ініціалізація текстового процесора
        except Exception as e:
            raise RuntimeError(f"Помилка ініціалізації TextScanner: {str(e)}")

    def set_banned_words_file(self, file):
        """
        Оновлення списку заборонених слів із нового файлу.
        """
        try:
            self.banned_words = self._load_banned_words(file)
        except Exception as e:
            return {"error": f"Не вдалося змінити базу слів: {str(e)}"}

    @staticmethod
    def _load_banned_words(file_path):
        """
        Завантаження списку заборонених слів із файлу.
        Слова розділяються символом ';'.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content.split(';')  # Розділення списку слів
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл {file_path} не знайдено.")
        except Exception as e:
            raise RuntimeError(f"Помилка при завантаженні списку заборонених слів: {str(e)}")

    async def scan_text(self, text, context_window=20, return_translation=False):
        """
        Асинхронне сканування тексту на заборонені слова.
        
        :param text: Вхідний текст
        :param context_window: Кількість символів до та після знайденого слова для контексту
        :param return_translation: Якщо True, повертає також перекладений текст
        :return: Список знайдених слів з контекстом або помилку
        """
        try:
            # Переклад тексту англійською для подальшого аналізу
            translation = await self.translator.translate(text, src='auto', dest='en')
            translated_text = translation.text
        except Exception as e:
            return {"error": f"Помилка під час перекладу тексту: {str(e)}"}

        try:
            results = []
            text_lower = translated_text.lower()  # Приведення до нижнього регістру для пошуку
            for word in self.banned_words:
                start_idx = text_lower.find(word)  # Пошук слова у тексті
                while start_idx != -1:
                    # Визначення контексту слова у тексті
                    start_context = max(0, start_idx - context_window)
                    end_context = min(len(translated_text), start_idx + len(word) + context_window)
                    context = translated_text[start_context:end_context]

                    try:
                        processed_context = self.txt_processor.preprocess_text(context)  # Обробка контексту
                    except Exception as e:
                        processed_context = context  # Якщо обробка не вдалася, залишаємо без змін

                    results.append({
                        "word": word,
                        "context": processed_context
                    })
                    start_idx = text_lower.find(word, start_idx + 1)  # Пошук наступного входження слова

            if return_translation:
                return results, translated_text  # Повернення результатів разом із перекладом
            return results  # Повернення лише результатів
        except Exception as e:
            return {"error": f"Помилка під час сканування тексту: {str(e)}"}
