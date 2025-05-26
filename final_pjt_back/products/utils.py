from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string  # HTML 템플릿을 사용할 경우


def send_rate_change_email(user_email, product_name, option_info, changes):
    """
    금리 변경 안내 이메일을 발송합니다.
    :param user_email: 수신자 이메일 주소
    :param product_name: 상품명
    :param option_info: 옵션 정보 (예: "6개월 - 단리")
    :param changes: 변경된 내용 딕셔너리 (예: {'기본 금리': ('3.00', '3.20'), '최고 우대금리': ('3.50', '3.70')})
    """
    subject = (
        f"[안내] 고객님이 가입하신 금융상품의 정보가 변경되었습니다: {product_name}"
    )

    changed_items = []
    for field, (old_val, new_val) in changes.items():
        changed_items.append(f"- {field}: {old_val}% -> {new_val}%")
    changes_description = "\n".join(changed_items)

    message_plain = f"""
안녕하세요, 고객님.
고객님이 가입하신 금융상품 [{product_name} ({option_info})]의 정보가 다음과 같이 변경되어 안내드립니다.

[변경 사항]
{changes_description}

항상 저희 Fin Sense를 이용해주셔서 감사합니다.
    """

    # HTML 템플릿을 사용하고 싶다면 아래와 같이 구성할 수 있습니다.
    # html_message = render_to_string('emails/rate_change_notification.html', {
    #     'product_name': product_name,
    #     'option_info': option_info,
    #     'changes': changes,
    # })

    try:
        send_mail(
            subject,
            message_plain,
            settings.DEFAULT_FROM_EMAIL,  # settings.py에 정의된 발신자 이메일
            [user_email],
            # html_message=html_message, # HTML 이메일을 사용하려면 주석 해제
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email to {user_email} for {product_name}: {e}")


def get_subscribers_and_send_emails(option_instance, changes):
    """
    옵션에 가입한 사용자들을 찾아 변경 사항 이메일을 발송합니다.
    """
    product_name = option_instance.product.fin_prdt_nm
    # 옵션의 __str__ 메소드가 너무 많은 정보를 포함할 수 있으므로, 필요한 정보만 추출합니다.
    option_info_str = (
        f"{option_instance.save_trm}개월 - {option_instance.intr_rate_type_nm}"
    )

    # DepositOption과 SavingOption 모두 related_name='subscriptions'를 사용합니다.
    # isintance()를 사용하여 타입을 확인하고 처리하는 것이 더 안전합니다.
    from .models import (
        DepositOption,
        SavingOption,
    )  # 순환 참조 방지를 위해 함수 내에서 import

    if isinstance(option_instance, DepositOption) or isinstance(
        option_instance, SavingOption
    ):
        subscriptions = option_instance.subscriptions.all()
    else:
        subscriptions = []

    sent_emails = set()

    for sub in subscriptions:
        if sub.user and sub.user.email and sub.user.email not in sent_emails:
            send_rate_change_email(
                sub.user.email, product_name, option_info_str, changes
            )
            sent_emails.add(sub.user.email)
