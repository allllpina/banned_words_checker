class BannedWordsFileEdit:
    def __init__(self, banned_words_file):
        # Зберігаємо шлях до файлу зі списком заборонених слів
        self.filePath = banned_words_file

    def add(self, words, bws):
        try:

            # Перевірка на порожній список
            if not words:
                return "Список слів порожній. Немає що додавати."

            # Відкриваємо файл у режимі дописування та додаємо нові слова
            with open(self.filePath, 'a', encoding='utf-8') as file:
                for word in words:
                    # Якщо словом є пуста стрічка, ми пропускаємо іттерацію
                    if word == "":
                        continue
                    file.write(f";{word}")
            
            # Оновлюємо базу заборонених слів
            bws.change_words_database(self.filePath)
            return f"'{words}' успішно додано до файлу!"

        except Exception as e:
            # Обробка помилок при записі у файл
            return f"Виникла помилка під час запису у файл: {e}"

    def remove(self, words, bws):
        try:
            
            # Перевірка на порожній список
            if not words:
                return "Список слів порожній. Немає що видаляти."
            
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
                if word == "":
                    continue
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

    def read_words(self):
        try:
            # Зчитуємо вміст файлу
            with open(self.filePath, 'r', encoding='utf-8') as file:
                content = file.read()

            # Розділяємо слова за символом ';' та фільтруємо порожні елементи
            words = content.split(';')
            words = [word for word in words if word.strip()]  # Видаляємо порожні рядки

            return {'length': len(words), "words": words}

        except Exception as e:
            # Обробка помилок при зчитуванні з файлу
            return f"Виникла помилка під час зчитування з файлу: {e}"