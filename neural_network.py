import numpy as np
import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer
from transformers import AutoModelForMultipleChoice
from torch.utils.data import DataLoader
from torch.nn.functional import softmax

from wikipeida_processor import add_context

from utils import *

model_dir = "./models/deberta-v3-large"
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForMultipleChoice.from_pretrained(model_dir).cuda()
model.eval()

def preprocess(example):
    # The AutoModelForMultipleChoice class expects a set of question/answer pairs
    # so we'll copy our question 5 times before tokenizing
    first_sentence = [example['prompt']] * 5
    second_sentence = []
    for option in options:
        second_sentence.append(example[option])
    # Our tokenizer will turn our text into token IDs BERT can understand
    tokenized_example = tokenizer(first_sentence, second_sentence, truncation=True)
    tokenized_example['label'] = option_to_index[example['answer']]
    return tokenized_example

def infer(query: pd):
    import time
    start = time.time()
    query = add_context(query)
    end = time.time()
    print("context time:", end - start)

    start = time.time()
    query.index = list(range(len(query)))
    query["id"] = list(range(len(query)))
    query["prompt"] = query["context"].apply(lambda x: x[:1750]) + " #### " + query["question"]
    query["answer"] = "A"

    tokenized_test_dataset = Dataset.from_pandas(query[['prompt', 'A', 'B', 'C', 'D', 'E', 'answer']]).map(preprocess, remove_columns=['prompt', 'A', 'B', 'C', 'D', 'E', 'answer'])
    tokenized_test_dataset = tokenized_test_dataset.remove_columns(["__index_level_0__"])
    data_collator = DataCollatorForMultipleChoice(tokenizer=tokenizer)
    test_dataloader = DataLoader(tokenized_test_dataset, batch_size=1, shuffle=False, collate_fn=data_collator)

    test_predictions = []
    for batch in test_dataloader:
        for k in batch.keys():
            batch[k] = batch[k].cuda()
        with torch.no_grad():
            outputs = model(**batch)
        test_predictions.append(outputs.logits.cpu().detach())
    prob = softmax(test_predictions[0])
    prob = float(torch.max(prob))
    print("prob:", prob)
    test_predictions = torch.cat(test_predictions)
    test_predictions = test_predictions.numpy()



    predictions_as_ids = np.argsort(-test_predictions, 1)
    predictions_as_answer_letters = np.array(list('ABCDE'))[predictions_as_ids]
    predictions_as_string = query['prediction'] = [
    ' '.join(row) for row in predictions_as_answer_letters[:, :3]
    ]

    end = time.time()
    print("infer time:", end - start)

    return predictions_as_string[0][0], prob
