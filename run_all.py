import subprocess
import time

# Start Flask server
flask_process = subprocess.Popen(["python", "app/main.py"])

# Delay to ensure Flask starts first
time.sleep(2)

# Start Streamlit app
streamlit_process = subprocess.Popen(["streamlit", "run", "app/url_shortener_frontend.py"])

# Wait for both to complete (optional if you want to keep the script alive)
try:
    flask_process.wait()
    streamlit_process.wait()
except KeyboardInterrupt:
    flask_process.terminate()
    streamlit_process.terminate()
