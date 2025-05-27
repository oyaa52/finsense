# final-pjt/final_pjt_back/assetinfo/utils.py
import os
import pandas as pd
from django.conf import settings
from .models import AssetPrice # AssetPrice 모델 임포트
from decimal import Decimal, InvalidOperation
from datetime import datetime

# 단일 Excel 파일을 파싱하여 AssetPrice DB에 데이터 로드/업데이트
def _parse_and_load_single_excel(file_path, asset_name_value):
    # asset_name_value: DB에 저장될 자산명 (예: "Gold", "Silver")
    messages = []
    if not os.path.exists(file_path):
        messages.append(f'[ERROR] 파일을 찾을 수 없습니다: {file_path}')
        return messages

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        messages.append(f'[INFO] 파일 읽기 성공: {file_path}')

        required_columns = ['Date', 'Close/Last'] # 필수 컬럼명
        for col in required_columns:
            if col not in df.columns:
                messages.append(f'[ERROR] 필수 컬럼 "{col}"이 없습니다: {file_path}')
                return messages
        
        loaded_count = 0 # 성공적으로 로드된 행 수
        skipped_count = 0 # 건너뛴 행 수
        # 엑셀 데이터 각 행 처리
        for index, row in df.iterrows():
            excel_row_num = index + 2 # 엑셀의 실제 행 번호 (헤더 포함)
            try:
                price_date_input = row['Date']
                # 날짜 형식 파싱 (문자열, datetime 객체 등 다양한 입력 처리)
                if isinstance(price_date_input, str):
                    try: # MM/DD/YYYY 형식 시도
                        price_date = datetime.strptime(str(price_date_input).split()[0], '%m/%d/%Y').date()
                    except ValueError: # YYYY-MM-DD 형식 시도
                        price_date = datetime.strptime(str(price_date_input).split()[0], '%Y-%m-%d').date()
                elif isinstance(price_date_input, datetime):
                    price_date = price_date_input.date()
                else: # 알 수 없는 날짜 형식
                    messages.append(f'[WARNING] 행 {excel_row_num}: 날짜 형식 오류로 건너뜁니다. 입력값: {price_date_input}')
                    skipped_count += 1
                    continue

                # 가격 데이터 파싱 (쉼표 제거, 공백/NaN 처리)
                raw_price = str(row['Close/Last']).replace(',', '') # 쉼표 제거
                if raw_price.strip().lower() in ["", "nan", "null"]: # 빈 값 또는 NaN 처리
                    messages.append(f'[WARNING] 행 {excel_row_num} ({price_date}): 가격 정보가 없어 건너뜁니다.')
                    skipped_count += 1
                    continue
                
                try:
                    price = Decimal(raw_price) # Decimal 타입으로 변환
                except InvalidOperation: # 유효하지 않은 숫자 형식
                    messages.append(f'[WARNING] 행 {excel_row_num} ({price_date}): 유효하지 않은 가격("{row["Close/Last"]}")으로 건너뜁니다.')
                    skipped_count += 1
                    continue

                # AssetPrice 객체 생성 또는 업데이트
                AssetPrice.objects.update_or_create(
                    asset_name=asset_name_value,
                    date=price_date,
                    defaults={'price': price}
                )
                loaded_count += 1
            except Exception as e_row: # 행 처리 중 기타 예외 발생
                messages.append(f'[ERROR] 행 {excel_row_num} 처리 중 오류: {e_row} - 데이터: {row.to_dict()}')
                skipped_count += 1
        
        messages.append(f'[INFO] {asset_name_value} 파일 처리 완료: {file_path}. 성공: {loaded_count} 건, 실패/건너뜀: {skipped_count} 건')

    except Exception as e_file: # 파일 읽기/처리 중 예외 발생
        messages.append(f'[ERROR] 파일 처리 중 오류 발생 {file_path}: {e_file}')
    return messages

# 지정된 경로의 Excel 파일들로부터 자산(금, 은) 가격 데이터를 DB에 로드
def load_asset_data_from_excel_files():
    results = {} # 각 파일 처리 결과 저장
    
    # 데이터 파일 기본 경로 (BASE_DIR/assetinfo/data/)
    base_data_path = os.path.join(settings.BASE_DIR, 'assetinfo', 'data')
    
    # 금 가격 데이터 파일 경로
    gold_file_path = os.path.join(base_data_path, 'Gold_prices.xlsx')
    # 은 가격 데이터 파일 경로
    silver_file_path = os.path.join(base_data_path, 'Silver_prices.xlsx')

    # 각 자산 데이터 로드 함수 호출 및 결과 저장
    results['gold_load_status'] = _parse_and_load_single_excel(gold_file_path, "Gold")
    results['silver_load_status'] = _parse_and_load_single_excel(silver_file_path, "Silver")
    
    return results