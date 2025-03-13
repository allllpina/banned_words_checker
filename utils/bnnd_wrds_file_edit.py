import os

class BannedWordsFileEdit:
    @staticmethod
    def add(db_path, words):
        try:
            if not words:
                return {"error": "No words found in request!"}

            # Читаємо поточний вміст файлу, якщо він існує
            existing_words = set()
            is_empty = not os.path.exists(db_path) or os.path.getsize(db_path) == 0

            if not is_empty:
                with open(db_path, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
                    if content:
                        existing_words = set(content.split(";"))  # Розбиваємо на слова

            # Фільтруємо слова, яких ще немає в файлі
            new_words = [word for word in words if word and word not in existing_words]

            if not new_words:
                return {"error": "All words already in database!"}

            # Відкриваємо файл для запису нових слів
            with open(db_path, 'a', encoding='utf-8') as file:
                for word in new_words:
                    if is_empty:
                        file.write(word)  # Перше слово без `;`, якщо файл порожній
                        is_empty = False
                    else:
                        file.write(f";{word}")

            return {"added": new_words, "skipped": list(set(words) - set(new_words))}

        except Exception as e:
            # Обробка помилок при записі у файл
            return {"error": f"Error writing to file: {e}"}

    @staticmethod
    def remove(db_path, words):
        try:

            # Перевірка на порожній список
            if not words:
                return {"error": "No words found in request!"}

            # Перевірка чи така база даних існує
            if not os.path.exists(db_path):
                return {"error": "Database with this name does not exist!"}

            # Зчитуємо вміст файлу
            with open(db_path, 'r', encoding='utf-8') as file:
                content = file.read()

            result = {
                'removed': [],  # Видалені слова
                'not_found': []  # Слова, яких немає у файлі
            }

            updated_content = content  # Робоча копія вмісту файлу
            tokens = [token for token in updated_content.split(';') if token]

            # Видаляємо вказані слова з файлу
            for word in words:
                if word == "":
                    continue
                if word in tokens:
                    tokens.remove(word)
                    result['removed'].append(word)
                else:
                    result['not_found'].append(word)

            # Запис тих слів що залишились після чистки у файл
            updated_content = ";".join(tokens)

            # Запис зміненого вмісту у файл ОДИН раз, щоб зменшити кількість операцій введення/виведення
            with open(db_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)

            return result

        except Exception as e:
            # Обробка помилок при видаленні з файлу
            return {"error": f"Error deleting from file: {e}"}

    @staticmethod
    def read_words(db_path):
        try:
            # Зчитуємо вміст файлу
            with open(db_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Розділяємо слова за символом ';' та фільтруємо порожні елементи
            words = content.split(';')
            words = [word for word in words if word.strip()]  # Видаляємо порожні рядки

            return {'length': len(words), "words": words}

        except Exception as e:
            # Обробка помилок при зчитуванні з файлу
            return {"error": f"Error reading from file: {e}"}
