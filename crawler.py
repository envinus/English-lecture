"""
StoryWeaver 동화책 크롤러 모듈
StoryWeaver(storyweaver.org.in) API를 사용하여 동화책 데이터를 가져옵니다.
"""

import requests
import json
import uuid
from deep_translator import GoogleTranslator
import time
import re


class StoryWeaverCrawler:
    """StoryWeaver 동화책 크롤러 클래스"""

    def __init__(self, json_file='stories.json'):
        self.json_file = json_file
        self.translator = GoogleTranslator(source='en', target='ko')
        self.api_base = 'https://storyweaver.org.in/api/v1'

    def extract_story_id(self, url):
        """
        URL에서 story ID를 추출합니다.
        예: https://storyweaver.org.in/stories/12345-title/read -> 12345
        """
        # 패턴: stories/ 뒤의 숫자
        match = re.search(r'/stories/(\d+)', url)
        if match:
            return match.group(1)
        return None

    def crawl_story(self, url):
        """
        StoryWeaver URL에서 동화책 데이터를 크롤링합니다.

        Args:
            url (str): StoryWeaver 동화책 URL

        Returns:
            dict: 크롤링된 동화책 데이터 또는 None (실패 시)
        """
        try:
            # URL에서 story ID 추출
            story_id = self.extract_story_id(url)
            if not story_id:
                print("오류: URL에서 story ID를 찾을 수 없습니다.")
                return None

            print(f"Story ID: {story_id}")

            # API를 통해 동화책 데이터 가져오기
            api_url = f"{self.api_base}/stories/{story_id}.json"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://storyweaver.org.in/',
                'Origin': 'https://storyweaver.org.in',
            }

            print(f"API 호출: {api_url}")
            response = requests.get(api_url, headers=headers, timeout=30)

            # 403이면 다른 방법 시도
            if response.status_code == 403:
                print("API 접근 거부됨. 대체 방법 시도...")
                # 직접 웹페이지에서 데이터 추출 시도
                return self._crawl_from_webpage(url, story_id)

            response.raise_for_status()

            data = response.json()

            # 동화책 정보 추출
            story = data.get('data', {})
            title = story.get('title', 'Untitled Story')
            pages_data = story.get('pages', [])

            print(f"제목: {title}")
            print(f"페이지 수: {len(pages_data)}")

            if not pages_data:
                print("오류: 페이지 데이터가 없습니다.")
                return None

            # 페이지 처리
            pages = []
            for i, page in enumerate(pages_data):
                print(f"페이지 {i+1}/{len(pages_data)} 처리 중...")

                # 이미지 URL
                image_url = ''
                if page.get('coverImage'):
                    image_url = page['coverImage'].get('sizes', [{}])[-1].get('url', '')
                elif page.get('illustration_crop'):
                    image_url = page['illustration_crop'].get('image_urls', {}).get('size7', '')

                # 영어 텍스트
                en_text = page.get('content', '').strip()

                # 빈 페이지는 건너뛰기
                if not en_text:
                    continue

                # 한국어 번역
                ko_text = self._translate_to_korean(en_text) if en_text else ""

                page_data = {
                    'image_url': image_url,
                    'en': en_text,
                    'ko': ko_text
                }

                pages.append(page_data)

                # API 호출 제한을 위한 딜레이
                if en_text:
                    time.sleep(0.5)

            if not pages:
                print("오류: 유효한 페이지가 없습니다.")
                return None

            # 동화책 데이터 구조 생성
            story_data = {
                'id': str(uuid.uuid4()),
                'title': title,
                'source_url': url,
                'pages': pages
            }

            print(f"크롤링 완료! 총 {len(pages)} 페이지")
            return story_data

        except requests.exceptions.RequestException as e:
            print(f"네트워크 오류: {str(e)}")
            return None
        except Exception as e:
            print(f"크롤링 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _crawl_from_webpage(self, url, story_id):
        """
        웹페이지에서 직접 동화책 데이터를 추출합니다 (fallback 방법).
        """
        try:
            from bs4 import BeautifulSoup

            print("웹페이지에서 데이터 추출 시도...")

            # 읽기 모드 URL로 변환
            read_url = f"https://storyweaver.org.in/en/stories/{story_id}/read"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            response = requests.get(read_url, headers=headers, timeout=30)

            if response.status_code != 200:
                print(f"웹페이지 접근 실패: {response.status_code}")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            # 제목 추출
            title = "Untitled Story"
            title_elem = soup.find('h1')
            if title_elem:
                title = title_elem.get_text().strip()

            # 페이지 데이터가 JavaScript로 로드되는 경우 script 태그에서 JSON 찾기
            script_tags = soup.find_all('script')
            story_data_json = None

            for script in script_tags:
                script_text = script.string
                if script_text and 'storyData' in script_text:
                    # JSON 데이터 추출 시도
                    import re
                    match = re.search(r'storyData\s*=\s*({.*?});', script_text, re.DOTALL)
                    if match:
                        try:
                            story_data_json = json.loads(match.group(1))
                            break
                        except:
                            pass

            if story_data_json:
                # JSON에서 페이지 데이터 추출
                pages = []
                pages_data = story_data_json.get('pages', [])

                for page in pages_data:
                    en_text = page.get('content', '').strip()
                    if not en_text:
                        continue

                    image_url = ''
                    if page.get('illustration_crop'):
                        image_url = page['illustration_crop'].get('image_urls', {}).get('size7', '')

                    ko_text = self._translate_to_korean(en_text)

                    pages.append({
                        'image_url': image_url,
                        'en': en_text,
                        'ko': ko_text
                    })
                    time.sleep(0.5)

                if pages:
                    return {
                        'id': str(uuid.uuid4()),
                        'title': title,
                        'source_url': url,
                        'pages': pages
                    }

            print("웹페이지에서 데이터 추출 실패")
            return None

        except Exception as e:
            print(f"웹페이지 크롤링 오류: {str(e)}")
            return None

    def _translate_to_korean(self, text):
        """영어 텍스트를 한국어로 번역합니다."""
        try:
            # 텍스트가 너무 길면 나눠서 번역
            if len(text) > 500:
                # 문장 단위로 나누기
                sentences = text.split('. ')
                translated = []
                for sentence in sentences:
                    if sentence.strip():
                        result = self.translator.translate(sentence)
                        translated.append(result)
                        time.sleep(0.3)
                return '. '.join(translated)
            else:
                result = self.translator.translate(text)
                return result
        except Exception as e:
            print(f"번역 오류: {str(e)}")
            return text

    def save_story(self, story_data):
        """크롤링된 동화책을 JSON 파일에 저장합니다."""
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

    def get_all_stories(self):
        """저장된 모든 동화책을 반환합니다."""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"파일 읽기 오류: {str(e)}")
            return []


# 테스트용 코드
if __name__ == "__main__":
    crawler = StoryWeaverCrawler()

    # 테스트 URL
    # 실제 StoryWeaver URL로 교체하여 테스트
    test_url = input("StoryWeaver 동화책 URL을 입력하세요: ")

    print("\n동화책 크롤링 시작...")
    story = crawler.crawl_story(test_url)

    if story:
        print(f"\n제목: {story['title']}")
        print(f"페이지 수: {len(story['pages'])}")

        if crawler.save_story(story):
            print("\n✅ 저장 완료!")
        else:
            print("\n❌ 저장 실패")
    else:
        print("\n❌ 크롤링 실패")
