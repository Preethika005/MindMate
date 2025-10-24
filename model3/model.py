import torch
from torch import nn
from datasets import load_dataset
from transformers import DistilBertTokenizer, DistilBertModel, Trainer, TrainingArguments
from transformers.modeling_outputs import SequenceClassifierOutput
import os
from google.colab import drive
import numpy as np
from sklearn.metrics import accuracy_score


# 1. Load Dataset (CSV files with text, label, stress_level, urgency columns)
data_files = {
    'train': '/content/merged_train_with_schema.csv',
    'validation': '/content/merged_val_with_schema.csv',
    'test': '/content/merged_test_with_schema.csv'
}
dataset = load_dataset('csv', data_files=data_files)


# 2. Tokenizer using DistilBERT
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True, max_length=128)  # reduced max_length
tokenized_datasets = dataset.map(tokenize_function, batched=True)


# 3. Encode labels as integers for each classification task
# Converts string labels (like 'joy', 'fear') into integer indices, because neural networks work with numbers.
label_list_emotion = sorted(set(dataset['train']['label']))  # e.g., ['fear', 'joy']
label_list_stress = sorted(set(dataset['train']['stress_level']))  # e.g., ['low', 'moderate', 'high']
label_list_urgency = sorted(set(dataset['train']['urgency']))  # e.g., ['low', 'high']

# Adds integer labels for all three tasks to each example.
def encode_labels(example):
    example['label_emotion'] = label_list_emotion.index(example['label'])
    example['label_stress'] = label_list_stress.index(example['stress_level'])
    example['label_urgency'] = label_list_urgency.index(example['urgency'])
    return example


tokenized_datasets = tokenized_datasets.map(encode_labels)


# 4. Define a multi-task DistilBERT model
class MultiTaskDistilBERT(nn.Module):
    def __init__(self, model_name, num_labels_emotion, num_labels_stress, num_labels_urgency):
        super(MultiTaskDistilBERT, self).__init__()
        self.distilbert = DistilBertModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.3)
        hidden_size = self.distilbert.config.hidden_size

        # Separate classification heads for each task
        self.classifier_emotion = nn.Linear(hidden_size, num_labels_emotion)
        self.classifier_stress = nn.Linear(hidden_size, num_labels_stress)
        self.classifier_urgency = nn.Linear(hidden_size, num_labels_urgency)

    def forward(self, input_ids, attention_mask=None,
                label_emotion=None, label_stress=None, label_urgency=None):
        outputs = self.distilbert(input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0]  # DistilBERT doesn't have pooler_output, use first token
        pooled_output = self.dropout(pooled_output)

        logits_emotion = self.classifier_emotion(pooled_output)
        logits_stress = self.classifier_stress(pooled_output)
        logits_urgency = self.classifier_urgency(pooled_output)

        loss = None
        loss_fct = nn.CrossEntropyLoss()
        if label_emotion is not None and label_stress is not None and label_urgency is not None:
            loss_emotion = loss_fct(logits_emotion, label_emotion)
            loss_stress = loss_fct(logits_stress, label_stress)
            loss_urgency = loss_fct(logits_urgency, label_urgency)
            loss = loss_emotion + loss_stress + loss_urgency

        return SequenceClassifierOutput(
            loss=loss,
            logits=(logits_emotion, logits_stress, logits_urgency),
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )


# 5. Instantiate model
num_labels_emotion = len(label_list_emotion)
num_labels_stress = len(label_list_stress)
num_labels_urgency = len(label_list_urgency)
model = MultiTaskDistilBERT('distilbert-base-uncased', num_labels_emotion, num_labels_stress, num_labels_urgency)


# 6. Prepare datasets for Trainer: rename columns for Trainer compatibility
def rename_columns(examples):
    return {
        'input_ids': examples['input_ids'],
        'attention_mask': examples['attention_mask'],
        'label_emotion': examples['label_emotion'],
        'label_stress': examples['label_stress'],
        'label_urgency': examples['label_urgency']
    }


tokenized_datasets = tokenized_datasets.map(rename_columns, batched=True)
tokenized_datasets.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label_emotion', 'label_stress', 'label_urgency'])


# Optional: Mount Google Drive for checkpoint persistence
drive.mount('/content/drive')

# Change output directory to Google Drive to save checkpoints persistently
output_dir = '/content/drive/MyDrive/mindmate_results'


# 7. Define a custom Trainer to handle multiple labels and outputs
from transformers import Trainer


class MultiTaskTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels_emotion = inputs.pop("label_emotion")
        labels_stress = inputs.pop("label_stress")
        labels_urgency = inputs.pop("label_urgency")
        outputs = model(**inputs, label_emotion=labels_emotion, label_stress=labels_stress, label_urgency=labels_urgency)
        loss = outputs.loss
        return (loss, outputs) if return_outputs else loss


def compute_metrics(eval_pred):
    logits_emotion, logits_stress, logits_urgency = eval_pred.predictions
    labels_emotion, labels_stress, labels_urgency = eval_pred.label_ids

    preds_emotion = np.argmax(logits_emotion, axis=1)
    preds_stress = np.argmax(logits_stress, axis=1)
    preds_urgency = np.argmax(logits_urgency, axis=1)

    acc_emotion = accuracy_score(labels_emotion, preds_emotion)
    acc_stress = accuracy_score(labels_stress, preds_stress)
    acc_urgency = accuracy_score(labels_urgency, preds_urgency)

    return {
        "accuracy_emotion": acc_emotion,
        "accuracy_stress": acc_stress,
        "accuracy_urgency": acc_urgency,
    }


training_args = TrainingArguments(
    output_dir=output_dir,
    eval_strategy='epoch',
    save_strategy='steps',       # Save by steps for frequent checkpointing
    save_steps=500,              # Save checkpoint every 500 steps
    save_total_limit=2,          # Keep last 2 checkpoints to save space
    learning_rate=2e-5,
    per_device_train_batch_size=32,  # Increased batch size for speed if GPU allows
    per_device_eval_batch_size=32,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_steps=100,           # Log training info every 100 steps
    fp16=True                    # Enable mixed precision for speed on supported GPUs
)


trainer = MultiTaskTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['validation'],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

# 8. Resume from last checkpoint if available
last_checkpoint = None
# if os.path.isdir(training_args.output_dir):
#     checkpoints = [os.path.join(training_args.output_dir, d) for d in os.listdir(training_args.output_dir) if d.startswith('checkpoint')]
#     if checkpoints:
#         last_checkpoint = sorted(checkpoints)[-1]
#         print(f"Resuming from checkpoint: {last_checkpoint}")

trainer.train(resume_from_checkpoint=last_checkpoint)

# 9. Evaluate & Test
eval_results = trainer.evaluate()
print("Evaluation results:", eval_results)

test_results = trainer.predict(tokenized_datasets['test'])
print("Test results:", test_results.metrics)

# 10. Save model & tokenizer using torch.save and tokenizer's save_pretrained
save_dir = '/content/drive/MyDrive/mindmatemodel3'
os.makedirs(save_dir, exist_ok=True)
torch.save(model.state_dict(), f'{save_dir}/model.pt')
tokenizer.save_pretrained(save_dir)
