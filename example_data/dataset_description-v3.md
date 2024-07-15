# CRAG Dataset Documentation

## Dataset Version Information

- **DATASET_DESCRIPTION_VERSION**: `v3`
- **DATASET_VERSION**: `v3`

## Overview

The CRAG dataset is designed to support the development and evaluation of Retrieval-Augmented Generation (RAG) models. It consists of two main types of data:

1. **Question Answering Pairs:** Pairs of questions and their corresponding answers.
2. **Retrieval Contents:** Contents for information retrieval to support answer generation.

Retrieval contents are divided into two types to simulate practical scenarios for RAG:

1. **Web Search Results:** For each question, up to `50` **full HTML pages** are stored, retrieved using the question text as a search query. For Task 1, `5 pages` are **randomly selected** from the `top-10 pages`. These pages are likely relevant to the question, but relevance is not guaranteed.
2. **Mock KGs and APIs:** The Mock API is designed to mimic real-world **Knowledge Graphs (KGs)** or **API searches**. Given some input parameters, they output relevant results, which may or may not be helpful in answering the user's question.

## Download CRAG Data

- **Task #1:** [Retreival Summarization Task Page](https://www.aicrowd.com/challenges/meta-comprehensive-rag-benchmark-kdd-cup-2024/problems/retrieval-summarization/dataset_files)
- **Task #2:** [Mock API Repository](https://gitlab.aicrowd.com/aicrowd/challenges/meta-comprehensive-rag-benchmark-kdd-cup-2024/crag-mock-api)
- **Task #3:** [End to End Retreival Augmentation Task Page](https://www.aicrowd.com/challenges/meta-comprehensive-rag-benchmark-kdd-cup-2024/problems/end-to-end-retrieval-augmented-generation)

## Data Schema

| Field Name             | Type          | Description                                                                                                                                                           |
|------------------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `interaction_id`       | string        | A unique identifier for each example.                                                                                                                                |
| `query_time`           | string        | Date and time when the query and the web search occurred.                                                                                                            |
| `domain`               | string        | Domain label for the query. Possible values: "finance", "music", "movie", "sports", "open". "Open" includes any factual queries not among the previous four domains. |
| `question_type`        | string        | Type label about the query. Possible values include: "simple", "simple_w_condition", "comparison", "aggregation", "set", "false_premise", "post-processing", "multi-hop".      |
| `static_or_dynamic`    | string        | Indicates whether the answer to a question changes and the expected rate of change. Possible values: "static", "slow-changing", "fast-changing", and "real-time".    |
| `query`                | string        | The question for RAG to answer.                                                                                                                                       |
| `answer`               | string        | The gold standard answer to the question.                                                                                                                             |
| `alt_ans`  | list        | Other valid gold standard answers to the question.                                                                                                                    |
| `split`                | integer       | Data split indicator, where 0 is for validation and 1 is for the public test.                                                                                         |
| `search_results`       | list of JSON  | Contains up to `k` HTML pages for each query (`k=5` for Task #1 and `k=50` for Task #3), including page name, URL, snippet, full HTML, and last modified time.         |

### Search Results Detail

| Key                  | Type   | Description                                             |
|----------------------|--------|---------------------------------------------------------|
| `page_name`          | string | The name of the webpage.                                |
| `page_url`           | string | The URL of the webpage.                                 |
| `page_snippet`       | string | A short paragraph describing the major content of the page. |
| `page_result`        | string | The full HTML of the webpage.                           |
| `page_last_modified` | string | The time when the page was last modified.               |

