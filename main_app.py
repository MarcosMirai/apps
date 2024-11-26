import requests
import streamlit as st

# GitHub repository details
GITHUB_USER = "MarcosMirai"
REPOSITORY = "apps"

def main():
    st.title("Streamlit App Viewer")
    st.write(f"Fetching Python apps from repository: `{GITHUB_USER}/{REPOSITORY}`")

    # Get the default branch (e.g., main or master)
    default_branch = get_default_branch(GITHUB_USER, REPOSITORY)
    if not default_branch:
        st.error("Failed to fetch the default branch. Check your repository settings.")
        return

    # Fetch Python files recursively
    apps = fetch_python_files_recursive(GITHUB_USER, REPOSITORY, default_branch)

    if apps:
        st.success(f"Found {len(apps)} Python file(s).")
        app_selected = st.selectbox("Select an app to view or run:", apps)

        if app_selected:
            file_url = f"https://github.com/{GITHUB_USER}/{REPOSITORY}/blob/{default_branch}/{app_selected}"
            raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPOSITORY}/{default_branch}/{app_selected}"

            st.markdown(f"### Selected App: `{app_selected}`")
            st.write(f"[View on GitHub]({file_url})")
            st.write(f"[View Raw File]({raw_url})")

            # Optionally display the content of the selected file
            if st.checkbox("Show File Content"):
                content = fetch_file_content(raw_url)
                if content:
                    st.code(content, language='python')
    else:
        st.warning("No Python files found in the repository.")

def get_default_branch(username, repository):
    """
    Fetch the default branch of a GitHub repository.
    """
    url = f"https://api.github.com/repos/{username}/{repository}"
    response = requests.get(url)

    if response.status_code == 200:
        repo_data = response.json()
        return repo_data.get("default_branch", "main")
    else:
        st.error(f"Failed to fetch repository details: {response.status_code}")
        return None

def fetch_python_files_recursive(username, repository, branch, path=""):
    """
    Fetch Python files from a GitHub repository, searching recursively.
    """
    url = f"https://api.github.com/repos/{username}/{repository}/contents/{path}?ref={branch}"
    response = requests.get(url)

    python_files = []
    if response.status_code == 200:
        files = response.json()
        for file in files:
            if file['type'] == 'file' and file['name'].endswith('.py'):
                python_files.append(file['path'])
            elif file['type'] == 'dir':
                # Recursively fetch files from subdirectories
                sub_path = file['path']
                python_files.extend(fetch_python_files_recursive(username, repository, branch, sub_path))
    else:
        st.error(f"Failed to fetch repository contents: {response.status_code}")
    
    return python_files

def fetch_file_content(raw_url):
    """
    Fetch the raw content of a file from a raw GitHub URL.
    """
    try:
        response = requests.get(raw_url)
        if response.status_code == 200:
            return response.text
        else:
            st.error(f"Failed to fetch file content: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Uncomment to run in a Streamlit environment
# if __name__ == "__main__":
#     main()
