from pathlib import Path

from setuptools import find_namespace_packages, setup

# Load packages from requirements.txt
BASE_DIR = Path(__file__).parent
with open(Path(BASE_DIR, "requirements.txt")) as file:
    required_packages = [ln.strip() for ln in file.readlines()]

# Define our package
setup(
    name="learnflow-ai",
    version="0.1.0",
    description="Multi-agent learning orchestration system with stateful syllabus-guided tutoring",
    author="hqanhh",
    author_email="Ankita Khartmol",
    url="https://github.com/Ankita2525/LearnFlow-AI",
    python_requires=">=3.10",
    packages=find_namespace_packages(),
    install_requires=required_packages,
    extras_require={
        "dev": ["pre-commit==2.19.0"],
    },
)
