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
# ------------------------------    Google Sheet 데이터베이스 호출 및 자료 전처리    ---------------------------------------
month_dict = {'jan':'1월','feb':'2월','mar':'3월','apr':'4월','may':'5월','jun':'6월','jul':'7월','aug':'8월','sep':'9월','oct':'10월','nov':'11월','dec':'12월'}

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
def call_sheets(select):
    df_select = pd.read_csv(st.secrets[f"{select}_url"].replace("/edit#gid=", "/export?format=csv&gid="))
    return df_select

# select : {수료현황 : attend}, {신청현황 : month}
@st.cache_data(ttl=600)
def call_data(select):
    # 데이터베이스 호출 & 컬럼 삭제 (번호)
    df_select = call_sheets(select).drop(columns=['번호'])
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

########################################################################################################################
##############################################     Class 정의 (교육관리)     ############################################
########################################################################################################################

class CallData:
    def __init__(self):
        pass

    #
    def call_regist_channel(self):
        df_regist = pd.read_csv(st.secrets["regist_url"].replace("/edit#gid=", "/export?format=csv&gid="))
        df_regist = df_regist[df_regist['구분'] == '소속부문']
        df_regist.rename(columns={'항목':'소속부문'}, inplace=True)
        df_regist = df_regist.drop(columns='구분')
        return df_regist
    
    def call_regist_career(self):
        df_regist = pd.read_csv(st.secrets["regist_url"].replace("/edit#gid=", "/export?format=csv&gid="))
        df_regist = df_regist[df_regist['구분'] == '입사연차']
        df_regist.rename(columns={'항목':'입사연차'}, inplace=True)
        df_regist = df_regist.drop(columns='구분')
        return df_regist

    # -------------------------------   수료현황 테이블 정리 및 테이블 병합 (신청현황 & 과정현황)   ------------------------------------ 
    def call_data_attend(self, select, theme):
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
        if theme == '입사연차':
            df_result = pd.merge(df_result, self.call_regist_career(), on=['월','입사연차'])
        elif theme == '소속부문':
            df_result = pd.merge(df_result, self.call_regist_channel(), on=['월','소속부문'])
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
        df_apply = df_apply.groupby(['날짜','과정코드','소속부문','파트너','사원번호','성명'])['사원번호'].count().reset_index(name='신청인원')
        # df_course2: 데이터 변경 ([지역]+과정명)
        df_course['과정명'] = '['+df_course['지역']+'] '+df_course['과정명']
        # df_apply의 '과정코드' 열을 문자열로 변환
        df_apply['과정코드'] = df_apply['과정코드'].astype(str)
        # df_course의 '과정코드' 열을 문자열로 변환
        df_course['과정코드'] = df_course['과정코드'].astype(str)
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
    def make_set_status(self, df, *columns):
        # dfv_atd를 '소속부문', '사원번호' 칼럼으로 묶고, 누적개수 구하기
        df_apply = df.groupby([*columns,'사원번호']).size().reset_index(name='신청누계')
        # df_func_number에서 묶여있는 '사원번호' 카운트 (중복값 제거한 인원)
        df_apply_unique = df_apply.groupby([*columns])['사원번호'].count().reset_index(name='신청인원')
        # df_func_number에서 '누적개수' 카운트 (중복값 더한 인원)
        df_apply_total = df_apply.groupby([*columns])['신청누계'].sum().reset_index(name='신청누계')
        df_units = df.groupby([*columns])['재적인원'].sum().reset_index(name='재적인원')
        # 위에서 중복값을 제거한 데이터프레임과 모두 더한 데이터프레임 병합
        df_apply = pd.merge(df_apply_unique, df_apply_total)
        df_apply = pd.merge(df_apply, df_units)
        # 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
        for i in range(len(self.index)):
            # 수료현황, IMO신청여부 1로 묶기
            df_attend = df.groupby(self.index[i][0]).get_group(1)
            # 수료현황 전체 더하기 (수료누계)
            df_attend_total = df.groupby([*columns])[self.index[i][0]].sum().reset_index(name=self.index[i][2])
            # 수료현황(1,0)별 사원번호 개수 (수료인원)
            df_attend_unique = df.groupby([*columns,self.index[i][0]])['사원번호'].nunique().reset_index(name=self.index[i][1])
            # 수료현항 0인 row 날리기
            df_attend_unique = df_attend_unique[df_attend_unique[self.index[i][0]] != 0]
            # 수료현황 column 날리기
            df_attend_unique = df_attend_unique.drop(columns=[self.index[i][0]])
            # 수료인원이랑 수료누계 합치기
            df_attend = pd.merge(df_attend_unique, df_attend_total, on=[*columns])
            # 수료율
            df_attend_total[self.index[i][3]] = (df_attend_total[self.index[i][2]]/df_apply['신청누계']*100).round(1)
            df_attend_total = df_attend_total.drop(columns=[self.index[i][2]])
            # 수료율/IMO신청률 합치기
            df_attend = pd.merge(df_attend, df_attend_total, on=[*columns])
            df_apply = pd.merge(df_apply, df_attend, on=[*columns])
        # 다 합쳐서 반환
        return df_apply
    
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
            df_apply = pd.merge(df_apply, df_attend, on=['월',columns])
        # 다 합쳐서 반환
        return df_apply

    # 코드리뷰필요
    def make_set_sums(self, df):
        df_sums = df.sum(axis=0)
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
        return df_sums

class Chart(MakeSet):
    def __init__(self):
        super().__init__()
        # self.index_card = [['신청누계','수료율'], ['수료누계','수료율'], ['수료율','수료누계'], ['수료율','수료누계']]

    def generate_chart_colors(self, df):
        presets = ['#636efa', '#ef553b', '#00cc96', '#ab63fa', '#ffa15a', '#19d3f3', '#ff6692', '#b6e880', '#ff97ff', '#fecb52']
        colors = [presets[i % len(presets)] for i in range(df.shape[0])]
        return colors
    
    def generate_chart_outsides(delf, df):
        outsides = ['outside' for i in range(df.shape[0])]
        return outsides
    
    def generate_barchart_orders(self, df, form):
        if form == '소속부문': orders = ['개인부문', '전략부문', 'CA부문', 'MA부문', 'PA부문', '다이렉트부문'][::-1]
        elif form == '입사연차': orders = [f'{i}년차' for i in df.index]
        elif form == '비고': orders = ['신청', '수료'][::-1]
        else: orders = [df.iat[i,1] for i in range(df.shape[0])]
        return orders
    
    def generate_linechart_orders(self, df, form):
        if form == '소속부문':
            orders = ['개인부문', '전략부문', 'CA부문', 'MA부문', 'PA부문', '다이렉트부문']
        elif form == '입사연차':
            orders = [f'{i}년차' for i in df.index]
        return orders
    
    # -------------------------------------  Horizontal Bar Chart (Single) 제작 함수 정의  -----------------------------------------
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

    # --------------------------------------  Horizontal Bar Chart (Group) 제작 함수 정의  -----------------------------------------
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

    # --------------------------------------  Vertical Bar Chart (Group) 제작 함수 정의  -----------------------------------------
    # axis_a: 고유값 (신청인원, 수료인원) / axis_b: 누계값 (신청누계, 수료누계)
    # Grouped Bar Chart 만들기
    def make_vbarchart(self, df, title):
        fig_chart_a = pl.graph_objs.Bar(
            x=df['과정명'],
            y=df['목표인원'],
            name='목표인원',
            text=df['목표인원'],
            marker={'color':'grey'},
            orientation='v'
        )
        fig_chart_b = pl.graph_objs.Bar(
            x=df['과정명'],
            y=df['신청인원'],
            name='신청인원',
            text=df['신청인원'],
            marker={'color':self.generate_chart_colors(df)},
            orientation='v'
        )
        data_chart = [fig_chart_a, fig_chart_b]
        layout_chart = pl.graph_objs.Layout(title=title,yaxis={'categoryorder':'array', 'categoryarray':self.generate_barchart_orders(df, None)})
        return_chart = pl.graph_objs.Figure(data=data_chart,layout=layout_chart)
        return_chart.update_traces(textposition=self.generate_chart_outsides(df))
        return_chart.update_layout(showlegend=False)
        return return_chart

    # ----------------------------------------------  Line Chart 제작 함수 정의  ---------------------------------------------------
    # xaxis : '월'(df_apply), '날짜'(df_attend) / yaxis : 데이터 (신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청률 등)
    def make_linechart(self, df, category, xaxis, yaxis, title):
        fig_chart = pl.graph_objs.Figure()
        # Iterate over unique channels and add a trace for each
        for reference in df[category].unique():
            line_data = df[df[category] == reference]
            fig_chart.add_trace(pl.graph_objs.Scatter(
                x=line_data[xaxis],
                y=line_data[yaxis],
                mode='lines+markers',
                name=reference,
            ))
        # Update the layout
        fig_chart.update_layout(
            title=title,
            xaxis_title=xaxis,
            yaxis_title=yaxis,
            legend_title=category,
            hovermode='x',
            template='plotly_white'  # You can choose different templates if you prefer
        )
        return fig_chart

    # -----------------------------------------------  Pie Chart 제작 함수 정의  ---------------------------------------------------
    def make_piechart(self, label, value):
        fig_pchart = pl.graph_objs.Figure(data=[pl.graph_objs.Pie(labels=label, values=value, hole=.3)])
        fig_pchart.update_traces(hoverinfo='label+percent', textinfo='label+value', textfont_size=20)
        return fig_pchart

    # ------------------------------------------------  랭킹 (스타일 카드 제작)  ----------------------------------------------------
    # 스타일카드 : FA, 파트너
    def make_cards_a(self, df, select, title):
        st.markdown('---')
        st.markdown(title)
        index_card = [['신청누계','수료율'], ['수료누계','수료율'], ['수료율','수료누계'], ['수료율','수료누계']]
        index_ascending = [False, False, False, True]
        index_columns = [3,5,6,6]
        # 랭킹 항목 4개씩 만들기
        for loop in range(4):
            st.write(select[loop])
            df = df.sort_values(by=[*index_card[loop]], ascending=[index_ascending[loop], False])
            # 카드 5개 씩 만들기
            sector = st.columns(5)
            for i in range(5):
                sector[i].metric(f"{df.iat[i,1]} ({df.iat[i, 0]})", df.iat[i, index_columns[loop]])

    # ------------------------------------------------  랭킹 (스타일 카드 제작)  ----------------------------------------------------
    # 스타일카드 : 소속부문, 입사연차
    def make_cards_b(self, df, select, title):
        st.markdown('---')
        st.markdown(title)
        index_card = [['신청누계','수료율'], ['수료누계','수료율'], ['수료율','수료누계'], ['수료율','수료누계']]
        index_ascending = [False, False, False, True]
        index_column = [2,4,5,5]
        # 랭킹 항목 4개씩 만들기
        for loop in range(4):
            st.write(select[loop])
            df = df.sort_values(by=[*index_card[loop]], ascending=[index_ascending[loop], False])
            # 카드 5개 씩 만들기
            sector = st.columns(6)
            for i in range(6):
                sector[i].metric(df.iat[i, 0], df.iat[i, index_column[loop]])

########################################################################################################################
##############################################     Class 정의 (보장분석)     ############################################
########################################################################################################################
class ServiceData:
    def __init__(self) -> None:
        pass

    # 데이터프레임 만들기 (보고서용)
    def make_service_data(self, df):
        # 컬럼 삭제
        df_result = df.drop(columns=['본부','지점'])
        # 컬럼 정리 (보고서 순으로)
        # df_result = df_result[['기준일자','컨설턴트ID','컨설턴트성명','로그인수','보장분석접속건수','보장분석고객등록수','보장분석컨설팅고객수','보장분석출력건수','간편보장_접속건수','간편보장_출력건수','APP 보험다보여전송건수','APP 주요보장합계조회건수','APP 명함_접속건수','APP 의료비/보험금조회건수','보험료비교접속건수','보험료비교출력건수','한장보험료비교_접속건수','상품비교설명확인서_접속건수','영업자료접속건수','영업자료출력건수','(NEW)영업자료접속건수','(NEW)영업자료출력건수','라이프사이클접속건수','라이프사이클출력건수']]
        # 컬럼명 변경
        df_result = df_result.rename(columns={'컨설턴트ID':'사원번호','컨설턴트성명':'성명'})
        # 약관조회 컬럼 추가
        df_result['약관조회'] = 0
        # 사번정리
        df_result['사원번호'] = df_result['사원번호'].astype(str)
        for i in range(df_result.shape[0]):
            if len(df_result.iat[i,1]) < 6: df_result.iat[i,1] = f"16{df_result.iat[i,1]}"
            else: pass
        # 소속찾기
        return df_result

    # 각 사원별 접속횟수 : [사원번호, 접속수]
    def make_service_branch(self, df):
        df_result = self.make_service_data(df).groupby(['사원번호'])['사원번호'].count().reset_index(name='접속수')
        return df_result

    # 보고서용 요약자료
    def make_service_summary(self, df):
        columns = [
            '로그인수',
            '보장분석접속건수',
            '보장분석고객등록수',
            '보장분석컨설팅고객수',
            '보장분석출력건수',
            '간편보장_접속건수',
            '간편보장_출력건수',
            'APP 보험다보여전송건수',
            'APP 주요보장합계조회건수',
            'APP 명함_접속건수',
            'APP 의료비/보험금조회건수',
            '보험료비교접속건수',
            '보험료비교출력건수',
            '한장보험료비교_접속건수',
            '약관조회',
            '상품비교설명확인서_접속건수',
            '영업자료접속건수',
            '영업자료출력건수',
            '(NEW)영업자료접속건수',
            '(NEW)영업자료출력건수',
            '라이프사이클접속건수',
            '라이프사이클출력건수'
        ]
        columns_sums = {}
        for i in range(len(columns)):
            columns_sums[columns[i]] = [self.make_service_data(df)[columns[i]].sum()]
        df_result = pd.DataFrame(columns_sums)
        return df_result

    # 1~12월 전체자료 불러오기
    '''
    month = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
    start_all = time.time()
    for i in range(9):
        start = time.time()
        st.write(month[i])
        st.dataframe(instance.make_service_data(call_sheets(month[i])))
        end = time.time()
        st.write(f"시간측정({month[i]}) : {end-start} 초")
    end_all = time.time()
    st.write(f"시간측정(전체) : {end_all-start_all} sec")
    '''


class Register:
    def __init__(self):
        self.dates = {'jan':'20230201','feb':'20230301','mar':'20230401','apr':'20230501','may':'20230601','jun':'20230701','jul':'20230801','aug':'20230901','sep':'20231001','oct':'20231101','nov':'20231201','dec':'20240101'}

    def find_register(self):
        # 재적인원관리 시트 호출
        df_fa = call_sheets("fa")[['사원번호','영업가족CD']]
        df_enter = call_sheets("enter")[['사원번호','입사일자(사원)']]
        df_quit = call_sheets("quit")[['사원번호','영업가족CD','퇴사일자(사원)']]
        # 입사인원관리 시트
        df_enter['입사일자(사원)'] = df_enter['입사일자(사원)'].str.replace('/','').astype(int) # 입사일자의 형식을 8자리 숫자로 변환
        df_enter = df_enter[df_enter['입사일자(사원)'] >= 20230901].drop(columns=['입사일자(사원)']) # 특정일자 이후에 입사한 인원을 추출
        df_fa = df_fa[~df_fa['사원번호'].isin(df_enter['사원번호'])] # 현재 재적인원에서 특정일자 이후에 입사한 인원 삭제
        # 퇴사인원관리 시트
        df_quit['퇴사일자(사원)'] = df_quit['퇴사일자(사원)'].str.replace('/','').astype(int) # 퇴사일자의 형식을 8자리 숫자로 변환
        df_quit = df_quit[df_quit['퇴사일자(사원)'] >= 20230901].drop(columns=['퇴사일자(사원)']) # 특정일자 이후에 퇴사한 인원 추출
        df_fa = pd.concat([df_fa, df_quit], axis=0) # 현재 재적인원에서 특정일자 이후에 퇴사한 인원 추가
        
        df_branch = call_sheets("branch")[['영업가족코드','소속부서']]
        st.write(df_branch.shape[0])
        df_open = call_sheets("open")[['영업가족코드','등록전환일자']]
        df_open['등록전환일자'] = df_open['등록전환일자'].str.replace('/','').astype(int) # 입사일자의 형식을 8자리 숫자로 변환
        df_open = df_open[df_open['등록전환일자'] >= 20230901].drop(columns=['등록전환일자'])
        df_branch = df_branch[~df_branch['영업가족코드'].isin(df_open['영업가족코드'])]
        st.write(df_open.shape[0])
        st.write(df_branch.shape[0])
        df_close = call_sheets("close")[['영업가족코드','소속부서','폐쇄일자']]
        df_close['폐쇄일자'] = df_close['폐쇄일자'].str.replace('/','').astype(int) # 입사일자의 형식을 8자리 숫자로 변환
        df_close = df_close[df_close['폐쇄일자'] >= 20230901].drop(columns=['폐쇄일자'])
        df_branch = pd.concat([df_branch, df_close], axis=0)
        st.write(df_close.shape[0])
        st.write(df_branch.shape[0])

        
        


