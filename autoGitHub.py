import os

def push2GitHub(comment):

    os.system("git remote -v")
    os.system("git add .")
    os.system(f'git commit -m "{comment}"')
    os.system("git push -u origin main")

push2GitHub('adding docstrings')