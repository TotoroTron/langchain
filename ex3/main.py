
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, PromptTemplate
from pydantic import BaseModel, Field

# https://github.com/mistralai/cookbook/blob/main/third_party/langchain/langgraph_code_assistant_mistral.ipynb

llm = ChatOpenAI(temperature=0.0, model="gpt-4o")


# Data model (llm structured output, ensures json output with this format)
class code(BaseModel):
    """Schema for code solutions to questions about LCEL."""
    prefix: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Code block not including import statements")

code_gen_chain = llm.with_structured_output(code, include_raw=False)

### GRAPH

from typing import Annotated
from typing import Dict, TypedDict, List
from langgraph.graph.message import add_messages
from langchain_core.messages.utils import AnyMessage
    
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        error : Binary flag for control flow to indicate whether test error was tripped
        messages : With user question, error messages, reasoning
        generation : Code solution
        iterations : Number of tries
    """

    error: str
    messages: Annotated[list[AnyMessage], add_messages]
    generation: str
    iterations: int



from operator import itemgetter
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate

# Parameters
max_iterations = 3

# Nodes
def generate(state: GraphState):
    """
    Generate a code solution

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation
    """

    print("--- GENERATING CODE SOLUTION ---")

    # State
    messages = state["messages"]
    iterations = state["iterations"]
    error = state.get("error", "")

    # Solution
    code_solution = code_gen_chain.invoke(messages)
    messages += [
        (
            "assistant",
            f"""
            Here is my attempt to solve the problem: {code_solution.prefix} \n
            Imports: {code_solution.imports} \n
            Code: {code_solution.code} \n
            """
        )
    ]

    # Increment
    iterations = iterations + 1
    return {
        "generation": code_solution, 
        "messages": messages, 
        "iterations": iterations
    }


def code_check(state: GraphState):
    """
    Check code

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, error
    """

    print("--- CHECKING CODE ---")

    # State 
    messages = state["messages"]
    code_solution = state["generation"]
    iterations = state["iterations"]

    # Get solution components
    prefix = code_solution.prefix
    imports = code_solution.imports
    code = code_solution.code

    # Check imports
    try:
        exec(imports)
    except Exception as e:
        print("--- CODE IMPORT CHECK: FAILED ---")
        error_message = [
            (
                "user", 
                f"""
                Your solution failed the import test with the error: {e}
                Reflect on this error and your prior attempt to solve the problem. 
                (1) State what you think went wrong with the prior solution and 
                (2) try to solve this problem again. 
                Return the full solution. 
                Use the code tool to structure the output with a prefix, imports, and code block:"
                """
            )
        ]
        messages += error_message
        return {
            "generation" : code_solution,
            "messages" : messages,
            "iterations" : iterations,
            "error" : "yes"
        }

    # Check execution
    try:
        combined_code = f"{imports}\n{code}"
        # Use a shared scope for exec
        global_scope = {}
        exec(combined_code, global_scope)
    except Exception as e:
        print("--- CODE BLOCK CHECK: FAILED ---")
        error_message = [
            (
                "user",
                f"""
                Your solution failed the code execution test with the error: {e}
                Reflect on this error and your prior attempt to solve the problem. 
                (1) State what you think went wrong with the prior solution and 
                (2) try to solve this problem again. 
                Return the full solution. 
                Use the code tool to structure the output with a prefix, imports, and code block:"
                """
            )
        ]
        messages += error_message
        return {
            "generation" : code_solution,
            "messages" : messages,
            "iterations" : iterations,
            "error" : "yes"
        }

    # No errors
    print("--- NO CODE TEST FAILURES ---")
    return {
        "generation" : code_solution,
        "messages" : messages,
        "iterations" : iterations,
        "error" : "no"
    }


# Conditional edges
def decide_to_finish(state: GraphState):
    """
    Determines whether to finish.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """
    error = state["error"]
    iterations = state["iterations"]

    if error == "no" or iterations == max_iterations:
        print("--- DECISION: FINISH ---")
        return "end"
    else:
        print("--- DECISION: RE-TRY SOLUTION ---")
        return "generate"




from langgraph.graph import END, StateGraph

# Define the graph
builder = StateGraph(GraphState)

# Define the nodes
builder.add_node("generate", generate)
builder.add_node("check_code", code_check)

# Build graph
builder.set_entry_point("generate")
builder.add_edge("generate", "check_code")
builder.add_conditional_edges(
    "check_code",
    decide_to_finish,
    {
        "end" : END,
        "generate" : "generate",
    }
)

graph = builder.compile()


from langchain_core.messages import HumanMessage
from pprint import pprint
import json

question = """
    You are an LLM programmer as part of a simple langgraph framework that facilitates LLM-driven auto-correcting code. 
    You will be prompted with a user defined problem and you will write a Python program to target that problem. 
    Your code will be interpreted by the Python interpreter. 
    You will be fed any error messages generated by the Python interpreter. 
    You will take these error messages and edit or rewrite your Python code accordingly. 
    This cycle will perpetuate until no error messages are reported by the interpreter. 
    For educational purposes, make obvious syntax errors in the Python code to trip an interpreter error for the first iteration of this cycle to demonstrate functionality of the langgraph model. 

    The user defined problem: 
    Write a Python program that prints the fibonacci numbers up to 250.
"""

# kick off graph traversal with an initial state
graph_events = graph.stream(
    {
        "messages" : [HumanMessage(content=question)], 
        "iterations" : 0
    }, 
    stream_mode="values"
)

last_event = None
for idx, event in enumerate(graph_events):
    f = open(f"sandbox/event_{idx}.py", "w", encoding="utf-8")
    if "generation" in event:
        code_solution = event["generation"]
        f.write(code_solution.code)
    print(f"\n EVENT: {idx}\n")
    print(str(event).replace("\\n", "\n"))
    last_event = event
    f.close()

f = open("sandbox/final_code.py", "w", encoding="utf-8")
if last_event and "generation" in last_event:
    code_solution = last_event["generation"]
    f.write(code_solution.code)
f.close()




