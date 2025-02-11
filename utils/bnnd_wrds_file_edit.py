class BannedWordsFileEdit:
    def __init__(self, banned_words_file):
        # Зберігаємо шлях до файлу зі списком заборонених слів
        self.filePath = banned_words_file

    def add(self, words, bws):
        try:
            # Відкриваємо файл у режимі дописування та додаємо нові слова
            with open(self.filePath, 'a', encoding='utf-8') as file:
                for word in words:
                    file.write(f";{word}")
            
            # Оновлюємо базу заборонених слів
            bws.change_words_database(self.filePath)
            return f"'{words}' успішно додано до файлу!"

        except Exception as e:
            # Обробка помилок при записі у файл
            return f"Виникла помилка під час запису у файл: {e}"

    def remove(self, words, bws):
        try:
            # Зчитуємо вміст файлу
            with open(self.filePath, 'r', encoding='utf-8') as file:
                content = file.read()

            result = {
                'removed': [],  # Видалені слова
                'not_found': []  # Слова, яких немає у файлі
            }

            updated_content = content  # Робоча копія вмісту файлу

            # Видаляємо вказані слова з файлу
            for word in words:
                formatted_word = f";{word}"
                if formatted_word in updated_content:
                    updated_content = updated_content.replace(formatted_word, "")
                    result['removed'].append(word)
                else:
                    result['not_found'].append(word)

            # Запис зміненого вмісту у файл ОДИН раз, щоб зменшити кількість операцій введення/виведення
            with open(self.filePath, 'w', encoding='utf-8') as file:
                file.write(updated_content)

            # Оновлюємо базу заборонених слів
            bws.change_words_database(self.filePath)

            return result

        except Exception as e:
            # Обробка помилок при видаленні з файлу
            return f"Виникла помилка під час видалення з файлу: {e}"

