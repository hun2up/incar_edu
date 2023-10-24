########################################################################################################################
##############################################     라이브러리 호출하기     ##################################################
########################################################################################################################
import time
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
hashed_passwords = stauth.Hasher(['XXX']).generate()
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
from utils import call_sheets
from utils import ServiceData

###########################################################################################################################
################################################     인증페이지 설정     ###################################################
###########################################################################################################################
# ---------------------------------------------    페이지 레이아웃 설정    --------------------------------------------------
st.set_page_config(page_title="보장분석 대시보드", layout='wide')

# -------------------------------------------------  인증페이지 삽입  -------------------------------------------------------
# 인증모듈 기본설정
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
# 로그인창 노출
name, authentication_status, username = authenticator.login('Login', 'main')
# 사이드바에 로그아웃 버튼 추가
authenticator.logout('Logout', 'sidebar')
# 인증상태 검증
if authentication_status == None:
    st.warning('아이디와 패스워드를 입력해주세요')
if authentication_status == False:
    st.error('아이디와 패스워드를 확인해주세요')
if authentication_status:
    ########################################################################################################################
    ##################################################     자료 제작     #####################################################
    ########################################################################################################################
    # ----------------------------------------    Google Sheet 데이터베이스 호출    --------------------------------------------- 
    
    instance_register = ServiceData()
    index = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
    df_summary = pd.DataFrame(columns=[
        '로그인수',
        '보장분석접속건수',
        '보장분석고객등록수',
        '보장분석컨설팅고객수',
        '보장분석출력건수',
        '간편보장_접속건수',
        '간편보장_출력건수',
        'APP 보험다보여전송건수',
        'APP 주요보장합계조회건수',
        'APP 명함_접속건수',
        'APP 의료비/보험금조회건수',
        '보험료비교접속건수',
        '보험료비교출력건수',
        '한장보험료비교_접속건수',
        '약관조회',
        '상품비교설명확인서_접속건수',
        '영업자료접속건수',
        '영업자료출력건수',
        '(NEW)영업자료접속건수',
        '(NEW)영업자료출력건수',
        '라이프사이클접속건수',
        '라이프사이클출력건수'
    ])
    # st.dataframe(instance_register.make_service_summary(call_sheets('jan')))
    
    for i in range(len(index)):
        df_summary = pd.concat([df_summary, instance_register.make_service_summary(call_sheets(index[i]))], axis=0)
    st.dataframe(df_summary)
    

    # 요약보고서 제작