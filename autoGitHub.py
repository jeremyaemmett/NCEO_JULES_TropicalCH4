import os

def push2GitHub(message):

    """Automatically commit and push all workspace files to a GitHub repository, with an optional commit message.
    """

    os.system("git remote -v")
    os.system("git add .")
    os.system(f'git commit -m "{message}"')
    os.system("git push -u origin main")


def push2GitHub2(message):
    """Automatically commit and push all workspace files to a GitHub repository."""
    os.system('git config user.name "jeremyaemmett"')
    os.system('git config user.email "jae35@leicester.ac.uk"')
    os.system("git remote -v")
    os.system("git add .")
    os.system(f'git commit -m "{message}"')
    os.system("git push -u origin main")

push2GitHub2('made time series overlap the zonal plots, made average row, made cumulative row')