"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Django 관리 작업을 실행합니다."""
    # Django 프로젝트의 settings 모듈을 환경 변수에 설정
    # 'backend.settings'는 Django 프로젝트 설정 파일의 경로
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:

        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # 커맨드 라인으로부터 명령을 실행
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # 이 스크립트가 직접 실행될 때 main() 함수를 호출
    main()
