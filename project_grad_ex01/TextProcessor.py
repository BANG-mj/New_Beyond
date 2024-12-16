class TextProcessor:
    def combine_text(self, texts):
        return "\n".join(texts)

    def prepare_context_for_topics(self, context_docs):
        # 주요 문장만 추출 (간단한 요약)
        key_sentences = []
        for doc in context_docs:
            sentences = doc.split(". ")
            key_sentences.extend(sentences[:10])  # 최대 10개의 문장 추출
        return key_sentences
