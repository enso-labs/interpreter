import os
from typing import List
from pydantic import Field

from langchain_core.tools import BaseToolkit
from langchain_community.tools import StructuredTool

from tools import Interpreter

class InterpreterToolkit(BaseToolkit):
	"""Toolkit for the interpreter."""

	api_url: str = Field(default=os.getenv("INTERPRETER_URL", "http://localhost:8100"))

	class Config:
		"""Pydantic config."""
		arbitrary_types_allowed = True

	def get_tools(self) -> List[StructuredTool]:
		"""Get the tools in the toolkit."""
		toolkit = Interpreter(api_url=self.api_url).toolkit()
		return toolkit
  
if __name__ == "__main__":
	toolkit = InterpreterToolkit(api_url=os.getenv("INTERPRETER_URL", "http://localhost:8100"))
	tools = toolkit.get_tools()
	result = tools[0].run({"session_id": "test", "code": "print('Hello, World!')"})
	print(">>> Tools: ", tools)
	print("\n\n")
	print(">>> Result: ", result)