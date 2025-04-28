import os
import sys
import io
import unittest
import subprocess


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
max_attempts = 4 


class GraphState(TypedDict):
    attempts : int
    messages : Annotated[list[AnyMessage], add_messages]
    testcase : str
    solution : str
    error : str


def write_testcase(state: GraphState):
    attempts = state["attempts"]
    messages = state["messages"]
    print(f"\n\n--- ATTEMPT : {attempts} : write_testcase() ---\n\n")
    f2 = open("packages.txt", "r")
    conda_packages = f2.read()
    test_prompt = messages + [
        (
            "system",
            f"""
            Design cycle: {attempts}
            First, write a unittest TestCase that will be used to verify your solution to the user defined problem. 
            The testcase must call the solution function. 
            The testcase must contain the main function. 
            Your entire response will be interpreted as Python code. 
            Adhere to Python syntax and use comment blocks for comments. 
            Do not work on the solution yet. 
            Do not import any external libraries. 

            At the top of the file, add:
                from solution import evaluate

            And make sure every `evaluate(...)` call is syntactically complete (no trailing commas).

            """
        )
    ]


    llm_testcase = llm_testcase_model.invoke(test_prompt)
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
    print(f"\n\n--- ATTEMPT : {attempts} : attempt_solution() ---\n\n")
    messages += [
    (
        "system",
        f"""
        Design cycle: {attempts}
        Now implement a Python solution that passes the test case below.
        Respond _only_ with valid Python code, and comment blocks for explanations.
        """
    )
    ]
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
    attempts     = state["attempts"]
    messages     = state["messages"]
    llm_solution = state["solution"]
    llm_testcase = state["testcase"]
    print(f"\n\n--- ATTEMPT : {attempts} : run_test() ---\n\n")

    # rewrite solution & test files
    sol_dir = f"src/attempt_{attempts:02d}"
    os.makedirs(sol_dir, exist_ok=True)
    sol_path = os.path.join(sol_dir, "solution.py")
    tc_path  = "test/test.py"

    with open(sol_path, "w") as f:
        f.write(llm_solution.solution)
    with open(tc_path, "w") as f:
        f.write(llm_testcase.testcase)

    # ensure Python can import our solution from the test folder
    env = os.environ.copy()
    env["PYTHONPATH"] = sol_dir + os.pathsep + env.get("PYTHONPATH", "")

    # invoke the standard unittest discovery
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "test", "-p", "test.py"],
        capture_output=True,
        text=True,
        env=env
    )
    output = proc.stdout + proc.stderr

    # save the raw output for inspection
    with open(os.path.join(sol_dir, "test_output.txt"), "w") as out:
        out.write(output)

    if proc.returncode == 0:
        # all tests passed
        return {
            "attempts":  attempts,
            "messages":  messages,
            "testcase":  llm_testcase,
            "solution":  llm_solution,
            "error":     "no"
        }
    else:
        # tests failed—feed the failure log back to the LLM
        fail_msg = (
            "system",
            f"""
            Design cycle: {attempts}
            Your solution failed the unit tests (exit code {proc.returncode}).  
            Here is the full test output:

            ```
            {output}
            ```
            Please fix your solution and respond _only_ with updated Python code.
            """
        )
        messages += [fail_msg]
        return {
            "attempts":  attempts,
            "messages":  messages,
            "testcase":  llm_testcase,
            "solution":  llm_solution,
            "error":     "yes"
        }

def decide_next_node(state: GraphState):
    error_state = state["error"]
    attempts = state["attempts"]

    if error_state == "no" or attempts == max_attempts:
        if attempts == max_attempts:
            print("\n\n--- DECISION: MAX-ATTEMPTS REACHED. TERMINATING.---\n\n")
        else:
            print("\n\n--- DECISION: NO ERRORS. TERMINATING.---\n\n")
        return "end"
    elif error_state == "yes":
        print("\n\n--- DECISION: ERRORS PRESENT. RE-TRYING SOLUTION ---\n\n")
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

# Traverse the graph
for ev in graph.stream(initial_state, stream_mode="events"):
    print(ev)








