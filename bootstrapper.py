# Copyright 2023 iiPython

# Modules
import re
import os
import subprocess
from getpass import getuser

# Initialization
class Terminal(object):
    def __init__(self) -> None:
        self.colors = {
            "red": 31, "green": 32, "yellow": 33,
            "end": 0
        }
        self.clear_line = "\033[2K\033[1G"
        self.up_double = "\033[2F"
        self.asked = False

    def escape(self, code: str) -> str:
        return f"\033[{code}"

    def c(self, name: str) -> str:
        return self.escape(str(self.colors[name]) + "m")

    def ask(self, question: str, default: str) -> str:
        double = self.up_double if self.asked else ""
        print(f"{double}{self.clear_line}{self.c('yellow')}{question}{self.c('end')}")
        self.asked = True
        return input(f"{self.clear_line}(default: '{default}') > ") or default

term = Terminal()

# Update methods
def update_copyright(owner: str) -> None:
    owner = rf"\1{owner}"
    with open("LICENSE.txt", "r") as fh:
        new_copyright = re.sub(r"(Copyright \(c\) 20\d+ ).*", owner, fh.read())
        with open("LICENSE.txt", "w") as fw:
            fw.write(new_copyright)

    for path, _, files in os.walk("./"):
        for file in files:
            if file[-3:] != ".py":
                continue

            full_path = os.path.join(path, file)
            with open(full_path, "r") as fh:
                new_content = re.sub(r"(\# Copyright 20\d+ ).*", owner, fh.read())
                with open(full_path, "w") as fw:
                    fw.write(new_content)

def update_repo(repo: str) -> None:
    if repo == "none":
        return

    subprocess.run(["git", "remote", "set-url", "origin", f"https://github.com/{repo}"])
    with open("README.md", "r") as fh:
        content = fh.read()
        with open("README.md", "w") as fw:
            fw.write(content.replace("template-dmmd/template-py", repo))

def update_project_name(name: str) -> None:
    os.rename("template", name)

def auto_push(option: str) -> None:
    option = option.lower()
    if option in ["yes", "y"]:
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Update template options"])
        subprocess.run(["git", "push"])

# Handle configuration questions
answers = []
for question in [
    {
        "q": "Select a username to use for LICENSE.txt and copyright statements.",
        "d": getuser(),
        "f": update_copyright
    },
    {
        "q": "Enter the new github repository to use in format <username>/<repo>.",
        "f": update_repo
    },
    {
        "q": "Enter the new project name (python friendly).",
        "d": (-1, lambda v: v.split("/")[1]),
        "f": update_project_name
    },
    {
        "q": "Would you like to commit these changes and push now?",
        "d": "yes",
        "f": auto_push
    }
]:

    # Handle fetching default (dynamic or static)
    default = question.get("d", "none")
    if isinstance(default, tuple):
        default = default[1](answers[default[0]])

    # Ask question and such
    result = term.ask(question["q"], default)
    answers.append(result)  # So future questions can reference this

    # Perform action
    question["f"](result)

os.remove("bootstrapper.py")

# Process is done
double_clear = term.up_double + term.clear_line
print(f"{double_clear}{term.c('green')}Bootstrapping complete!{term.c('end')}")
