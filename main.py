########################################################################################################################
##############################################     라이브러리 호출하기     ##################################################
########################################################################################################################
from datetime import datetime
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
st.set_page_config(page_title="교육관리 대시보드", layout='wide')
hashed_passwords = stauth.Hasher(['XXX']).generate()
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
# from utils import fn_status, fn_trends, fig_vbarchart
# from utils import df_apl
from utils import Chart

########################################################################################################################
################################################     인증페이지 설정     ###################################################
########################################################################################################################
instance = Chart()
df_apply = instance.call_data_apply("month")

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
    #########################################################################################################################
    ##################################################     자료 제작     #####################################################
    #########################################################################################################################
    # -----------------------------------------------  당일 교육신청 현황  ---------------------------------------------------
    # df_apply_line = ['날짜','과정명','신청인원']
    df_apply_line = df_apply.groupby(['날짜','과정명'])['신청인원'].sum().reset_index(name='신청인원')
    # df_apply_bar = ['날짜','과정명','목표인원','신청인원']
    df_apply_bar = df_apply.drop(df_apply[df_apply.iloc[:,0] != df_apply.iloc[-1,0]].index)
    month_today = pd.to_datetime(df_apply_bar.iloc[-1]['날짜'], format="%Y. %m. %d").month
    df_apply_bar = df_apply_bar.groupby(['날짜','과정명','목표인원'])['신청인원'].sum().reset_index(name='신청인원')
    st.dataframe(df_apply_bar)
    st.dataframe(df_apply_line)

    '''
    bar_today, line_today = st.columns(2)
    line_today.plotly_chart(instance.make_linechart(
        df=instance.make_set_trend(df=df_apply_line, columns='소속부문'),
        category='과정명',
        xaxis='날짜',
        yaxis='신청인원',
        title=f'{month_today}월 신청인원 추이'), use_container_width=True)
    '''


    '''
    # -------------------------------------------------  barchart 제작  ------------------------------------------------------    
    barlist_apl = [df_apl_bar, apl_colors, apl_outsides, f'{month_today}월 신청인원 현황']
    bc_apl = fig_vbarchart(barlist_apl)
    linelist_apl = [df_apl_line, '과정명', '신청인원', f'{month_today}월 신청인원 추이', '날짜']
    lc_apl = fig_linechart(linelist_apl)

    ###########################################################################################################################
    ################################################     메인페이지 설정     ###################################################
    ###########################################################################################################################
    authenticator.logout('Logout', 'sidebar')
    # 메인페이지 타이틀
    st.header(":bar_chart: 인카금융서비스 교육과정 대시보드")

    # -------------------------------------------  차트 노출 (당일 교육신청 현황)  ----------------------------------------------
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("당월 교육과정 신청현황")
    # 첫번째 행 (신청인원)
    r1_c1, r1_c2 = st.columns(2)
    r1_c1.plotly_chart(bc_apl, use_container_width=True)
    r1_c2.plotly_chart(lc_apl, use_container_width=True)

    ###########################################################################################################################
    ###########################################     stremalit 워터마크 숨기기     ##############################################
    ###########################################################################################################################
    hide_st_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    '''