from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string  # HTML 템플릿을 사용할 경우


def send_rate_change_email(user_email, product_name, option_info, changes):
    # 금리 변경 안내 이메일 발송
    # user_email: 수신자 이메일
    # product_name: 상품명
    # option_info: 옵션 정보 (예: "6개월 - 단리")
    # changes: 변경 내용 dict (예: {'기본 금리': ('3.00', '3.20')})
    subject = (
        f"[안내] 가입 금융상품 정보 변경: {product_name}" # 메일 제목 수정
    )

    changed_items = []
    for field, (old_val, new_val) in changes.items():
        changed_items.append(f"- {field}: {old_val}% → {new_val}%") # 화살표 변경
    changes_description = "\n".join(changed_items)

    message_plain = f"""안녕하세요.
가입하신 금융상품 [{product_name} ({option_info})] 정보가 아래와 같이 변경되어 안내드립니다.

[변경 사항]
{changes_description}

Fin Sense 이용에 감사드립니다.
    """ # 문구 간소화

    # HTML 템플릿 사용 예시 (현재 미사용)
    # html_message = render_to_string('emails/rate_change_notification.html', {
    #     'product_name': product_name,
    #     'option_info': option_info,
    #     'changes': changes,
    # })

    try:
        send_mail(
            subject,
            message_plain,
            settings.DEFAULT_FROM_EMAIL,  # settings.py의 발신자 이메일
            [user_email],
            # html_message=html_message, # HTML 메일 사용 시 주석 해제
            fail_silently=False,
        )
    except Exception as e:
        # 이메일 발송 실패 시 로깅 필요 (현재는 print문 제거)
        pass # print(f"Error sending email to {user_email} for {product_name}: {e}")


def get_subscribers_and_send_emails(option_instance, changes):
    # 특정 옵션 가입자에게 변경 사항 이메일 발송
    product_name = option_instance.product.fin_prdt_nm
    # 옵션 정보 문자열 생성 (간결하게 필요한 정보만 추출)
    option_info_str = (
        f"{option_instance.save_trm}개월 - {option_instance.intr_rate_type_nm}"
    )

    # 순환 참조 방지를 위해 모델을 함수 내에서 import
    from .models import (
        DepositOption,
        SavingOption,
    )  

    # DepositOption, SavingOption 인스턴스 타입 확인 후 구독자 정보 조회
    if isinstance(option_instance, DepositOption) or isinstance(
        option_instance, SavingOption
    ):
        subscriptions = option_instance.subscriptions.all()
    else:
        subscriptions = [] # 해당 없는 타입이면 빈 리스트

    sent_emails = set() # 중복 발송 방지를 위한 이메일 set

    for sub in subscriptions:
        if sub.user and sub.user.email and sub.user.email not in sent_emails:
            send_rate_change_email(
                sub.user.email, product_name, option_info_str, changes
            )
            sent_emails.add(sub.user.email)
