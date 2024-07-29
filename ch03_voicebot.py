#### 기본 정보 입력 #####
import streamlit as st
from audiorecorder import audiorecorder   # 모듈 이름을 올바르게 수정했습니다.
import openai
import os
from datetime import datetime
from gtts import gTTS
import base64

##### 기능 구현 함수 #####
def STT(audio):
    """
    음성 파일을 텍스트로 변환하는 함수입니다.
    :param audio: 녹음된 음성 파일
    :return: 음성에서 추출된 텍스트
    """
    filename = 'input.mp3'
    audio.export(filename, format="mp3")  # 음성 파일을 MP3 형식으로 저장
    with open(filename, "rb") as audio_file:
        # Whisper 모델을 사용해 음성을 텍스트로 변환
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    os.remove(filename)  # 사용 후 파일 삭제
    return transcript["text"]

def ask_gpt(prompt, model):
    """
    GPT 모델에 프롬프트를 보내고 답변을 얻는 함수입니다.
    :param prompt: GPT 모델에 전달할 프롬프트
    :param model: 사용하고자 하는 GPT 모델
    :return: GPT 모델의 응답
    """
    response = openai.ChatCompletion.create(model=model, messages=prompt)
    return response["choices"][0]["message"]["content"]

def TTS(response):
    """
    텍스트를 음성으로 변환하여 재생하는 함수입니다.
    :param response: 변환할 텍스트
    """
    filename = "output.mp3"
    tts = gTTS(text=response, lang="ko")
    tts.save(filename)  # 음성 파일 저장

    # 음원 파일 자동 재생
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        audio_html = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(audio_html, unsafe_allow_html=True)
    
    os.remove(filename)  # 사용 후 파일 삭제

##### 메인 함수 #####
def main():
    # 스트림릿 페이지 설정
    st.set_page_config(page_title="음성 비서 프로그램", layout="wide")

    # 세션 상태 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False

    st.header("음성 비서 프로그램")
    st.markdown("---")

    # 프로그램 설명
    with st.expander("음성비서 프로그램에 관하여", expanded=True):
        st.write(
        """     
        - 음성비서 프로그램의 UI는 스트림릿을 활용했습니다.
        - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용했습니다. 
        - 답변은 OpenAI의 GPT 모델을 활용했습니다. 
        - TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용했습니다.
        """
        )
        st.markdown("")

    # 사이드바 설정
    with st.sidebar:
        # OpenAI API 키 입력받기
        openai.api_key = st.text_input(label="OPENAI API 키", placeholder="Enter Your API Key", value="", type="password")

        st.markdown("---")

        # GPT 모델 선택
        model = st.radio(label="GPT 모델", options=["gpt-4", "gpt-3.5-turbo"])

        st.markdown("---")

        # 리셋 버튼
        if st.button(label="초기화"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
            st.session_state["check_reset"] = True

    # 기능 구현 영역
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("질문하기")
        # 음성 녹음 아이콘 추가
        audio = audiorecorder("클릭하여 녹음하기", "녹음중...")  # 올바른 함수로 수정
        if (audio.duration_seconds > 0) and not st.session_state["check_reset"]:
            st.audio(audio.export().read())  # 음성 재생
            question = STT(audio)  # 음성에서 텍스트 추출

            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"].append(("user", now, question))
            st.session_state["messages"].append({"role": "user", "content": question})

    with col2:
        st.subheader("질문/답변")
        if (audio.duration_seconds > 0) and not st.session_state["check_reset"]:
            response = ask_gpt(st.session_state["messages"], model)  # GPT 모델에서 답변 얻기

            st.session_state["messages"].append({"role": "system", "content": response})

            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"].append(("bot", now, response))

            # 채팅 시각화
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
            
            TTS(response)  # 답변을 음성으로 변환 및 재생
        else:
            st.session_state["check_reset"] = False

if __name__ == "__main__":
    main()
