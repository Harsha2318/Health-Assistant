import os
import subprocess

def run_streamlit():
    # Set the working directory to the app directory
    app_dir = os.path.join(os.path.dirname(__file__), 'app')
    
    # Run the Streamlit app
    subprocess.run(["streamlit", "run", "streamlit_app.py"], cwd=app_dir)

if __name__ == "__main__":
    run_streamlit()
