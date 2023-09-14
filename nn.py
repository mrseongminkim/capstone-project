from typing import Optional, Union
from dataclasses import dataclass

import pandas as pd
import numpy as np
import torch
from datasets import Dataset
from transformers import AutoTokenizer
from transformers.tokenization_utils_base import PreTrainedTokenizerBase, PaddingStrategy
from transformers import AutoModelForMultipleChoice, TrainingArguments, Trainer

model_name = "deberta-v3-large-hf-weights-0-734"
model = AutoModelForMultipleChoice.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

option_to_index = {option: idx for idx, option in enumerate('ABCDE')}
index_to_option = {v: k for k,v in option_to_index.items()}

def preprocess(example):
    first_sentence = [example['question']] * 5
    second_sentences = [example[option] for option in 'ABCDE']
    tokenized_example = tokenizer(first_sentence, second_sentences, truncation=False)
    tokenized_example['label'] = option_to_index[example['answer']]
    return tokenized_example

@dataclass
class DataCollatorForMultipleChoice:
    tokenizer: PreTrainedTokenizerBase
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None
    
    def __call__(self, features):
        label_name = 'label' if 'label' in features[0].keys() else 'labels'
        labels = [feature.pop(label_name) for feature in features]
        batch_size = len(features)
        num_choices = len(features[0]['input_ids']) # 5
        flattened_features = [
            [{k: v[i] for k, v in feature.items()} for i in range(num_choices)] for feature in features
        ]
        flattened_features = sum(flattened_features, [])
        batch = self.tokenizer.pad(
            flattened_features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors='pt',
        )
        batch = {k: v.view(batch_size, num_choices, -1) for k, v in batch.items()}
        batch['labels'] = torch.tensor(labels, dtype=torch.int64)
        return batch

training_args = TrainingArguments(
    warmup_ratio=0.8,
    learning_rate=5e-6,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    report_to='none',
    output_dir='.',
)

trainer = Trainer(
    model=model,
    args=training_args,
    tokenizer=tokenizer,
    data_collator=DataCollatorForMultipleChoice(tokenizer=tokenizer),
)

def run_model(test_df):
    test_df['answer'] = 'A'
    tokenized_test_dataset = Dataset.from_pandas(test_df).map(preprocess, remove_columns=['question', 'A', 'B', 'C', 'D', 'E'])
    test_predictions = trainer.predict(tokenized_test_dataset).predictions
    predictions_as_ids = np.argsort(-test_predictions, 1)
    predictions_as_answer_letters = np.array(list('ABCDE'))[predictions_as_ids]
    return predictions_as_answer_letters[0][0]