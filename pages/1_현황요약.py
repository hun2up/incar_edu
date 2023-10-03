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
from utils import fn_sidebar, fn_status, fn_trends, fig_piechart, generate_colors, generate_outsides, fig_hbarchart, fig_vbarchart, fn_rank_fa, fn_rank_partner, fn_rank_channel
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
    df_sums_apl = df_sums_apl.rename(columns={'index':'비고'})
    df_sums_atd = df_sums.drop(columns=['신청인원','신청누계','수료율','IMO신청인원','IMO신청누계','IMO신청률']).rename(columns={'수료인원':'고유인원','수료누계':'누계인원'})
    df_sums_atd.index = ['수료']
    df_sums_atd = df_sums_atd.reset_index()
    df_sums_atd = df_sums_atd.rename(columns={'index':'비고'})
    df_sums = pd.concat([df_sums_atd, df_sums_apl], axis=0)
    # 온오프라인
    df_line = df_all.groupby(['과정형태','과정코드']).size().reset_index(name='홧수')
    df_line = df_line.groupby(['과정형태'])['과정코드'].count().reset_index(name='횟수')
    # 유무료
    df_all['유무료'] = df_all['수강료'].apply(lambda x: '무료' if x == 0 else '유료')
    df_fee = df_all.groupby(['유무료','과정코드']).size().reset_index(name='홧수')
    df_fee = df_fee.groupby(['유무료'])['과정코드'].count().reset_index(name='횟수')
    # 수료율
    comrate = {'구분':['수료','미수료'],'수료율':[df_sums.iloc[0,1]/df_sums.iloc[1,1]*100, 100-df_sums.iloc[0,1]/df_sums.iloc[1,1]*100]}
    df_comrate = pd.DataFrame(comrate)
    # IMO신청률
    imo = {'구분':['IMO','IIMS'],'신청률':[(df_all['IMO신청여부'].sum()/df_all.shape[0]*100).round(1), (100-df_all['IMO신청여부'].sum()/df_all.shape[0]*100).round(1)]}
    df_imo = pd.DataFrame(imo)

    df_rank_fa = fn_rank_fa(df_all)
    df_rank_partner = fn_rank_partner(df_all)
    df_rank_channel = fn_rank_channel(df_all)
    # ---------------------------------------------------  chart 제작  ------------------------------------------------------
    # 온오프라인
    fig_line = fig_piechart(df_line['과정형태'], df_line['횟수'])
    # 유무료
    fig_fee = fig_piechart(df_fee['유무료'], df_fee['횟수'])
    # 수료율
    fig_comrate = fig_piechart(df_comrate['구분'], df_comrate['수료율'])
    # IMO 신청률
    fig_imo = fig_piechart(df_imo['구분'], df_imo['신청률'])

    # 신청인원 및 수료인원
    # 색상(hexcode) 제작
    sums_colors = generate_colors(df_sums.shape[0])
    # 텍스트위치(outsides) 제작
    sums_outsides = generate_outsides(df_sums.shape[0])
    # barchart 항목 순서 지정
    orders_sums = ['신청', '수료'][::-1]
    sums_list = [df_sums, '비고', '고유인원', '누계인원', 'group', 'h', sums_colors, sums_outsides, orders_sums, '', '']
    fig_sums = fig_hbarchart(sums_list)

    ########################################################################################################################
    ################################################     페이지 노출     ####################################################
    ########################################################################################################################
    # 메인페이지 타이틀
    st.header("교육운영 현황요약")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
    r1_c1.plotly_chart(fig_line, use_container_width=True)
    r1_c2.plotly_chart(fig_fee, use_container_width=True)
    r1_c3.plotly_chart(fig_comrate, use_container_width=True)
    r1_c4.plotly_chart(fig_imo, use_container_width=True)

    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    r2_c1.plotly_chart(fig_sums, use_container_width=True)

    df_rank_fa = df_rank_fa.sort_values(by='신청누계', ascending=False)
    st.dataframe(df_rank_fa)
    cols_rank = st.columns([1,1,1,1,1])
    cols_rank[0].metric(df_rank_fa.iat[0,1] + df_rank_fa.iat[0,2], df_rank_fa.iat[0,3], df_rank_fa.iat[0,3])
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