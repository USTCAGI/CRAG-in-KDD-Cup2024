# Create an index over the documents
import bz2
import json
from tqdm import tqdm
from langchain_milvus.vectorstores import Milvus
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.runnables import RunnableLambda
from langchain_core.documents import Document
from retriever import get_all_chunks



# embeddings = OpenAIEmbeddings(api_key="<your-api-key>", base_url="<your-base-url>")
embeddings = HuggingFaceBgeEmbeddings(
    model_name="embedding_models/bge-m3",
    model_kwargs = {'device': 'cuda'},
    encode_kwargs = {'normalize_embeddings': True}, # set True to compute cosine similarity
    query_instruction = "",
)

# Milvus Server
# uri = "http://localhost:19530"
# Milvus Lite
uri = "./milvus.db"

collection_name = "bge_m3_crag_dev_v3_llamaindex"

vectorstore = Milvus(
    embeddings,
    connection_args={"uri": uri},
    collection_name=collection_name,
    partition_key_field="interaction_id",
    drop_old=True,
    auto_id=True,
    index_params={
        "metric_type": "IP",
        "index_type": "IVF_FLAT",
        "params": {
            "nlist": 65536
        }
    }
)

all_data = []
with bz2.open('data/crag_task_1_dev_v3_release.jsonl.bz2', "rt") as f:
    for line in f:
        all_data.append(json.loads(line))

batch_size = 5
bacth_data = []
for i, data in tqdm(enumerate(all_data)):
    d = {"interaction_id": data["interaction_id"], "search_results": data["search_results"], "query": data["query"]}
    if i % batch_size == 0:
        bacth_data.append([d])
    else:
        bacth_data[-1].append(d)

build_docs = RunnableLambda(lambda x: [Document(chunk, metadata={"interaction_id": x['interaction_id']}) for chunk in get_all_chunks(x['query'], x['search_results'])])

for data in tqdm(bacth_data):
    docs = []
    for doc in build_docs.batch(data):
        docs.extend(doc)
    if vectorstore is None:
        vectorstore = Milvus.from_documents(
            docs,
            embeddings,
            connection_args={"uri": uri},
            collection_name=collection_name,
            partition_key_field="interaction_id",
            drop_old=True,
            index_params={
                "metric_type": "IP",
                "index_type": "IVF_FLAT",
                "params": {
                    "nlist": 65536
                }
            }
        )
    else:
        vectorstore.add_documents(docs)


# Test
query = all_data[0]["query"]
interaction_id = all_data[0]["interaction_id"]
print(vectorstore.similarity_search(query, expr=f"interaction_id == '{interaction_id}'"))