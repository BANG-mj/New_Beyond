import streamlit as st
import time
from RAGBookClubGPT import RAGBookClubGPT
import openai

# OpenAI API 설정
openai.api_key =  "api key"

# Streamlit 상태 초기화: 사용자가 앱을 사용할 때 유지해야 하는 데이터를 저장합니다.
if "rag_gpt" not in st.session_state:
    st.session_state.rag_gpt = None  # RAGBookClubGPT 인스턴스를 저장할 공간
if "topics" not in st.session_state:
    st.session_state.topics = []  # 생성된 토론 주제를 저장할 공간
if "current_topic_index" not in st.session_state:
    st.session_state.current_topic_index = 0  # 현재 진행 중인 토론 주제의 인덱스
if "all_responses" not in st.session_state:
    st.session_state.all_responses = []  # 각 주제에 대한 응답을 저장
if "summary" not in st.session_state:
    st.session_state.summary = ""  # 생성된 요약을 저장할 공간
if "messages" not in st.session_state:
    st.session_state.messages = []  # 각 주제별 메시지를 저장할 공간

# 앱 제목 표시
st.title("AI 기반 독서 모임")

# PDF 파일 업로드: 사용자가 PDF 파일을 업로드하면 이를 처리합니다.
uploaded_file = st.file_uploader("PDF 파일 업로드", type=["pdf"])
if uploaded_file:
    pdf_path = f"uploaded_{uploaded_file.name}"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())  # 업로드된 파일의 내용을 저장

    # RAGBookClubGPT 인스턴스 초기화: 업로드된 PDF 파일과 OpenAI API 키를 사용하여 독서 모임 AI를 초기화합니다.
    try:
        st.session_state.rag_gpt = RAGBookClubGPT(pdf_path, openai.api_key)
        st.success("PDF 파일이 성공적으로 로드되었습니다!")

        # 주제 생성: 처음 한 번만 주제를 생성하고 저장합니다.
        if not st.session_state.topics:
            user_responses = ["독서 감상문 또는 초기 의견"]  # 사용자 초기 입력 예시
            st.session_state.topics = st.session_state.rag_gpt.generate_topics(user_responses)
            if st.session_state.topics:
                st.success("토론 주제가 성공적으로 생성되었습니다!")
                for idx, topic in enumerate(st.session_state.topics, start=1):
                    st.write(f"{idx}. {topic}")  # 생성된 주제를 화면에 표시
            else:
                st.error("토론 주제를 생성하지 못했습니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")  # 예외 발생 시 오류 메시지 출력

# 토론 진행: 생성된 주제가 있을 경우
if st.session_state.topics:
    if st.session_state.current_topic_index < len(st.session_state.topics):
        current_topic = st.session_state.topics[st.session_state.current_topic_index]  # 현재 주제 가져오기
        st.header("자유 토론 진행 중")
        st.subheader(f"현재 주제: {current_topic}")

        # 채팅 로그 표시: 사용자와 AI 간의 대화를 기록하고 화면에 출력합니다.
        for message in st.session_state.messages:
            role = "나" if message["role"] == "user" else "AI 사회자"
            st.write(f"**{role}:** {message['content']}")

        # 사용자 입력 받기: 사용자가 의견을 입력합니다.
        user_input_key = f"chat_input_{st.session_state.current_topic_index}"
        user_input = st.text_input("의견을 입력하세요:", key=user_input_key)

        if st.button("전송", key=f"send_button_{st.session_state.current_topic_index}") and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})  # 사용자 메시지를 저장

            # AI 응답 생성: 사용자의 입력에 대한 AI의 응답을 생성합니다.
            ai_response = f"현재 의견: {user_input}. 이에 대해 자유 토론을 진행해 주세요."
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

            # 자유 토론 시간 제공: 제한된 시간 동안 토론을 진행합니다.
            st.write("💡 자유 토론 시간: 3분")
            with st.spinner("자유 토론 중..."):
                time.sleep(10)  # 테스트 목적으로 10초 대기 (실제는 3분 권장)

            st.write("⏳ 자유 토론 시간이 종료되었습니다.")

            # 현재 주제의 응답 저장
            st.session_state.all_responses.append([msg["content"] for msg in st.session_state.messages if msg["role"] == "user"])

            # 다음 주제로 이동
            st.session_state.messages = []  # 메시지 초기화
            st.session_state.current_topic_index += 1

    # 마지막 주제라면 요약 생성
    if st.session_state.current_topic_index == len(st.session_state.topics):
        st.write("모든 주제가 완료되었습니다. 요약을 생성합니다.")

        try:
            st.session_state.summary = st.session_state.rag_gpt.summarize_meeting(
                st.session_state.topics, st.session_state.all_responses
            )
            st.success("요약이 완료되었습니다!")
            st.write(st.session_state.summary)
        except Exception as e:
            st.error(f"요약 생성 중 오류 발생: {e}")

# 요약 페이지 표시: 생성된 요약을 화면에 출력합니다.
if st.session_state.summary:
    st.header("독서 모임 요약")
    st.write(st.session_state.summary)
