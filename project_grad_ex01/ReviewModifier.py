import openai
import os
import difflib

# OpenAI API 키 설정
# 여기에 키 설정

def correct_spelling_and_grammar(user_input):
    """
    독서 감상문 맞춤법과 문법을 교정하는 함수
    """

    prompt = (
        "다음 텍스트의 맞춤법과 문법을 수정해 주세요. 필요하면 부드럽게 수정해주세요.\n\n"
        f"원문:\n{user_input}\n\n수정된 문장:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 사용할 GPT 모델, mini로 수정
            messages=[
                {"role": "system", "content": "You are a professor of Korean language at a university. Please edit the book review written by a student.Do not change the content. Just edit the spelling errors, awkward sentences, or context. And explain the parts you edited."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2  # 낮은 값으로 설정해 안정적인 결과를 얻음
        )
        corrected_text = response.choices[0].message.content.strip()
        return corrected_text

    except Exception as e:
        return f"오류가 발생했습니다: {e}"


def highlight_differences(original, corrected):
    """
    원본과 수정된 텍스트의 차이를 강조하는 함수
    - 추가된 부분: **굵은 글씨**
    - 삭제된 부분: ~~취소선~~
    """

    diff = difflib.ndiff(original.split(), corrected.split())
    result = []

    for token in diff:
        if token.startswith("+ "):  # 추가된 부분
            result.append(f"**{token[2:]}**")  # 두꺼운 글씨로 표시
        elif token.startswith("- "):  # 삭제된 부분
            result.append("")
        else:  # 변경 없는 부분
            result.append(token[2:])

    return " ".join(result)

# 사용자 입력 받기
# 예시 데이터(감상문) 출처: https://blog.naver.com/lugenzhe/90103035753
user_review = input("독서 감상문을 입력하세요: ")
corrected_review = correct_spelling_and_grammar(user_review)

# 차이 강조하기
highlighted_review = highlight_differences(user_review, corrected_review)

print("\n[수정된 독서 감상문]")
print(corrected_review)

print("\n[수정된 부분 강조]")
print(highlighted_review)
