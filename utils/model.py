import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel


class ModerationModel(nn.Module):
    def __init__(self, input_size=384, output_size=11):
        super(ModerationModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


class TextModeration:
    def __init__(self, model_path, transformer_name):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(transformer_name)
        self.model_embeddings = AutoModel.from_pretrained(transformer_name).to(self.device)
        
        self.model = ModerationModel()
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        self.category_names = [
            "harassment", "harassment-threatening", "hate", "hate-threatening",
            "self-harm", "self-harm-instructions", "self-harm-intent",
            "sexual", "sexual-minors", "violence", "violence-graphic"
        ]

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def get_embeddings(self, text):
        encoded_input = self.tokenizer([text], padding=True, truncation=True, return_tensors='pt').to(self.device)
        with torch.no_grad():
            model_output = self.model_embeddings(**encoded_input)
        return self.mean_pooling(model_output, encoded_input['attention_mask']).cpu().numpy()[0]

    def predict(self, text, threshold=0.5):
        embeddings = torch.tensor(self.get_embeddings(text), dtype=torch.float).to(self.device)
        with torch.no_grad():
            outputs = torch.sigmoid(self.model(embeddings.unsqueeze(0))).squeeze(0).tolist()
        
        result = {category: score for category, score in zip(self.category_names, outputs)}
        detected = {category: score > threshold for category, score in zip(self.category_names, outputs)}
        detect_value = any(detected.values())
        
        return {"category_scores": result, "detect": detected, "detected": detect_value}


# if __name__ == "__main__":
#     model_path = './materials/moderation_model.pth'
#     transformer_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
#     analyzer = TextModeration(model_path, transformer_name)
    
#     text = 'I think it is time to kill him'
#     prediction = analyzer.predict(text)
#     print(json.dumps(prediction, indent=4))
