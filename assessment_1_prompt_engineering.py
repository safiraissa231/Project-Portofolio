# -*- coding: utf-8 -*-
"""Assessment 1-Prompt Engineering.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NmWZccseqM3yX_ulZRB7kxnmI2AjMYCI
"""

import json
import re
import requests
import streamlit as st

# Define prompts for each model in Bahasa Indonesia.
prompts = {
    "Mistral-7B-Instruct-v0.2": """<s>[INST] <<SYS>> You are a helpful, respectful, and honest assistant for summarize discussion text in Bahasa Indonesia.<</SYS>>
              I have an example discussion text in Bahasa Indonesia:
              Membahas perkembangan fintech dalam sebuah diskusi, Andi memulai dengan pernyataan penuh keyakinan, "Saya percaya bahwa fintech telah memberikan kontribusi besar dalam memodernisasi sektor keuangan kita." Pernyataan ini menandai awal dari sebuah dialog yang mendalam dan informatif mengenai dampak positif serta tantangan yang dihadapi oleh teknologi keuangan.
              Menanggapi Andi, Budi menyatakan dukungannya, "Benar, Andi. Aplikasi pembayaran digital saja telah membuat transaksi keuangan jauh lebih mudah." Budi menekankan bagaimana kemudahan akses dan efisiensi yang ditawarkan oleh aplikasi pembayaran digital telah mengubah cara orang bertransaksi, menunjukkan salah satu aspek paling nyata dari pengaruh fintech.
              Namun, Clara mengambil sudut pandang yang lebih kritis. Dia menambahkan ke dalam diskusi, "Saya setuju dengan kalian berdua, tapi jangan lupakan bahwa tantangan regulasi dan keamanan data juga meningkat seiring dengan inovasi ini." Clara mengingatkan bahwa di balik kemudahan yang ditawarkan, terdapat isu penting yang tidak boleh diabaikan. Isu tersebut berkaitan dengan bagaimana fintech diatur dan bagaimana data pengguna dilindungi dari ancaman keamanan.
              Dina, dengan bijak, mengakhiri diskusi dengan mencetuskan ide penting, "Penting bagi kita untuk menemukan solusi yang seimbang antara inovasi dan keamanan, agar fintech dapat terus berkembang tanpa merugikan pengguna." Dina menekankan pentingnya mencari keseimbangan, dimana inovasi teknologi finansial dapat berlanjut tanpa mengorbankan privasi dan keamanan pengguna.
              Melalui diskusi ini, diungkapkan bahwa meskipun fintech telah membawa banyak kemajuan dalam sektor keuangan, seperti memudahkan transaksi dan membuat layanan keuangan lebih inklusif, masih ada tantangan yang harus diatasi. Tantangan-tantangan tersebut meliputi regulasi yang memadai dan perlindungan data yang kuat untuk mencegah penyalahgunaan. Diskusi menunjukkan bahwa keberhasilan fintech di masa depan tidak hanya bergantung pada inovasi teknologinya, tetapi juga pada bagaimana industri dapat mengatasi isu-isu seperti regulasi dan keamanan data.

              Based on that discussion text, summarize in one formal brief paragraph in Bahasa Indonesia. [\INST]
              Dalam diskusi tentang perkembangan fintech, Andi memulai dengan menyatakan keyakinannya bahwa fintech telah signifikan dalam memodernisasi sektor keuangan, memberikan akses yang lebih mudah dan efisien kepada layanan keuangan. Budi menambahkan, menyoroti bagaimana aplikasi pembayaran digital telah memudahkan transaksi keuangan. Namun, Clara mengingatkan tentang tantangan yang datang bersama inovasi ini, khususnya terkait regulasi dan keamanan data, menekankan pentingnya memperhatikan aspek keamanan dalam pengembangan fintech. Dina mengakhiri diskusi dengan menekankan pentingnya mencari keseimbangan antara inovasi dan keamanan untuk memastikan fintech dapat berkembang tanpa merugikan pengguna. Diskusi ini menunjukkan bahwa meskipun fintech membawa banyak manfaat dalam mempermudah akses ke layanan keuangan dan meningkatkan efisiensi transaksi, industri ini juga dihadapkan pada tantangan penting yang harus diatasi, yaitu regulasi yang memadai dan perlindungan data pengguna.

              [INST]I have a discussion text in Bahasa Indonesia:""",
      "Llama-2-7B-32K-Instruct": """[INST]Write a concise summary of the discussion text, return your responses consisted of 5 lines that cover the key points of the discussion text in Bahasa Indonesia.""",
      "Qwen1.5-1.8B-Chat": """Write a concise summary of the discussion text. Use Bahasa Indonesia."""
}

# Model identifiers mapping.
model_identifiers = {
    "Mistral-7B-Instruct-v0.2": "mistralai/Mistral-7B-Instruct-v0.2",
    "Llama-2-7B-32K-Instruct": "togethercomputer/Llama-2-7B-32K-Instruct",
    "Qwen1.5-1.8B-Chat": "Qwen/Qwen1.5-1.8B-Chat"
}

# App title
st.title("Open Source LLMs Model Demo")

# Function to reset state except for the API key.
def reset_state():
    for key in list(st.session_state.keys()):
        if key != 'api_key':
            del st.session_state[key]

# Sidebar for resetting chat and selecting the model.
with st.sidebar:
    if st.button('User Chat'):
        reset_state()
    selected_model = st.selectbox("Select Model", ['Mistral-7B-Instruct-v0.2', 'Llama-2-7B-32K-Instruct', 'Qwen1.5-1.8B-Chat'])

# Input for the API key.
if 'api_key' not in st.session_state:
    api_key = st.sidebar.text_input('Enter API key:', type='password')
    if api_key:
        st.session_state['api_key'] = api_key
        st.sidebar.success('API key provided!', icon='✅')

# Unified function to generate completions from different models.
def generate_completion(prompt, model, messages=None, temperature=0.8, max_tokens=512, n=1, stop=None):
    endpoint = 'https://api.together.xyz/v1/completions'
    headers = {"Authorization": f"Bearer {st.session_state['api_key']}"}
    json_payload = {
        "model": model,
        "prompt": prompt,
        "messages": messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'n': n,
        'stop': stop
    }
    response = requests.post(endpoint, json=json_payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to generate summary. API responded with status code: {response.status_code}. Response: {response.text}")
        return None

# Main interaction area for user input with enhanced processing and display logic.
if 'api_key' in st.session_state:
    USER_PROMPT = st.text_area("Enter your discussion:")
    if USER_PROMPT:
        USER_PROMPT = re.sub(r"^\d+\n|\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+\n|\[.+?\]\n|\n\n+", '', USER_PROMPT)
        USER_PROMPT = re.sub(r'(\d+)(?=\n)', '', USER_PROMPT)
        USER_PROMPT = re.sub(r'\[[^\]]+\]', '', USER_PROMPT)
        USER_PROMPT = re.sub(r'\n+', ' ', USER_PROMPT)

        if selected_model == 'Mistral-7B-Instruct-v0.2':
            complete_prompt = f"{prompts[selected_model]}\n\n{USER_PROMPT}\n\nBased on that discussion text, summarize in one formal brief paragraph in Bahasa Indonesia."
        elif selected_model == 'Llama-2-7B-32K-Instruct':
            complete_prompt = f"{prompts[selected_model]}\n\n{USER_PROMPT}\n\n[\INST]"
        else:
            complete_prompt = f"{prompts[selected_model]}\n\n{USER_PROMPT}"

        model_name = model_identifiers.get(selected_model, "")
        response = generate_completion(complete_prompt, model_name, temperature=0.7, max_tokens=2048, n=1)

        if response and "choices" in response and response["choices"]:
            summary = response["choices"][0].get("text", "No summary generated.")
            if summary:
                st.write("### Generated Summary:")
                st.write(summary)
            else:
                st.error("The model was unable to generate a summary. Please try again or modify your input.")
        else:
            st.error("Failed to generate a summary. Please check your API key and model selection, or try again later.")
