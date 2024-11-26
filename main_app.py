import requests
import streamlit as st

# GitHub repository details
GITHUB_USER = "MarcosMirai"
REPOSITORY = "apps"

def main():
    st.title("Streamlit App Viewer")
    st.write(f"Fetching Python apps from repository: `{GITHUB_USER}/{REPOSITORY}`")

    # Fetch Python files from the repository
    apps = fetch_python_files(GITHUB_USER, REPOSITORY)

    if apps:
        st.success(f"Found {len(apps)} Python file(s).")
        app_selected = st.selectbox("Select an app to view or run:", apps)

        if app_selected:
            file_url = f"https://github.com/{GITHUB_USER}/{REPOSITORY}/blob/main/{app_selected}"
            raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPOSITORY}/main/{app_selected}"

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

def fetch_python_files(username, repository):
    """
    Fetch Python files from a public GitHub repository.
    """
    url = f"https://api.github.com/repos/{username}/{repository}/contents"
    response = requests.get(url)

    if response.status_code == 200:
        files = response.json()
        python_files = [file['name'] for file in files if file['name'].endswith('.py')]
        return python_files
    else:
        st.error(f"Failed to fetch repository contents: {response.status_code}")
        return []

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
