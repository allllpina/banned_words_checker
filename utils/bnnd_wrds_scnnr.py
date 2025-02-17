from .text_scanner import TextScanner  # Імпортуємо клас для перевірки слів за списком
from .model import TextModeration  # Імпортуємо клас для перевірки контексту використання слів
import asyncio

class BannedWordsScanner:
    def __init__(self, banned_words_file, model_path, transformer_name):
        try:
            # Ініціалізуємо простий сканер слів за забороненим списком
            self.simpleScanner = TextScanner(banned_words_file)
            # Ініціалізуємо модель перевірки контексту
            self.contextScanner = TextModeration(model_path, transformer_name)
        except Exception as e:
            # Якщо сталася помилка під час ініціалізації, викликаємо виняток
            raise RuntimeError(f"Помилка ініціалізації: {str(e)}")

    def change_words_database(self, file):
        try:
            # Змінюємо файл із забороненими словами
            self.simpleScanner.set_banned_words_file(file)
        except Exception as e:
            # Повертаємо повідомлення про помилку, якщо файл не вдалося змінити
            return {"error": f"Не вдалося змінити базу слів: {str(e)}"}

    async def scan(self, text, threshold=0.5, return_translation = False):
        try:
            # Асинхронно перевіряємо текст на наявність заборонених слів
            # Якщо виставлено параметр `return_translation` то від 'TextScanner' запитується переклад тексту
            if return_translation:
                found, translation = await self.simpleScanner.scan_text(text, return_translation = return_translation)
            else:
                found = await self.simpleScanner.scan_text(text, return_translation = return_translation)
            
            if found:
                result = []
                # Перебираємо всі знайдені слова
                for res in found:
                    try:
                        # Перевіряємо контекст використання слова за допомогою моделі
                        check_context = self.contextScanner.predict(res['context'], threshold=threshold)
                        if check_context['detected']:
                            # Якщо слово використане у неприпустимому контексті,
                            # зберігаємо інформацію про причину спрацьовування
                            reason = [k for k, v in check_context['detect'].items() if v]
                            result.append({
                                'word': res['word'],
                                'context': res['context'],
                                'reason': reason
                            })
                    except Exception as e:
                        # Повертаємо помилку, якщо сталася проблема з аналізом контексту
                        return {"error": f"Помилка при аналізі контексту: {str(e)}"}
                
                # Якщо знайдено небезпечні слова в контексті, повертаємо їх список
                if return_translation:
                    return {"message": result} if result else {"message": "Жодне слово не виявлено у небезпечному контексті", "translated_text": translation}
                else:
                    return {"message": result} if result else {"message": "Жодне слово не виявлено у небезпечному контексті"}
            else:
                # Якщо заборонених слів не знайдено
                if return_translation:
                    return {"message": "There is no banned words", "translated_text": translation}
                else:
                    return {"message": "There is no banned words"}
        except Exception as e:
            # Обробляємо помилку при скануванні тексту
            return {"error": f"Помилка під час сканування тексту: {str(e)}"}
