#!/usr/bin/env python3

INSTRUCTIONS = """
# Task: 
You are given a Question, a model Prediction, and a list of Ground Truth answers, judge whether the model Prediction matches any answer from the list of Ground Truth answers. Follow the instructions step by step to make a judgement. 
1. If the model prediction matches any provided answers from the Ground Truth Answer list, "Accuracy" should be "True"; otherwise, "Accuracy" should be "False".
2. If the model prediction says that it couldn't answer the question or it doesn't have enough information, "Accuracy" should always be "False".
3. If the Ground Truth is "invalid question", "Accuracy" is "True" only if the model prediction is exactly "invalid question".
# Output: 
Respond with only a single JSON string with an "Accuracy" field which is "True" or "False".
"""

IN_CONTEXT_EXAMPLES = """
# Examples:
Question: how many seconds is 3 minutes 15 seconds?
Ground truth: ["195 seconds"]
Prediction: 3 minutes 15 seconds is 195 seconds.
Accuracy: True

Question: Who authored The Taming of the Shrew (published in 2002)?
Ground truth: ["William Shakespeare", "Roma Gill"]
Prediction: The author to The Taming of the Shrew is Roma Shakespeare.
Accuracy: False

Question: Who played Sheldon in Big Bang Theory?
Ground truth: ["Jim Parsons", "Iain Armitage"]
Prediction: I am sorry I don't know.
Accuracy: False
"""

COT_PROMPT = """For the given question and multiple references from web pages, think step by step, then provide the final answer.
Current date: {query_time}

Note: 
- For your final answer, please use as few words as possible. 
- The user's question may contain factual errors, in which case you MUST reply `invalid question`
- If you don't know the answer, you MUST respond with `I don't know`
- Your output format needs to meet the requirements: First, start with `## Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `## Final Answer\n` and using as few words as possible.

### Question
{query}

### References
{references}
"""

FEWSHOT_COT_MOVIE_KG = """For the given question and multiple references from Mock API and Web Pages, think step by step, then provide the final answer.
Current date: {query_time}

Note: 
- For your final answer, please use as few words as possible. 
- The user's question may contain factual errors, in which case you MUST reply `invalid question`. Here are some examples of invalid questions:
    - `when was "soul" released on hulu?` (The movie "Soul" was not released on Hulu. Instead, it was released on Disney+.)
    - `what year did the simpsons stop airing?` ("The Simpsons" is an ongoing series that has been continuously airing new episodes for over three decades.)
- If you don't know the answer, you MUST respond with `I don't know`
- If the references do not contain the necessary information to answer the question, respond with `I don't know`
- Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`
- Your output format needs to meet the requirements: First, start with `## Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `## Final Answer\n` and using as few words as possible.

### Question
{query}

### References
{references}
"""

FEWSHOT_COT_MUSIC_KG = """For the given question and multiple references from Mock API and Web Pages, think step by step, then provide the final answer.
Current date: {query_time}

Note: 
- For your final answer, please use as few words as possible. 
- The user's question may contain factual errors, in which case you MUST reply `invalid question`. Here are some examples of invalid questions:
    - `how long was phil rudd the drummer for the band van halen?` (Phil Rudd was the drummer for AC/DC, and Alex Van Halen has been the primary drummer for Van Halen.)
    - `what was the name of justin bieber's album last year?` (Justin Bieber did not release an album last year.)
- If you don't know the answer, you MUST respond with `I don't know`
- If the references do not contain the necessary information to answer the question, respond with `I don't know`
- Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`
- Your output format needs to meet the requirements: First, start with `## Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `## Final Answer\n` and using as few words as possible.

### Question
{query}

### References
{references}
"""

FEWSHOT_COT_SPORTS_KG = """For the given question and multiple references from Mock API, think step by step, then provide the final answer.
Current date: {query_time}

Note: 
- For your final answer, please use as few words as possible. 
- The user's question may contain factual errors, in which case you MUST reply `invalid question`. Here are some examples of invalid questions:
    - `what's the latest score update for OKC's game today?` (There is no game for OKC today)
    - `how many times has curry won the nba dunk contest?` (Steph Curry has never participated in the NBA dunk contest)
- If you don't know the answer, you MUST respond with `I don't know`
- If the references do not contain the necessary information to answer the question, respond with `I don't know`
- Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`
- Your output format needs to meet the requirements: First, start with `## Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `## Final Answer\n` and using as few words as possible.

### Question
{query}

### References
{references}
"""

FEWSHOT_COT_FINANCE_KG = """For the given question and multiple references from Mock API, think step by step, then provide the final answer.
Current date: {query_time}

Note: 
- For your final answer, please use as few words as possible. 
- The user's question may contain factual errors, in which case you MUST reply `invalid question`. Here are some examples of invalid questions:
    - `what is the price of bitcoin when it launch in 2015?` (Bitcoin was launched in 2009.)
    - `which country has adopted ethereum as legal tender?` (In reality, no country has done so.)
- If you don't know the answer, you MUST respond with `I don't know`
- If the references do not contain the necessary information to answer the question, respond with `I don't know`
- Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`
- Your output format needs to meet the requirements: First, start with `## Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `## Final Answer\n` and using as few words as possible.

### Question
{query}

### References
{references}
"""

FEWSHOT_COT_MOVIE = """For the given question and multiple references from Web Pages, think step by step, then provide the final answer.
Current date: {query_time}

Note: 
- For your final answer, please use as few words as possible. 
- The user's question may contain factual errors, in which case you MUST reply `invalid question`. Here are some examples of invalid questions:
    - `when was "soul" released on hulu?` (The movie "Soul" was not released on Hulu. Instead, it was released on Disney+.)
    - `what year did the simpsons stop airing?` ("The Simpsons" is an ongoing series that has been continuously airing new episodes for over three decades.)
- If you don't know the answer, you MUST respond with `I don't know`
- If the references do not contain the necessary information to answer the question, respond with `I don't know`
- Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`
- Your output format needs to meet the requirements: First, start with `## Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `## Final Answer\n` and using as few words as possible.

### Question
{query}

### References
{references}
"""

FEWSHOT_COT_MUSIC = """For the given question and multiple references from Web Pages, think step by step, then provide the final answer.
Current date: {query_time}

Note: 
- For your final answer, please use as few words as possible. 
- The user's question may contain factual errors, in which case you MUST reply `invalid question`. Here are some examples of invalid questions:
    - `how long was phil rudd the drummer for the band van halen?` (Phil Rudd was the drummer for AC/DC, and Alex Van Halen has been the primary drummer for Van Halen.)
    - `what was the name of justin bieber's album last year?` (Justin Bieber did not release an album last year.)
- If you don't know the answer, you MUST respond with `I don't know`
- If the references do not contain the necessary information to answer the question, respond with `I don't know`
- Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`
- Your output format needs to meet the requirements: First, start with `## Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `## Final Answer\n` and using as few words as possible.

### Question
{query}

### References
{references}
"""

FEWSHOT_COT_SPORTS = """For the given question and multiple references from Web Pages, think step by step, then provide the final answer.
Current date: {query_time}

Note: 
- For your final answer, please use as few words as possible. 
- The user's question may contain factual errors, in which case you MUST reply `invalid question`. Here are some examples of invalid questions:
    - `what's the latest score update for OKC's game today?` (There is no game for OKC today)
    - `how many times has curry won the nba dunk contest?` (Steph Curry has never participated in the NBA dunk contest)
- If you don't know the answer, you MUST respond with `I don't know`
- If the references do not contain the necessary information to answer the question, respond with `I don't know`
- Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`
- Your output format needs to meet the requirements: First, start with `## Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `## Final Answer\n` and using as few words as possible.

### Question
{query}

### References
{references}
"""

FEWSHOT_COT_FINANCE = """For the given question and multiple references from Web Pages, think step by step, then provide the final answer.
Current date: {query_time}

Note: 
- For your final answer, please use as few words as possible. 
- The user's question may contain factual errors, in which case you MUST reply `invalid question`. Here are some examples of invalid questions:
    - `what is the price of bitcoin when it launch in 2015?` (Bitcoin was launched in 2009.)
    - `which country has adopted ethereum as legal tender?` (In reality, no country has done so.)
- If you don't know the answer, you MUST respond with `I don't know`
- If the references do not contain the necessary information to answer the question, respond with `I don't know`
- Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`
- Your output format needs to meet the requirements: First, start with `## Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `## Final Answer\n` and using as few words as possible.

### Question
{query}

### References
{references}
"""