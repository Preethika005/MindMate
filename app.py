from flask import Flask, request, jsonify
import torch
from torch import nn
from transformers import DistilBertTokenizer, DistilBertModel
import os

# -- Define the model class (must match your training definition) --
class MultiTaskDistilBERT(nn.Module):
    def __init__(self, model_name, num_labels_emotion, num_labels_stress, num_labels_urgency):
        super(MultiTaskDistilBERT, self).__init__()
        self.distilbert = DistilBertModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.3)
        hidden_size = self.distilbert.config.hidden_size
        self.classifier_emotion = nn.Linear(hidden_size, num_labels_emotion)
        self.classifier_stress = nn.Linear(hidden_size, num_labels_stress)
        self.classifier_urgency = nn.Linear(hidden_size, num_labels_urgency)

    def forward(self, input_ids, attention_mask=None):
        outputs = self.distilbert(input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0]
        pooled_output = self.dropout(pooled_output)
        logits_emotion = self.classifier_emotion(pooled_output)
        logits_stress = self.classifier_stress(pooled_output)
        logits_urgency = self.classifier_urgency(pooled_output)
        return logits_emotion, logits_stress, logits_urgency

# -- Update these lists to match your training data --
label_list_emotion = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'stress', 'surprise']  # 8 classes
label_list_stress = ['high', 'low', 'moderate']  # 3 classes
label_list_urgency = ['critical', 'high', 'low', 'medium']  # 4 classes

num_labels_emotion = len(label_list_emotion)
num_labels_stress = len(label_list_stress)
num_labels_urgency = len(label_list_urgency)

# -- Paths --
MODEL_DIR = "multitask-distilbert-model"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pt")

# -- Load tokenizer and model --
tokenizer = DistilBertTokenizer.from_pretrained(MODEL_DIR)
model = MultiTaskDistilBERT("distilbert-base-uncased", num_labels_emotion, num_labels_stress, num_labels_urgency)
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.eval()

# -- Flask App --
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get('text', None)
    if text is None:
        return jsonify({"error": "No text sent"}), 400

    # Tokenize
    inputs = tokenizer(text, return_tensors='pt', padding='max_length', truncation=True, max_length=128)

    with torch.no_grad():
        logits_emotion, logits_stress, logits_urgency = model(
            input_ids=inputs['input_ids'],
            attention_mask=inputs['attention_mask']
        )
        pred_emotion = torch.argmax(logits_emotion, dim=1).item()
        pred_stress = torch.argmax(logits_stress, dim=1).item()
        pred_urgency = torch.argmax(logits_urgency, dim=1).item()

    # Map indices to labels
    result = {
        "emotion": label_list_emotion[pred_emotion],
        "stress": label_list_stress[pred_stress],
        "urgency": label_list_urgency[pred_urgency]
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)






