import streamlit as st
import openai
import time
import random

# OpenAI API 설정
# 여기에 키 넣기

# 상태 초기화
if "rag_gpt" not in st.session_state:
    st.session_state.rag_gpt = None
if "topics" not in st.session_state:
    st.session_state.topics = []
if "current_topic_index" not in st.session_state:
    st.session_state.current_topic_index = 0  # 현재 주제 인덱스
if "comments_count" not in st.session_state:
    st.session_state.comments_count = 0  # 현재 주제에서 생성된 의견 수
if "messages" not in st.session_state:
    st.session_state.messages = []  # 채팅 메시지 저장
if "summary_page" not in st.session_state:
    st.session_state.summary_page = False  # 요약 페이지 표시 여부

# 참여자 리스트
participants = ["가연", "나연", "다연"]

# OpenAI API 호출 함수 (재시도 로직 포함)
def call_openai_with_retry(messages, model="gpt-4", max_retries=3, retry_delay=5):
    """
    OpenAI API를 호출하고, 실패 시 재시도하는 함수.
    """
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
            )
            return response["choices"][0]["message"]["content"]
        except openai.error.OpenAIError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return "참여자의 의견을 생성하는 중 문제가 발생했습니다. 다시 시도해주세요."

# 주제 발표 및 사용자 의견 처리
def handle_topic_and_user_input(user_input):
    """
    사용자 입력 처리 및 참여자 의견 생성
    """
    current_topic = st.session_state.topics[st.session_state.current_topic_index]

    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 참여자 의견 생성 (1초 간격으로 출력)
    for participant in participants:
        time.sleep(1)
        messages = [
            {"role": "system", "content": f"참여자 {participant}는 '{user_input}'에 대해 100자 이내로 의견을 작성합니다."}
        ]
        opinion = call_openai_with_retry(messages)[:100]
        st.session_state.messages.append({"role": participant, "content": opinion})

    # AI 사회자: 자유 토론 시작 알림
    time.sleep(1)
    st.session_state.messages.append({"role": "assistant", "content": "지금부터 자유 토론이 시작됩니다."})

# 자유 토론 진행
def handle_free_discussion():
    """
    자유 토론 진행 (랜덤 참여자 의견 생성 및 사용자 의견 추가)
    """
    while st.session_state.comments_count < 10:
        # 사용자 입력 확인
        user_input = st.text_input("메시지를 입력하세요 (최대 100자)", key="chat_input", max_chars=100)
        if st.button("전송", key="send_button"):
            if user_input.strip():
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.comments_count += 1

        # 랜덤 참여자 의견 생성
        random_participant = random.choice(participants)
        previous_opinion = random.choice(
            [msg["content"] for msg in st.session_state.messages if msg["role"] != "assistant"]
        )
        time.sleep(1)
        messages = [
            {"role": "system", "content": f"{random_participant}는 '{previous_opinion}'에 대해 100자 이내로 의견을 작성합니다."}
        ]
        random_opinion = call_openai_with_retry(messages)[:100]
        st.session_state.messages.append({"role": random_participant, "content": random_opinion})
        st.session_state.comments_count += 1

# 주제별 진행 로직
def discussion_page():
    st.title("자유 토론 진행 중")
    current_topic = st.session_state.topics[st.session_state.current_topic_index]

    # AI 사회자: 주제 발표
    if st.session_state.comments_count == 0 and not st.session_state.get("topic_announced", False):
        st.session_state.messages.append(
            {"role": "assistant", "content": f"이번 독서모임의 주제는 '{current_topic}'입니다. 의견을 하나씩 보내주세요."}
        )
        st.session_state.topic_announced = True

    # 채팅 로그 출력
    st.write("### 채팅 로그:")
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.write(f"**나**: {message['content']}")
        elif message["role"] == "assistant":
            st.write(f"**AI 사회자**: {message['content']}")
        else:
            st.write(f"**{message['role']}**: {message['content']}")

    # 사용자 입력
    user_input = st.text_input("메시지를 입력하세요 (최대 100자)", key="chat_input", max_chars=100)
    if st.button("전송", key="send_button"):
        if user_input.strip():
            handle_topic_and_user_input(user_input)
            handle_free_discussion()

            # 다음 주제로 이동
            if st.session_state.comments_count >= 10:
                st.session_state.comments_count = 0
                st.session_state.topic_announced = False
                if st.session_state.current_topic_index < len(st.session_state.topics) - 1:
                    st.session_state.current_topic_index += 1
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"다음 주제로 넘어갑니다: '{st.session_state.topics[st.session_state.current_topic_index]}'"}
                    )
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "토의가 끝났습니다."})
                    st.session_state.page = "summary"

# 요약 페이지
def summary_page():
    st.title("독서 모임 요약")
    st.write("### 토론 요약")
    st.write("독서 모임이 성공적으로 끝났습니다. AI 사회자와 참여자들의 의견 요약은 아래와 같습니다.")
    for idx, topic in enumerate(st.session_state.topics, start=1):
        st.write(f"**주제 {idx}:** {topic}")
    st.write("로그를 통해 상세 내용을 확인하세요.")

# PDF 업로드 및 주제 생성 페이지
def main_page():
    st.title("AI 기반 사회자 채팅 시스템")
    st.subheader("PDF 파일에서 텍스트를 추출하고 토론 주제를 생성합니다.")

    # PDF 파일 업로드
    uploaded_file = st.file_uploader("PDF 파일 업로드", type=["pdf"])
    if uploaded_file:
        file_path = uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        from RAGBookClubGPT import RAGBookClubGPT
        st.session_state.rag_gpt = RAGBookClubGPT(file_path)
        file_text = st.session_state.rag_gpt.load_file()
        st.session_state.file_text = file_text

        # 토론 주제 생성
        st.success("PDF 텍스트가 성공적으로 로드되었습니다!")
        user_responses = [st.session_state.file_text]
        st.session_state.topics = st.session_state.rag_gpt.generate_topics(user_responses)[:3]
        st.write("### 생성된 토론 주제:")
        for idx, topic in enumerate(st.session_state.topics, start=1):
            st.write(f"{idx}. {topic}")

        if st.button("자유 토론 시작"):
            st.session_state.page = "discussion"

# 페이지 라우팅
current_page = st.session_state.get("page", "main")

if current_page == "main":
    main_page()
elif current_page == "discussion":
    discussion_page()
elif current_page == "summary":
    summary_page()
