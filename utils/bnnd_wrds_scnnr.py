from .text_scanner import TextScanner
from .model import TextModeration
import asyncio

class BannedWordsScanner:
    def __init__(self, banned_words_file, model_path, transformer_name):
        try:
            self.simpleScanner = TextScanner(banned_words_file)
            self.contextScanner = TextModeration(model_path, transformer_name)
        except Exception as e:
            raise RuntimeError(f"Помилка ініціалізації: {str(e)}")

    def change_words_database(self, file):
        try:
            self.simpleScanner.set_banned_words_file(file)
        except Exception as e:
            return {"error": f"Не вдалося змінити базу слів: {str(e)}"}

    async def scan(self, text, threshold=0.5):
        try:
            found = await self.simpleScanner.scan_text(text)
            if found:
                result = []
                for res in found:
                    try:
                        check_context = self.contextScanner.predict(res['context'], threshold=threshold)
                        if check_context['detected']:
                            reason = [k for k, v in check_context['detect'].items() if v]
                            result.append({
                                'word': res['word'],
                                'context': res['context'],
                                'reason': reason
                            })
                    except Exception as e:
                        return {"error": f"Помилка при аналізі контексту: {str(e)}"}
                
                return {"message": result} if result else {"message": "Жодне слово не виявлено у небезпечному контексті"}
            else:
                return {"message": "There is no banned words"}
        except Exception as e:
            return {"error": f"Помилка під час сканування тексту: {str(e)}"}


