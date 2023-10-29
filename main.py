########################################################################################################################
##############################################     라이브러리 호출하기     ##################################################
########################################################################################################################
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
st.set_page_config(page_title="교육관리 대시보드", layout='wide')
hashed_passwords = stauth.Hasher(['XXX']).generate()
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
from utils import make_sidebar, hide_st_style
from utils import EduMain

########################################################################################################################
################################################     인증페이지 설정     ###################################################
########################################################################################################################
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
    # ------------------------------------------          인스턴스 생성 및 페이지 타이틀          ---------------------------------------------
    hide_st_style()
    instance = EduMain()
    df_main = instance.call_data_main()
    st.header("당월 교육과정 신청현황")

    # -----------------------------------------------  당일 교육신청 현황  ---------------------------------------------------
    # df_main_line = ['날짜','과정명','신청인원']
    df_main_line = df_main.groupby(['날짜','과정명'])['신청인원'].sum().reset_index(name='신청인원')
    # df_main_bar = ['날짜','과정명','목표인원','신청인원']
    df_main_result = df_main.drop(df_main[df_main.iloc[:,0] != df_main.iloc[-1,0]].index)
    month_today = pd.to_datetime(df_main_result.iloc[-1]['날짜'], format="%Y. %m. %d").month
    df_main_list = df_main_result[['교육일자','과정명','소속부문','파트너','사원번호','성명']]
    df_main_list['사원번호'] = df_main_list['사원번호'].astype(str)
    df_main_bar = df_main_result.groupby(['날짜','과정명','목표인원'])['신청인원'].sum().reset_index(name='신청인원')

    bar_today, line_today = st.columns(2)
    bar_today.plotly_chart(instance.make_vbarchart(
        df=df_main.drop(df_main[df_main.iloc[:,0] != df_main.iloc[-1,0]].index).groupby(['날짜','과정명','목표인원'])['신청인원'].sum().reset_index(name='신청인원'),
        title='과정별 신청현황'), use_container_width=True)
    line_today.plotly_chart(instance.make_linechart(
        df=df_main_line,
        category='과정명',
        xaxis='날짜',
        yaxis='신청인원',
        title=f'{month_today}월 신청인원 추이'), use_container_width=True)
    st.dataframe(df_main.drop(df_main[df_main.iloc[:,0] != df_main.iloc[-1,0]].index)[['교육일자','과정명','소속부문','파트너','사원번호','성명']]) # 마지막 날짜 제외한 나머지 신청내역 삭제



#df_attend.insert(0, column='과정코드', value=None) # 첫번째 컬럼에 [과정코드] 컬럼 추가
    # -------------------------------------------  차트 노출 (당일 교육신청 현황)  ----------------------------------------------
    
    '''
    instance = Chart()
    df_apply = instance.call_data_apply("month")

    # -------------------------------------------  차트 노출 (당일 교육신청 현황)  ----------------------------------------------
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("당월 교육과정 신청현황")
    
    # -----------------------------------------------  당일 교육신청 현황  ---------------------------------------------------
    # df_apply_line = ['날짜','과정명','신청인원']
    df_apply_line = df_apply.groupby(['날짜','과정명'])['신청인원'].sum().reset_index(name='신청인원')
    # df_apply_bar = ['날짜','과정명','목표인원','신청인원']
    df_apply_result = df_apply.drop(df_apply[df_apply.iloc[:,0] != df_apply.iloc[-1,0]].index)
    month_today = pd.to_datetime(df_apply_result.iloc[-1]['날짜'], format="%Y. %m. %d").month
    df_apply_list = df_apply_result[['교육일자','과정명','소속부문','파트너','사원번호','성명']]
    df_apply_list['사원번호'] = df_apply_list['사원번호'].astype(str)
    df_apply_bar = df_apply_result.groupby(['날짜','과정명','목표인원'])['신청인원'].sum().reset_index(name='신청인원')

    bar_today, line_today = st.columns(2)
    bar_today.plotly_chart(instance.make_vbarchart(
        df=df_apply_bar,
        title='과정별 신청현황'), use_container_width=True)
    line_today.plotly_chart(instance.make_linechart(
        df=df_apply_line,
        category='과정명',
        xaxis='날짜',
        yaxis='신청인원',
        title=f'{month_today}월 신청인원 추이'), use_container_width=True)
    st.dataframe(df_apply_list, use_container_width=True)
    '''