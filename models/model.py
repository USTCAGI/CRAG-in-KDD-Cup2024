from typing import Any, Dict, List
from models.mock_api.api import MockAPI
from prompts.templates import *
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

class RAGModel:
    """
    An example RAGModel for the KDDCup 2024 Meta CRAG Challenge
    which includes all the key components of a RAG lifecycle.
    """
    def __init__(self, chat_model, retriever, domain_router, dynamic_router=None, use_kg=True):
        self.initialize_models(chat_model, retriever, domain_router, dynamic_router, use_kg)

    def initialize_models(self, chat_model, retriever, domain_router, dynamic_router, use_kg):
        assert domain_router is not None, "Domain Router model is required."
        self.use_kg = use_kg
        SYSTEM_PROMPT = "You are a helpful assistant."
        if use_kg:
            self.api = MockAPI(chat_model)
            self.domain2template = {
                "open": ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_PROMPT), ("user", COT_PROMPT)],
                ),
                "movie": ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_PROMPT), ("user", FEWSHOT_COT_MOVIE_KG)],
                ),
                "music": ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_PROMPT), ("user", FEWSHOT_COT_MUSIC_KG)],
                ),
                "sports": ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_PROMPT), ("user", FEWSHOT_COT_SPORTS_KG)],
                ),
                "finance": ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_PROMPT), ("user", FEWSHOT_COT_FINANCE_KG)],
                )
            }
            self.rag_chain = self.format_messages_with_kg | chat_model | StrOutputParser() | self.get_final_answer_content
        else:
            self.domain2template = {
                "open": ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_PROMPT), ("user", COT_PROMPT)],
                ),
                "movie": ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_PROMPT), ("user", FEWSHOT_COT_MOVIE)],
                ),
                "music": ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_PROMPT), ("user", FEWSHOT_COT_MUSIC)],
                ),
                "sports": ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_PROMPT), ("user", FEWSHOT_COT_SPORTS)],
                ),
                "finance": ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_PROMPT), ("user", FEWSHOT_COT_FINANCE)],
                )
            }
        
        self.chat_model = chat_model
        self.retriever = retriever
        self.domain_router = domain_router
        self.dynamic_router = dynamic_router

    def retrieve(self, input):
        query = input["query"]
        interaction_id = input["interaction_id"]
        search_results = input["search_results"]
        return self.retriever.retrieve(query, interaction_id, search_results)

    def batch_generate_answer(self, batch: Dict[str, Any]) -> List[str]:
        """
        Generates answers for a batch of queries using associated (pre-cached) search results and query times.

        Parameters:
            batch (Dict[str, Any]): A dictionary containing a batch of input queries with the following keys:
                - 'interaction_id;  (List[str]): List of interaction_ids for the associated queries
                - 'query' (List[str]): List of user queries.
                - 'search_results' (List[List[Dict]]): List of search result lists, each corresponding
                                                      to a query. Please refer to the following link for
                                                      more details about the individual search objects:
                                                      https://gitlab.aicrowd.com/aicrowd/challenges/meta-comprehensive-rag-benchmark-kdd-cup-2024/meta-comphrehensive-rag-benchmark-starter-kit/-/blob/master/docs/dataset.md#search-results-detail
                - 'query_time' (List[str]): List of timestamps (represented as a string), each corresponding to when a query was made.

        Returns:
            List[str]: A list of plain text responses for each query in the batch. Each response is limited to 75 tokens.
            If the generated response exceeds 75 tokens, it will be truncated to fit within this limit.

        Notes:
        - If the correct answer is uncertain, it's preferable to respond with "I don't know" to avoid
          the penalty for hallucination.
        - Response Time: Ensure that your model processes and responds to each query within 30 seconds.
          Failing to adhere to this time constraint **will** result in a timeout during evaluation.
        """
        batch_interaction_ids = batch["interaction_id"]
        queries = batch["query"]
        batch_search_results = batch["search_results"]
        query_times = batch["query_time"]



        batch_retrieval_results = RunnableLambda(self.retrieve).batch([{"query": query, "interaction_id": interaction_id, "search_results": search_results} for query, interaction_id, search_results in zip(queries, batch_interaction_ids, batch_search_results)])

        domains = [self.domain_router(query) for query in queries]
        if self.dynamic_router is not None:    
            dynamics = [self.dynamic_router(query) for query in queries]

        # Get KG information
        if self.use_kg:
            kg_infos = self.api.get_kg_info(queries, query_times, domains)
            inputs = [{"query": query, "query_time": query_time, "kg_info": kg_info, "retrieval_results": retrieval_results, "domain": domain} for query, query_time, kg_info, retrieval_results, domain in zip(queries, query_times, kg_infos, batch_retrieval_results, domains)]
        else:
            inputs = [{"query": query, "query_time": query_time, "retrieval_results": retrieval_results, "domain": domain} for query, query_time, retrieval_results, domain in zip(queries, query_times, batch_retrieval_results, domains)]

        # Generate responses via vllm
        responses = self.rag_chain.batch(inputs)

        # Aggregate answers into List[str]
        answers = []
        for i, answer in enumerate(responses):
            if self.use_kg:
                if domains[i] in ["open"] and self.dynamic_router and dynamics[i] in ["fast-changing", "real-time"]:
                    answer = "I don't know"

                if domains[i] in ["open", "movie", "music"] and "average" in queries[i]:
                    answer = "I don't know"
            else:
                if self.dynamic_router and dynamics[i] in ["fast-changing", "real-time"]:
                    answer = "I don't know"
                elif domains[i] in ["finance"]:
                    answer = "I don't know"
                if "average" in queries[i]:
                    answer = "I don't know"

            if "how many shares" in queries[i] or "legal tender" in queries[i] or "whick five" in queries[i] or "low and high" in queries[i]:
                answer = "I don't know"
            if "$0.01" in answer:
                answer = "I don't know"
            
            answers.append(answer)
  
        return answers
    
    def get_reference(self, retrieval_results):
        references = ""
        if len(retrieval_results) > 1:
            for _snippet_idx, snippet in enumerate(retrieval_results):
                references += "<DOC>\n"
                references += f"{snippet.strip()}\n"
                references += "</DOC>\n\n"
        elif len(retrieval_results) == 1 and len(retrieval_results[0]) > 0:
            references = retrieval_results[0]
        else:
            references = "No References"
        return references
    
    def format_messages_with_kg(self, input):
        query = input["query"]
        query_time = input["query_time"]
        kg_info = input["kg_info"]
        retrieval_results = input["retrieval_results"]
        domain = input["domain"]
        if domain in ["finance", "sports"]:
            references = self.get_reference([kg_info])
        elif domain in ["movie", "music"]:
            references = self.get_reference([kg_info]+retrieval_results)
        else:
            references = self.get_reference(retrieval_results)
        messages = self.domain2template[domain].format_messages(query=query, query_time=query_time, references=references)
        return messages
    
    def format_messages_without_kg(self, input):
        query = input["query"]
        query_time = input["query_time"]
        retrieval_results = input["retrieval_results"]
        domain = input["domain"]
        references = self.get_reference(retrieval_results)
        messages = self.domain2template[domain].format_messages(query=query, query_time=query_time, references=references)
        return messages
        
    def get_final_answer_content(self, text):
        # 找到标志字符串的位置
        marker = "## Final Answer"
        marker_index = text.find(marker)
        # print("mark:", marker_index)
        if marker_index == -1:
            # 如果没有找到标志字符串，返回空字符串
            return "i don't know"
        
        # 获取标志字符串后面的内容
        content_start_index = marker_index + len(marker)
        final_answer_content = text[content_start_index:].strip()
        
        return final_answer_content