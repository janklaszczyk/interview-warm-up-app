import streamlit as st
from openai import OpenAI
from io import BytesIO
from system_prompt import mixed_sys_prompt

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
LLM_model = "gpt-3.5-turbo"
STT_model = "whisper-1"

st.title("Job Interview Simulator")
st.write(
    "Get ready for your mock interview by answering AI-generated questions.\
        The interview process might take from 10 to 30 minutes."
)
job_position = st.text_input(
    "1. What is the job position you are preparing for?", key="job_position"
)

if job_position != "":
    job_description = st.text_area(
        "2. OPTIONAL Describe the job position you are preparing for. You can paste it from the job offer:",
        key="job_description",
    )
    st.write(
        "Instructions: Every time you want to give an answer, press the microphone button below to start recording and press stop if you finished."
    )

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = LLM_model

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio bytes to text using OpenAI's Whisper model.

    :param audio_bytes: The audio bytes to transcribe.
    :type audio_bytes: bytes
    :return: The transcribed text.
    :rtype: str
    """
    audio_file = BytesIO(audio_bytes)
    audio_file.name = "answer.webm"  # st.audio_input outputs webm
    transcript = client.audio.transcriptions.create(
        model=STT_model, file=audio_file, response_format="text"
    )
    return transcript
if job_position != "":
    if audio_prompt := st.audio_input(
        "Record an answer to interview question",
        key="audio_input",
        label_visibility="collapsed",
    ):
        audio_bytes = audio_prompt.read()
        with st.spinner("Transcribing your answer..."):
            try:
                user_audio_transcript = transcribe_audio(audio_bytes)
            except Exception as e:
                st.error(f"Transcription failed: {e}")
                st.stop()

        st.session_state.messages.append(
            {"role": "user", "content": user_audio_transcript}
        )
        with st.chat_message("user"):
            st.markdown(user_audio_transcript)
        
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{"role": "system", "content": mixed_sys_prompt(job_position, job_description)}] # add which kind of system prompts do you like from system_prompts.py
                + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=0.2,
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )