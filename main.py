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
    df_apply = instance.target_set_apply(df_main)
    df_target = instance.target_set_target()
    st.header("당월 교육과정 신청현황")

    # --------------------------------------------          사이드바          ------------------------------------------------
    # 사이드바 헤더
    st.sidebar.header("원하는 옵션을 선택하세요")
    #사이드바 제작
    channel = make_sidebar(df_main,'소속부문')
    career = make_sidebar(df_main,'입사연차') # 입사연차 선택 사이드바
    course = make_sidebar(df_main,'과정명')
    target = make_sidebar(df_target, '타겟명')
    date_apply = make_sidebar(df_main,'신청일자') # 신청일자 선택 사이드바
    date_course = make_sidebar(df_main,'교육일자')
    # 데이터와 사이드바 연결
    df_main = df_main.query("소속부문 == @channel & 입사연차 == @career & 과정명 == @course & 신청일자 == @date_apply & 교육일자 == @date_course")
    df_apply = df_apply.query("과정명 == @course")
    df_target = df_target.query("타겟명 == @target")
    st.sidebar.markdown('---')

    # -----------------------------------------------  당일 교육신청 현황  ---------------------------------------------------
    # 첫번째 행 (과정별 신청현황, 과정별 신청추이)
    bar_today, line_today = st.columns(2)
    bar_today.plotly_chart(instance.make_vbarchart_group(
        df=df_main.drop(df_main[df_main.iloc[:,0] != df_main.iloc[-1,0]].index).groupby(['신청일자','과정명','목표인원'])['신청인원'].sum().reset_index(name='신청인원'),
        category='과정명',
        axis_a='목표인원',
        axis_b='신청인원',
        title='과정별 신청현황',
        caption=False), use_container_width=True)
    line_today.plotly_chart(instance.make_linechart(
        df=df_main.groupby(['신청일자','과정명'])['신청인원'].sum().reset_index(name='신청인원'),
        category='과정명',
        xaxis='신청일자',
        yaxis='신청인원',
        title=f'{pd.to_datetime(df_main.iloc[-1,0], format="%Y. %m. %d").month}월 신청인원 추이'), use_container_width=True)

    # 두번째 행 (소속부문별 신청현황, 입사연차별 신청현황)
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

    # 세번째 행 (신청현황 리스트)
    title_new, title_all = st.columns(2)
    title_new.markdown('###### 신규 교육신청 명단 (전전일 대비 전일 기준)')
    title_all.markdown('###### 전체 교육신청 명단 (전일 기준)')
    chart_new, chart_all = st.columns(2)
    chart_new.dataframe(instance.make_set_new(df_main), use_container_width=True)
    chart_all.dataframe(df_main.drop(df_main[df_main.iloc[:,0] != df_main.iloc[-1,0]].index)[['신청일자','교육일자','과정명','소속부문','파트너','사원번호','성명','입사연차']].reset_index(drop=True), use_container_width=True) # 마지막 신청일자 제외한 나머지 신청내역 삭제


    # -----------------------------------------------  타겟홍보 효과성 분석  ---------------------------------------------------
    # 네번째 행 (신청인원 기준 타겟홍보 유입현황)
    st.markdown('---')
    apply_by_target = st.columns((1,2))
    apply_by_target[0].plotly_chart(instance.make_piechart(
        label=instance.make_pie_target(df=df_main,data_type='신청')['구분'],
        value=instance.make_pie_target(df=df_main,data_type='신청')['인원'],
        title="신청인원 기준 타겟홍보 유입률", font=18), use_container_width=True)
    apply_by_target[1].plotly_chart(instance.make_vbarchart_group(
        df=instance.make_set_target(df=df_main,data_type='신청'),
        category='과정명',
        axis_a='신청인원',
        axis_b='유입인원',
        title='교육과정별 타겟홍보 유입현황',
        caption=False), use_container_width=True)
    
    # 다섯번째 행 (홍보인원 기준 교육신청 반응현황)
    target_by_apply = st.columns((1,2))
    target_by_apply[0].plotly_chart(instance.make_piechart(
        label=instance.make_pie_target(df=df_main,data_type='타겟')['구분'],
        value=instance.make_pie_target(df=df_main,data_type='타겟')['인원'],
        title="홍보인원 기준 교육신청 반응률", font=18), use_container_width=True)
    target_by_apply[1].plotly_chart(instance.make_vbarchart_group(
        df=instance.make_set_target(df=df_main,data_type='타겟'),
        category='타겟명',
        axis_a='타겟인원',
        axis_b='반응인원',
        title='타겟홍보별 교육과정 반응현황',
        caption=False), use_container_width=True)
    
    # 여섯번째 행
    channel_apply, channel_apply_rate = st.columns(2)
    channel_apply.plotly_chart(instance.make_hbarchart_group(
        df=instance.make_bar_target(df_main,'소속부문'),
        category='소속부문',
        axis_a='신청인원',
        axis_b='유입인원',
        title='소속부문별 신청인원 대비 타겟홍보 유입인원'), use_container_width=True)
    channel_apply_rate.plotly_chart(instance.make_hbarchart_single(
        df=instance.make_bar_target(df_main,'소속부문'),
        category='소속부문',
        axis_a='유입률',
        title='소속부문별 신청인원 대비 타겟홍보 유입률'), use_container_width=True)
    
    # 일곱번째 행
    channel_target, channel_target_rate = st.columns(2)
    channel_target.plotly_chart(instance.make_hbarchart_group(
        df=instance.make_bar_target(df_main,'소속부문'),
        category='소속부문',
        axis_a='타겟인원',
        axis_b='반응인원',
        title='소속부문별 홍보인원 대비 교육신청 반응인원'), use_container_width=True)
    channel_target_rate.plotly_chart(instance.make_hbarchart_single(
        df=instance.make_bar_target(df_main,'소속부문'),
        category='소속부문',
        axis_a='반응률',
        title='소속부문별 홍보인원 대비 교육신청 반응률'), use_container_width=True)
    
    # 여덟번째 행
    career_apply, career_apply_rate = st.columns(2)
    career_apply.plotly_chart(instance.make_hbarchart_group(
        df=instance.make_bar_target(df_main,'입사연차'),
        category='입사연차',
        axis_a='신청인원',
        axis_b='유입인원',
        title='입사연차별 신청인원 대비 타겟홍보 유입인원'), use_container_width=True)
    career_apply_rate.plotly_chart(instance.make_hbarchart_single(
        df=instance.make_bar_target(df_main,'입사연차'),
        category='입사연차',
        axis_a='유입률',
        title='입사연차별 신청인원 대비 타겟홍보 유입률'), use_container_width=True)
    
    # 아홉번째 행
    career_target, career_target_rate = st.columns(2)
    career_target.plotly_chart(instance.make_hbarchart_group(
        df=instance.make_bar_target(df_main,'입사연차'),
        category='입사연차',
        axis_a='타겟인원',
        axis_b='반응인원',
        title='입사연차별 홍보인원 대비 교육신청 반응인원'), use_container_width=True)
    career_target_rate.plotly_chart(instance.make_hbarchart_single(
        df=instance.make_bar_target(df_main,'입사연차'),
        category='입사연차',
        axis_a='반응률',
        title='입사연차별 홍보인원 대비 교육신청 반응률'), use_container_width=True)

    # 열번째 행
    title_apply, title_target = st.columns(2)
    title_apply.markdown('###### 타겟홍보 유입여부 (교육신청인원)')
    title_target.markdown('###### 교육신청 반응여부 (타겟홍보인원)')
    chart_apply, chart_target = st.columns(2)
    chart_apply.dataframe(instance.make_dataframe_target(apply=df_apply,target=df_target,data_type='신청'), use_container_width=True)
    chart_target.dataframe(instance.make_dataframe_target(apply=df_apply,target=df_target,data_type='타겟'), use_container_width=True)