class ResponseFilter:
    BAD_WORDS = ["욕설1", "욕설2", "비방1"]

    def filter_bad_words(self, responses):
        filtered_responses = []
        for response in responses:
            if not self.contains_bad_words(response):
                filtered_responses.append(response)
        return filtered_responses

    def contains_bad_words(self, text):
        for bad_word in self.BAD_WORDS:
            if bad_word in text:
                return True
        return False
