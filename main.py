########################################################################################################################
##############################################     라이브러리 호출하기     ##################################################
########################################################################################################################
from datetime import datetime
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
hashed_passwords = stauth.Hasher(['XXX']).generate()
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
from utils import generate_colors, generate_outsides, fig_vbarchart, fig_linechart
from utils import df_apl

########################################################################################################################
################################################     인증페이지 설정     ###################################################
########################################################################################################################
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == None:
    st.warning('아이디와 패스워드를 입력해주세요')
if authentication_status == False:
    st.error('아이디와 패스워드를 확인해주세요')
if authentication_status:
    ########################################################################################################################
    ##################################################     자료 제작     #####################################################
    ########################################################################################################################
    # df_apl: 컬럼삭제 (소속부문,목표인원)
    df_apl_line = df_apl.groupby(['날짜','과정명'])['신청인원'].sum().reset_index(name='신청인원')
    ##### df_apl_line = ['날짜','과정명','신청인원']
    df_apl_bar = df_apl.drop(df_apl[df_apl.iloc[:,0] != df_apl.iloc[-1,0]].index)
    month_today = pd.to_datetime(df_apl_bar.iloc[-1]['날짜'], format="%Y. %m. %d").month
    df_apl_bar = df_apl_bar.groupby(['날짜','과정명','목표인원'])['신청인원'].sum().reset_index(name='신청인원')
    
    ##### df_apl_bar = ['날짜','과정명','목표인원','신청인원']

    # ------------------------------------------  차트 제작에 필요한 리스트 제작  ---------------------------------------------
    apl_colors = generate_colors(df_apl_bar.shape[0])
    apl_outsides = generate_outsides(df_apl_bar.shape[0])

    # -------------------------------------------------  barchart 제작  ------------------------------------------------------
    barlist_apl = [df_apl_bar, apl_colors, apl_outsides, f'{month_today}월 신청인원 현황']
    bc_apl = fig_vbarchart(barlist_apl)
    linelist_apl = [df_apl_line, '과정명', '신청인원', f'{month_today}월 신청인원 추이', '날짜']
    lc_apl = fig_linechart(linelist_apl)

    ########################################################################################################################
    ################################################     메인페이지 설정     ###################################################
    ########################################################################################################################
    authenticator.logout('Logout', 'sidebar')
    # 메인페이지 타이틀
    st.header(":bar_chart: 인카금융서비스 교육과정 대시보드")

    # -----------------------------------------------------  차트 노출  ---------------------------------------------------------
    st.markdown("<hr>", unsafe_allow_html=True)
    st.plotly_chart(bc_apl, use_container_width=True)
    st.plotly_chart(lc_apl, use_container_width=True)

    ########################################################################################################################
    ###########################################     stremalit 워터마크 숨기기     ##############################################
    ########################################################################################################################
    hide_st_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_st_style, unsafe_allow_html=True)