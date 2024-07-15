from models.load_model import load_model
from prompts.templates import IN_CONTEXT_EXAMPLES, INSTRUCTIONS
from tqdm import tqdm
import json
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

BATCH_SIZE = 50

def parse_response(resp: str):
    """Pass auto-eval output from the evaluator."""
    try:
        resp = resp.lower()
        model_resp = json.loads(resp)
        answer = -1
        if "accuracy" in model_resp and (
            (model_resp["accuracy"] is True)
            or (
                isinstance(model_resp["accuracy"], str)
                and model_resp["accuracy"].lower() == "true"
            )
        ):
            answer = 1
        else:
            raise ValueError(f"Could not parse answer from response: {model_resp}")

        return answer
    except:
        return -1
    
def evaluate_predictions(queries, ground_truths, predictions, evaluation_model):
    n_miss, n_correct, n_correct_exact = 0, 0, 0
    system_message = INSTRUCTIONS + IN_CONTEXT_EXAMPLES
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_message), ("user", "Question: {query}\n Ground truth: {ground_truth}\n Prediction: {prediction}\n")]
    )
    output_parser = StrOutputParser()
    chain = prompt_template | evaluation_model | output_parser

    messages = []

    for _idx, prediction in enumerate(tqdm(
        predictions, total=len(predictions), desc="Evaluating Predictions"
    )):
        query = queries[_idx]
        ground_truth = ground_truths[_idx].strip()
        prediction = prediction.strip()
        
        ground_truth_lowercase = ground_truth.lower()
        prediction_lowercase = prediction.lower()
        
        if "i don't know" in prediction_lowercase:
            n_miss += 1
            continue
        elif prediction_lowercase == ground_truth_lowercase:
            n_correct_exact += 1
            n_correct += 1
            continue

        messages.append({"query": query, "ground_truth": ground_truth, "prediction": prediction})

    for i in tqdm(range(0, len(messages), BATCH_SIZE)):
        batch = messages[i:i + BATCH_SIZE]
        responses = chain.batch(batch)
        for response in responses:
            eval_res = parse_response(response)
            if eval_res == 1:
                n_correct += 1

    n = len(predictions)
    results = {
        "score": (2 * n_correct + n_miss) / n - 1,
        "exact_accuracy": n_correct_exact / n,
        "accuracy": n_correct / n,
        "hallucination": (n - n_correct - n_miss) / n,
        "missing": n_miss / n,
        "n_miss": n_miss,
        "n_correct": n_correct,
        "n_correct_exact": n_correct_exact,
        "total": n,
    }
    logger.info(results)
    return results

if __name__ == "__main__":
    # Load the model
    api_key = "<your-api-key>"
    base_url = "<your-api-base>"
    evaluation_model = load_model(model_name="gpt-4-turbo", api_key=api_key, base_url=base_url, temperature=0)

    # Evaluate the predictions
    model_name = "Llama3-70B"
    predictions_path = f"results/{model_name}_predictions.jsonl"
    with open(predictions_path, "r") as file:
        predictions = [json.loads(line) for line in file]

    queries = [item["query"] for item in predictions]
    ground_truths = [item["ground_truth"] for item in predictions]
    predictions = [item["prediction"] for item in predictions]

    evaluate_predictions(queries, ground_truths, predictions, evaluation_model)
