from django.core.management.base import BaseCommand, CommandError
from assetinfo.utils import load_asset_data_from_excel_files # utils.py 에서 함수 임포트

class Command(BaseCommand):
    help = 'Loads asset price data from Gold_prices.xlsx and Silver_prices.xlsx files into the AssetPrice database table using the utility function.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('Starting the process to load asset data from Excel files...'))
        
        try:
            # assetinfo.utils에 정의된 함수를 호출합니다.
            results = load_asset_data_from_excel_files()
            
            # 결과 메시지들을 터미널에 출력합니다.
            overall_success = True
            for asset_key, status_list in results.items():
                # 'gold_load_status' -> 'Gold'
                asset_display_name = asset_key.replace('_load_status', '').capitalize()
                self.stdout.write(self.style.SUCCESS(f"--- {asset_display_name} Loading Status ---"))
                for msg in status_list:
                    if 'ERROR' in msg:
                        self.stderr.write(self.style.ERROR(msg))
                        overall_success = False # 에러가 하나라도 있으면 전체 실패로 간주
                    elif 'WARNING' in msg:
                        self.stdout.write(self.style.WARNING(msg))
                    else:
                        self.stdout.write(msg)
            
            if overall_success:
                self.stdout.write(self.style.SUCCESS('\nData loading process completed successfully overall.'))
            else:
                self.stderr.write(self.style.ERROR('\nData loading process encountered errors. Please check the messages above.'))
                # 에러 발생 시 0이 아닌 종료 코드를 반환하도록 CommandError 발생시키는 것도 고려 가능
                # raise CommandError('Data loading failed due to errors mentioned above.')

        except Exception as e:
            # load_asset_data_from_excel_files 함수 호출 자체에서 예외가 발생한 경우
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred during the data loading process: {e}'))
            # CommandError를 발생시켜 Django가 이 명령이 실패했음을 알 수 있도록 합니다.
            raise CommandError(f'Failed to load asset data due to an unexpected error: {e}')
