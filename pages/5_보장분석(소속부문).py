########################################################################################################################
##############################################     라이브러리 호출하기     ##################################################
########################################################################################################################
import time
import streamlit as st
import streamlit_authenticator as stauth
hashed_passwords = stauth.Hasher(['XXX']).generate()
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
from utils import call_sheets
from utils import month_dict
from utils import ServiceData, Register

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
    # 9월 실적현황 SHEET 호출
    instance = ServiceData()
    month = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
    start_all = time.time()
    for i in range(len(month)):
        start = time.time()
        st.write(month[i])
        st.dataframe(instance.make_service_data(call_sheets(month[i])))
        end = time.time()
        st.write(f"시간측정({month[i]}) : {end-start} 초")
    end_all = time.time()
    st.write(f"시간측정(전체) : {end_all-start_all} sec")
    
    
    # instance_register = Register()
    # st.dataframe(instance.make_service_summary())
    # st.dataframe(instance.make_service_branch())

    # instance_register.find_register()

    # 요약보고서 제작