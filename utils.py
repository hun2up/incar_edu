########################################################################################################################
################################################     라이브러리 호출     ###################################################
########################################################################################################################
import pandas as pd
import streamlit as st
import plotly as pl
from datetime import datetime

########################################################################################################################
##############################################     function 정의     ####################################################
########################################################################################################################
# -------------------------------------------    스트림릿 워터마크 제거    ---------------------------------------------------
def hide_st_style():
    hide_st_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

# ------------------------------------    랭킹 디스플레이를 위한 스타일 카드 정의    --------------------------------------------
def style_metric_cards(
    border_size_px: int = 1,
    border_color: str = "#CCC",
    border_radius_px: int = 5,
    border_left_color: str = "rgb(55,126,184)",
    box_shadow: bool = True,
):

    box_shadow_str = (
        "box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;"
        if box_shadow
        else "box-shadow: none !important;"
    )
    st.markdown(
        f"""
        <style>
            div[data-testid="metric-container"] {{
                border: {border_size_px}px solid {border_color};
                padding: 5% 5% 5% 10%;
                border-radius: {border_radius_px}px;
                border-left: 0.5rem solid {border_left_color} !important;
                {box_shadow_str}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------    Google Sheet 데이터베이스 호출    ----------------------------------------------
# select : {수료현황 : attend}, {신청현황 : month}
@st.cache_data(ttl=600)
def call_data(select):
    # 데이터베이스 호출 & 컬럼 삭제 (번호)
    df_select = pd.read_csv(st.secrets[f"{select}_url"].replace("/edit#gid=", "/export?format=csv&gid=")).drop(columns=['번호'])
    df_select.rename(columns={'성함':'성명'}, inplace=True)
    # 과정현황 데이터베이스 호출 (과정현황) & 컬럼 삭제 (번호)
    df_course = pd.read_csv(st.secrets["course_url"].replace("/edit#gid=", "/export?format=csv&gid=")).drop(columns=['번호'])
    return df_select, df_course

# ----------------------------------------------    sidebar 제작    -----------------------------------------------------
def make_sidebar(dfv_sidebar, colv_sidebar):
    return st.sidebar.multiselect(
        colv_sidebar,
        options=dfv_sidebar[colv_sidebar].unique(),
        default=dfv_sidebar[colv_sidebar].unique()
    )




# ---------------------------------------    Google Sheet 데이터베이스 호출    ----------------------------------------------
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

# ----------------------------------------------    sidebar 제작    -----------------------------------------------------
def fn_sidebar(dfv_sidebar, colv_sidebar):
    return st.sidebar.multiselect(
        colv_sidebar,
        options=dfv_sidebar[colv_sidebar].unique(),
        default=dfv_sidebar[colv_sidebar].unique()
    )

# -------------------------------   수료현황 테이블 정리 및 테이블 병합 (신청현황 & 과정현황)   ------------------------------------ 
def fn_attend(dfv_attend, dfv_course1):
    # df_attend: 컬럼 생성 (과정코드)
    dfv_attend.insert(loc=1, column='과정코드', value=None)
    # 데이터 정리 (과정코드)
    for modify_attend in range(dfv_attend.shape[0]):
        dfv_attend.iloc[modify_attend,1] = dfv_attend.iloc[modify_attend,0].split(")")[0].replace('(','')
    # df_attend: 컬럼 삭제 (과정명, 비고)
    dfv_attend = dfv_attend.drop(columns=['과정명','비고'])
    # df_attend: 데이터 정리 (IMO신청여부: Y -> 1)
    dfv_attend['IMO신청여부'] = dfv_attend['IMO신청여부'].replace({'Y':1, 'N':0})
    # df_attend: 데이터 정리 (수료현황: 텍스트 -> 숫자)
    dfv_attend['수료현황'] = pd.to_numeric(dfv_attend['수료현황'], errors='coerce')
    # df_attend: 컬럼 추가 및 데이터 삽입 (입사연차)
    dfv_attend['입사연차'] = (datetime.now().year%100 + 1 - dfv_attend['사원번호'].astype(str).str[:2].astype(int, errors='ignore')).apply(lambda x: f'{x}년차')
    # df_attend: 데이터 삭제 (파트너: 인카본사)
    dfv_attend = dfv_attend.drop(dfv_attend[dfv_attend.iloc[:,4] == '인카본사'].index)
    dfv_attend['과정코드'] = dfv_attend['과정코드'].astype(str)
    # df_course1: 컬럼명 & 데이터 변경 (course1_date -> 월)
    for date in range(dfv_course1.shape[0]):
        value_date = pd.to_datetime(dfv_course1.at[date, '교육일자'], format="%Y. %m. %d")
        month = value_date.month
        dfv_course1.at[date, '교육일자'] = f'{month}월'
    dfv_course1['과정코드'] = dfv_course1['과정코드'].astype(str)
    ###### df_course1 = [과정코드, 과정분류, 과정명, 보험사, 교육일자, 과정형태, 수강료, 지역, 교육장소, 정원, 목표인원]
    # 테이블 병합 (과정현황 + 수료현황)
    dfv_attend = pd.merge(dfv_course1, dfv_attend, on=['과정코드'])
    # df_atd: 컬럼명 변경 (교육일자 -> 월)
    dfv_attend.rename(columns={'교육일자':'월'}, inplace=True)
    ###### df_atd = [과정코드, 과정분류, 과정명, 보험사, 월, 과정형태, 수강료, 지역, 교육장소, 정원, 목표인원, 소속부문, 소속총괄, 소속부서, 파트너, 사원번호, 성함, IMO신청여부, 수료현황, 입사연차]
    return dfv_attend

# ------------------------------   신청현황 테이블 정리 및 테이블 병합 (신청현황 & 과정현황)   -------------------------------------
def fn_apply(dfv_apply, dfv_course2):
    # df_apply: 컬럼 생성 (과정코드)
    dfv_apply.insert(loc=1, column='과정코드', value=None)
    # df_apply: 데이터 정리 (과정코드)
    for modify_apply in range(dfv_apply.shape[0]):
        dfv_apply.iloc[modify_apply,1] = dfv_apply.iloc[modify_apply,0].split(")")[0].replace('(','')
    # df_apply: 컬럼 추가 (신청인원)
    dfv_apply = dfv_apply.groupby(['날짜','과정코드','소속부문'])['사원번호'].count().reset_index(name='신청인원')
    # df_course2: 데이터 변경 ([지역]+과정명)
    dfv_course2['과정명'] = '['+dfv_course2['지역']+'] '+dfv_course2['과정명']
    # 테이블 병합 (신청현황 + 과정현황)
    dfv_apply = pd.merge(dfv_apply, dfv_course2[['과정코드','과정명','교육일자','목표인원']], on=['과정코드'])
    # df_apl: 날짜 오름차순으로 정렬
    dfv_apply = dfv_apply.sort_values(by='날짜', ascending=True)
    ##### df_apl = ['날짜','과정코드','소속부문','신청인원','목표인원','과정명']
    return dfv_apply

# 필요한 변수(리스트) 정의: 수료인원, 수료누계, IMO신청인원, IMO신청누계
basic_index = [['수료현황', '수료인원', '수료누계', '수료율'], ['IMO신청여부', 'IMO신청인원', 'IMO신청누계', 'IMO신청률']]

# -------------------------------------------  소속부문별 고유값 및 누계값  --------------------------------------------------
# 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
def fn_status(dfv_atd, colv_reference):
    # dfv_atd를 '소속부문', '사원번호' 칼럼으로 묶고, 누적개수 구하기
    dfv_status_apply = dfv_atd.groupby([colv_reference,'사원번호']).size().reset_index(name='신청누계')
    # df_func_number에서 묶여있는 '사원번호' 카운트 (중복값 제거한 인원)
    dfv_status_apply_unique = dfv_status_apply.groupby([colv_reference])['사원번호'].count().reset_index(name='신청인원')
    # df_func_number에서 '누적개수' 카운트 (중복값 더한 인원)
    dfv_status_apply_total = dfv_status_apply.groupby([colv_reference])['신청누계'].sum().reset_index(name='신청누계')
    # 위에서 중복값을 제거한 데이터프레임과 모두 더한 데이터프레임 병합
    dfv_status_apply = pd.merge(dfv_status_apply_unique, dfv_status_apply_total)
    # 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
    for groups in range(len(basic_index)):
        # 수료현황, IMO신청여부 1로 묶기
        dfv_status_attend = dfv_atd.groupby(basic_index[groups][0]).get_group(1)
        # 수료현황 전체 더하기 (수료누계)
        dfv_status_attend_total = dfv_atd.groupby([colv_reference])[basic_index[groups][0]].sum().reset_index(name=basic_index[groups][2])
        # 수료현황(1,0)별 사원번호 개수 (수료인원)
        dfv_status_attend_unique = dfv_atd.groupby([colv_reference,basic_index[groups][0]])['사원번호'].nunique().reset_index(name=basic_index[groups][1])
        # 수료현항 0인 row 날리기
        dfv_status_attend_unique = dfv_status_attend_unique[dfv_status_attend_unique[basic_index[groups][0]] != 0]
        # 수료현황 column 날리기
        dfv_status_attend_unique = dfv_status_attend_unique.drop(columns=[basic_index[groups][0]])
        # 수료인원이랑 수료누계 합치기
        dfv_status_attend = pd.merge(dfv_status_attend_unique, dfv_status_attend_total, on=[colv_reference])
        # 수료율
        dfv_status_attend_total[basic_index[groups][3]] = (dfv_status_attend_total[basic_index[groups][2]]/dfv_status_apply['신청누계']*100).round(1)
        dfv_status_attend_total = dfv_status_attend_total.drop(columns=[basic_index[groups][2]])
        # 수료율/IMO신청률 합치기
        dfv_status_attend = pd.merge(dfv_status_attend, dfv_status_attend_total, on=[colv_reference])
        dfv_status_apply = pd.merge(dfv_status_apply, dfv_status_attend, on=[colv_reference])
    # 다 합쳐서 반환
    return dfv_status_apply

# ----------------------------------------  월별 & 소속부문별 고유값 및 누계값  -----------------------------------------------
# 월별, 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
def fn_trends(dfv_atd, colv_reference):
    # 월, 소속부문, 사원번호, 그리고 신청누계(추가)
    dfv_trends_apply = dfv_atd.groupby(['월',colv_reference,'사원번호']).size().reset_index(name='신청누계')
    # 월, 소속부문, 그리고 신청인원 (df_func_monthly에서 사원번호 중복제거) (추가)
    dfv_trends_apply_unique = dfv_trends_apply.groupby(['월',colv_reference])['사원번호'].count().reset_index(name='신청인원')
    # 월, 소속부문, 신청인원 (df_func_monthly에서 사원번호 없애고 신청누계 다 더하기)
    dfv_trends_apply_total = dfv_trends_apply.groupby(['월',colv_reference])['신청누계'].sum().reset_index(name='신청누계')
    # 월, 소속부문, 신청누계, 신청인원 (df_func_unique와 df_func_total 합치기)
    dfv_trends_apply = pd.merge(dfv_trends_apply_total, dfv_trends_apply_unique, on=['월',colv_reference])
    # 수료인원, 수료누계, IMO신청인원, IMO신청누계
    for groups in range(len(basic_index)):
        # 수료현황, IMO신청여부 1로 묶기
        dfv_trends_attend = dfv_atd.groupby(basic_index[groups][0]).get_group(1)
        # 수료현황(1,0)별 사원번호 개수 (수료인원)
        dfv_trends_attend_unique = dfv_atd.groupby(['월',colv_reference,basic_index[groups][0]])['사원번호'].count().reset_index(name=basic_index[groups][1])
        # 수료현항 0인 row 날리기
        dfv_trends_attend_unique = dfv_trends_attend_unique[dfv_trends_attend_unique[basic_index[groups][0]] != 0]
        # 수료현황 column 날리기
        dfv_trends_attend_unique = dfv_trends_attend_unique.drop(columns=[basic_index[groups][0]])
        # 수료현황 전체 더하기 (수료누계)
        dfv_trends_attend_total = dfv_atd.groupby(['월',colv_reference])[basic_index[groups][0]].sum().reset_index(name=basic_index[groups][2])
        # 수료율
        dfv_trends_attend_total[basic_index[groups][3]] = (dfv_trends_attend_total[basic_index[groups][2]]/dfv_trends_apply['신청누계']*100).round(1)
        # 수료인원이랑 수료누계 합치기
        dfv_trends_attend = pd.merge(dfv_trends_attend_unique, dfv_trends_attend_total, on=['월',colv_reference])
        dfv_trends_apply = pd.merge(dfv_trends_apply, dfv_trends_attend, on=['월',colv_reference])
    # 다 합쳐서 반환
    return dfv_trends_apply

# -------------------------------------------  소속부문별 고유값 및 누계값  --------------------------------------------------
# 소속부문, 파트너, FA 별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
def fn_rank_fa(dfv_atd):
    # dfv_atd를 '소속부문', '사원번호' 칼럼으로 묶고, 누적개수 구하기
    dfv_rank = dfv_atd.groupby(['소속부문','파트너','성명'])['사원번호'].size().reset_index(name='신청누계')
    # 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
    for groups in range(len(basic_index)):
        # 수료현황, IMO신청여부 1로 묶기
        dfv_rank_attend = dfv_atd.groupby(basic_index[groups][0]).get_group(1)
        # 수료현황 전체 더하기 (수료누계)
        dfv_rank_attend_total = dfv_atd.groupby(['소속부문','파트너','성명'])[basic_index[groups][0]].sum().reset_index(name=basic_index[groups][2])
        # 수료현황(1,0)별 사원번호 개수 (수료인원)
        dfv_rank_attend_unique = dfv_atd.groupby(['소속부문','파트너','성명',basic_index[groups][0]])['사원번호'].nunique().reset_index(name=basic_index[groups][1])
        # 수료현항 0인 row 날리기
        dfv_rank_attend_unique = dfv_rank_attend_unique[dfv_rank_attend_unique[basic_index[groups][0]] != 0]
        # 수료현황 column 날리기
        dfv_rank_attend_unique = dfv_rank_attend_unique.drop(columns=[basic_index[groups][0]])
        # 수료인원이랑 수료누계 합치기
        dfv_rank_attend = pd.merge(dfv_rank_attend_unique, dfv_rank_attend_total, on=['소속부문','파트너','성명'])
        # 수료율
        dfv_rank_attend_total[basic_index[groups][3]] = (dfv_rank_attend_total[basic_index[groups][2]]/dfv_rank['신청누계']*100).round(1)
        dfv_rank_attend_total = dfv_rank_attend_total.drop(columns=[basic_index[groups][2]])
        # 수료율/IMO신청률 합치기
        dfv_rank_attend = pd.merge(dfv_rank_attend, dfv_rank_attend_total, on=['소속부문','파트너','성명'])
        dfv_rank = pd.merge(dfv_rank, dfv_rank_attend, on=['소속부문','파트너','성명'])
    dfv_rank = dfv_rank.drop(columns=['수료인원','IMO신청인원'])
    # 다 합쳐서 반환
    return dfv_rank

# -------------------------------------------  소속부문별 고유값 및 누계값  --------------------------------------------------
# 소속부문, 파트너, FA 별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
def fn_rank_partner(dfv_atd):
    # dfv_atd를 '소속부문', '사원번호' 칼럼으로 묶고, 누적개수 구하기
    dfv_rank = dfv_atd.groupby(['소속부문','파트너'])['사원번호'].size().reset_index(name='신청누계')
    # 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
    for groups in range(len(basic_index)):
        # 수료현황, IMO신청여부 1로 묶기
        dfv_rank_attend = dfv_atd.groupby(basic_index[groups][0]).get_group(1)
        # 수료현황 전체 더하기 (수료누계)
        dfv_rank_attend_total = dfv_atd.groupby(['소속부문','파트너'])[basic_index[groups][0]].sum().reset_index(name=basic_index[groups][2])
        # 수료현황(1,0)별 사원번호 개수 (수료인원)
        dfv_rank_attend_unique = dfv_atd.groupby(['소속부문','파트너',basic_index[groups][0]])['사원번호'].nunique().reset_index(name=basic_index[groups][1])
        # 수료현항 0인 row 날리기
        dfv_rank_attend_unique = dfv_rank_attend_unique[dfv_rank_attend_unique[basic_index[groups][0]] != 0]
        # 수료현황 column 날리기
        dfv_rank_attend_unique = dfv_rank_attend_unique.drop(columns=[basic_index[groups][0]])
        # 수료인원이랑 수료누계 합치기
        dfv_rank_attend = pd.merge(dfv_rank_attend_unique, dfv_rank_attend_total, on=['소속부문','파트너'])
        # 수료율
        dfv_rank_attend_total[basic_index[groups][3]] = (dfv_rank_attend_total[basic_index[groups][2]]/dfv_rank['신청누계']*100).round(1)
        dfv_rank_attend_total = dfv_rank_attend_total.drop(columns=[basic_index[groups][2]])
        # 수료율/IMO신청률 합치기
        dfv_rank_attend = pd.merge(dfv_rank_attend, dfv_rank_attend_total, on=['소속부문','파트너'])
        dfv_rank = pd.merge(dfv_rank, dfv_rank_attend, on=['소속부문','파트너'])
    dfv_rank = dfv_rank.drop(columns=['수료인원','IMO신청인원'])
    # 다 합쳐서 반환
    return dfv_rank

# -------------------------------------------  소속부문별 고유값 및 누계값  --------------------------------------------------
# 소속부문, 파트너, FA 별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
def fn_rank_channel(dfv_atd):
    # dfv_atd를 '소속부문', '사원번호' 칼럼으로 묶고, 누적개수 구하기
    dfv_rank = dfv_atd.groupby(['소속부문'])['사원번호'].size().reset_index(name='신청누계')
    # 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
    for groups in range(len(basic_index)):
        # 수료현황, IMO신청여부 1로 묶기
        dfv_rank_attend = dfv_atd.groupby(basic_index[groups][0]).get_group(1)
        # 수료현황 전체 더하기 (수료누계)
        dfv_rank_attend_total = dfv_atd.groupby(['소속부문'])[basic_index[groups][0]].sum().reset_index(name=basic_index[groups][2])
        # 수료현황(1,0)별 사원번호 개수 (수료인원)
        dfv_rank_attend_unique = dfv_atd.groupby(['소속부문',basic_index[groups][0]])['사원번호'].nunique().reset_index(name=basic_index[groups][1])
        # 수료현항 0인 row 날리기
        dfv_rank_attend_unique = dfv_rank_attend_unique[dfv_rank_attend_unique[basic_index[groups][0]] != 0]
        # 수료현황 column 날리기
        dfv_rank_attend_unique = dfv_rank_attend_unique.drop(columns=[basic_index[groups][0]])
        # 수료인원이랑 수료누계 합치기
        dfv_rank_attend = pd.merge(dfv_rank_attend_unique, dfv_rank_attend_total, on=['소속부문'])
        # 수료율
        dfv_rank_attend_total[basic_index[groups][3]] = (dfv_rank_attend_total[basic_index[groups][2]]/dfv_rank['신청누계']*100).round(1)
        dfv_rank_attend_total = dfv_rank_attend_total.drop(columns=[basic_index[groups][2]])
        # 수료율/IMO신청률 합치기
        dfv_rank_attend = pd.merge(dfv_rank_attend, dfv_rank_attend_total, on=['소속부문'])
        dfv_rank = pd.merge(dfv_rank, dfv_rank_attend, on=['소속부문'])
    dfv_rank = dfv_rank.drop(columns=['수료인원','IMO신청인원'])
    # 다 합쳐서 반환
    return dfv_rank

# ------------------------------------  차트 제작에 필요한 색상과 outside 생성 함수  ------------------------------------------
def generate_colors(shape):
    color_preset = ['#636efa', '#ef553b', '#00cc96', '#ab63fa', '#ffa15a', '#19d3f3', '#ff6692', '#b6e880', '#ff97ff', '#fecb52']
    color_hexcodes = []
    for i in range(shape):
        color_hexcodes.append(color_preset[i % len(color_preset)])
    return color_hexcodes
def generate_outsides(shape):
    text_outsides = []
    for i in range(shape):
        text_outsides.append('outside')
        i += 1
    return text_outsides
def generate_orders(shape):
    text_orders = []
    for i in range(shape.shape[0]):
        text_orders.append(shape.index[0])
        i += 1
    return text_orders

# ---------------------------------------------  Bar Chart 제작 함수 정의  --------------------------------------------------
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
def fig_hbarchart(list_hbarchart):
    # Single Bar Chart 만들기
    if list_hbarchart[4] == 'single' :
        fig_singlebar = pl.graph_objs.Bar(
            x=list_hbarchart[0][list_hbarchart[2]],
            y=list_hbarchart[0][list_hbarchart[1]],
            width=0.3,
            name=list_hbarchart[2],
            text=list_hbarchart[0][list_hbarchart[2]],
            marker={'color':list_hbarchart[6]},
            orientation=list_hbarchart[5]
        )
        data_singlebar = [fig_singlebar]
        layout_singlebar = pl.graph_objs.Layout(title=list_hbarchart[9],yaxis={'categoryorder':'array', 'categoryarray':list_hbarchart[8]}) # 여기수정
        return_singlebar = pl.graph_objs.Figure(data=data_singlebar,layout=layout_singlebar)
        return_singlebar.update_traces(textposition=list_hbarchart[7])
        return_singlebar.update_layout(showlegend=False) 
        return return_singlebar
    # Grouped Bar Chart 만들기
    if list_hbarchart[4] == 'group' :
        fig_groupbar1 = pl.graph_objs.Bar(
            x=list_hbarchart[0][list_hbarchart[2]],
            y=list_hbarchart[0][list_hbarchart[1]],
            name=list_hbarchart[2],
            text=list_hbarchart[0][list_hbarchart[2]],
            marker={'color':'grey'},
            orientation=list_hbarchart[5]
        )
        fig_groupbar2 = pl.graph_objs.Bar(
            x=list_hbarchart[0][list_hbarchart[3]],
            y=list_hbarchart[0][list_hbarchart[1]],
            name=list_hbarchart[3],
            text=list_hbarchart[0][list_hbarchart[3]],
            marker={'color':list_hbarchart[6]},
            orientation=list_hbarchart[5]
        )
        data_groupbar = [fig_groupbar1, fig_groupbar2]
        layout_groupbar = pl.graph_objs.Layout(title=list_hbarchart[9],yaxis={'categoryorder':'array', 'categoryarray':list_hbarchart[8]}, annotations=[dict(text=list_hbarchart[10],showarrow=False,xref='paper',yref='paper',x=0,y=1.1)])
        return_groupbar = pl.graph_objs.Figure(data=data_groupbar,layout=layout_groupbar)
        return_groupbar.update_traces(textposition=list_hbarchart[7])
        return_groupbar.update_layout(showlegend=False)
        return return_groupbar

'''
list_vbarchart[0]: dataframe (df_stat, df_trnd)
list_vbarchart[1]: 색상 리스트 ()
list_vbarchart[2]: outside 리스트 ()
list_vbarchart[3]: 차트 제목
'''
def fig_vbarchart(list_vbarchart):
    # 오늘의 신청현황 막대그래프
    fig_vbar1 = pl.graph_objs.Bar(
        x=list_vbarchart[0]['과정명'],
        y=list_vbarchart[0]['목표인원'],
        name='목표인원',
        text=list_vbarchart[0]['목표인원'],
        marker={'color':'grey'}, # 여기수정
        orientation='v'
    )
    fig_fig_vbar2 = pl.graph_objs.Bar(
        x=list_vbarchart[0]['과정명'],
        y=list_vbarchart[0]['신청인원'],
        name='신청인원',
        text=list_vbarchart[0]['신청인원'],
        marker={'color':list_vbarchart[1]},
        orientation='v'
    )
    data_fig_vbar = [fig_vbar1, fig_fig_vbar2]
    layout_fig_vbar = pl.graph_objs.Layout(title=list_vbarchart[3],xaxis={'categoryorder':'array', 'categoryarray':None})
    return_fig_vbar = pl.graph_objs.Figure(data=data_fig_vbar,layout=layout_fig_vbar)
    return_fig_vbar.update_traces(textposition=list_vbarchart[2])
    return_fig_vbar.update_layout(showlegend=True)
    return return_fig_vbar

'''
list_linechart[0]: dataframe (df_stat, df_trnd)
list_linechart[1]: 참조 컬럼 (소속부문, 입사연차, 과정명)
list_linechart[2]: 데이터 (신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청률 등)
list_linechart[3]: 차트 제목
list_linechart[4]: df_apply: '월' / df_attend: '날짜'
'''
def fig_linechart(list_linechart):
    fig_line = pl.graph_objs.Figure()
    # Iterate over unique channels and add a trace for each
    for reference in list_linechart[0][list_linechart[1]].unique():
        line_data = list_linechart[0][list_linechart[0][list_linechart[1]] == reference]
        fig_line.add_trace(pl.graph_objs.Scatter(
            x=line_data[list_linechart[4]],
            y=line_data[list_linechart[2]],
            mode='lines+markers',
            name=reference,
        ))
    # Update the layout
    fig_line.update_layout(
        title=list_linechart[3],
        xaxis_title=list_linechart[4],
        yaxis_title=list_linechart[2],
        legend_title=list_linechart[1],
        hovermode='x',
        template='plotly_white'  # You can choose different templates if you prefer
    )
    return fig_line

def fig_piechart(label, value):
    fig_pchart = pl.graph_objs.Figure(data=[pl.graph_objs.Pie(labels=label, values=value, hole=.3)])
    fig_pchart.update_traces(hoverinfo='label+percent', textinfo='label+value', textfont_size=20)
    return fig_pchart

def style_metric_cards(
    background_color: str = "#ADD8E6",
    border_size_px: int = 1,
    border_color: str = "#CCC",
    border_radius_px: int = 5,
    border_left_color: str = "rgb(55,126,184)",
    box_shadow: bool = True,
):

    box_shadow_str = (
        "box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;"
        if box_shadow
        else "box-shadow: none !important;"
    )
    st.markdown(
        f"""
        <style>
            div[data-testid="metric-container"] {{
                background-color: {background_color};
                border: {border_size_px}px solid {border_color};
                padding: 5% 5% 5% 10%;
                border-radius: {border_radius_px}px;
                border-left: 0.5rem solid {border_left_color} !important;
                {box_shadow_str}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

########################################################################################################################
################################################     자료 전처리     ######################################################
########################################################################################################################

# ---------------------------------------    Google Sheet 데이터베이스 호출    ----------------------------------------------
# 출석부 데이터베이스 호출 (교육과정수료현황) & 컬럼 삭제 (번호)
df_attend = load_data(st.secrets["attend_url"]).drop(columns=['번호'])
df_attend.rename(columns={'성함':'성명'}, inplace=True)
##### df_attend = ['과정명','소속부문','소속총괄','소속부서','파트너','사원번호','성명','IMO신청여부','수료현황','비고']
# 과정현황 데이터베이스 호출 (과정현황) & 컬럼 삭제 (번호)
df_course = load_data(st.secrets["course_url"]).drop(columns=['번호'])
##### df_course = ['과정명','보험사','교육일자','과정형태','수강료','지역','교육장소','정원','목표인원']
# 신청현황 데이터베이스 호출 (신청현황) & 컬럼 삭제 (번호)
df_apply = load_data(st.secrets["month_url"]).drop(columns=['번호'])
df_apply.rename(columns={'성함':'성명'}, inplace=True)
##### df_attend = ['과정명','소속부문','소속총괄','소속부서','파트너','사원번호','성명','IMO신청여부','수료현황','비고', '날짜']

# -----------------------------------------------    기본 자료 수정    ----------------------------------------------------
###### df_atd = [과정코드, 과정분류, 과정명, 보험사, 월, 과정형태, 수강료, 지역, 교육장소, 정원, 목표인원, 소속부문, 소속총괄, 소속부서, 파트너, 사원번호, 성함, IMO신청여부, 수료현황, 입사연차]
df_atd = fn_attend(df_attend, df_course)
df_apl = fn_apply(df_apply, df_course)

class CallData:
    def __init__(self):
        pass

    # -------------------------------   수료현황 테이블 정리 및 테이블 병합 (신청현황 & 과정현황)   ------------------------------------ 
    def call_data_attend(self, select):
        df_attend, df_course = call_data(select)
        # df_attend: 컬럼 생성 (과정코드)
        df_attend.insert(loc=1, column='과정코드', value=None)
        # 데이터 정리 (과정코드)
        for modify_attend in range(df_attend.shape[0]):
            df_attend.iloc[modify_attend,1] = df_attend.iloc[modify_attend,0].split(")")[0].replace('(','')
        # df_attend: 컬럼 삭제 (과정명, 비고)
        df_attend = df_attend.drop(columns=['과정명','비고'])
        # df_attend: 데이터 정리 (IMO신청여부: Y -> 1)
        df_attend['IMO신청여부'] = df_attend['IMO신청여부'].replace({'Y':1, 'N':0})
        # df_attend: 데이터 정리 (수료현황: 텍스트 -> 숫자)
        df_attend['수료현황'] = pd.to_numeric(df_attend['수료현황'], errors='coerce')
        # df_attend: 컬럼 추가 및 데이터 삽입 (입사연차)
        df_attend['입사연차'] = (datetime.now().year%100 + 1 - df_attend['사원번호'].astype(str).str[:2].astype(int, errors='ignore')).apply(lambda x: f'{x}년차')
        # df_attend: 데이터 삭제 (파트너: 인카본사)
        df_attend = df_attend.drop(df_attend[df_attend.iloc[:,4] == '인카본사'].index)
        df_attend['과정코드'] = df_attend['과정코드'].astype(str)
        # df_course1: 컬럼명 & 데이터 변경 (course1_date -> 월)
        for date in range(df_course.shape[0]):
            value_date = pd.to_datetime(df_course.at[date, '교육일자'], format="%Y. %m. %d")
            month = value_date.month
            df_course.at[date, '교육일자'] = f'{month}월'
        df_course['과정코드'] = df_course['과정코드'].astype(str)
        ###### df_course1 = [과정코드, 과정분류, 과정명, 보험사, 교육일자, 과정형태, 수강료, 지역, 교육장소, 정원, 목표인원]
        # 테이블 병합 (과정현황 + 수료현황)
        df_result = pd.merge(df_course, df_attend, on=['과정코드'])
        # df_atd: 컬럼명 변경 (교육일자 -> 월)
        df_result.rename(columns={'교육일자':'월'}, inplace=True)
        ###### df_atd = [과정코드, 과정분류, 과정명, 보험사, 월, 과정형태, 수강료, 지역, 교육장소, 정원, 목표인원, 소속부문, 소속총괄, 소속부서, 파트너, 사원번호, 성함, IMO신청여부, 수료현황, 입사연차]
        return df_result

    # ------------------------------   신청현황 테이블 정리 및 테이블 병합 (신청현황 & 과정현황)   -------------------------------------
    def call_data_apply(self, select):
        df_apply, df_course = call_data(select)
        # df_apply: 컬럼 생성 (과정코드)
        df_apply.insert(loc=1, column='과정코드', value=None)
        # df_apply: 데이터 정리 (과정코드)
        for modify_apply in range(df_apply.shape[0]):
            df_apply.iloc[modify_apply,1] = df_apply.iloc[modify_apply,0].split(")")[0].replace('(','')
        # df_apply: 컬럼 추가 (신청인원)
        df_apply = df_apply.groupby(['날짜','과정코드','소속부문'])['사원번호'].count().reset_index(name='신청인원')
        # df_course2: 데이터 변경 ([지역]+과정명)
        df_course['과정명'] = '['+df_course['지역']+'] '+df_course['과정명']
        # 테이블 병합 (신청현황 + 과정현황)
        df_result = pd.merge(df_apply, df_course[['과정코드','과정명','교육일자','목표인원']], on=['과정코드'])
        # df_apl: 날짜 오름차순으로 정렬
        df_result = df_result.sort_values(by='날짜', ascending=True)
        ##### df_apl = ['날짜','과정코드','소속부문','신청인원','목표인원','과정명']
        return df_result
    
class MakeSet(CallData):
    def __init__(self):
        super().__init__()
        self.index = [['수료현황', '수료인원', '수료누계', '수료율'], ['IMO신청여부', 'IMO신청인원', 'IMO신청누계', 'IMO신청률']]

    # -------------------------------------------  소속부문별 고유값 및 누계값  --------------------------------------------------
    # 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
    def make_set_status(self, df, columns):
        # dfv_atd를 '소속부문', '사원번호' 칼럼으로 묶고, 누적개수 구하기
        df_apply = df.groupby([columns,'사원번호']).size().reset_index(name='신청누계')
        # df_func_number에서 묶여있는 '사원번호' 카운트 (중복값 제거한 인원)
        df_apply_unique = df_apply.groupby([columns])['사원번호'].count().reset_index(name='신청인원')
        # df_func_number에서 '누적개수' 카운트 (중복값 더한 인원)
        df_apply_total = df_apply.groupby([columns])['신청누계'].sum().reset_index(name='신청누계')
        # 위에서 중복값을 제거한 데이터프레임과 모두 더한 데이터프레임 병합
        df_apply = pd.merge(df_apply_unique, df_apply_total)
        # 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
        for i in range(len(self.index)):
            # 수료현황, IMO신청여부 1로 묶기
            df_attend = df.groupby(self.index[i][0]).get_group(1)
            # 수료현황 전체 더하기 (수료누계)
            df_attend_total = df.groupby([columns])[self.index[i][0]].sum().reset_index(name=self.index[i][2])
            # 수료현황(1,0)별 사원번호 개수 (수료인원)
            df_attend_unique = df.groupby([columns,self.index[i][0]])['사원번호'].nunique().reset_index(name=self.index[i][1])
            # 수료현항 0인 row 날리기
            df_attend_unique = df_attend_unique[df_attend_unique[self.index[i][0]] != 0]
            # 수료현황 column 날리기
            df_attend_unique = df_attend_unique.drop(columns=[self.index[i][0]])
            # 수료인원이랑 수료누계 합치기
            df_attend = pd.merge(df_attend_unique, df_attend_total, on=[columns])
            # 수료율
            df_attend_total[self.index[i][3]] = (df_attend_total[self.index[i][2]]/df_apply['신청누계']*100).round(1)
            df_attend_total = df_attend_total.drop(columns=[self.index[i][2]])
            # 수료율/IMO신청률 합치기
            df_attend = pd.merge(df_attend, df_attend_total, on=[columns])
            df_result = pd.merge(df_apply, df_attend, on=[columns])
        # 다 합쳐서 반환
        return df_result
    
    # ----------------------------------------  월별 & 소속부문별 고유값 및 누계값  -----------------------------------------------
    # 월별, 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
    def make_set_trend(self, df, columns):
        # 월, 소속부문, 사원번호, 그리고 신청누계(추가)
        df_apply = df.groupby(['월',columns,'사원번호']).size().reset_index(name='신청누계')
        # 월, 소속부문, 그리고 신청인원 (df_func_monthly에서 사원번호 중복제거) (추가)
        df_apply_unique = df_apply.groupby(['월',columns])['사원번호'].count().reset_index(name='신청인원')
        # 월, 소속부문, 신청인원 (df_func_monthly에서 사원번호 없애고 신청누계 다 더하기)
        df_apply_total = df_apply.groupby(['월',columns])['신청누계'].sum().reset_index(name='신청누계')
        # 월, 소속부문, 신청누계, 신청인원 (df_func_unique와 df_func_total 합치기)
        df_apply = pd.merge(df_apply_total, df_apply_unique, on=['월',columns])
        # 수료인원, 수료누계, IMO신청인원, IMO신청누계
        for groups in range(len(self.index)):
            # 수료현황, IMO신청여부 1로 묶기
            df_attend = df.groupby(self.index[groups][0]).get_group(1)
            # 수료현황(1,0)별 사원번호 개수 (수료인원)
            df_attend_unique = df.groupby(['월',columns,self.index[groups][0]])['사원번호'].count().reset_index(name=self.index[groups][1])
            # 수료현항 0인 row 날리기
            df_attend_unique = df_attend_unique[df_attend_unique[self.index[groups][0]] != 0]
            # 수료현황 column 날리기
            df_attend_unique = df_attend_unique.drop(columns=[self.index[groups][0]])
            # 수료현황 전체 더하기 (수료누계)
            df_attend_total = df.groupby(['월',columns])[self.index[groups][0]].sum().reset_index(name=self.index[groups][2])
            # 수료율
            df_attend_total[self.index[groups][3]] = (df_attend_total[self.index[groups][2]]/df_apply['신청누계']*100).round(1)
            # 수료인원이랑 수료누계 합치기
            df_attend = pd.merge(df_attend_unique, df_attend_total, on=['월',columns])
            df_result = pd.merge(df_apply, df_attend, on=['월',columns])
        # 다 합쳐서 반환
        return df_result

class Chart(MakeSet):
    def __init__(self):
        super().__init__()

    def generate_chart_colors(self, df):
        presets = ['#636efa', '#ef553b', '#00cc96', '#ab63fa', '#ffa15a', '#19d3f3', '#ff6692', '#b6e880', '#ff97ff', '#fecb52']
        colors = [presets[i % len(presets)] for i in range(df.shape[0])]
        return colors
    
    def generate_chart_outsides(delf, df):
        outsides = ['outside' for i in range(df.shape[0])]
        return outsides
    
    def generate_barchart_orders(self, df, form):
        if form == '소속부문':
            orders = ['개인부문', '전략부문', 'CA부문', 'MA부문', 'PA부문', '다이렉트부문'][::-1]
        elif form == '입사연차':
            orders = [f'{i}년차' for i in df.index]
        return orders
    
    def generate_linechart_orders(self, df, form):
        if form == '소속부문':
            orders = ['개인부문', '전략부문', 'CA부문', 'MA부문', 'PA부문', '다이렉트부문']
        elif form == '입사연차':
            orders = [f'{i}년차' for i in df.index]
        return orders
    
    # -----------------------------------------  Horizontal Bar Chart 제작 함수 정의  -----------------------------------------------
    # axis_a : 신청인원, 수료인원, 수료율, IMO신청률
    # Single Bar Chart 만들기
    def make_hbarchart_single(self, df, category, axis_a, title):
        fig_chart = pl.graph_objs.Bar(
            x=df[axis_a],
            y=df[category],
            width=0.3,
            name=axis_a,
            text=df[axis_a],
            marker={'color':self.generate_chart_colors(df)},
            orientation='h'
        )
        data_chart = [fig_chart]
        layout_chart = pl.graph_objs.Layout(title=title,yaxis={'categoryorder':'array', 'categoryarray':self.generate_barchart_orders(df,category)}) # 여기수정
        return_chart = pl.graph_objs.Figure(data=data_chart,layout=layout_chart)
        return_chart.update_traces(textposition=self.generate_chart_outsides(df))
        return_chart.update_layout(showlegend=False) 
        return return_chart

    # ---------------------------------------------  Bar Chart 제작 함수 정의  --------------------------------------------------
    # axis_a: 고유값 (신청인원, 수료인원) / axis_b: 누계값 (신청누계, 수료누계)
    # Grouped Bar Chart 만들기
    def make_hbarchart_group(self, df, category, axis_a, axis_b, title):
        fig_chart_a = pl.graph_objs.Bar(
            x=df[axis_a],
            y=df[category],
            name=axis_a,
            text=df[axis_a],
            marker={'color':'grey'},
            orientation='h'
        )
        fig_chart_b = pl.graph_objs.Bar(
            x=df[axis_b],
            y=df[category],
            name=axis_b,
            text=df[axis_b],
            marker={'color':self.generate_chart_colors(df)},
            orientation='h'
        )
        data_chart = [fig_chart_a, fig_chart_b]
        layout_chart = pl.graph_objs.Layout(title=title,yaxis={'categoryorder':'array', 'categoryarray':self.generate_barchart_orders(df,category)}, annotations=[dict(text='색상 차트는 누적인원(중복포함), 회색 차트는 고유인원(중복제거)',showarrow=False,xref='paper',yref='paper',x=0,y=1.1)])
        return_chart = pl.graph_objs.Figure(data=data_chart,layout=layout_chart)
        return_chart.update_traces(textposition=self.generate_chart_outsides(df))
        return_chart.update_layout(showlegend=False)
        return return_chart

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