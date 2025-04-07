from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI()

language = "Spanish"
text = "Hello, world!"



system_template = f"Translate the following from English into {language}"
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", text)]
)

prompt = prompt_template.invoke({"language": language, "text": text})

prompt.to_messages()

response = llm.invoke(prompt)
print(response)
print(response.content)

f = open("response.txt", "w")
f.write(str(response.content))

