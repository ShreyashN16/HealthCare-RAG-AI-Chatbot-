import streamlit as st, requests

st.title('Fingerprint Research UI')
up = st.file_uploader('Upload fingerprint', type=['png', 'jpg', 'jpeg', 'bmp'])

API_URL = 'http://localhost:8000'

if up:
    st.image(up, caption='Uploaded', width=200)
    if st.button('Predict'):
        try:
            r = requests.post(f'{API_URL}/predict', files={'file': (up.name, up.getvalue(), up.type)}, timeout=30)
            r.raise_for_status()
            st.write(r.json())
        except requests.exceptions.ConnectionError:
            st.error(
                "**Backend not running.** Start it in a separate terminal:\n\n"
                "```\ncd \"F:\\ml projects\\fingerprint_kagglehub_project\"\n"
                "uvicorn backend.main:app --host 127.0.0.1 --port 8000\n```"
            )
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
