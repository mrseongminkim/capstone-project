import os
import gc
import ctypes
libc = ctypes.CDLL("libc.so.6")

import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from faiss import write_index, read_index
import tqdm

from document_processor import process_documents

SIM_MODEL = '/kaggle/input/sentencetransformers-allminilml6v2/sentence-transformers_all-MiniLM-L6-v2'
DEVICE = 0
MAX_LENGTH = 384
BATCH_SIZE = 16

WIKI_PATH = "/kaggle/input/wikipedia-20230701"
wiki_files = os.listdir(WIKI_PATH)

trn = pd.read_csv("/kaggle/input/kaggle-llm-science-exam/test.csv").drop("id", 1)
trn.head()

model = SentenceTransformer(SIM_MODEL, device='cuda')
model.max_seq_length = MAX_LENGTH
model = model.half()

sentence_index = read_index("/kaggle/input/wikipedia-2023-07-faiss-index/wikipedia_202307.index")

prompt_embeddings = model.encode(trn.prompt.values, batch_size=BATCH_SIZE, device=DEVICE, show_progress_bar=True, convert_to_tensor=True, normalize_embeddings=True)
prompt_embeddings = prompt_embeddings.detach().cpu().numpy()
_ = gc.collect()

## Get the top 3 pages that are likely to contain the topic of interest
search_score, search_index = sentence_index.search(prompt_embeddings, 5)

## Save memory - delete sentence_index since it is no longer necessary
del sentence_index
del prompt_embeddings
_ = gc.collect()
libc.malloc_trim(0)

df = pd.read_parquet("/kaggle/input/wikipedia-20230701/wiki_2023_index.parquet",
                     columns=['id', 'file'])

## Get the article and associated file location using the index
wikipedia_file_data = []

for i, (scr, idx) in tqdm(enumerate(zip(search_score, search_index)), total=len(search_score)):
    scr_idx = idx
    _df = df.loc[scr_idx].copy()
    _df['prompt_id'] = i
    wikipedia_file_data.append(_df)
wikipedia_file_data = pd.concat(wikipedia_file_data).reset_index(drop=True)
wikipedia_file_data = wikipedia_file_data[['id', 'prompt_id', 'file']].drop_duplicates().sort_values(['file', 'id']).reset_index(drop=True)

## Save memory - delete df since it is no longer necessary
del df
_ = gc.collect()
libc.malloc_trim(0)

## Get the full text data
wiki_text_data = []

for file in tqdm(wikipedia_file_data.file.unique(), total=len(wikipedia_file_data.file.unique())):
    _id = [str(i) for i in wikipedia_file_data[wikipedia_file_data['file']==file]['id'].tolist()]
    _df = pd.read_parquet(f"{WIKI_PATH}/{file}", columns=['id', 'text'])

    _df_temp = _df[_df['id'].isin(_id)].copy()
    del _df
    _ = gc.collect()
    libc.malloc_trim(0)
    wiki_text_data.append(_df_temp)
wiki_text_data = pd.concat(wiki_text_data).drop_duplicates().reset_index(drop=True)
_ = gc.collect()

## Parse documents into sentences
processed_wiki_text_data = process_documents(wiki_text_data.text.values, wiki_text_data.id.values)

## Get embeddings of the wiki text data
wiki_data_embeddings = model.encode(processed_wiki_text_data.text,
                                    batch_size=BATCH_SIZE,
                                    device=DEVICE,
                                    show_progress_bar=True,
                                    convert_to_tensor=True,
                                    normalize_embeddings=True)#.half()
wiki_data_embeddings = wiki_data_embeddings.detach().cpu().numpy()

_ = gc.collect()

