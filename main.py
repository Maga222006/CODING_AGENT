from langchain.agents import tool, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from github import Github
import os

load_dotenv()

class ToolResponse:
    def __init__(self, tool, text=None, error=None, link=None, location=None, alarm=None, timer=None, stopwatch=None):
        self.tool = tool
        self.text = text
        self.error = error
        self.link = link
        self.location = location
        self.alarm = alarm
        self.timer = timer
        self.stopwatch = stopwatch

@tool
def create_repo(repo_name: str, private: bool = False):
    """Creates a GitHub repository with the given repo_name."""
    github = Github(os.getenv('GITHUB_TOKEN'))
    user = github.get_user()
    repo = user.create_repo(repo_name, private=private)
    return f"Repository '{repo_name}' created successfully!"

@tool
def commit_file_to_repo(repo_name: str, file_path: str, file_contents: str):
    """Adds a new file to the GitHub repository or updates the existing one."""
    github = Github(os.getenv('GITHUB_TOKEN'))
    user = github.get_user()
    repo = user.get_repo(repo_name)

    try:
        # Check if file exists
        file = repo.get_contents(file_path)
        sha = file.sha
        repo.update_file(file_path, "Updating file", file_contents, sha)
        return f"File '{file_path}' updated successfully in '{repo_name}'."
    except:
        repo.create_file(file_path, "Adding new file", file_contents)
        return f"File '{file_path}' created successfully in '{repo_name}'."

@tool
def read_file(repo_name: str, file_path: str):
    """Reads the content of a file from a GitHub repository."""
    github = Github(os.getenv('GITHUB_TOKEN'))
    user = github.get_user()
    repo = user.get_repo(repo_name)

    try:
        file = repo.get_contents(file_path)
        return file.decoded_content.decode('utf-8')
    except:
        return f"File '{file_path}' not found in '{repo_name}'."

@tool
def list_repos():
    """Lists all repositories owned by the authenticated GitHub user."""
    github = Github(os.getenv('GITHUB_TOKEN'))
    user = github.get_user()

    try:
        repos = user.get_repos()
        repo_names = [repo.name for repo in repos]
        return f"Repositories: {', '.join(repo_names)}"
    except:
        return "Unable to fetch repositories."

@tool
def list_files(repo_name: str):
    """Lists all files in the GitHub repository."""
    github = Github(os.getenv('GITHUB_TOKEN'))
    user = github.get_user()
    repo = user.get_repo(repo_name)

    try:
        files = repo.get_contents("")
        file_list = [file.name for file in files]
        return f"Files in '{repo_name}': {', '.join(file_list)}"
    except:
        return f"Unable to fetch files from repository '{repo_name}'."

@tool
def delete_file(repo_name: str, file_path: str):
    """Deletes a file from the GitHub repository."""
    github = Github(os.getenv('GITHUB_TOKEN'))
    user = github.get_user()
    repo = user.get_repo(repo_name)

    try:
        file = repo.get_contents(file_path)
        sha = file.sha
        repo.delete_file(file_path, "Deleting file", sha)
        return f"File '{file_path}' deleted successfully from '{repo_name}'."
    except:
        return f"File '{file_path}' not found in '{repo_name}'."

@tool
def list_branches(repo_name: str):
    """Lists all branches in a GitHub repository."""
    github = Github(os.getenv('GITHUB_TOKEN'))
    user = github.get_user()
    repo = user.get_repo(repo_name)

    try:
        branches = repo.get_branches()
        branch_names = [branch.name for branch in branches]
        return f"Branches in '{repo_name}': {', '.join(branch_names)}"
    except:
        return f"Unable to fetch branches from repository '{repo_name}'."

@tool
def create_branch(repo_name: str, branch_name: str):
    """Creates a new branch in a GitHub repository."""
    github = Github(os.getenv('GITHUB_TOKEN'))
    user = github.get_user()
    repo = user.get_repo(repo_name)

    try:
        main_branch = repo.get_branch("main")  # assuming the default branch is named 'main'
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)
        return f"Branch '{branch_name}' created successfully in '{repo_name}'."
    except:
        return f"Unable to create branch '{branch_name}' in '{repo_name}'."

llm = ChatOpenAI(model=os.getenv("MODEL"))
agent = initialize_agent(
    llm=llm,
    tools=[create_repo, commit_file_to_repo, read_file, list_files, list_repos, delete_file, list_branches, create_branch],
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    memory=ConversationBufferMemory(),
    verbose=True,
)

if __name__ == "__main__":
    while True:
        print(agent.run(input("input:"))['output'])