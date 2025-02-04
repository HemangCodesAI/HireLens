from phi.agent import Agent
from  phi.tools.duckduckgo import DuckDuckGo
from phi.tools.file import FileTools
from dotenv import load_dotenv
from pathlib import Path
from phi.model.google import Gemini
import os
# from phi.utils.pprint import pprint_run_response
# from typing import Iterator

load_dotenv()
api_key=os.getenv("Google_API_KEY")
dir='data'
path = Path(dir)
inputs=Path('inputs')
Research_agent=Agent(
    name='research_agent',
    role='expand the job role',
    tools=[DuckDuckGo()],
    model=Gemini(id="gemini-2.0-flash-exp",api_key=api_key),
    verbose=False,
    show_tool_calls=False,
    stream=False,
    instructions=["use the duckduckgo tool to search the web for relevant information about the company policies.",
                  "analyse the job role to understand its responsibilities, required skills, and qualifications.",
                  "Use the insights to draft a summary of the company's profile and the job role.",
                  "pass the information to the writer_agent for further processing."],
    markdown=False
    )
                     
Writer_agent=Agent(
    name='writer_agent',
    role='Search the web for the information.',
    tools=[FileTools(base_dir=path, read_files=True, list_files=True,save_files=True)],
    model=Gemini(id="gemini-2.0-flash-exp",api_key=api_key),
    verbose=False,
    instructions=["Analyze the provided summary of the  the job role.",
                  "Use the insights to Draft a job posting for the role described.",
                  "Start with a compelling introduction,followed by a detailed role description, responsibilities, and required skills and qualifications.",
                  "use the filetool to Write the draft in a markdown file",
                  "Save the file in markdown format"],
    show_tool_calls=False,
    markdown=False
)

Post_editor_agent=Agent(
    name='post_editor_agent',
    role='Edit the intial draft and submit the final version for approval and publication.',
    tools=[FileTools(base_dir=path, read_files=True, list_files=True,save_files=True)],
    model=Gemini(id="gemini-2.0-flash-exp",api_key=api_key),
    verbose=False,
    instructions=["Review the initial draft of the job posting created by the writer_agent.",
                  "Edit the content for clarity, accuracy, and alignment with the company's culture and values.",
                  "Ensure the language is professional, engaging, and free of errors.",
                  "Make Sure you Save the final version in markdown format for publication using the files tool."],
    show_tool_calls=True,
    markdown=True
)
multiple_agent=Agent(
    team=[Research_agent, Writer_agent],
    verbose=False,
    instructions=["Expand the job role by adding requirements ,skills needed.",
                  "Summathe findings and pass the information to the writer_agent for further processing.",
                  "write a deatiled job posting for the role described.",
                  "Always Save the complete job posting in markdown format"],
    markdown=True,
    tools=[DuckDuckGo(), FileTools(base_dir=path, read_files=True, list_files=True,save_files=True)],
    show_tool_calls=True,
    model=Gemini(id="gemini-2.0-flash-exp",api_key=api_key),
    stream=True,
    name='multiple_agent',
)
HR_agent=Agent(
    name='HR_agent',
    role='Comapre the job posting with the submitted resume',
    tools=[FileTools(base_dir=inputs, read_files=True, list_files=True,save_files=False)],
    model=Gemini(id="gemini-2.0-flash-exp",api_key=api_key),
    verbose=False,
    instructions=["Use the filetool to read the job_posting.md and  resume.md files",
                  "Compare how the candidate resume fit the job posting.",
                  "Provide detailed analysis weather the candidate is a good fit for the job role or not.",
                  "Score the candidate (out of 100) based on the analysis.",
                  "Give 3 reasons why the candidate is a good and not a good  fit for the job role.",],
    show_tool_calls=False,
    markdown=False
)
def process_resume():
    prompt = "Compare this candidates resume for this job posting and provide a detailed analysis on how well the candidate fits the job role."
    out=HR_agent.run(prompt, markdown=True, show_time=True)
    return out.content[out.content.find('**'):]
    # return out.content
def get_posting(prompt):
    response = multiple_agent.run(prompt, markdown=True, show_time=True)
    return response.content[response.content.find("#"):response.content.find('''", "additional_information"''')]