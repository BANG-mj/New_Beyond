import streamlit as st
import time
from RAGBookClubGPT import RAGBookClubGPT
import openai

# OpenAI API 설정
openai.api_key =  "api KEY"

# 상태 초기화
if "rag_gpt" not in st.session_state:
    st.session_state.rag_gpt = None
if "topics" not in st.session_state:
    st.session_state.topics = []
if "current_topic_index" not in st.session_state:
    st.session_state.current_topic_index = 0
if "messages" not in st.session_state:
    st.session_state.messages = []
if "summary" not in st.session_state:
    st.session_state.summary = ""

# PDF 업로드 및 주제 생성
st.title("AI 기반 독서 모임")

uploaded_file = st.file_uploader("PDF 파일 업로드", type=["pdf"])
if uploaded_file:
    pdf_path = f"uploaded_{uploaded_file.name}"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # RAGBookClubGPT 인스턴스 초기화
    try:
        st.session_state.rag_gpt = RAGBookClubGPT(pdf_path, openai.api_key)
        st.success("PDF 파일이 성공적으로 로드되었습니다!")

        # 주제 생성
        user_responses = ["독서 감상문 또는 초기 의견"]  # 사용자 초기 입력 예시
        st.session_state.topics = st.session_state.rag_gpt.generate_topics(user_responses)
        if st.session_state.topics:
            st.success("토론 주제가 성공적으로 생성되었습니다!")
            for idx, topic in enumerate(st.session_state.topics, start=1):
                st.write(f"{idx}. {topic}")
        else:
            st.error("토론 주제를 생성하지 못했습니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")

# 토론 진행
if st.session_state.topics:
    st.header("자유 토론 진행 중")
    current_topic = st.session_state.topics[st.session_state.current_topic_index]
    st.subheader(f"현재 주제: {current_topic}")

    # 채팅 로그 표시
    for message in st.session_state.messages:
        role = "나" if message["role"] == "user" else "AI 사회자"
        st.write(f"**{role}:** {message['content']}")

    # 사용자 입력
    user_input = st.text_input("의견을 입력하세요:", key="chat_input")
    if st.button("전송") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # AI 응답 생성 (다시 발제문을 생성하지 않음)
        ai_response = f"현재 의견: {user_input}. 이에 대해 자유 토론을 진행해 주세요."
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

        # 자유 토론 시간 부여
        st.write("💡 자유 토론 시간: 3분")
        with st.spinner("자유 토론 중..."):
            time.sleep(10)  # 테스트를 위해 10초로 설정

        st.write("⏳ 자유 토론 시간이 종료되었습니다.")

        # 다음 주제로 이동 조건
        if st.session_state.current_topic_index < len(st.session_state.topics) - 1:
            st.session_state.current_topic_index += 1
            st.session_state.messages = []
            st.write("다음 주제로 이동합니다!")
        else:
            st.write("모든 주제가 완료되었습니다. 요약을 생성합니다.")

            # 모임 요약 생성
            all_responses = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
            st.session_state.summary = st.session_state.rag_gpt.summarize_meeting(
                st.session_state.topics, [all_responses]
            )
            st.success("요약이 완료되었습니다!")
            st.write(st.session_state.summary)

# 요약 페이지 표시
if st.session_state.summary:
    st.header("독서 모임 요약")
    st.write(st.session_state.summary)