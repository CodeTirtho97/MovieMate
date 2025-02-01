import subprocess
import os

notebooks = [
    os.path.join("notebooks", "Data_Exploration.ipynb"),
    os.path.join("notebooks", "Content_Based_Filtering.ipynb"),
    os.path.join("notebooks", "Collaborative_Filtering.ipynb")
]


def run_notebooks():
    """Execute Jupyter notebooks in order without user intervention."""
    for notebook in notebooks:
        print(f"Executing {notebook}...")
        subprocess.run(["python", "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", notebook], check=True)
        print(f"Execution of {notebook} completed.\n")

if __name__ == "__main__":
    run_notebooks()
    print("All notebooks executed successfully.")
