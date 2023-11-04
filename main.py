########################################################################################################################
##############################################     라이브러리 호출하기     ##################################################
########################################################################################################################
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
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

    # --------------------------------------------          사이드바          ------------------------------------------------
    # 사이드바 헤더
    st.sidebar.header("원하는 옵션을 선택하세요")
    #사이드바 제작
    date_apply = make_sidebar(df_main,'신청일자') # 신청일자 선택 사이드바
    date_course = make_sidebar(df_main,'교육일자')
    course = make_sidebar(df_main,'과정명')
    channel = make_sidebar(df_main,'소속부문')
    # career = make_sidebar(df_main,'입사연차') # 입사연차 선택 사이드바
    # 데이터와 사이드바 연결
    df_main = df_main.query(
        "신청일자 == @date_apply & 교육일자 == @date_course & 소속부문 == @channel"
    )

    # -----------------------------------------------  당일 교육신청 현황  ---------------------------------------------------
    

    # 첫번째 행 (과정별 신청현황, 과정별 신청추이)
    bar_today, line_today = st.columns(2)
    bar_today.plotly_chart(instance.make_vbarchart(
        df=df_main.drop(df_main[df_main.iloc[:,0] != df_main.iloc[-1,0]].index).groupby(['신청일자','과정명','목표인원'])['신청인원'].sum().reset_index(name='신청인원'),
        title='과정별 신청현황'), use_container_width=True)
    line_today.plotly_chart(instance.make_linechart(
        df=df_main.groupby(['신청일자','과정명'])['신청인원'].sum().reset_index(name='신청인원'),
        category='과정명',
        xaxis='신청일자',
        yaxis='신청인원',
        title=f'{pd.to_datetime(df_main.iloc[-1,0], format="%Y. %m. %d").month}월 신청인원 추이'), use_container_width=True)

    # 세번째 행 (소속부문별 신청현황, 입사연차별 신청현황)
    st.markdown('---')
    hbar_channel, hbar_career = st.columns(2)
    hbar_channel.plotly_chart(instance.make_hbarchart_single(
        df=instance.make_set_main(df_main,'소속부문'),
        category='소속부문',
        axis_a='신청인원',
        title='소속부문별 신청인원 현황'), use_container_width=True)
    hbar_career.plotly_chart(instance.make_hbarchart_single(
        df=instance.make_set_main(df_main,'입사연차'),
        category='입사연차',
        axis_a='신청인원',
        title='입사연차별 신청인원 현황'), use_container_width=True)

    pie_apply, pie_target = st.columns(2)
    pie_apply.write("신청인원 기준 타겟홍보 유입률")
    pie_target.write("홍보인원 기준 반응률")
    
    #st.dataframe()
    
    # 두번째 행 (신청현황 리스트)
    st.markdown('---')
    st.markdown('###### 신규 교육신청 명단 (전전일 대비 전일 기준)')
    st.dataframe(instance.make_set_new(df_main), use_container_width=True)
    st.markdown('---')
    st.markdown('###### 전체 교육신청 명단 (전일 기준)')
    st.dataframe(df_main.drop(df_main[df_main.iloc[:,0] != df_main.iloc[-1,0]].index)[['교육일자','과정명','소속부문','파트너','사원번호','성명','입사연차']], use_container_width=True) # 마지막 신청일자 제외한 나머지 신청내역 삭제

    df_apply = df_main.drop(df_main[df_main.iloc[:,0] != df_main.iloc[-1,0]].index)[['교육일자','과정명','소속부문','파트너','사원번호','성명','입사연차']]
    df_target = instance.make_set_target().drop(columns='번호').reset_index(drop=True)
    df_target = df_target.drop(df_target[df_target['파트너'] == '인카본사'].index)
    df_target.insert(1, column='과정코드', value=df_target['과정명'].str.split("]")[1])
    df_target['과정코드'] = df_target['과정코드'].replace('[','')
    # df_target['과정코드'] = [df_target.iloc[change,2].split("]")[1].replace('[','') for change in range(df_target.shape[0])] # [과정명]에서 '과정코드'만 추출하여 [과정코드] 컬럼에 추가
    df_target.insert(2, column='타겟명', value=df_target['과정명'].str.split(']').str[2])
    df_target = df_target.drop(columns='과정명')
    # df_target['과정코드'] = df_target['과정명'].str.split(']').str[1]
    st.dataframe(df_target)
    df_apply['사원번호'] = df_apply['사원번호'].astype(str)
    df_target['사원번호'] = df_target['사원번호'].astype(str)
    # df_apply = pd.merge(df_apply, df_target, on='사원번호', how='inner')

    # st.dataframe(df_apply)
    