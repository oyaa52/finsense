from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.conf import settings
from .models import DepositProduct, DepositOption
from .serializers import DepositProductsSerializer, DepositOptionsSerializer
import requests

FIN_API_KEY = settings.FIN_API_KEY

@api_view(["GET"])
def save_deposit_products(request):
    r = requests.get(
        f"http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={FIN_API_KEY}&topFinGrpNo=020000&pageNo=1"
    )
    response = r.json()
    base_lst = response.get("result", {}).get("baseList", [])
    option_lst = response.get("result", {}).get("optionList", [])

    save(base_lst, option_lst)

    return Response(response, status=status.HTTP_200_OK)

def save(base_lst, option_lst):
    for entry in base_lst:
        DepositProduct.objects.update_or_create(
            fin_prdt_cd=entry['fin_prdt_cd'],
            defaults={
                "kor_co_nm": entry["kor_co_nm"],
                "fin_prdt_nm": entry["fin_prdt_nm"],
                "etc_note": entry["etc_note"],
                "join_deny": entry["join_deny"],
                "join_member": entry["join_member"],
                "join_way": entry["join_way"],
                "spcl_cnd": entry["spcl_cnd"],
            }
        )

    for entry in option_lst:
        parent = DepositProduct.objects.get(fin_prdt_cd=entry['fin_prdt_cd'])
        DepositOption.objects.update_or_create(
            product=parent,
            intr_rate_type_nm=entry['intr_rate_type_nm'],
            save_trm=int(entry.get('save_trm', 0)),  # 이게 모델에서 save_trm인지 확인!
            defaults={
                "product": parent,
                "fin_prdt_cd": entry["fin_prdt_cd"],
                "intr_rate_type_nm": entry["intr_rate_type_nm"],
                "intr_rate": entry.get("intr_rate", -1),
                "intr_rate2": entry.get("intr_rate2", -1),
                "save_trm": int(entry.get("save_trm", 0)),
            }
        )

@api_view(['GET'])
def deposit_product_options(request, fin_prdt_cd):
    product = DepositProduct.objects.get(fin_prdt_cd=fin_prdt_cd)
    option = DepositOption.objects.filter(product_id=product.id)
    serializer = DepositOptionsSerializer(option, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def top_rate(request):
    high_rate_option = DepositOption.objects.order_by('-intr_rate2').first()
    high_rate_product = DepositProduct.objects.get(id=high_rate_option.product_id)
    data = {
        'product': DepositProductsSerializer(high_rate_product).data,
        'option': DepositOptionsSerializer(high_rate_option).data
    }
    return Response(data)

@api_view(['GET', 'POST'])
def deposit_products(request):
    if request.method == 'GET':
        products = DepositProduct.objects.all()
        serializer = DepositProductsSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = DepositProductsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"message": "이미 있는 데이터이거나, 데이터가 잘못 입력되었습니다."},
            status=status.HTTP_400_BAD_REQUEST
        )
