# final-pjt/final_pjt_back/assetinfo/utils.py
import os
import pandas as pd
from django.conf import settings
from .models import AssetPrice # assetinfo.models에서 AssetPrice 모델을 가져옵니다.
from decimal import Decimal, InvalidOperation
from datetime import datetime

def _parse_and_load_single_excel(file_path, asset_name_value):
    """
    단일 엑셀 파일을 파싱하고 AssetPrice 데이터베이스에 데이터를 로드합니다.
    성공/실패 메시지 리스트를 반환합니다.
    """
    messages = []
    if not os.path.exists(file_path):
        messages.append(f'ERROR: File not found: {file_path}')
        return messages

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        messages.append(f'INFO: Successfully read {file_path}')

        required_columns = ['Date', 'Close/Last']
        for col in required_columns:
            if col not in df.columns:
                messages.append(f'ERROR: Missing required column "{col}" in {file_path}')
                return messages
        
        loaded_count = 0
        skipped_count = 0
        for index, row in df.iterrows():
            try:
                price_date_input = row['Date']
                if isinstance(price_date_input, str):
                    try:
                        price_date = datetime.strptime(str(price_date_input).split()[0], '%m/%d/%Y').date()
                    except ValueError:
                        price_date = datetime.strptime(str(price_date_input).split()[0], '%Y-%m-%d').date()
                elif isinstance(price_date_input, datetime):
                    price_date = price_date_input.date()
                else:
                    messages.append(f'WARNING: Skipping row {index+2} in {file_path} (0-indexed) due to unknown date format: {price_date_input}')
                    skipped_count += 1
                    continue

                raw_price = str(row['Close/Last']).replace(',', '')
                if raw_price.strip().lower() in ["", "nan", "null"]:
                    messages.append(f'WARNING: Skipping row {index+2} in {file_path} (0-indexed) due to empty or NaN price for date {price_date}')
                    skipped_count += 1
                    continue
                
                try:
                    price = Decimal(raw_price)
                except InvalidOperation:
                    messages.append(f'WARNING: Skipping row {index+2} in {file_path} (0-indexed) due to invalid price value "{row["Close/Last"]}" for date {price_date}')
                    skipped_count += 1
                    continue

                AssetPrice.objects.update_or_create(
                    asset_name=asset_name_value,
                    date=price_date,
                    defaults={'price': price}
                )
                loaded_count += 1
            except Exception as e_row:
                messages.append(f'ERROR: Processing row {index+2} in {file_path} (0-indexed): {e_row} - Data: {row.to_dict()}')
                skipped_count += 1
        
        messages.append(f'INFO: Finished processing {file_path} for {asset_name_value}. Loaded: {loaded_count}, Skipped: {skipped_count}')

    except Exception as e_file:
        messages.append(f'ERROR: Reading or processing file {file_path}: {e_file}')
    return messages

def load_asset_data_from_excel_files():
    """
    지정된 엑셀 파일들(Gold, Silver)에서 자산 가격 데이터를 로드합니다.
    각 파일 처리 결과를 담은 딕셔너리를 반환합니다.
    """
    results = {}
    
    base_data_path = os.path.join(settings.BASE_DIR, 'assetinfo', 'data')
    
    gold_file_path = os.path.join(base_data_path, 'Gold_prices.xlsx')
    silver_file_path = os.path.join(base_data_path, 'Silver_prices.xlsx')

    results['gold_load_status'] = _parse_and_load_single_excel(gold_file_path, "Gold")
    results['silver_load_status'] = _parse_and_load_single_excel(silver_file_path, "Silver")
    
    return results