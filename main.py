import os
import bz2
import json
from tqdm import tqdm
from loguru import logger

from models.load_model import load_model, load_model_ollama
from models.router.router import SequenceClassificationRouter
from models.retrieve.retriever import Retriever, Retriever_Milvus
from models.model import RAGModel

BATCH_SIZE = 20

def load_data_in_batches(dataset_path, batch_size):
    """
    Generator function that reads data from a compressed file and yields batches of data.
    Each batch is a dictionary containing lists of interaction_ids, queries, search results, query times, and answers.
    
    Args:
    dataset_path (str): Path to the dataset file.
    batch_size (int): Number of data items in each batch.
    
    Yields:
    dict: A batch of data.
    """
    def initialize_batch():
        """ Helper function to create an empty batch. """
        return {"interaction_id": [], "query": [], "search_results": [], "query_time": [], "answer": []}

    try:
        if dataset_path.endswith(".bz2"):
            with bz2.open(dataset_path, "rt") as file:
                batch = initialize_batch()
                for line in file:
                    try:
                        item = json.loads(line)
                        for key in batch:
                            batch[key].append(item[key])
                        
                        if len(batch["query"]) == batch_size:
                            yield batch
                            batch = initialize_batch()
                    except json.JSONDecodeError:
                        logger.warn("Warning: Failed to decode a line.")
                # Yield any remaining data as the last batch
                if batch["query"]:
                    yield batch
        else:
            with open(dataset_path, "r") as file:
                batch = initialize_batch()
                for line in file:
                    try:
                        item = json.loads(line)
                        for key in batch:
                            batch[key].append(item[key])
                        
                        if len(batch["query"]) == batch_size:
                            yield batch
                            batch = initialize_batch()
                    except json.JSONDecodeError:
                        logger.warn("Warning: Failed to decode a line.")
                # Yield any remaining data as the last batch
                if batch["query"]:
                    yield batch
    except FileNotFoundError as e:
        logger.error(f"Error: The file {dataset_path} was not found.")
        raise e
    except IOError as e:
        logger.error(f"Error: An error occurred while reading the file {dataset_path}.")
        raise e
    
def generate_predictions(dataset_path, participant_model):
    """
    Processes batches of data from a dataset to generate predictions using a model.
    
    Args:
    dataset_path (str): Path to the dataset.
    participant_model (object): UserModel that provides `get_batch_size()` and `batch_generate_answer()` interfaces.
    
    Returns:
    tuple: A tuple containing lists of queries, ground truths, and predictions.
    """
    queries, ground_truths, predictions = [], [], []
    batch_size = BATCH_SIZE

    for batch in tqdm(load_data_in_batches(dataset_path, batch_size), desc="Generating predictions"):
        batch_ground_truths = batch.pop("answer")  # Remove answers from batch and store them
        batch_predictions = participant_model.batch_generate_answer(batch)
        queries.extend(batch["query"])
        ground_truths.extend(batch_ground_truths)
        predictions.extend(batch_predictions)
        logger.info(f"Query Example: {queries[-1]}")
        logger.info(f"Ground Truth Example: {ground_truths[-1]}")
        logger.info(f"Prediction Example: {predictions[-1]}")
    return queries, ground_truths, predictions

if __name__ == "__main__":
    # Set the environment variable for the mock API
    os.environ["CRAG_MOCK_API_URL"] = "http://localhost:8000"

    # Load the model
    api_key = "<your-api-key>"
    base_url = "<your-base-url>"
    model_name = "gpt-4o"
    chat_model = load_model(model_name=model_name, api_key=api_key, base_url=base_url, temperature=0)
    # chat_model = load_model_ollama(model_name=model_name, temperature=0)

    # Load the retriever
    embedding_model_path = "models/retrieve/embedding_models/bge-m3"
    reranker_model_path = "models/retrieve/reranker_models/bge-reranker-v2-m3"

    retriever = Retriever(10, 5, embedding_model_path, reranker_model_path, rerank=True)
    # To use the retriever with Milvus, uncomment the following lines and comment the previous line
    # collection_name = "bge_m3_crag_task_3_dev_v3_llamaindex"
    # uri = "http://localhost:19530"
    # uri = ".models/retrieve/milvus.db"
    # retriever = Retriever_Milvus(10, 5, collection_name, uri, embedding_model_path, reranker_model_path, rerank=True)

    # Load the domain router
    domain_router = SequenceClassificationRouter(
        model_path="models/llm/Meta-Llama-3-8B-Instruct-hf",
        classes=["finance", "music", "movie", "sports", "open"],
        device_map="auto",
        peft_path="models/router/domain",
        use_bits_and_bytes=True,
        use_peft=True,
    )

    # Load the dynamic router
    use_kg = True
    use_dynamic = True
    if use_dynamic:
        dynamic_router = SequenceClassificationRouter(
            model_path="models/llm/Meta-Llama-3-8B-Instruct-hf",
            classes=['static', 'slow-changing', 'fast-changing', 'real-time'],
            device_map="auto",
            peft_path="models/router/dynamic",
            use_bits_and_bytes=True,
            use_peft=True
        )
    # Initialize the RAG model
        rag_model = RAGModel(chat_model, retriever, domain_router, dynamic_router, use_kg=use_kg)
    else:
        rag_model = RAGModel(chat_model, retriever, domain_router, use_kg=use_kg)
    # Generate predictions
    dataset_path = "example_data/dev_data.jsonl.bz2"
    queries, ground_truths, predictions = generate_predictions(dataset_path, rag_model)
    
    # Save the predictions
    output_path = f"results/{model_name}_predictions.jsonl"
    with open(output_path, "w") as file:
        for query, ground_truth, prediction in zip(queries, ground_truths, predictions):
            item = {"query": query, "ground_truth": ground_truth, "prediction": prediction}
            file.write(json.dumps(item) + "\n")
    
    logger.info(f"Predictions saved to {output_path}.")