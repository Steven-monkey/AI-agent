import os
from langchain_deepseek import ChatDeepSeek
from typing import Optional
from pydantic import BaseModel, Field


llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.8,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


class Joke(BaseModel):
    """Joke to tell user."""

    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline to the joke")
    rating: Optional[int] = Field(
        default=None, description="How funny the joke is, from 1 to 10"
    )


structured_llm = llm.with_structured_output(Joke)
print(structured_llm.invoke("给我讲一个关于程序员的笑话"))
