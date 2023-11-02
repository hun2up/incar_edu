#########################################################################################################################
################                                    라이브러리 호출                                     ##################
#########################################################################################################################
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
hashed_passwords = stauth.Hasher(['XXX']).generate()
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
from utils import make_sidebar, hide_st_style, style_metric_cards
from utils import EduPages

#########################################################################################################################
#################                                    인증페이지 설정                                     #################
#########################################################################################################################
# ------------------------------------------         인증페이지 삽입          --------------------------------------------
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
    ###################                                    페이지 제작                                     ###################
    #########################################################################################################################
    # ------------------------------------------          인스턴스 생성 및 페이지 타이틀          ---------------------------------------------
    hide_st_style()
    instance = EduPages() # 인스턴스 생성
    df_all = instance.call_data_pages()
    st.header("교육운영 현황요약") # 페이지 타이틀

    # --------------------------------------------          사이드바          ------------------------------------------------
    # 사이드바 헤더
    st.sidebar.header("원하는 옵션을 선택하세요")
    #사이드바 제작
    month = make_sidebar(df_all,'월') # 월도 선택 사이드바
    region = make_sidebar(df_all,'지역') # 지역 선택 사이드바
    partner = make_sidebar(df_all,'보험사') # 보험사 선택 사이드바
    line = make_sidebar(df_all,'과정형태') # 과정 온오프라인 선택 사이드바
    theme = make_sidebar(df_all,'과정분류') # 과정 테마 선택 사이드바
    name = make_sidebar(df_all,'과정명') # 세부과정 선택 사이드바
    channel = make_sidebar(df_all,'소속부문') # 소속부문 선택 사이드바
    career = make_sidebar(df_all,'입사연차') # 입사연차 선택 사이드바
    # 데이터와 사이드바 연결
    df_all = df_all.query(
        "월 == @month & 지역 == @region & 보험사 == @partner & 과정형태 == @line & 과정분류 == @theme & 과정명 == @name & 소속부문 == @channel & 입사연차 == @career"
    )

    # ------------------------------------------          차트 제작          ---------------------------------------------
    # 첫번째 행 (집합 & 온라인 / 유료 & 무료 / 수료율 / IMO신청률)
    pie_line, pie_fee, pie_attend_rate, pie_imo_rate = st.columns(4)
    pie_line.plotly_chart(instance.make_piechart(
        label=df_all.groupby(['과정형태'])['과정코드'].nunique().reset_index(name='횟수')['과정형태'],
        value=df_all.groupby(['과정형태'])['과정코드'].nunique().reset_index(name='횟수')['횟수']),
        use_container_width=True)
    df_all['유무료'] = df_all['수강료'].apply(lambda x: '무료' if x == 0 else '유료')
    pie_fee.plotly_chart(instance.make_piechart(
        label=df_all.groupby(['유무료'])['과정코드'].nunique().reset_index(name='횟수')['유무료'],
        value=df_all.groupby(['유무료'])['과정코드'].nunique().reset_index(name='횟수')['횟수']),
        use_container_width=True)
    pie_attend_rate.plotly_chart(instance.make_piechart(
        label=instance.make_rates(df=df_all,item_a='수료',item_b='미수료',reference='수료현황',column='수료율')['구분'],
        value=instance.make_rates(df=df_all,item_a='수료',item_b='미수료',reference='수료현황',column='수료율')['수료율']),
        use_container_width=True)
    pie_imo_rate.plotly_chart(instance.make_piechart(
        label=instance.make_rates(df=df_all,item_a='IMO',item_b='IIMS',reference='IMO신청여부',column='IMO신청률')['구분'],
        value=instance.make_rates(df=df_all,item_a='IMO',item_b='IIMS',reference='IMO신청여부',column='IMO신청률')['IMO신청률']),
        use_container_width=True)

    # 두번째 행 (신청인원 & 수료인원 / 월별 신청인원 & 수료인원 현황)
    edu_total = st.columns((1,3))
    edu_total[0].plotly_chart(instance.make_vbarchart_group(
        df=instance.make_summary_status(df_all),
        category='구분',
        axis_a='고유인원',
        axis_b='누계인원',
        title='신청/수료 현황'), use_container_width=True)
    edu_total[1].plotly_chart(instance.make_linechart(
        df=instance.make_trend_all(df_all),
        category='구분',
        xaxis='월',
        yaxis='값',
        title='신청인원 및 수료인원 추이'), use_container_width=True)

    ##########################################################################################################################
    ##############################################     스타일 카드 (랭킹)     #################################################
    ##########################################################################################################################  
    style_metric_cards()

    # [소속부문, 파트너, 성명, 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률]
    instance.make_cards_a(
        df=instance.make_set_status(df_all,*['파트너','성명']),
        select=['교육신청 TOP5 (FA)','교육수료 TOP5 (FA)','수료율 TOP5 (FA) (수료율 동률일 경우 수료누계 기준 순위정렬)','수료율 하위 TOP5 (FA) (수료율 동률일 경우 신청누계 기준 순위정렬)'],
        title="##### 주요랭킹 (FA)")

    # [소속부문, 파트너, 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률]
    instance.make_cards_a(
        df=instance.make_set_status(df_all,*['소속부문','파트너']),
        select=['교육신청 TOP5 (파트너)','교육수료 TOP5 (파트너)','수료율 TOP5 (파트너) (수료율 동률일 경우 수료누계 기준 순위정렬)','수료율 하위 TOP5 (파트너) (수료율 동률일 경우 신청누계 기준 순위정렬)'],
        title="##### 주요랭킹 (파트너)")

    # [소속부문, 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률]
    instance.make_cards_b(
        df=instance.make_set_status(df_all,*['소속부문']),
        select=['교육신청 순위 (소속부문)','교육수료 순위 (소속부문)','수료율 순위 (소속부문) (수료율 동률일 경우 수료누계 기준 순위정렬)','수료율 하위 (소속부문) (수료율 동률일 경우 신청누계 기준 순위정렬)'],
        title="##### 주요랭킹 (소속부문)")

    # [입사연차, 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률]
    instance.make_cards_b(
        df=instance.make_set_status(df_all,*['입사연차']),
        select=['교육신청 순위 (입사연차)','교육수료 순위 (입사연차)','수료율 순위 (입사연차) (수료율 동률일 경우 수료누계 기준 순위정렬)','수료율 순위 (입사연차) (수료율 동률일 경우 신청누계 기준 순위정렬)'],
        title="##### 주요랭킹 (입사연차)")