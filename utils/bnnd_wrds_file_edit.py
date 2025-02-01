class BannedWordsFileEdit:
    def __init__(self, banned_words_file):
        self.filePath = banned_words_file

    def add(self, words, bws):
        try:
            with open(self.filePath, 'a', encoding='utf-8') as file:
                for word in words:
                    file.write(f";{word}")
            bws.change_words_database(self.filePath)
            return f"'{words}' успішно додано до файлу!"

        except Exception as e:
            return f"Виникла помилка під час запису у файл: {e}"

    def remove(self, words, bws):
        try:
            with open(self.filePath, 'r', encoding='utf-8') as file:
                content = file.read()

            result = {
                'removed': [],
                'not_found': []
            }

            updated_content = content  # Робоча копія вмісту файлу

            for word in words:
                formatted_word = f";{word}"
                if formatted_word in updated_content:
                    updated_content = updated_content.replace(formatted_word, "")
                    result['removed'].append(word)
                else:
                    result['not_found'].append(word)

            # Запис зміненого вмісту у файл ОДИН раз
            with open(self.filePath, 'w', encoding='utf-8') as file:
                file.write(updated_content)

            # Оновлення бази даних
            bws.change_words_database(self.filePath)

            return result

        except Exception as e:
            return f"Виникла помилка під час видалення з файлу: {e}"
