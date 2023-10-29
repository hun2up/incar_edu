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
    # ------------------------------------------          인스턴스 생성          ---------------------------------------------
    instance = EduPages()
    df_all = instance.call_data()
    
    # ------------------------------------------          페이지 타이틀          ---------------------------------------------
    # 메인페이지 타이틀
    st.header("교육운영 현황요약")

    pie_line, pie_fee, pie_attend_rate, pie_imo_rate = st.columns(4)
    # 집합/온라인 과정현황
    df_line = df_all.groupby(['과정형태'])['과정코드'].nunique().reset_index(name='횟수')
    pie_line.plotly_chart(instance.make_piechart(label=df_line['과정형태'], value=df_line['횟수']), use_container_width=True)
    # 유료/무료 과정현황
    df_all['유무료'] = df_all['수강료'].apply(lambda x: '무료' if x == 0 else '유료')
    df_fee = df_all.groupby(['유무료'])['과정코드'].nunique().reset_index(name='횟수')
    pie_fee.plotly_chart(instance.make_piechart(label=df_fee['유무료'], value=df_fee['횟수']), use_container_width=True)
    # 수료율
    df_attend_rate = pd.DataFrame({'구분':['수료','미수료'],'수료율':[(df_sums.iloc[0,3]/df_sums.iloc[1,3]*100).round(1), (100-df_sums.iloc[0,3]/df_sums.iloc[1,3]*100).round(1)]})
    pie_attend_rate.plotly_chart(instance.make_piechart(label=df_attend_rate['구분'],value=df_attend_rate['수료율']), use_container_width=True)
    # IMO신청률
    df_imo_rate = pd.DataFrame({'구분':['IMO','IIMS'],'신청률':[(df_all['IMO신청여부'].sum()/df_all.shape[0]*100).round(1), (100-df_all['IMO신청여부'].sum()/df_all.shape[0]*100).round(1)]})
    pie_imo_rate.plotly_chart(instance.make_piechart(label=df_imo_rate['구분'],value=df_imo_rate['신청률']), use_container_width=True)



'''
########################################################################################################################
##############################################     라이브러리 호출하기     ##################################################
########################################################################################################################
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
hashed_passwords = stauth.Hasher(['XXX']).generate()
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
from utils import make_sidebar, hide_st_style, style_metric_cards
from utils import Chart

########################################################################################################################
################################################     인증페이지 설정     ###################################################
########################################################################################################################
hide_st_style()
instance = Chart()
df_all = instance.call_data_attend("attend", '소속부문')
# -----------------------------------------------------  사이드바  ---------------------------------------------------------
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
    ################################################     메인페이지 설정     ###################################################
    ########################################################################################################################
    # ----------------------------------------------  메이페이지 타이틀  -----------------------------------------------------
    st.header("교육운영 현황요약")
    st.markdown("<hr>", unsafe_allow_html=True)
    df_sums = instance.make_set_sums(instance.make_set_status(df_all,*['소속부문']))

    pie_line, pie_fee, pie_attend_rate, pie_imo_rate = st.columns(4)
    # 집합/온라인 과정현황
    df_line = df_all.groupby(['과정형태'])['과정코드'].count().reset_index(name='횟수')
    pie_line.plotly_chart(instance.make_piechart(label=df_line['과정형태'], value=df_line['횟수']), use_container_width=True)
    # 유료/무료 과정현황
    df_all['유무료'] = df_all['수강료'].apply(lambda x: '무료' if x == 0 else '유료')
    df_fee = df_all.groupby(['유무료'])['과정코드'].count().reset_index(name='횟수')
    pie_fee.plotly_chart(instance.make_piechart(label=df_fee['유무료'], value=df_fee['횟수']), use_container_width=True)
    # 수료율
    df_attend_rate = pd.DataFrame({'구분':['수료','미수료'],'수료율':[(df_sums.iloc[0,3]/df_sums.iloc[1,3]*100).round(1), (100-df_sums.iloc[0,3]/df_sums.iloc[1,3]*100).round(1)]})
    pie_attend_rate.plotly_chart(instance.make_piechart(label=df_attend_rate['구분'],value=df_attend_rate['수료율']), use_container_width=True)
    # IMO신청률
    df_imo_rate = pd.DataFrame({'구분':['IMO','IIMS'],'신청률':[(df_all['IMO신청여부'].sum()/df_all.shape[0]*100).round(1), (100-df_all['IMO신청여부'].sum()/df_all.shape[0]*100).round(1)]})
    pie_imo_rate.plotly_chart(instance.make_piechart(label=df_imo_rate['구분'],value=df_imo_rate['신청률']), use_container_width=True)

    hbar_sums, hbar_sums_people = st.columns(2)
    hbar_sums.plotly_chart(instance.make_hbarchart_group(
        df=df_sums,
        category='비고',
        axis_a='고유인원',
        axis_b='누계인원',
        title='신청/수료 현황'), use_container_width=True)
    hbar_sums_people.plotly_chart(instance.make_hbarchart_group(
        df=df_sums,
        category='비고',
        axis_a='재적인원 대비 고유인원',
        axis_b='재적인원 대비 누계인원',
        title='재적인원 대비 신청/수료 현황'), use_container_width=True)

    ##########################################################################################################################
    ##############################################     스타일 카드 (랭킹)     #################################################
    ##########################################################################################################################  
    style_metric_cards()

    # [소속부문, 파트너, 성명, 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률]
    titles_fa = ['교육신청 TOP5 (FA)','교육수료 TOP5 (FA)','수료율 TOP5 (FA) (수료율 동률일 경우 수료누계 기준 순위정렬)','수료율 하위 TOP5 (FA) (수료율 동률일 경우 신청누계 기준 순위정렬)'] # 각 항목별 제목
    instance.make_cards_a(df=instance.make_set_status(df_all,*['파트너','성명']), select=titles_fa, title="##### 주요랭킹 (FA)")

    # [소속부문, 파트너, 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률]
    titles_partner = ['교육신청 TOP5 (파트너)','교육수료 TOP5 (파트너)','수료율 TOP5 (파트너) (수료율 동률일 경우 수료누계 기준 순위정렬)','수료율 하위 TOP5 (파트너) (수료율 동률일 경우 신청누계 기준 순위정렬)']
    instance.make_cards_a(df=instance.make_set_status(df_all,*['소속부문','파트너']), select=titles_partner, title="##### 주요랭킹 (파트너)")

    # [소속부문, 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률]
    titles_channel = ['교육신청 순위 (소속부문)','교육수료 순위 (소속부문)','수료율 순위 (소속부문) (수료율 동률일 경우 수료누계 기준 순위정렬)','수료율 하위 (소속부문) (수료율 동률일 경우 신청누계 기준 순위정렬)']
    instance.make_cards_b(df=instance.make_set_status(df_all,*['소속부문']), select=titles_channel, title="##### 주요랭킹 (소속부문)")

    # [입사연차, 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률]
    titles_career = ['교육신청 순위 (입사연차)','교육수료 순위 (입사연차)','수료율 순위 (입사연차) (수료율 동률일 경우 수료누계 기준 순위정렬)','수료율 순위 (입사연차) (수료율 동률일 경우 신청누계 기준 순위정렬)']
    instance.make_cards_b(df=instance.make_set_status(df_all,*['입사연차']), select=titles_career, title="##### 주요랭킹 (입사연차)")
'''