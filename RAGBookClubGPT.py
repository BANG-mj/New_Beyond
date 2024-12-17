from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import time

class RAGBookClubGPT:
    def __init__(self, pdf_path, api_key, persist_directory="chroma_db"):
        """
        RAG 기반 독서 모임 AI 초기화
        pdf_path: 독서 모임 관련 PDF 문서 경로
        api_key: OpenAI API 키
        persist_directory: Chroma 데이터베이스 디렉토리
        """
        loader = PyPDFLoader(pdf_path)
        self.docs = loader.load()

        embeddings_model = OpenAIEmbeddings(openai_api_key=api_key)
        self.db = Chroma.from_documents(
            self.docs,
            embeddings_model,
            persist_directory=persist_directory
        )
        self.db.persist()  # 데이터베이스를 디스크에 저장

        self.retriever = self.db.as_retriever()
        self.llm = ChatOpenAI(model_name="gpt-4", api_key=api_key)
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever
        )

    def generate_topics(self, user_responses):
        """
        RAG 기반으로 발제문 생성
        user_responses: 참가자 감상문
        """

        system_message = "Generate three non-political, open-ended discussion topics in Korean based on this book. The topics must end with a sentence."
        user_message = "\n".join(user_responses)

        # RAG 기반 문맥 검색 및 발제문 생성
        context_docs = self.retriever.get_relevant_documents("발제문 생성에 필요한 주요 내용")
        context_text = "\n".join(doc.page_content for doc in context_docs)

        prompt = f"{system_message}\n\nPDF 문서 내용:\n{context_text}\n\n참가자 감상문:\n{user_message}"
        response = self.llm.predict(prompt)

        # 발제문 나누기 및 공백 제거
        topics = [topic.strip() for topic in response.split("\n") if topic.strip()]
        if len(topics) < 3:
            print("⚠️ 발제문 생성에 실패했습니다. 출력을 확인하세요.")
            print(response)
            return []

        print("선정된 발제문:")
        for topic in topics:
            print(f"- {topic}")

        return topics

    def collect_responses(self, topic):
        """
        주어진 주제에 대해 참가자들의 의견을 수집하고, 욕설 및 비방 내용을 필터링하는 메서드
        """

        print(f'\n주제: {topic}')
        print('이 주제에 대해 의견을 작성해 주세요.')

        responses = []
        while True:
            user_input = input("사용자 입력 (형식: 사용자명: 의견, 종료 시 '종료' 입력): ").strip()
            if user_input.lower() == "종료":
                break

            try:
                user, response = user_input.split(":", 1)
                responses.append(f"{user.strip()}: {response.strip()}")
            except ValueError:
                print("잘못된 입력 형식입니다. '사용자명: 의견' 형식으로 입력해주세요.")

        filtered_responses = self.filter_responses(responses)
        print('필터링된 의견:')
        for response in filtered_responses:
            print(response)

        return filtered_responses

    def filter_responses(self, responses):
        """
        참가자들의 응답에서 욕설이나 비방이 포함된 내용을 필터링하는 메서드.
        """

        bad_words = ['욕설', '비방']
        filtered = [response for response in responses if not any(bad_word in response for bad_word in bad_words)]
        return filtered


    def facilitate_free_discussion(self, opinion, time_limit=10):
        """
        특정 의견에 대한 자유 토의를 제한 시간 동안 진행
        opinion: 논의 중심이 될 사용자 의견
        time_limit: 제한 시간(초 단위)
        """
        # 테스트를 위해 test_limit = 10으로 설정. 원래는 180
        print(f"💡이 의견에 대해 3분간 자유롭게 이야기를 나눠주세요")
        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            remaining_time = time_limit - elapsed_time

            if remaining_time <= 0:
                print("\n⏳ 자유토의 시간이 종료되었습니다.")
                break

            print(f"⏱️ 남은 시간: {int(remaining_time)}초", end="\r")
            time.sleep(1)

        print("다음 의견으로 넘어갑니다.")

    def summarize_meeting(self, topics, all_responses):
        """
        RAG 기반으로 모임 내용을 요약하는 메서드
        topics: 논의된 주제들
        all_responses: 참가자들의 모든 응답
        """

        print('\n모임 내용을 요약합니다...')
        summary_prompt = "다음은 독서 모임에서 논의된 내용입니다. 각 주제에 대해 요약을 작성해줘.:\n"

        for i, topic in enumerate(topics):
            summary_prompt += f"주제 {i + 1}: {topic}\n응답:\n" + "\n".join(all_responses[i]) + "\n"

        response = self.llm.predict(summary_prompt)
        summary = response.strip()

        print("모임 요약:")
        print(summary)

    def run_meeting(self, user_responses):
        """
        전체 독서 모임 흐름 실행
        """

        topics = self.generate_topics(user_responses)
        if not topics:
            print("모임을 시작할 수 없습니다. 발제문을 생성하지 못했습니다.")
            return

        all_responses = []
        for topic in topics:
            responses = self.collect_responses(topic)
            all_responses.append(responses)

            for opinion in responses:
                print(f"현재 의견: {opinion}")
                self.facilitate_free_discussion(opinion, time_limit=10) # 테스트를 위해 10초로 설정

        self.summarize_meeting(topics, all_responses)
