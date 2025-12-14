"""
PDF 동화책 처리 모듈
StoryWeaver PDF에서 텍스트와 이미지를 추출합니다.
"""

import fitz  # PyMuPDF
import base64
from io import BytesIO
from PIL import Image
import uuid
import json
try:
    from gemini_helper import translate_to_korean as gemini_translate
    USE_GEMINI = True
except:
    from deep_translator import GoogleTranslator
    USE_GEMINI = False


class PDFProcessor:
    """PDF 동화책 처리 클래스"""

    def __init__(self, json_file='stories.json'):
        self.json_file = json_file
        if not USE_GEMINI:
            self.translator = GoogleTranslator(source='en', target='ko')
        else:
            self.translator = None

    def process_pdf(self, pdf_file, title=None):
        """
        PDF 파일에서 동화책 데이터를 추출합니다.

        Args:
            pdf_file: 업로드된 PDF 파일 객체
            title: 동화책 제목 (없으면 자동 생성)

        Returns:
            dict: 동화책 데이터 또는 {'error': 에러메시지} (실패 시)
        """
        try:
            # PDF 파일 읽기
            pdf_bytes = pdf_file.read()
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

            # 제목 설정
            if not title:
                title = pdf_file.name.replace('.pdf', '')

            print(f"PDF 처리 시작: {title}")
            print(f"총 페이지 수: {len(pdf_document)}")

            pages = []

            # 각 페이지 처리
            for page_num in range(len(pdf_document)):
                print(f"\n페이지 {page_num + 1}/{len(pdf_document)} 처리 중...")

                page = pdf_document[page_num]

                # 텍스트 추출 (여러 방법 시도)
                text = page.get_text().strip()

                # 텍스트가 없으면 다른 방법 시도
                if not text:
                    text = page.get_text("text").strip()

                if not text:
                    # blocks 방식으로 시도
                    blocks = page.get_text("blocks")
                    text_parts = []
                    for block in blocks:
                        if len(block) >= 5 and block[4].strip():
                            text_parts.append(block[4].strip())
                    text = ' '.join(text_parts)

                # 빈 페이지 건너뛰기
                if not text or len(text) < 3:
                    print(f"  - 빈 페이지, 건너뜀")
                    continue

                # 텍스트 정리 (불필요한 줄바꿈 제거)
                text = ' '.join(text.split())

                # "page" 단어 제거 (페이지 번호 표시 제거)
                import re
                # "page 1", "Page 1", "page1" 등의 패턴 제거
                text = re.sub(r'\bpage\s*\d*\b', '', text, flags=re.IGNORECASE)
                text = re.sub(r'\d+\s*/\s*\d+', '', text)  # "1 / 10" 같은 페이지 번호 제거
                text = text.strip()

                # 빈 텍스트가 되면 건너뛰기
                if not text or len(text) < 3:
                    print(f"  - 페이지 번호만 있음, 건너뜀")
                    continue

                # 너무 긴 텍스트는 자르기 (동화책이므로 한 페이지당 적당한 길이)
                if len(text) > 500:
                    text = text[:500] + '...'

                try:
                    print(f"  - 텍스트: {text[:50]}...")
                except UnicodeEncodeError:
                    print(f"  - 텍스트 추출됨 (인코딩 문제로 표시 불가)")

                # 이미지 추출
                image_data_url = self._extract_page_image(page, page_num)

                # 한국어 번역
                print(f"  - 번역 중...")
                ko_text = self._translate_to_korean(text)

                page_data = {
                    'image_url': image_data_url,
                    'en': text,
                    'ko': ko_text
                }

                pages.append(page_data)

            pdf_document.close()

            if not pages:
                error_msg = "추출된 페이지가 없습니다. PDF에 텍스트가 없거나 이미지로만 구성되어 있을 수 있습니다."
                print(f"오류: {error_msg}")
                return {'error': error_msg, 'pages': []}

            # 동화책 데이터 구조 생성
            story_data = {
                'id': str(uuid.uuid4()),
                'title': title,
                'source_url': 'pdf_upload',
                'pages': pages
            }

            print(f"\nPDF 처리 완료! 총 {len(pages)} 페이지")
            return story_data

        except UnicodeEncodeError as e:
            print(f"인코딩 오류 (무시 가능): {str(e)}")
            # 이미 story_data가 생성되었다면 반환
            if 'story_data' in locals() and story_data:
                return story_data
            error_msg = f"인코딩 오류: {str(e)}"
            return {'error': error_msg, 'pages': []}
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"PDF 처리 중 오류 발생: {str(e)}")
            print(f"오류 타입: {type(e).__name__}")
            print(f"상세 오류 정보:\n{error_details}")

            error_msg = f"{type(e).__name__}: {str(e)}"
            return {'error': error_msg, 'error_details': error_details, 'pages': []}

    def _extract_page_image(self, page, page_num):
        """
        페이지를 이미지로 변환하고 base64 data URL로 반환합니다.
        """
        try:
            # 페이지를 이미지로 렌더링 (해상도 조절: 2.0 = 2배)
            zoom = 2.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # PIL Image로 변환
            img_data = pix.tobytes("png")
            img = Image.open(BytesIO(img_data))

            # 이미지 크기 조절 (너무 크면 용량 문제)
            max_width = 800
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # base64 인코딩
            buffered = BytesIO()
            img.save(buffered, format="PNG", optimize=True)
            img_base64 = base64.b64encode(buffered.getvalue()).decode()

            # data URL 생성
            data_url = f"data:image/png;base64,{img_base64}"

            print(f"  - 이미지 추출 완료 (크기: {len(img_base64)} bytes)")
            return data_url

        except Exception as e:
            print(f"  - 이미지 추출 오류: {str(e)}")
            return ""

    def _translate_to_korean(self, text):
        """영어 텍스트를 한국어로 번역합니다."""
        try:
            if USE_GEMINI:
                # Gemini API 사용
                return gemini_translate(text)
            else:
                # Deep Translator 사용
                if len(text) > 500:
                    sentences = text.split('. ')
                    translated = []
                    for sentence in sentences:
                        if sentence.strip():
                            result = self.translator.translate(sentence)
                            translated.append(result)
                    return '. '.join(translated)
                else:
                    result = self.translator.translate(text)
                    return result
        except Exception as e:
            print(f"  - 번역 오류: {str(e)}")
            return text

    def save_story(self, story_data):
        """동화책을 JSON 파일에 저장합니다."""
        try:
            # 기존 데이터 로드
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    stories = json.load(f)
            except FileNotFoundError:
                stories = []

            # 새 동화책 추가
            stories.append(story_data)

            # 파일에 저장
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(stories, f, ensure_ascii=False, indent=2)

            print(f"'{story_data['title']}' 저장 완료!")
            return True

        except Exception as e:
            print(f"저장 중 오류 발생: {str(e)}")
            return False


# 테스트용 코드
if __name__ == "__main__":
    print("PDF 프로세서 모듈이 로드되었습니다.")
    print("Streamlit 앱에서 PDF를 업로드해주세요.")
