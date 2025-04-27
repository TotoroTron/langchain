import os


from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages.utils import AnyMessage
from langchain_core.messages import HumanMessage 
from langgraph.graph.message import add_messages
from langgraph.graph import END, StateGraph

from pydantic import BaseModel, Field

from typing import Annotated
from typing import TypedDict


class test_model(BaseModel):
    problem: str = Field(description="User defined problem.")
    testcase: str = Field(description="Unit test case derived from user defined problem.")

class solution_model(BaseModel):
    problem: str = Field(description="User defined problem.")
    solution: str = Field(description="LLM generated solution to the user defined problem.")



llm = ChatOpenAI(model="gpt-4o")
llm_testcase_model = llm.with_structured_output(test_model, include_raw=False)
llm_solution_model = llm.with_structured_output(solution_model, include_raw=False)
max_attempts = 5


class GraphState(TypedDict):
    attempts : int
    messages : Annotated[list[AnyMessage], add_messages]
    testcase : str
    solution : str
    error : str


def write_testcase(state: GraphState):
    attempts = state["attempts"]
    messages = state["messages"]
    print(f"--- ATTEMPT : {attempts} : write_testcase() ---")
    messages += [
        (
            "system",
            f"""
            Design cycle: {attempts}
            First, write a unittest TestCase that will be used to verify your solution to the user defined problem. 
            Your entire response will be interpreted as Python code. 
            Adhere to Python syntax and use comment blocks for comments. 
            Do not work on the solution yet. 
            """
        )
    ]
    llm_testcase = llm_testcase_model.invoke(messages)
    messages += [
        (
            "assistant",
            f"""
            Design cycle: {attempts}
            User defined problem: {llm_testcase.problem}
            LLM testcase: {llm_testcase.testcase}
            """
        )
    ]
    f = open("test/test.py", "w")
    f.write(llm_testcase.testcase)
    f.close()
    return {
        "attempts": attempts,
        "messages": messages,
        "testcase": llm_testcase 
    }

def attempt_solution(state: GraphState):
    attempts = state["attempts"]
    messages = state["messages"]
    attempts = attempts + 1
    print(f"--- ATTEMPT : {attempts} : attempt_solution() ---")
    llm_solution = llm_solution_model.invoke(messages)
    os.mkdir(f"src/attempt_{attempts:02d}")
    f = open(f"src/attempt_{attempts:02d}/solution.py", "w")
    f.write(llm_solution.solution)
    f.close()
    messages += [
        (
            "assistant",
            f"""
            Design cycle: {attempts}
            User defined problem: {llm_solution.problem}
            LLM solution: {llm_solution.solution}
            """
        )
    ]
    return {
        "attempts": attempts,
        "messages": messages,
        "solution": llm_solution
    }


def run_test(state: GraphState):
    attempts = state["attempts"]
    messages = state["messages"]
    llm_solution = state["solution"]
    llm_testcase = state["testcase"]
    print(f"--- ATTEMPT : {attempts} : run_test() ---")

    problem_description = llm_solution.problem
    python_solution = llm_solution.solution
    python_testcase = llm_testcase.testcase

    python_combined = python_solution + "\n" + python_testcase

    try:
        exec(python_combined)
    except Exception as e:
        f = open(f"src/attempt_{attempts:02d}/error.txt", "w")
        f.write(str(e))
        f.close()
        error_message = [
            (
                "system",
                f"""
                Design cycle: {attempts}
                Your solution failed execution with the error: {e}
                With this new information, retry your solution in the next design cycle attempt. 
                Your entire response will be interpreted as Python code. 
                Adhere to Python syntax and use comment blocks for explanations. 
                """
            )
        ]
        messages += error_message
        return {
            "attempts" : attempts,
            "messages" : messages,
            "error" : "yes"
        }

    return {
        "attempts" : attempts,
        "messages" : messages,
        "error" : "no"
    }

def decide_next_node(state: GraphState):
    error_state = state["error"]
    attempts = state["attempts"]

    if error_state == "no" or attempts == max_attempts:
        print("--- DECISION: MAX-ATTEMPTS REACHED. TERMINATING.---")
        return "end"
    elif error_state == "yes":
        print("--- DECISION: RE-TRY SOLUTION ---")
        return "attempt_solution"



builder = StateGraph(GraphState)

builder.add_node("write_testcase", write_testcase)
builder.add_node("attempt_solution", attempt_solution)
builder.add_node("run_test", run_test)

builder.set_entry_point("write_testcase")
builder.add_edge("write_testcase", "attempt_solution")
builder.add_edge("attempt_solution", "run_test")
builder.add_conditional_edges(
    "run_test",
    decide_next_node,
    {
        "end" : END,
        "attempt_solution" : "attempt_solution"
    }
)

graph = builder.compile()

f1 = open("user_problem.txt", "r")
f2 = open("packages.txt", "r")
user_problem = f1.read()
conda_packages = f2.read()
f1.close()
f2.close()

# initial_prompt = "Conda environment: \n\n" + conda_packages + "User defined problem: \n\n" + user_problem

initial_prompt = user_problem

print(initial_prompt)

initial_state = {
  "attempts": 0,
  "messages": [HumanMessage(content=initial_prompt)],
  "testcase": "",
  "solution": "",
  "error": "yes"
}

# start the traversal
for event in graph.stream(initial_state, stream_mode="values"):
    print(event)












