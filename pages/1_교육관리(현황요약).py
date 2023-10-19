########################################################################################################################
##############################################     라이브러리 호출하기     ##################################################
########################################################################################################################
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
# from streamlit_extras.metric_cards import style_metric_cards
hashed_passwords = stauth.Hasher(['XXX']).generate()
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
from utils import make_sidebar, fn_status, fig_piechart, generate_colors, generate_outsides, fig_hbarchart, fn_rank_fa, fn_rank_partner, fn_rank_channel, style_metric_cards
from utils import df_atd as df_all
from utils import Chart

########################################################################################################################
################################################     인증페이지 설정     ###################################################
########################################################################################################################
isinstance = Chart()
df_all = isinstance.call_data_attend("attend")
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

    pie_line, pie_fee, pie_attend_rate, pie_imo_rate = st.columns(4)
    df_line = df_all.groupby(['과정형태'])['과정코드'].count().reset_index(name='횟수')
    pie_line = isinstance.make_piechart(label=df_line['과정형태'], value=['횟수'])

    ########################################################################################################################
    ##################################################     자료 제작     #####################################################
    ########################################################################################################################
    # ------------------------------------------------  dataframe 제작  -----------------------------------------------------
    df_chn = fn_status(df_all, '소속부문')
    df_crr = fn_status(df_all, '입사연차')
    # 신청수료인원
    df_sums = df_chn.sum(axis=0)
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
    # df_line = df_all.groupby(['과정형태','과정코드']).size().reset_index(name='횟수')
    df_line = df_all.groupby(['과정형태'])['과정코드'].count().reset_index(name='횟수')
    # df_line = df_line.groupby(['과정형태'])['과정코드'].count().reset_index(name='횟수')
    # 유무료
    df_all['유무료'] = df_all['수강료'].apply(lambda x: '무료' if x == 0 else '유료')
    df_fee = df_all.groupby(['유무료','과정코드']).size().reset_index(name='횟수')
    df_fee = df_fee.groupby(['유무료'])['과정코드'].count().reset_index(name='횟수')
    # 수료율
    comrate = {'구분':['수료','미수료'],'수료율':[(df_sums.iloc[0,1]/df_sums.iloc[1,1]*100).round(1), (100-df_sums.iloc[0,1]/df_sums.iloc[1,1]*100).round(1)]}
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


    # --------------------------------------------------  주요지표  ---------------------------------------------------------
    r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
    r1_c1.plotly_chart(fig_line, use_container_width=True)
    r1_c2.plotly_chart(fig_fee, use_container_width=True)
    r1_c3.plotly_chart(fig_comrate, use_container_width=True)
    r1_c4.plotly_chart(fig_imo, use_container_width=True)

    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    r2_c1.plotly_chart(fig_sums, use_container_width=True)

    # ----------------------------------------------------  랭킹  -----------------------------------------------------------
    def metrics_fa(st, title, df, column_name1, column_name2, column_name3, ascend):
        st.write(title)
        df = df.sort_values(by=[column_name1, column_name2], ascending=[ascend, False])
        columns = st.columns(5)
        for i in range(5):
            columns[i].metric(df.iat[i, 1] + ' ' + df.iat[i, 2], df.iat[i, column_name3])

    def metrics_category(st, title, df, column_name1, column_name2, column_name3):
        st.write(title)
        df = df.sort_values(by=[column_name1, column_name2], ascending=[False, False])
        columns = st.columns(5)
        for i in range(5):
            columns[i].metric(df.iat[i, 0], df.iat[i, column_name3])
    
    st.markdown('---')
    st.write("주요랭킹 (FA)")
    metrics_fa(st, "교육신청 TOP5 (FA)", df_rank_fa, '신청누계', '수료율', 3, False)
    metrics_fa(st, "교육수료 TOP5 (FA)", df_rank_fa, '수료누계', '수료율', 4, False)
    metrics_fa(st, "수료율 TOP5 (FA) (수료율 동률일 경우 수료누계 기준 순위정렬)", df_rank_fa, '수료율', '수료누계', 5, False)
    metrics_fa(st, "수료율 하위 TOP5 (FA) (수료율 동률일 경우 신청누계 기준 순위정렬)", df_rank_fa, '수료율', '신청누계', 5, True)

    st.markdown('---')
    st.write("주요랭킹 (소속부문)")
    metrics_category(st, "교육신청 TOP5 (소속부문)", df_chn, '신청누계', '수료율', 2)
    metrics_category(st, "교육수료 TOP5 (소속부문)", df_chn, '수료누계', '수료율', 4)
    metrics_category(st, "수료율 TOP5 (소속부문) (수료율 동률일 경우 수료누계 기준 순위정렬)", df_chn, '수료율', '수료누계', 5)

    st.markdown('---')
    st.write("주요랭킹 (입사연차)")
    metrics_category(st, "교육신청 TOP5 (입사연차)", df_crr, '신청누계', '수료율', 2)
    metrics_category(st, "교육수료 TOP5 (입사연차)", df_crr, '수료누계', '수료율', 4)
    metrics_category(st, "수료율 TOP5 (입사연차) (수료율 동률일 경우 수료누계 기준 순위정렬)", df_crr, '수료율', '수료누계', 5)

    st.dataframe(df_rank_fa)
    style_metric_cards()
