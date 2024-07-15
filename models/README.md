# Guide to Writing Your Own Models

## Model Code Organization
For a streamlined experience, we suggest placing the code for all your models within the `models` directory. This is a recommendation for organizational purposes, but it's not a strict requirement.

## Model Base Class
Your models should follow the format from the `DummyModel` class found in [dummy_model.py](dummy_model.py). We provide the example model, `dummy_model.py`, to illustrate the structure your own model. Crucially, your model class must implement the `batch_generate_answer` method.

## Selecting which model to use
To ensure your model is recognized and utilized correctly, please specify your model class name in the [`user_config.py`](user_config.py) file, by following the instructions in the inline comments.

## Model Inputs and Outputs

### Inputs
Your model will receive a batch of input queries as a dictionary, where the dictionary has the following keys:

```
    - 'query' (List[str]): List of user queries.
    - 'search_results' (List[List[Dict]]): List of search result lists, each corresponding 
                                            to a query. Please refer to the following link for 
                                            more details about the individual search objects:
                                            https://gitlab.aicrowd.com/aicrowd/challenges/meta-comprehensive-rag-benchmark-kdd-cup-2024/meta-comphrehensive-rag-benchmark-starter-kit/-/blob/master/docs/dataset.md#search-results-detail
    - 'query_time' (List[str]): List of timestamps (represented as a string), each corresponding to when a query was made.
```

### Outputs
The output from your model's `batch_generate_answer` function should be a list of string responses for all the queries in the input batch.

## Internet Access
Your model will not have access to the internet during evaluation. 