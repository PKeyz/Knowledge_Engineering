# What is RAG?

Retrieval Augmented Generation, is extended LLM data storage via vector-processed information chunks from relevant sources.

This allows the LLM to hallucinate less, deliver sources when answering user prompts and keep responses current and relevant,
since the vector DB can be updated as often as necessary to provide the most useful data.

When responding to a user prompt, the LLM first finds the top-k relevant sources from the vectorDB, which are evaluated by the model
to generate the most useful/fitting answer.

# Why RAG is better, than LLM alone? 

A LLM alone, is reduced to what data-set it was trained on, this may, or may not be relevant to the questions asked.
A foundation model (general LLM) will not have any specific knowledge to work in a niche environment like medical or law.
The model can be expanded via RAG vectorDB information, to expand the knowledge available to it, to be able to respond to 
more specific queries without needing to train a new model.
