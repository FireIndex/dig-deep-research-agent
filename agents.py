from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from datetime import date
from tools import web_search, scrape_url
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

#model setup 
if os.getenv('LLM') == 'openai':
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-5-nano")
else:
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="openai/gpt-oss-20b")

#1st agent
def build_search_agent():
    return create_agent(
        model = llm,
        tools= [web_search],
        # today's date is injected here, so no extra date_today tool round-trip
        system_prompt=(
            f"Today is {date.today():%Y-%m-%d}. You are a search agent. "
            "Call web_search EXACTLY ONCE with one well-formed query, then answer with the results. "
            "Never search a second time."
        ),
    )

#2nd agent
def build_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url],
        system_prompt=(
            "You are a reader agent. Call scrape_url EXACTLY ONCE on the single most relevant URL, "
            "then summarise what you read. Never scrape a second URL."
        ),
    )

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()


#critic_chain
critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()