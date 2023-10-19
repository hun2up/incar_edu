########################################################################################################################
##############################################     라이브러리 호출하기     ##################################################
########################################################################################################################
import streamlit as st
import streamlit_authenticator as stauth
hashed_passwords = stauth.Hasher(['XXX']).generate()
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
from utils import make_sidebar, hide_st_style
from utils import df_atd as df_chn
from utils import Chart

########################################################################################################################
################################################     인증페이지 설정     ###################################################
########################################################################################################################
instance_channel = Chart()

# -----------------------------------------------------  사이드바  ---------------------------------------------------------
# 사이드바 헤더
st.sidebar.header("원하는 옵션을 선택하세요")
#사이드바 제작
month = make_sidebar(instance_channel.call_data_attend('소속부문'),'월') # 월도 선택 사이드바
region = make_sidebar(instance_channel.call_data_attend('소속부문'),'지역') # 지역 선택 사이드바
partner = make_sidebar(instance_channel.call_data_attend('소속부문'),'보험사') # 보험사 선택 사이드바
line = make_sidebar(instance_channel.call_data_attend('소속부문'),'과정형태') # 과정 온오프라인 선택 사이드바
theme = make_sidebar(instance_channel.call_data_attend('소속부문'),'과정분류') # 과정 테마 선택 사이드바
name = make_sidebar(instance_channel.call_data_attend('소속부문'),'과정명') # 세부과정 선택 사이드바
channel = make_sidebar(instance_channel.call_data_attend('소속부문'),'소속부문') # 소속부문 선택 사이드바
career = make_sidebar(instance_channel.call_data_attend('소속부문'),'입사연차') # 입사연차 선택 사이드바
# 데이터와 사이드바 연결
df_channel = instance_channel.call_data_attend('소속부문').query(
    "월 == @month & 지역 == @region & 보험사 == @partner & 과정형태 == @line & 과정분류 == @theme & 과정명 == @name & 소속부문 == @channel & 입사연차 == @career"
)

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
    hide_st_style()
    # --------------------------------------------------  페이지 타이틀  -------------------------------------------------------
    # 메인페이지 타이틀
    st.header("소속부문별 교육지표")
    

    # 첫번째 행 (신청인원)
    hbar_apply, hbar_apply_people = st.columns(2)
    hbar_apply.plotly_chart(instance_channel.make_hbarchart_group(
        df=instance_channel.make_set_status(df=instance_channel.call_data_attend("attend"), columns='소속부문'),
        category='소속부문',
        axis_a='신청인원',
        axis_b='신청누계',
        title='부문별 교육신청 현황'), use_container_width=True)
    
    # 두번째 행 (수료인원)
    hbar_attend, hbar_attend_people = st.columns(2)
    hbar_attend.plotly_chart(instance_channel.make_hbarchart_group(
        df=instance_channel.make_set_status(df=instance_channel.call_data_attend("attend"), columns='소속부문'),
        category='소속부문',
        axis_a='수료인원',
        axis_b='수료누계',
        title='부문별 교육수료 현황'), use_container_width=True)
    
    # 세번째 행 (수료율 & IMO신청률)
    hbar_attend_rate, hbar_imo_rate = st.columns(2)
    hbar_attend_rate.plotly_chart(instance_channel.make_hbarchart_single(
        df=instance_channel.make_set_status(df=instance_channel.call_data_attend("attend"), columns='소속부문'),
        category='소속부문',
        axis_a='수료율',
        title='부문별 수료율'), use_container_width=True)
    hbar_imo_rate.plotly_chart(instance_channel.make_hbarchart_single(
        df=instance_channel.make_set_status(df=instance_channel.call_data_attend("attend"), columns='소속부문'),
        category='소속부문',
        axis_a='IMO신청률',
        title='부문별 IMO신청률'), use_container_width=True)
    
    # 네번째 행 (신청누계 & 수료누계 추이그래프) 수료율, IMO신청률)
    line_apply, line_attend = st.columns(2)
    line_apply.plotly_chart(instance_channel.make_linechart(
        df=instance_channel.make_set_trend(df=instance_channel.call_data_attend("attend"), columns='소속부문'),
        category='소속부문',
        xaxis='월',
        yaxis='신청누계',
        title='소속부문별 신청인원 추이 (신청누계 기준)'), use_container_width=True)
    line_attend.plotly_chart(instance_channel.make_linechart(
        df=instance_channel.make_set_trend(df=instance_channel.call_data_attend("attend"), columns='소속부문'),
        category='소속부문',
        xaxis='월',
        yaxis='수료누계',
        title='소속부문별 수료인원 추이 (수료누계 기준)'), use_container_width=True)
    
    # 다섯번째 행 (수료율 & IMO신청률 추이그래프)
    line_attend_rate, line_imo_rate = st.columns(2)
    line_attend_rate.plotly_chart(instance_channel.make_linechart(
        df=instance_channel.make_set_trend(df=instance_channel.call_data_attend("attend"), columns='소속부문'),
        category='소속부문',
        xaxis='월',
        yaxis='수료율',
        title='소속부문별 수료율 추이'), use_container_width=True)
    line_imo_rate.plotly_chart(instance_channel.make_linechart(
        df=instance_channel.make_set_trend(df=instance_channel.call_data_attend("attend"), columns='소속부문'),
        category='소속부문',
        xaxis='월',
        yaxis='IMO신청률',
        title='소속부문별 IMO신청률 추이'), use_container_width=True)