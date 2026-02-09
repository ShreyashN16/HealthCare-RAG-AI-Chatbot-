import streamlit as st, requests

st.title('Fingerprint Research UI')
up = st.file_uploader('Upload fingerprint', type=['png', 'jpg', 'jpeg', 'bmp'])

if up:
    st.image(up,caption='Uploaded',width=200)
    if st.button('Predict'):
        r=requests.post('http://localhost:8000/predict', files={'file':(up.name,up.getvalue(),up.type)})
        st.write(r.json())
