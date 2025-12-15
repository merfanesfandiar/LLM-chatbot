import streamlit as st
from dotenv import load_dotenv
from models import generate_openai, generate_ollama

load_dotenv()


st.set_page_config(page_title="Ai English teacher", layout="centered",page_icon="robot")

col1, col2 = st.columns([1, 6])

with col1:
    st.image("static/logo.png", width=120)

with col2:
    st.title("Ai English teacher")

backend = st.sidebar.selectbox("Backend", ("OpenAI (cloud)", "Ollama (local)"))
openai_model = st.sidebar.selectbox("OpenAI model", ["gpt-4o","gpt-4o-mini","gpt-4o-nano"])
st.sidebar.button("new lesson", on_click=lambda: st.session_state.clear())

#history for saving previous messages
if "history" not in st.session_state:
    st.session_state.history = [{"role": " ","content" :" "}]

if "id" not in st.session_state:
    st.session_state.id= 1

# Display chat history
for message in st.session_state.history[1:]:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
# Function to send message to api and get response
def send_message(user_text: str):
    st.session_state.history.append({"role":"user","content": user_text})
    try:    #checking which backend is selected
        if backend.startswith("OpenAI"):
            bot_text = generate_openai(user_text, model_name=openai_model)
            st.write(bot_text)
            
        else:
            bot_text = generate_ollama(user_text)
            st.write(bot_text)        
    except Exception as e:
        resp = f"[Error] {e}"
    #add response to history  
    st.session_state.history.append({"role":"assistant","content": bot_text})
    

        
if prompt := st.chat_input():
    # If user submits a message,show it in the chat and send it to the model
    with st.chat_message("user"):
        st.markdown(prompt)
        send_message(prompt)
      

