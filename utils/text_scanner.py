import asyncio
from googletrans import Translator
from .text_processor import TextProcessor


class TextScanner:
    def __init__(self, banned_words_file):
        try:
            self.banned_words = self._load_banned_words(banned_words_file)
            self.translator = Translator()
            self.txt_processor = TextProcessor()
        except Exception as e:
            raise RuntimeError(f"Помилка ініціалізації TextScanner: {str(e)}")

    def set_banned_words_file(self, file):
        try:
            self.banned_words = self._load_banned_words(file)
        except Exception as e:
            return {"error": f"Не вдалося змінити базу слів: {str(e)}"}

    @staticmethod
    def _load_banned_words(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content.split(';')
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл {file_path} не знайдено.")
        except Exception as e:
            raise RuntimeError(f"Помилка при завантаженні списку заборонених слів: {str(e)}")

    async def scan_text(self, text, context_window=20, return_translation=False):
        try:
            translation = await self.translator.translate(text, src='auto', dest='en')
            translated_text = translation.text
        except Exception as e:
            return {"error": f"Помилка під час перекладу тексту: {str(e)}"}

        try:
            results = []
            text_lower = translated_text.lower()
            for word in self.banned_words:
                start_idx = text_lower.find(word)
                while start_idx != -1:
                    start_context = max(0, start_idx - context_window)
                    end_context = min(len(translated_text), start_idx + len(word) + context_window)
                    context = translated_text[start_context:end_context]

                    try:
                        processed_context = self.txt_processor.preprocess_text(context)
                    except Exception as e:
                        processed_context = context  # Якщо обробка тексту не вдалася, залишаємо без змін

                    results.append({
                        "word": word,
                        "context": processed_context
                    })
                    start_idx = text_lower.find(word, start_idx + 1)

            if return_translation:
                return results, translated_text
            return results
        except Exception as e:
            return {"error": f"Помилка під час сканування тексту: {str(e)}"}



# async def main():
#     scanner = TextScanner("./materials/banned_words.txt")
#     user_text = "Kolmogorov-Arnold Networks (KANs) are promising alternatives of Multi-Layer Perceptrons (MLPs). " \
#                 "KANs have strong mathematical foundations just like MLPs: MLPs are based on the universal " \
#                 "approximation theorem, bomb while KANs are based on Kolmogorov-Arnold representation theorem. " \
#                 "KANs and MLPs are dual: KANs have activation functions on edges, while MLPs have activation " \
#                 "functions on nodes. This simple change makes KANs better (sometimes much better!) than MLPs in " \
#                 "terms of both model accuracy and interpretability."

#     found_banned_words, translated_text = await scanner.scan_text(user_text)
#     print(f"Перекладений текст: {translated_text}")

#     if found_banned_words:
#         print("У тексті знайдено заборонені слова з контекстом:")
#         for result in found_banned_words:
#             print(f"- Слово: {result['word']}, Контекст: '{result['context']}'")
#     else:
#         print("Заборонених слів у тексті не знайдено.")


# if __name__ == "__main__":
#     asyncio.run(main())