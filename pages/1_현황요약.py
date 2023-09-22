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
from utils import fn_sidebar, fn_status, fn_trends, fig_piechart ,generate_colors, generate_outsides, fig_hbarchart, fig_vbarchart ,fig_linechart
from utils import df_atd as df_all


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
    # 신청수료인원
    df_stats = fn_status(df_all, '소속부문')
    df_sums = df_stats.sum(axis=0)
    df_sums = pd.DataFrame({'합계':df_sums}).transpose().drop(columns='소속부문')
    df_sums_apl = df_sums.drop(columns=['수료인원','수료누계','수료율','IMO신청인원','IMO신청누계','IMO신청률']).rename(columns={'신청인원':'고유인원','신청누계':'누계인원'})
    df_sums_apl.index = ['신청']
    df_sums_apl = df_sums_apl.reset_index()
    df_sums_apl = df_sums_apl.rename(columns={'index':'과정명'})
    df_sums_atd = df_sums.drop(columns=['신청인원','신청누계','수료율','IMO신청인원','IMO신청누계','IMO신청률']).rename(columns={'수료인원':'고유인원','수료누계':'누계인원'})
    df_sums_atd.index = ['수료']
    df_sums_atd = df_sums_atd.reset_index()
    df_sums_atd = df_sums_atd.rename(columns={'index':'비고'})
    df_sums = pd.concat([df_sums_atd, df_sums_apl], axis=0)
    st.dataframe(df_sums)

    
    # 온오프라인
    df_line = df_all.groupby(['과정형태','과정코드']).size().reset_index(name='홧수')
    df_line = df_line.groupby(['과정형태'])['과정코드'].count().reset_index(name='횟수')
    
    # 유무료
    df_all['유무료'] = df_all['수강료'].apply(lambda x: '무료' if x == 0 else '유료')
    df_fee = df_all.groupby(['유무료','과정코드']).size().reset_index(name='홧수')
    df_fee = df_fee.groupby(['유무료'])['과정코드'].count().reset_index(name='횟수')

    # ------------------------------------------  차트 제작에 필요한 리스트 제작  ---------------------------------------------
    sums_colors = generate_colors(df_sums.shape[0])
    sums_outsides = generate_outsides(df_sums.shape[0])
    sums_orders = ['신청','수료'][::-1]

    # ---------------------------------------------------  chart 제작  ------------------------------------------------------
    '''
    list_hbarchart[0]: dataframe (df_stat, df_trnd)
    list_hbarchart[1]: 참조 컬럼 (소속부문, 입사연차)
    list_hbarchart[2]: 고유값 (신청인원, 수료인원)
    list_hbarchart[3]: 누계값 (신청누계, 수료누계)
    list_hbarchart[4]: 차트 형태 (single, group)
    list_hbarchart[5]: 차트 방향 (horizontal, vertical)
    list_hbarchart[6]: 색상 리스트 ()
    list_hbarchart[7]: outside 리스트 ()
    list_hbarchart[8]: 항목 순서
    list_hbarchart[9]: 차트 제목
    list_hbarchart[10]: 캡션
    '''
    # 신청수료
    barlist_sums = [df_sums, '비고', '고유인원', '누계인원', 'group', 'h', sums_colors, sums_outsides, sums_orders, '', '']
    fig_sums = fig_hbarchart(barlist_sums)
    # 온오프라인
    fig_line = fig_piechart(df_line['과정형태'], df_line['횟수'])
    # 유무료
    fig_fee = fig_piechart(df_fee['유무료'], df_fee['횟수'])

    ########################################################################################################################
    ################################################     페이지 노출     ####################################################
    ########################################################################################################################
    # 메인페이지 타이틀
    st.header("교육운영 현황요약")
    st.markdown("<hr>", unsafe_allow_html=True)

    r1_c1, r1_c2, r1_c3, r1_c4, r1_c5 = st.columns(5)
    r1_c1.plotly_chart(fig_sums, use_container_width=True)
    r1_c2.plotly_chart(fig_line, use_container_width=True)
    r1_c3.plotly_chart(fig_fee, use_container_width=True)
    
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