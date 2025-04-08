from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, PromptTemplate

# greedy
llm = ChatOpenAI(temperature=0.0, model="gpt-4o")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI coder that writes Python solutions to user defined problems."),
    ("user", "{input}")
])

output_parser = StrOutputParser()

chain = prompt | llm | output_parser

input = """
    Write a Python program that prints the fibonacci numbers up to 250. 
    Your entire response must comply with Python syntax as it will be written directly into a new .py file to be compiled by the Python interpreter. 
    Use double quote symbols (") for comment blocks. 
    Do not use wrap your code in ```python ```. Assume your entire response is Python code. 
"""

f = open("sandbox/main.py", "w")
f.write(chain.invoke(
    {"input" : input}
))
f.close()

