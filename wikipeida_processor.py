import os
import gc
import ctypes
libc = ctypes.CDLL("libc.so.6")

import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from faiss import read_index
from tqdm.auto import tqdm

from document_processor import process_documents

SIM_MODEL = "./models/all-MiniLM-L6-v2"
DEVICE = 0
MAX_LENGTH = 384
NUM_SENTENCES_INCLUDE = 20

WIKI_PATH = "./data/wikipedia-20230701"
WIKI_INDEX = "./data/wikipedia_202307.index"
wiki_files = os.listdir(WIKI_PATH)

model = SentenceTransformer(SIM_MODEL, device='cuda')
model.max_seq_length = MAX_LENGTH
model = model.half()

sentence_index = read_index(WIKI_INDEX)
df = pd.read_parquet(WIKI_PATH + "/wiki_2023_index.parquet", columns=['id', 'file'])

def add_context(query: pd):
    try:
        prompt_embedding = model.encode(query.question.values, batch_size=1, device=DEVICE, show_progress_bar=False, convert_to_tensor=True, normalize_embeddings=True)
        prompt_embedding = prompt_embedding.detach().cpu().numpy()
        _ = gc.collect()
        search_score, search_index = sentence_index.search(prompt_embedding, 1)
        del prompt_embedding
        _ = gc.collect()
        libc.malloc_trim(0)
        wikipedia_file_data = []
        for i, (scr, idx) in tqdm(enumerate(zip(search_score, search_index)), total=len(search_score)):
            scr_idx = idx
            _df = df.loc[scr_idx].copy()
            _df['prompt_id'] = i
            wikipedia_file_data.append(_df)
        wikipedia_file_data = pd.concat(wikipedia_file_data).reset_index(drop=True)
        wikipedia_file_data = wikipedia_file_data[['id', 'prompt_id', 'file']].drop_duplicates().sort_values(['file', 'id']).reset_index(drop=True)
        _ = gc.collect()
        libc.malloc_trim(0)
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

        processed_wiki_text_data = process_documents(wiki_text_data.text.values, wiki_text_data.id.values)
        wiki_data_embeddings = model.encode(processed_wiki_text_data.text,
                                            batch_size=32,
                                            device=DEVICE,
                                            show_progress_bar=False,
                                            convert_to_tensor=True,
                                            normalize_embeddings=True)
        wiki_data_embeddings = wiki_data_embeddings.detach().cpu().numpy()
        _ = gc.collect()
        query["answer_all"] = query.apply(lambda x: " ".join([x['A'], x['B'], x['C'], x['D'], x['E']]), axis=1)
        query['prompt_answer_stem'] = query['question'] + " " + query['answer_all']
        question_embedding = model.encode(query.prompt_answer_stem.values, batch_size=1, device=DEVICE, show_progress_bar=False, convert_to_tensor=True, normalize_embeddings=True)
        question_embedding = question_embedding.detach().cpu().numpy()
        contexts = []
        for r in tqdm(query.itertuples(), total=len(query)):
            prompt_id = r.Index
            prompt_indices = processed_wiki_text_data[processed_wiki_text_data['document_id'].isin(wikipedia_file_data[wikipedia_file_data['prompt_id']==prompt_id]['id'].values)].index.values
            if prompt_indices.shape[0] > 0:
                prompt_index = faiss.index_factory(wiki_data_embeddings.shape[1], "Flat")
                prompt_index.add(wiki_data_embeddings[prompt_indices])
                context = ""
                ## Get the top matches
                ss, ii = prompt_index.search(question_embedding, NUM_SENTENCES_INCLUDE)
                for _s, _i in zip(ss[prompt_id], ii[prompt_id]):
                    context += processed_wiki_text_data.loc[prompt_indices]['text'].iloc[_i] + " "
            contexts.append(context)
        query['context'] = contexts
    except:
        query['context'] = ""
    return query[["question", "context", "A", "B", "C", "D", "E"]]
