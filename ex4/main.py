import subprocess
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


llm = ChatOpenAI(temperature=0.0, model="gpt-4o")


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a FPGA developer that writes Verilog modules to target user defined problems and SystemVerilog testbenches to verify said modules.
        
        """
    ),
    ("placeholder", "{messages}")
])


def run_bash(script_path: str) -> str:
    result = subprocess.run(
        ["bash", script_path],
        capture_output=True,
        text=True
    )

    # Check for errors
    if result.returncode != 0:
        error_msg = (
            f"Script failed with exit code {result.returncode}\n"
            f"stderr:\n{result.stderr}"
        )
        raise RuntimeError(error_msg)

    return result.stdout



