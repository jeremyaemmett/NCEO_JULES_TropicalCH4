import os
import subprocess

def push2GitHub(message):

    """Automatically commit and push all workspace files to a GitHub repository, with an optional commit message.
    """

    os.system("git remote -v")
    os.system("git add .")

    files = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], text=True
    ).splitlines()

    for f in files:
        if os.path.isfile(f) and os.path.getsize(f) >= 100 * 1024 * 1024:
            os.system(f'git reset -- "{f}"')

    os.system(f'git commit -m "{message}"')
    os.system("git push -u origin main")


def push2GitHub2(message):
    """Automatically commit and push all workspace files to a GitHub repository."""

    os.system('git config user.name "jeremyaemmett"')
    os.system('git config user.email "jae35@leicester.ac.uk"')
    os.system("git remote -v")
    os.system("git add .")

    files = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], text=True
    ).splitlines()

    for f in files:
        if os.path.isfile(f) and os.path.getsize(f) >= 100 * 1024 * 1024:
            os.system(f'git reset -- "{f}"')

    os.system(f'git commit -m "{message}"')
    os.system("git push -u origin main")


push2GitHub2('automatic looping of postprocessing scripts')