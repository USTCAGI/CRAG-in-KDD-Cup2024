import html
from bs4 import BeautifulSoup
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
from llama_index.core.schema import Document, QueryBundle
from llama_index.core.node_parser import SentenceSplitter
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.vector_stores.milvus import MilvusVectorStore
import newspaper
import ray
import threading
import logging

def html2txt(html):
    if html is None or html.strip() == "":
        return ""
    article = newspaper.Article('')
    article.set_html(html)
    try:
        article.parse()
        return article.text
    except:
        soup = BeautifulSoup(
            html, features="html.parser"
        )
        text = soup.get_text()
        return text.replace("\n", " ")
    
def html2txt_with_timeout(html, timeout=20):
    text = ""
    def timeout_function():
        nonlocal text
        text = html2txt(html)
    thread = threading.Thread(target=timeout_function)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        logging.warning("Timeout occurred")
    return text
        
@ray.remote
def _extract_html(html_text):
    # Parse the HTML content
    text = html2txt_with_timeout(html_text['page_result'])
    snippet = html.unescape(html_text['page_snippet'])
    return text, snippet

def get_all_chunks(query, search_results):
    documents = []
    # delete replicate search results
    page_urls = set()
    search_results = [result for result in search_results if not (result['page_url'] in page_urls or page_urls.add(result['page_url']))]

    ray_response_refs = [
        _extract_html.remote(
            html_text
        )
        for html_text in search_results
    ]

    for response_ref in ray_response_refs:
        text, snippet = ray.get(response_ref)  # Blocking call until parallel execution is complete
        if len(text) > 0:
            documents.append(Document(text=text))
        if len(snippet) > 0:
            documents.append(Document(text=snippet))

    ######################### pre-retrieval #########################
    if len(search_results) > 5:
        node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
        nodes = node_parser.get_nodes_from_documents(documents)
        similarity_top_k = 50
        if len(nodes) < 50:
            print(f"Not enough nodes for BM25 retrieval. Using all nodes({len(nodes)}).")
            similarity_top_k = len(nodes)
        bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=similarity_top_k)
        nodes = bm25_retriever.retrieve(query)
        texts = [node.get_text().strip() for node in nodes]
    else:
        texts = [node.get_text().strip() for node in documents]

    ######################### retrieval #########################
    node_parser = SentenceSplitter(chunk_size=256, chunk_overlap=20)
    texts = node_parser.split_texts(texts)
    return texts

class Retriever:
    def __init__(self, top_k, top_n, embedding_model_path, reranker_model_path=None, rerank=False, device="cuda"):
        self.top_k = top_k
        self.top_n = top_n
        self.embedding_model = HuggingFaceEmbedding(
            model_name=embedding_model_path, device=device
        )
        self.rerank = rerank
        if self.rerank:
            self.reranker = SentenceTransformerRerank(top_n=self.top_n, model=reranker_model_path, device=device)   
    
    def retrieve(self, query, interaction_id, search_results):
        documents = []
        page_urls = set()
        search_results = [result for result in search_results if not (result['page_url'] in page_urls or page_urls.add(result['page_url']))]

        ray_response_refs = [
            _extract_html.remote(
                html_text
            )
            for html_text in search_results
        ]

        for response_ref in ray_response_refs:
            text, snippet = ray.get(response_ref)  # Blocking call until parallel execution is complete
            if len(text) > 0:
                documents.append(Document(text=text))
            if len(snippet) > 0:
                documents.append(Document(text=snippet))

        ######################### pre-retrieval #########################
        if len(search_results) > 5:
            node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
            nodes = node_parser.get_nodes_from_documents(documents)
            similarity_top_k = 50
            if len(nodes) < 50:
                print(f"Not enough nodes for BM25 retrieval. Using all nodes({len(nodes)}).")
                similarity_top_k = len(nodes)
            bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=similarity_top_k)
            nodes = bm25_retriever.retrieve(query)
            documents = [Document(text=node.get_text().strip()) for node in nodes]       

        ######################### retrieval #########################
        node_parser = SentenceSplitter(chunk_size=256, chunk_overlap=20)
        nodes = node_parser.get_nodes_from_documents(documents)
        index = VectorStoreIndex(nodes, embed_model=self.embedding_model)
        retriever = index.as_retriever(similarity_top_k=self.top_k)
        nodes = retriever.retrieve(query)


        ######################### rerank #########################
        if self.rerank:
            reranked_nodes = self.reranker.postprocess_nodes(
                nodes,
                query_bundle=QueryBundle(query_str=query)
            )
            top_sentences = [node.get_text().strip() for node in reranked_nodes]
        else:
            top_sentences = [node.get_text().strip() for node in nodes]
        return top_sentences

class Retriever_Milvus:
    def __init__(self, top_k, top_n, collection_name, uri, embedding_model_path, reranker_model_path=None, rerank=False, device="cuda"):
        self.top_k = top_k
        self.top_n = top_n
        self.embedding_model = HuggingFaceEmbedding(
            model_name=embedding_model_path, device=device
        )
        vector_store = MilvusVectorStore(
            collection_name=collection_name,
            uri=uri,
            embedding_field="vector",
            text_key="text",
        )
        self.index = VectorStoreIndex.from_vector_store(vector_store, embed_model=self.embedding_model)
        self.rerank = rerank
        if self.rerank:
            self.reranker = self.reranker = SentenceTransformerRerank(top_n=self.top_k, model=reranker_model_path, device=device)
           
    def retrieve(self, query, iteraction_id, search_results):
        metadata_filter = MetadataFilters(
            filters=[ExactMatchFilter(key="interaction_id", value=f"{iteraction_id}")]
        )
        retriever = self.index.as_retriever(similarity_top_k=self.top_n, filters=metadata_filter)
        nodes = retriever.retrieve(query)

        ######################### rerank #########################
        if self.rerank:
            reranked_nodes = self.reranker.postprocess_nodes(
                nodes,
                query_bundle=QueryBundle(query_str=query)
            )
            top_sentences = [node.get_text().strip() for node in reranked_nodes]
        else:
            top_sentences = [node.get_text().strip() for node in nodes]
        return top_sentences