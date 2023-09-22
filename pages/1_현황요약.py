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
from utils import fn_sidebar, fn_status, fn_trends, fig_piechart ,generate_colors, generate_outsides, fig_hbarchart, fig_linechart
from utils import df_atd as df_all
from utils import df_course

########################################################################################################################
################################################     인증페이지 설정     ###################################################
########################################################################################################################
# -----------------------------------------------------  사이드바  ---------------------------------------------------------
# 사이드바 헤더
st.sidebar.header("원하는 옵션을 선택하세요")
#사이드바 제작
month = fn_sidebar(df_all,'월') # 월도 선택 사이드바
region = fn_sidebar(df_all,'지역') # 지역 선택 사이드바
partner = fn_sidebar(df_all,'보험사') # 보험사 선택 사이드바
line = fn_sidebar(df_all,'과정형태') # 과정 온오프라인 선택 사이드바
theme = fn_sidebar(df_all,'과정분류') # 과정 테마 선택 사이드바
name = fn_sidebar(df_all,'과정명') # 세부과정 선택 사이드바
channel = fn_sidebar(df_all,'소속부문') # 소속부문 선택 사이드바
career = fn_sidebar(df_all,'입사연차') # 입사연차 선택 사이드바
# 데이터와 사이드바 연결
df_all = df_all.query(
    "월 == @month & 지역 == @region & 보험사 == @partner & 과정형태 == @line & 과정분류 == @theme & 과정명 == @name & 소속부문 == @channel & 입사연차 == @career"
)

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
    ################################################     메인페이지 설정     ###################################################
    ########################################################################################################################
    authenticator.logout('Logout', 'sidebar')

    ########################################################################################################################
    ##################################################     자료 제작     #####################################################
    ########################################################################################################################
    # ------------------------------------------------  dataframe 제작  -----------------------------------------------------
    # barchart 제작을 위한 현황 dataframe (소속부문별)
    df_all_stat = fn_status(df_all, '소속부문')
    # linechart 제작을 위한 추세 dataframe (월별 & 소속부문별)
    df_all_trnd = fn_trends(df_all, '소속부문')

    # 영수/환급보험료 데이터를 숫자로 변환
    # df_course['수강료'] = pd.to_numeric(df_course['수강료'].astype(str), errors='coerce')
    '''
    # 유무료
    for modify_fee in range(df_course.shape[0]):
        if df_course.iloc[modify_fee,6] == 0:
            
            df_course.iloc[modify_fee,6] = "무료"
        else:
            df_course.iloc[modify_fee,6] = "유료"
    '''
    df_course['유무료'] = df_course['수강료'].apply(lambda x: '무료' if x == 0 else '유료')


    st.dataframe(df_course)
    
    # 온오프라인
    df_line = df_all.groupby(['과정형태','과정코드']).size().reset_index(name='홧수')
    df_line = df_line.groupby(['과정형태'])['과정코드'].count().reset_index(name='횟수')
    # 유무료
    df_fee = df_course.groupby(['유무료','과정코드']).size().reset_index(name='홧수')
    df_fee = df_fee.groupby(['유무료'])['과정코드'].count().reset_index(name='횟수')

    fig_line = fig_piechart(df_line['과정형태'], df_line['횟수'])
    fig_fee = fig_piechart(df_fee['유무료'], df_fee['횟수'])

    ########################################################################################################################
    ################################################     페이지 노출     ####################################################
    ########################################################################################################################
    # 메인페이지 타이틀
    st.header("교육운영 현황요약")
    st.markdown("<hr>", unsafe_allow_html=True)
    

    r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
    r1_c1.plotly_chart(fig_line, use_container_width=True)
    r1_c2.plotly_chart(fig_fee, use_container_width=True)
    
    


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