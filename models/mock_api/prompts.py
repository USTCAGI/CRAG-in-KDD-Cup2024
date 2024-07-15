NER_MOVIE_PROMPT_TEMPLATE = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

please identify and list all the named entities present in the following question about movie instead answering it, categorizing them appropriately (e.g., person, movie) Your answer should be short and concise in 50 words.
Format your response as follows: For each entity, provide the name followed by its category in parentheses. Categories include persons, and movies. Ensure that your response is clearly structured and easy to read.<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: "{query}"

Output only the named entities present in the question. Do not include any other information. If there are no named entities in the question, please provide an empty response.
Expected Output Format:
a name of a company in the sentence  (person)
a name of a movie in the sentence  (movie)
every entity should be in a new line and be in the format of "entity_name (entity_category)"

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

NER_FINANCE_PROMPT_TEMPLATE = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Please identify and list all the named entities present in the following question about finance instead answering it, categorizing them appropriately (e.g., company, ticker symbol) Your answer should be short and concise in 50 words.
Format your response as follows: For each entity, provide the name followed by its category in parentheses. Categories include company, and symbol(which means the ticker symbol of a company). Ensure that your response is clearly structured and easy to read.<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: "{query}"

Output only the named entities present in the question. Do not include any other information. If there are no named entities in the question, please provide an empty response.
Expected Output Format:
a name of a company in the sentence  (company)
a name of a ticker symbol in the sentence  (symbol)
every entity should be in a new line and be in the format of "entity_name (entity_category)"

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

NER_MUSIC_PROMPT_TEMPLATE = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

please identify and list all the named entities present in the following question about music instead answering it, categorizing them appropriately (e.g., persons, song, band) Your answer should be short and concise in 50 words.
Format your response as follows: For each entity, provide the name followed by its category in parentheses. Categories include persons, songs and bands. Ensure that your response is clearly structured and easy to read.<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: "{query}"

Output only the named entities present in the question. Do not include any other information. If there are no named entities in the question, please provide an empty response.
Expected Output Format:
a name of a person in the sentence  (person)
a name of a song in the sentence  (song)
a name of a band in the sentence  (band)
every entity should be in a new line and be in the format of "entity_name (entity_category)"

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

NER_SPORTS_PROMPT_TEMPLATE = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

please identify and list all the named entities present in the following question about sports instead answering it, categorizing them appropriately (e.g., nba team, soccer team, nba player, soccer player) Your answer should be short and concise in 50 words.
Format your response as follows: For each entity, provide the name followed by its category in parentheses. Categories include nba team, soccer team, nba player, soccer player. Ensure that your response is clearly structured and easy to read.<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: "{query}"

Output only the named entities present in the question. Do not include any other information. If there are no named entities in the question, please provide an empty response.
Expected Output Format:
a name of a nba team in the sentence  (nba team)
a name of a soccer team in the sentence  (soccer team)
a name of a nba player in the sentence  (nba player)
a name of a soccer player in the sentence  (soccer player)
every entity should be in a new line and be in the format of "entity_name (entity_category)"

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

NER_OPEN_SYSTEM_PROMPT = """please identify and list all the named entities present in the following question instead answering it, categorizing them appropriately (e.g., person, location, orgnization, product, event and so on)Your answer should be short and concise in 50 words.
Format your response as follows: For each entity, provide the name followed by its category in parentheses.  Categories include person, location, orgnization, product, event and so on. Ensure that your response is clearly structured and easy to read."""

NER_MOVIE_SYSTEM_PROMPT = """please identify and list all the named entities present in the following question about movie instead answering it, categorizing them appropriately (e.g., person, movie) Your answer should be short and concise in 50 words.
Format your response as follows: For each entity, provide the name followed by its category in parentheses. Categories include persons, and movies. Ensure that your response is clearly structured and easy to read."""

NER_FINANCE_SYSTEM_PROMPT = """Please identify and list all the named entities present in the following question about finance instead answering it, categorizing them appropriately (e.g., company, ticker symbol) Your answer should be short and concise in 50 words.
Format your response as follows: For each entity, provide the name followed by its category in parentheses. Categories include company, and symbol(which means the ticker symbol of a company). Ensure that your response is clearly structured and easy to read."""

NER_MUSIC_SYSTEM_PROMPT = """please identify and list all the named entities present in the following question about music instead answering it, categorizing them appropriately (e.g., persons, song, band) Your answer should be short and concise in 50 words.
Format your response as follows: For each entity, provide the name followed by its category in parentheses. Categories include persons, songs and bands. Ensure that your response is clearly structured and easy to read."""

NER_SPORTS_SYSTEM_PROMPT = """please identify and list all the named entities present in the following question about sports instead answering it, categorizing them appropriately (e.g., nba team, soccer team, nba player, soccer player) Your answer should be short and concise in 50 words.
Format your response as follows: For each entity, provide the name followed by its category in parentheses. Categories include nba team, soccer team, nba player, soccer player. Ensure that your response is clearly structured and easy to read."""

NER_OPEN_USER_PROMPT = """Question: "{query}"

Output only the named entities present in the question. Do not include any other information. If there are no named entities in the question, please provide an empty response.
Expected Output Format:
a name of a person in the sentence  (person)
a name of a location in the sentence  (location)
a name of an organization in the sentence  (organization)
a name of a product in the sentence  (product)
a name of an event in the sentence  (event)
every entity should be in a new line and be in the format of "entity_name (entity_category)"""

NER_MOVIE_USER_PROMPT = """Question: "{query}"

Output only the named entities present in the question. Do not include any other information. If there are no named entities in the question, please provide an empty response.
Expected Output Format:
a name of a company in the sentence  (person)
a name of a movie in the sentence  (movie)
every entity should be in a new line and be in the format of "entity_name (entity_category)"""

NER_FINANCE_USER_PROMPT = """Question: "{query}"

Output only the named entities present in the question. Do not include any other information. If there are no named entities in the question, please provide an empty response.
Expected Output Format:
a name of a company in the sentence  (company)
a name of a ticker symbol in the sentence  (symbol)
every entity should be in a new line and be in the format of "entity_name (entity_category)"""

NER_MUSIC_USER_PROMPT = """Question: "{query}"

Output only the named entities present in the question. Do not include any other information. If there are no named entities in the question, please provide an empty response.
Expected Output Format:
a name of a person in the sentence  (person)
a name of a song in the sentence  (song)
a name of a band in the sentence  (band)
every entity should be in a new line and be in the format of "entity_name (entity_category)"""

NER_SPORTS_USER_PROMPT = """Question: "{query}"

Output only the named entities present in the question. Do not include any other information. If there are no named entities in the question, please provide an empty response.
Expected Output Format:
a name of a nba team in the sentence  (nba team)
a name of a soccer team in the sentence  (soccer team)
a name of a nba player in the sentence  (nba player)
a name of a soccer player in the sentence  (soccer player)
every entity should be in a new line and be in the format of "entity_name (entity_category)"""

