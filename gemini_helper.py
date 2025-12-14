"""
Gemini API 헬퍼 모듈
번역, 발음 평가, 퀴즈 생성 등을 Gemini API로 처리합니다.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일 로드
load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
else:
    model = None


def translate_to_korean(text):
    """
    영어 텍스트를 한국어로 번역합니다.

    Args:
        text (str): 영어 텍스트

    Returns:
        str: 한국어 번역
    """
    print(f"[DEBUG] translate_to_korean 함수 호출됨")
    print(f"[DEBUG] 입력 텍스트: {text[:50]}..." if len(text) > 50 else f"[DEBUG] 입력 텍스트: {text}")
    print(f"[DEBUG] model 객체 존재 여부: {model is not None}")

    if not model:
        # Gemini API가 설정되지 않은 경우 대체 번역기 사용
        print(f"[DEBUG] Gemini model이 없음. deep_translator 사용")
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='en', target='ko')
            result = translator.translate(text)
            print(f"[DEBUG] deep_translator 번역 결과: {result[:50]}..." if len(result) > 50 else f"[DEBUG] deep_translator 번역 결과: {result}")
            return result
        except Exception as e:
            print(f"[DEBUG] deep_translator 오류: {str(e)}")
            return text

    try:
        prompt = f"""다음 영어 문장을 9살 어린이가 이해하기 쉬운 자연스러운 한국어로 번역해주세요.
동화책 문장이므로 부드럽고 친근한 표현을 사용해주세요.

영어: {text}

한국어 번역만 출력하고, 다른 설명은 하지 마세요."""

        print(f"[DEBUG] Gemini API 호출 시작...")
        response = model.generate_content(prompt)
        result = response.text.strip()
        print(f"[DEBUG] Gemini 번역 성공!")
        print(f"[DEBUG] 번역 결과: {result[:50]}..." if len(result) > 50 else f"[DEBUG] 번역 결과: {result}")
        return result
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini 번역 오류: {error_msg}")
        print(f"[DEBUG] 오류 타입: {type(e).__name__}")

        # Gemini API 할당량 초과 또는 오류 시 deep_translator로 fallback
        print(f"[DEBUG] Gemini API 실패. deep_translator로 전환합니다...")
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='en', target='ko')
            result = translator.translate(text)
            print(f"[DEBUG] deep_translator 번역 성공: {result[:50]}..." if len(result) > 50 else f"[DEBUG] deep_translator 번역 성공: {result}")
            return result
        except Exception as fallback_error:
            print(f"[DEBUG] deep_translator도 실패: {str(fallback_error)}")
            # 최후의 수단: 원문 반환
            return text


def evaluate_pronunciation(original_text, spoken_text):
    """
    발음을 평가하고 상세한 피드백을 제공합니다.

    Args:
        original_text (str): 원본 영어 문장
        spoken_text (str): 사용자가 말한 텍스트 (STT 결과)

    Returns:
        dict: {
            'score': float (0-1),
            'feedback': str,
            'is_good': bool
        }
    """
    if not model:
        # Gemini API가 없으면 간단한 유사도로 평가
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, original_text.lower(), spoken_text.lower()).ratio()

        is_good = similarity >= 0.7
        feedback = "참 잘했어요! 완벽해요!" if similarity >= 0.7 else \
                   "좋아요! 조금만 더 연습해봐요!" if similarity >= 0.5 else \
                   "다시 한 번 해볼까요? 천천히 따라해봐요!"

        return {
            'score': similarity,
            'feedback': feedback,
            'is_good': is_good
        }

    try:
        prompt = f"""당신은 9살 어린이를 위한 영어 발음 선생님입니다.

원본 문장: {original_text}
아이가 말한 문장: {spoken_text}

아이의 발음을 평가하고, 격려하는 피드백을 한국어로 작성해주세요.

다음 형식으로 답변해주세요:
점수: [0-100 사이의 숫자]
피드백: [격려하는 한마디]

- 점수가 70점 이상이면 칭찬을 많이 해주세요
- 점수가 50-70점이면 격려하며 조금 더 연습하도록 유도해주세요
- 점수가 50점 미만이면 다시 도전하도록 친절하게 독려해주세요
- 피드백은 한 문장으로 짧고 친근하게 작성해주세요"""

        response = model.generate_content(prompt)
        result_text = response.text.strip()

        # 결과 파싱
        lines = result_text.split('\n')
        score = 0.5
        feedback = "잘했어요! 계속 연습해봐요!"

        for line in lines:
            if '점수:' in line or 'Score:' in line or '점수 :' in line:
                try:
                    score_str = line.split(':')[1].strip()
                    # 숫자만 추출
                    import re
                    numbers = re.findall(r'\d+', score_str)
                    if numbers:
                        score = int(numbers[0]) / 100.0
                except:
                    pass
            elif '피드백:' in line or 'Feedback:' in line or '피드백 :' in line:
                feedback = line.split(':', 1)[1].strip()

        is_good = score >= 0.7

        return {
            'score': score,
            'feedback': feedback,
            'is_good': is_good
        }
    except Exception as e:
        print(f"Gemini 발음 평가 오류: {str(e)}")
        # 오류 시 기본 평가
        return {
            'score': 0.5,
            'feedback': "좋아요! 계속 연습해봐요!",
            'is_good': False
        }


def generate_vocabulary_quiz(story):
    """
    동화책 내용을 기반으로 창의적인 단어 퀴즈를 생성합니다.

    Args:
        story (dict): 동화책 데이터

    Returns:
        dict: {
            'question': str,
            'options': list of dict,
            'correct': str
        }
    """
    if not model:
        # Gemini API가 없으면 기존 방식 사용
        import random
        all_words = []
        for page in story['pages']:
            if page['en'] and page['ko']:
                words = page['en'].split()
                valid_words = [w.strip('.,!?;:').lower() for w in words if len(w.strip('.,!?;:')) >= 3]
                for word in valid_words:
                    all_words.append({
                        'en': word,
                        'ko': page['ko']
                    })

        if len(all_words) < 3:
            return None

        correct = random.choice(all_words)
        wrong_answers = [w for w in all_words if w['en'] != correct['en']]

        if len(wrong_answers) < 2:
            return None

        options = random.sample(wrong_answers, min(2, len(wrong_answers)))
        options.append(correct)
        random.shuffle(options)

        return {
            'question': correct['en'],
            'options': options,
            'correct': correct['ko']
        }

    try:
        # 동화책의 모든 텍스트 수집
        all_texts = []
        for page in story['pages']:
            if page['en']:
                all_texts.append(page['en'])

        story_content = " ".join(all_texts[:5])  # 처음 5페이지만 사용

        prompt = f"""다음은 어린이 동화책의 내용입니다:

{story_content}

이 동화책 내용을 기반으로 9살 어린이를 위한 영어 단어 퀴즈를 하나 만들어주세요.

다음 형식으로 답변해주세요:
단어: [영어 단어]
정답: [한국어 뜻]
오답1: [다른 한국어 뜻]
오답2: [또 다른 한국어 뜻]

- 동화책에 나온 주요 단어 중 하나를 선택하세요
- 정답과 오답은 명확하게 구분되어야 합니다
- 오답도 그럴듯하게 만들어주세요"""

        response = model.generate_content(prompt)
        result_text = response.text.strip()

        # 결과 파싱
        lines = result_text.split('\n')
        question = ""
        correct = ""
        options = []

        for line in lines:
            line = line.strip()
            if '단어:' in line or 'Word:' in line:
                question = line.split(':', 1)[1].strip()
            elif '정답:' in line or 'Correct:' in line:
                correct = line.split(':', 1)[1].strip()
                options.append({'en': question, 'ko': correct})
            elif '오답' in line or 'Wrong' in line:
                wrong = line.split(':', 1)[1].strip()
                options.append({'en': question + '_wrong', 'ko': wrong})

        if len(options) >= 3 and question and correct:
            import random
            random.shuffle(options)
            return {
                'question': question,
                'options': options,
                'correct': correct
            }
        else:
            # 파싱 실패 시 None 반환
            return None

    except Exception as e:
        print(f"Gemini 퀴즈 생성 오류: {str(e)}")
        return None


def extract_key_vocabulary(story):
    """
    동화책 내용에서 핵심 단어를 추출하고 설명을 생성합니다.

    Args:
        story (dict): 동화책 데이터

    Returns:
        dict: {
            'explanation': str,  # 핵심 단어와 문법 설명
            'vocabulary': list of dict  # 단어 목록
        }
    """
    if not model:
        # Gemini API가 없으면 빈 결과 반환
        return {'explanation': '', 'vocabulary': []}

    try:
        # 동화책 전체 텍스트 수집
        all_texts = []
        for page in story['pages']:
            if page['en']:
                all_texts.append(page['en'])

        story_content = " ".join(all_texts)

        prompt = f"""다음은 어린이 동화책의 내용입니다:

{story_content}

이 동화책의 내용을 기반으로 핵심 단어와 문법을 설명해주세요. 또한, 핵심 단어 30개 이하를 추출하고, 각 단어에 대해 영어 단어와 한국어 뜻을 제공해주세요.

다음 형식으로 답변해주세요:

[핵심 단어와 문법 설명]
- 핵심 단어들에 대한 설명과 문법 설명
- 어린이가 이해하기 쉬운 언어로

[단어 목록]
- 단어: [영어 단어] | 뜻: [한국어 뜻]
- 각 줄마다 하나의 단어를 표시

- 핵심 단어는 최대 30개까지 추출해주세요
- 동화책에서 자주 등장하거나 중요한 단어 위주로 선택하세요
- 어린이가 학습하기 좋은 기초 단어를 선정하세요"""

        response = model.generate_content(prompt)
        result_text = response.text.strip()

        # 결과 파싱
        lines = result_text.split('\n')
        
        explanation = ""
        vocabulary = []
        in_vocabulary_section = False

        for line in lines:
            line = line.strip()
            if '[단어 목록]' in line:
                in_vocabulary_section = True
                continue
            
            if in_vocabulary_section:
                # 단어 형식: - 단어: [영어] | 뜻: [한국어]
                import re
                match = re.search(r'-\s*단어:\s*([^\|]+)\s*\|\s*뜻:\s*(.+)', line)
                if match:
                    english_word = match.group(1).strip()
                    korean_meaning = match.group(2).strip()
                    
                    # 불필요한 문장 제거 (예: "영어", "한국어" 등)
                    if english_word.lower() not in ['영어', '한국어'] and korean_meaning.lower() not in ['영어', '한국어']:
                        vocabulary.append({
                            'en': english_word,
                            'ko': korean_meaning
                        })
            else:
                if not '[핵심 단어와 문법 설명]' in line:
                    explanation += line + "\n"

        return {
            'explanation': explanation.strip(),
            'vocabulary': vocabulary[:30]  # 최대 30개로 제한
        }

    except Exception as e:
        print(f"Gemini 단어 추출 오류: {str(e)}")
        return {'explanation': '', 'vocabulary': []}


def extract_vocabulary_simple(story):
    """
    Gemini API 없이 간단하게 단어를 추출합니다. (대체 방법)

    Args:
        story (dict): 동화책 데이터

    Returns:
        dict: {
            'explanation': str,
            'vocabulary': list of dict
        }
    """
    try:
        from deep_translator import GoogleTranslator
        import re
        from collections import Counter

        translator = GoogleTranslator(source='en', target='ko')

        # 모든 텍스트 수집
        all_text = []
        for page in story['pages']:
            if page['en']:
                all_text.append(page['en'])

        full_text = ' '.join(all_text)

        # 단어 추출 (3글자 이상의 단어만)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', full_text.lower())

        # 불용어 제거
        stop_words = {
            'the', 'and', 'was', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
            'her', 'when', 'there', 'use', 'your', 'how', 'said', 'each', 'she',
            'which', 'their', 'will', 'way', 'about', 'many', 'then', 'them',
            'would', 'like', 'him', 'into', 'has', 'two', 'more', 'her', 'could',
            'make', 'than', 'first', 'been', 'its', 'who', 'now', 'people', 'out',
            'other', 'were', 'what', 'this', 'that', 'with', 'have', 'from', 'they'
        }

        # 불용어 제거 및 빈도수 계산
        filtered_words = [w for w in words if w not in stop_words]
        word_freq = Counter(filtered_words)

        # 상위 30개 단어 선택
        top_words = [word for word, count in word_freq.most_common(30)]

        # 번역
        vocabulary = []
        for word in top_words:
            try:
                ko_translation = translator.translate(word)
                vocabulary.append({
                    'en': word,
                    'ko': ko_translation
                })
            except Exception as e:
                print(f"번역 실패: {word} - {str(e)}")
                continue

        explanation = f"이 동화책에서 자주 등장하는 {len(vocabulary)}개의 핵심 단어입니다."

        return {
            'explanation': explanation,
            'vocabulary': vocabulary
        }

    except Exception as e:
        print(f"간단한 단어 추출 오류: {str(e)}")
        return {'explanation': '', 'vocabulary': []}


def generate_vocabulary_cards(vocabulary_list):
    """
    단어 목록을 기반으로 카드 학습을 위한 문제를 생성합니다.

    Args:
        vocabulary_list (list): 단어 목록

    Returns:
        list: 카드 문제 목록
    """
    import random
    
    cards = []
    
    for vocab in vocabulary_list:
        # 영어 -> 한국어 카드
        cards.append({
            'type': 'en_to_ko',
            'question': vocab['en'],
            'answer': vocab['ko'],
            'options': []
        })
        
        # 한국어 -> 영어 카드
        cards.append({
            'type': 'ko_to_en',
            'question': vocab['ko'],
            'answer': vocab['en'],
            'options': []
        })
    
    # 문제와 정답을 섞음
    random.shuffle(cards)
    
    # 선택지 생성 (각 카드에 대한 오답 선택지 생성)
    for card in cards:
        # 동일한 유형의 다른 단어 중에서 선택지 생성
        if card['type'] == 'en_to_ko':
            other_options = [v['ko'] for v in vocabulary_list if v['ko'] != card['answer']]
        else:  # ko_to_en
            other_options = [v['en'] for v in vocabulary_list if v['en'] != card['answer']]
        
        # 3개의 오답 선택지를 무작위로 선택
        if len(other_options) >= 3:
            wrong_options = random.sample(other_options, 3)
        else:
            wrong_options = other_options
        
        card['options'] = [card['answer']] + wrong_options
        random.shuffle(card['options'])
    
    return cards


# 테스트용 코드
if __name__ == "__main__":
    print("Gemini API 헬퍼 모듈")

    if GEMINI_API_KEY:
        print("✓ Gemini API 키가 설정되었습니다.")

        # 번역 테스트
        test_text = "This is a cat."
        translation = translate_to_korean(test_text)
        print(f"\n번역 테스트:")
        print(f"영어: {test_text}")
        print(f"한국어: {translation}")
    else:
        print("✗ Gemini API 키가 설정되지 않았습니다.")
        print("  .env 파일에 GEMINI_API_KEY를 추가해주세요.")
