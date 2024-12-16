import openai
from PDFLoader import PDFLoader
from TextProcessor import TextProcessor
from ResponseFilter import ResponseFilter
from DiscussionManager import DiscussionManager

class RAGBookClubGPT:
    def __init__(self, file_path):
        if not file_path.endswith(".pdf"):
            raise ValueError("PDF 파일만 지원합니다.")
        self.loader = PDFLoader(file_path)
        self.text_processor = TextProcessor()
        self.response_filter = ResponseFilter()
        self.discussion_manager = DiscussionManager()

    def load_file(self):
        return self.loader.load_pdf()

    def generate_topics(self, user_responses):
        # 텍스트 결합 및 토큰 제한 적용
        combined_text = self.text_processor.combine_text(user_responses)

        # GPT 요청 크기를 제한하기 위해 텍스트를 줄임
        max_characters = 5000  # 5,000자 내외로 제한 (약 2,500 토큰)
        truncated_text = combined_text[:max_characters]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "이 텍스트에서 세 가지 주요 토론 주제를 생성하세요."},
                    {"role": "user", "content": truncated_text},
                ],
            )
            # GPT의 응답에서 주제를 추출
            topics = response["choices"][0]["message"]["content"].split("\n")
            return [topic.strip() for topic in topics if topic.strip()]
        except Exception as e:
            print(f"GPT 호출 실패: {e}")
            return ["GPT 호출 실패: 기본 주제를 사용합니다."]
