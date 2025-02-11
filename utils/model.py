import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel


class ModerationModel(nn.Module):
    """
    Нейромережа для класифікації тексту на 11 категорій модерації.
    """
    def __init__(self, input_size=384, output_size=11):
        super(ModerationModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)  # Повнозв'язаний шар із 128 нейронами
        self.fc2 = nn.Linear(128, output_size)  # Вихідний шар із 11 класами

    def forward(self, x):
        """
        Прямий прохід через модель із функцією активації ReLU.
        """
        x = F.relu(self.fc1(x))  # Активація ReLU
        x = self.fc2(x)  # Лінійний вихід
        return x


class TextModeration:
    """
    Клас для перевірки тексту на заборонений контент за допомогою трансформера та моделі модерації.
    """
    def __init__(self, model_path, transformer_name):
        """
        Ініціалізує токенізатор, трансформер та завантажує модель модерації.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"  # Визначення пристрою
        self.tokenizer = AutoTokenizer.from_pretrained(transformer_name)  # Завантаження токенізатора
        self.model_embeddings = AutoModel.from_pretrained(transformer_name).to(self.device)  # Завантаження трансформера
        
        self.model = ModerationModel()
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))  # Завантаження ваг моделі
        self.model.to(self.device)
        self.model.eval()  # Переклад у режим оцінки

        # Категорії, за якими класифікується текст
        self.category_names = [
            "harassment", "harassment-threatening", "hate", "hate-threatening",
            "self-harm", "self-harm-instructions", "self-harm-intent",
            "sexual", "sexual-minors", "violence", "violence-graphic"
        ]

    def mean_pooling(self, model_output, attention_mask):
        """
        Виконує mean pooling (усереднення) токенів з урахуванням маски уваги.
        """
        token_embeddings = model_output[0]  # Витягуємо токенізовані представлення
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def get_embeddings(self, text):
        """
        Отримує векторне представлення тексту за допомогою трансформера.
        """
        encoded_input = self.tokenizer([text], padding=True, truncation=True, return_tensors='pt').to(self.device)
        with torch.no_grad():
            model_output = self.model_embeddings(**encoded_input)
        return self.mean_pooling(model_output, encoded_input['attention_mask']).cpu().numpy()[0]

    def predict(self, text, threshold=0.5):
        """
        Передбачає категорії модерації для даного тексту.
        
        :param text: Вхідний текст
        :param threshold: Поріг для визначення, чи є категорія активною
        :return: Словник із оцінками категорій та статусом виявлення
        """
        embeddings = torch.tensor(self.get_embeddings(text), dtype=torch.float).to(self.device)
        with torch.no_grad():
            outputs = torch.sigmoid(self.model(embeddings.unsqueeze(0))).squeeze(0).tolist()
        
        # Формування результату
        result = {category: score for category, score in zip(self.category_names, outputs)}
        detected = {category: score > threshold for category, score in zip(self.category_names, outputs)}
        detect_value = any(detected.values())  # Чи було знайдено небажаний контент
        
        return {"category_scores": result, "detect": detected, "detected": detect_value}