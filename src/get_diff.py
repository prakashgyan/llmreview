import subprocess
import os


def get_file_diff_between_branches(source_branch: str, target_branch: str, filename: str) -> str:
    """
    Return the git diff of a specific file between two branches.
    
    Parameters:
        source_branch (str): The branch containing the original version of the file.
        target_branch (str): The branch containing the updated version.
        filename (str): The path to the file to compare.

    Returns:
        str: A unified diff showing changes from source_branch to target_branch.
    """
    if not os.path.isfile(filename):
        print(f"Provided file '{filename}' does not exist.")
        exit(0)
    try:
        # Fetch latest refs (optional, but safe)
        subprocess.run(['git', 'fetch'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Use git diff with --no-prefix for cleaner output, or remove if you prefer full paths
        result = subprocess.run(
            ['git', 'diff', f'{source_branch}..{target_branch}', '--', filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        diff_output = result.stdout.strip()
        if not diff_output:
            return f"No changes in '{filename}' between {source_branch} and {target_branch}."
        return diff_output

    except subprocess.CalledProcessError as e:
        return f"Error running git diff:\n{e.stderr.strip()}"

    except Exception as ex:
        return f"Unexpected error: {str(ex)}"


