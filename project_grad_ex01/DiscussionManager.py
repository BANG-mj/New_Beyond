class DiscussionManager:
    def create_topics(self, topics):
        # 주제 생성 로직
        for topic in topics:
            print(f"새로운 토픽 생성: {topic}")

    def collect_user_responses(self, topic):
        # 사용자 응답 수집 (예시로 고정된 응답을 반환)
        return ["응답1", "응답2", "응답3"]

    def start_free_discussion(self):
        # 자유 토론 시작
        print("자유 토론 시작!")

    def summarize_meeting(self, topics, all_responses):
        # 토론 요약
        print("토론 요약:")
        for i, topic in enumerate(topics):
            print(f"주제: {topic}")
            print(f"응답: {', '.join(all_responses[i])}")
