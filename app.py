import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
from datetime import datetime

load_dotenv()

client = OpenAI(api_key = os.getenv("OPEN_API_KEY"))

CHAT_FOLDER = 'chats'
PINNED_FILE = os.path.join(CHAT_FOLDER, 'pinned_chats.json')
os.makedirs(CHAT_FOLDER, exist_ok=True)

def save_chat(chat_name, messages):
    filepath = os.path.join(CHAT_FOLDER, chat_name)
    with open(filepath, 'w', encoding="utf-8") as f:
        json.dump(messages, f, indent=4)

def load_chat(chat_name):
    filepath = os.path.join(CHAT_FOLDER, chat_name)
    with open(filepath, 'r', encoding="utf-8") as f:
        return json.load(f)

def load_pinned_chats():
    if os.path.exists(PINNED_FILE):
        with open(PINNED_FILE, 'r', encoding="utf-8") as f:
            return json.load(f)
    return []

def save_pinned_chats(pinned):
    with open(PINNED_FILE, 'w', encoding="utf-8") as f:
        json.dump(pinned, f, indent=4)

def toggle_pin(chat_name):
    pinned = load_pinned_chats()
    if chat_name in pinned:
        pinned.remove(chat_name)
    else:
        pinned.append(chat_name)
    save_pinned_chats(pinned)

st.sidebar.title('Chat History')
chat_files = sorted(os.listdir(CHAT_FOLDER), reverse=True)
chat_files = [f for f in chat_files if f.endswith('.json') and f != 'pinned_chats.json']
pinned_chats = load_pinned_chats()

if st.sidebar.button('➕ New Chat'):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    chat_name = f"chat_{timestamp}.json"
    st.session_state.chat_name = chat_name
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant"
        }
    ]
    save_chat(chat_name, st.session_state.messages)
    st.rerun()

st.sidebar.markdown("---")

# Display pinned chats
if pinned_chats:
    st.sidebar.subheader("📌 Pinned")
    for chat in pinned_chats:
        if chat in chat_files:
            col1, col2 = st.sidebar.columns([4, 1])
            with col1:
                if st.button(chat, key=f"pinned_{chat}"):
                    st.session_state.chat_name = chat
                    st.session_state.messages = load_chat(chat)
                    st.rerun()
            with col2:
                if st.button("📍", key=f"unpin_{chat}", help="Unpin"):
                    toggle_pin(chat)
                    st.rerun()
    st.sidebar.markdown("---")

# Display all chats
st.sidebar.subheader("📂 All Chats")
for chat in chat_files:
    if chat not in pinned_chats:
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            if st.button(chat, key=f"chat_{chat}"):
                st.session_state.chat_name = chat
                st.session_state.messages = load_chat(chat)
                st.rerun()
        with col2:
            if st.button("📌", key=f"pin_{chat}", help="Pin"):
                toggle_pin(chat)
                st.rerun()

if "messages" not in st.session_state:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    chat_name = f"chat_{timestamp}.json"
    st.session_state.chat_name = chat_name
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant"
        }
    ]
    save_chat(chat_name, st.session_state.messages)

st.title('OpenAI Chatbot')

for msg in st.session_state.messages:
    if msg['role'] == 'system':
        continue

    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

prompt = st.chat_input('Ask something')
if prompt:
    st.chat_message('user').markdown(prompt)
    st.session_state.messages.append(
        {
            'role': 'user',
            'content': prompt
        }
    )

    with st.spinner("Generating response ..."):
        response = client.responses.create(
            model='gpt-4o-mini',
            input=st.session_state.messages
        )

        answer = response.output_text

        st.chat_message('assistant').markdown(answer)
        st.session_state.messages.append(
            {
                'role': 'assistant',
                'content': answer
            }
        )
        save_chat(st.session_state.chat_name, st.session_state.messages)
