import requests
from bs4 import BeautifulSoup
import json
import os
from collections import defaultdict
from django.core.management.base import BaseCommand

# --- 크롤링 대상 URLS ---
URL_9TO6 = 'https://omoney.kbstar.com/quics?page=C027860' # 9To6 Bank URL (사용자 최종 수정본 반영)
URL_LUNCH_FOCUS = 'https://omoney.kbstar.com/quics?page=C112033' # 점심시간 집중 상담 지점

# --- JSON 파일 저장 경로 설정 ---
CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(CURRENT_SCRIPT_DIR, '..', '..', '..', '..') # final-pjt/final_pjt_back/
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'final_pjt_front', 'public') 

OUTPUT_FILE_9TO6 = os.path.join(OUTPUT_DIR, '9to6_kb_banks.json')
OUTPUT_FILE_LUNCH_FOCUS = os.path.join(OUTPUT_DIR, 'lunch_focus_kb_banks.json')

# 크롤링 대상이 되는 실제 지역명 목록 (KB국민은행 웹사이트 기준)
VALID_REGION_NAMES = [
    "서울", "경기·인천", "강원", "대구·경북", 
    "부산·울산·경남", "세종·대전·충청", "광주·전라·제주"
]

def _crawl_bank_data_by_region(url: str, region_tag_name: str = 'h3', region_class: str = 'tit_dep3 s4'):
    """
    지정된 URL에서 지역별 은행 지점명 데이터를 크롤링합니다.
    h3.tit_dep3.s4 태그를 찾고, 그 내용이 VALID_REGION_NAMES에 있는 경우에만 처리합니다.
    """
    try:
        print(f"INFO: '{url}'에서 데이터 크롤링 중...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: 웹사이트 '{url}'에 접속할 수 없습니다: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    banks_by_region = defaultdict(list)
    
    # 지정된 태그와 클래스로 모든 후보 제목 태그를 찾음
    candidate_title_tags = soup.find_all(region_tag_name, class_=region_class)

    if not candidate_title_tags:
        print(f"WARNING: '{url}'에서 지역명 후보 태그({region_tag_name}.{region_class})를 찾을 수 없습니다.")
        # fallback: 클래스 없이 태그명으로만 다시 시도
        candidate_title_tags = soup.find_all(region_tag_name)
        if not candidate_title_tags:
            print(f"ERROR: '{url}'에서 지역명 후보 태그({region_tag_name})조차 찾을 수 없습니다.")
            return None
        else:
            print(f"INFO: 클래스 없이 '{region_tag_name}' 태그로 지역명 후보를 찾았습니다.")


    found_valid_region = False
    for title_tag in candidate_title_tags:
        region_name = title_tag.text.strip()

        # 실제 지역명인지 VALID_REGION_NAMES 리스트를 통해 확인
        if region_name not in VALID_REGION_NAMES:
            # print(f"DEBUG: 건너뜀 (유효한 지역명 아님): '{region_name}' (from tag: {title_tag.name}.{title_tag.get('class')})")
            continue # 유효한 지역명이 아니면 다음 태그로

        found_valid_region = True
        print(f"INFO: 유효한 지역명 발견: '{region_name}'")
        
        ul_tag = title_tag.find_next_sibling('ul', class_='n_branch_ulist')
        
        if not ul_tag: # 직접적인 형제가 아닐 경우, 부모 레벨에서 다시 찾아보기 (div id="seoul" 같은 구조 고려)
            parent_div = title_tag.parent
            if parent_div:
                 # print(f"DEBUG: '{region_name}'의 부모({parent_div.name})에서 ul.n_branch_ulist 탐색...")
                 ul_tag = parent_div.find('ul', class_='n_branch_ulist')

        if not ul_tag:
            print(f"WARNING: '{url}'의 '{region_name}' 지역에서 지점 목록(ul.n_branch_ulist)을 찾지 못했습니다. 건너뜁니다.")
            continue
        
        branch_name_spans = ul_tag.select('li a span')
        if not branch_name_spans:
            print(f"WARNING: '{url}'의 '{region_name}' 지역에서 지점명(li a span)을 찾지 못했습니다.")
            continue

        current_region_branches = []
        for span_tag in branch_name_spans:
            branch_name = span_tag.text.strip()
            if branch_name:
                current_region_branches.append(branch_name)
        
        if current_region_branches:
            print(f"INFO: '{region_name}' 지역에서 {len(current_region_branches)}개의 지점 추출.")
            banks_by_region[region_name].extend(sorted(list(set(current_region_branches))))
        else:
            print(f"INFO: '{region_name}' 지역에서 추출된 지점명이 없습니다.")

    if not found_valid_region:
        print(f"ERROR: '{url}'에서 '{VALID_REGION_NAMES}' 목록에 포함된 유효한 지역명을 하나도 찾지 못했습니다.")
        return None
    if not banks_by_region: # 유효 지역은 찾았으나, 그 안에서 지점명을 못찾은 경우
        print(f"ERROR: '{url}'의 유효한 지역들에서 실제 지점 정보를 추출하지 못했습니다.")
        return None
            
    return banks_by_region

class Command(BaseCommand):
    help = 'KB국민은행 웹사이트에서 9To6 Bank 및 점심시간 집중 상담 지점명을 지역별로 크롤링하여 별도의 JSON 파일로 저장합니다.'

    def _save_data_to_json(self, data, output_file, bank_type_name):
        if data is None or not data:
            self.stderr.write(self.style.ERROR(f'{bank_type_name}: 크롤링된 데이터가 없거나 오류가 발생하여 저장하지 않습니다.'))
            return False
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            total_branches = sum(len(branches) for branches in data.values())
            self.stdout.write(self.style.SUCCESS(
                f"성공({bank_type_name}): {len(data)}개 지역의 {total_branches}개 지점명을 '{output_file}'에 저장했습니다."
            ))
            
            for i, (region, branches) in enumerate(data.items()):
                if i < 1: 
                    self.stdout.write(f"- {region}: {branches[:2]}{'...' if len(branches) > 2 else ''}")
                else:
                    break
            return True
        except IOError as e:
            self.stderr.write(self.style.ERROR(f"{bank_type_name} 파일 저장 중 오류: {e}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"{bank_type_name} 처리 중 예기치 않은 오류: {e}"))
        return False

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('KB국민은행 특화지점 정보 크롤링을 시작합니다...'))
        
        self.stdout.write(self.style.HTTP_INFO(f"--- 9To6 Bank ('{URL_9TO6}') 크롤링 시작 ---"))
        nine_to_six_banks = _crawl_bank_data_by_region(URL_9TO6, region_tag_name='h3', region_class='tit_dep3 s4')
        self._save_data_to_json(nine_to_six_banks, OUTPUT_FILE_9TO6, "9To6 Bank")

        self.stdout.write("") 

        self.stdout.write(self.style.HTTP_INFO(f"--- 점심시간 집중 상담 지점 ('{URL_LUNCH_FOCUS}') 크롤링 시작 ---"))
        # 점심시간 페이지도 h3.tit_dep3.s4 구조를 사용한다고 하셨으므로 동일한 파라미터 전달
        lunch_focus_banks = _crawl_bank_data_by_region(URL_LUNCH_FOCUS, region_tag_name='h3', region_class='tit_dep3 s4')
        self._save_data_to_json(lunch_focus_banks, OUTPUT_FILE_LUNCH_FOCUS, "점심시간 집중 상담 지점")
        
        self.stdout.write(self.style.SUCCESS('모든 특화지점 정보 크롤링 시도가 완료되었습니다.')) 