import os

def push2GitHub(message):

    """Automatically commit and push all workspace files to a GitHub repository, with a commit message.
    """

    os.system("git remote -v")
    os.system("git add .")
    os.system(f'git commit -m "{message}"')
    os.system("git push -u origin main")

push2GitHub('adding docstrings, testing more variables, revised global min/max calculation')