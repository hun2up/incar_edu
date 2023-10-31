#########################################################################################################################
################                                    라이브러리 호출                                     ##################
#########################################################################################################################
import pandas as pd             # Documents (API reference) : https://pandas.pydata.org/docs/reference/index.html
import streamlit as st          # Documents (API reference) : https://docs.streamlit.io/library/api-reference
import plotly as pl             # Documents (Graphing Library) : https://plotly.com/python/
from datetime import datetime   # Documents (API reference) : https://docs.python.org/3/library/datetime.html?highlight=datetime#module-datetime

#########################################################################################################################
################                                    범용 함수 정의                                      ##################
#########################################################################################################################
# ------------------------------------          스트림릿 워터마크 제거          ------------------------------------------
def hide_st_style():
    hide_st_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

# -------------------------              랭킹 디스플레이를 위한 스타일 카드 정의          ---------------------------------
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

# ----------------------------------------          사이드바 제작          ----------------------------------------------
def make_sidebar(df, column):
    return st.sidebar.multiselect(
        column,
        options=df[column].unique(),
        default=df[column].unique()
    )

# -------------------------------          데이터베이스 호출 (Google Sheets)          -----------------------------------
@st.cache_data(ttl=600)
def call_sheets(select):
    df_call = pd.read_csv(st.secrets[f"{select}_url"].replace("/edit#gid=", "/export?format=csv&gid="))
    return df_call

#########################################################################################################################
##############                        차트제작 클래스 정의                        ################
#########################################################################################################################
class Charts():
    def __init__(self):
        pass

    # ---------------------------          차트 제작을 위한 차트색상 생성 (Plotly 컬러)          ---------------------------------
    def generate_chart_colors(self, df):    # 참고 : https://plotly.com/python/discrete-color/
        presets = ['#636efa', '#ef553b', '#00cc96', '#ab63fa', '#ffa15a', '#19d3f3', '#ff6692', '#b6e880', '#ff97ff', '#fecb52']
        colors = [presets[i % len(presets)] for i in range(df.shape[0])]
        return colors
    
    # -------------------------------          차트 제작을 위한 라벨위치 생성 (외부)          ------------------------------------
    def generate_chart_outsides(delf, df):
        outsides = ['outside' for i in range(df.shape[0])]
        return outsides
    
    # -----------------------------          차트 제작을 위한 항목순서 지정 (막대그래프)         -----------------------------------
    def generate_barchart_orders(self, df, form):
        if form == '소속부문': orders = ['개인부문', '전략부문', 'CA부문', 'MA부문', 'PA부문', '다이렉트부문'][::-1]
        elif form == '입사연차': orders = [f'{i}년차' for i in df.index]
        elif form == '비고': orders = ['신청', '수료'][::-1]
        else: orders = [df.iat[i,1] for i in range(df.shape[0])]
        return orders
    
    # ----------------------------          차트 제작을 위한 항목순서 지정 (꺾은선그래프)         ----------------------------------
    def generate_linechart_orders(self, df, form):
        if form == '소속부문':
            orders = ['개인부문', '전략부문', 'CA부문', 'MA부문', 'PA부문', '다이렉트부문']
        elif form == '입사연차':
            orders = [f'{i}년차' for i in df.index]
        return orders
    
    # -----------------------------------          수평막대그래프 제작 (Single)          -------------------------------------
    def make_hbarchart_single(self, df, category, axis_a, title):
        # axis_a : 신청인원, 수료인원, 수료율, IMO신청률
        fig = pl.graph_objs.Bar(
            x=df[axis_a],
            y=df[category],
            width=0.3,
            name=axis_a,
            text=df[axis_a],
            marker={'color':self.generate_chart_colors(df)},
            orientation='h'
        )
        layout_chart = pl.graph_objs.Layout(title=title,yaxis={'categoryorder':'array', 'categoryarray':self.generate_barchart_orders(df,category)}) # 여기수정
        return_chart = pl.graph_objs.Figure(data=[fig],layout=layout_chart)
        return_chart.update_traces(textposition=self.generate_chart_outsides(df))
        return_chart.update_layout(showlegend=False) 
        return return_chart

    # -----------------------------------          수평막대그래프 제작 (Grouped)          ------------------------------------
    def make_hbarchart_group(self, df, category, axis_a, axis_b, title):
        # axis_a: 고유값 (신청인원, 수료인원) / axis_b: 누계값 (신청누계, 수료누계)
        fig_a = pl.graph_objs.Bar(
            x=df[axis_a],
            y=df[category],
            name=axis_a,
            text=df[axis_a],
            marker={'color':'grey'},
            orientation='h'
        )
        fig_b = pl.graph_objs.Bar(
            x=df[axis_b],
            y=df[category],
            name=axis_b,
            text=df[axis_b],
            marker={'color':self.generate_chart_colors(df)},
            orientation='h'
        )
        layout_chart = pl.graph_objs.Layout(title=title,yaxis={'categoryorder':'array', 'categoryarray':self.generate_barchart_orders(df,category)}, annotations=[dict(text='색상 차트는 누적인원(중복포함), 회색 차트는 고유인원(중복제거)',showarrow=False,xref='paper',yref='paper',x=0,y=1.1)])
        return_chart = pl.graph_objs.Figure(data=[fig_a, fig_b],layout=layout_chart)
        return_chart.update_traces(textposition=self.generate_chart_outsides(df))
        return_chart.update_layout(showlegend=False)
        return return_chart

    # -----------------------------------          수직막대그래프 제작 (Grouped)          ------------------------------------
    def make_vbarchart(self, df, title):
        # axis_a: 고유값 (신청인원, 수료인원) / axis_b: 누계값 (신청누계, 수료누계)
        fig_a = pl.graph_objs.Bar(
            x=df['과정명'],
            y=df['목표인원'],
            name='목표인원',
            text=df['목표인원'],
            marker={'color':'grey'},
            orientation='v'
        )
        fig_b = pl.graph_objs.Bar(
            x=df['과정명'],
            y=df['신청인원'],
            name='신청인원',
            text=df['신청인원'],
            marker={'color':self.generate_chart_colors(df)},
            orientation='v'
        )
        layout_chart = pl.graph_objs.Layout(title=title,yaxis={'categoryorder':'array', 'categoryarray':self.generate_barchart_orders(df, None)})
        return_chart = pl.graph_objs.Figure(data=[fig_a,fig_b],layout=layout_chart)
        return_chart.update_traces(textposition=self.generate_chart_outsides(df))
        return_chart.update_layout(showlegend=False)
        return return_chart

    # ----------------------------------------          꺾은선그래프 제작          ------------------------------------------
    def make_linechart(self, df, category, xaxis, yaxis, title):
        # xaxis : '월'(df_apply), '날짜'(df_attend) / yaxis : 데이터 (신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청률 등)
        fig = pl.graph_objs.Figure()
        # Iterate over unique channels and add a trace for each
        for reference in df[category].unique():
            line_data = df[df[category] == reference]
            fig.add_trace(pl.graph_objs.Scatter(
                x=line_data[xaxis],
                y=line_data[yaxis],
                mode='lines+markers',
                name=reference,
            ))
        # Update the layout
        fig.update_layout(
            title=title,
            xaxis_title=xaxis,
            yaxis_title=yaxis,
            legend_title=category,
            hovermode='x',
            template='plotly_white'  # You can choose different templates if you prefer
        )
        return fig

    # -----------------------------------------          원형그래프 제작          -------------------------------------------
    def make_piechart(self, label, value):
        fig_pchart = pl.graph_objs.Figure(data=[pl.graph_objs.Pie(labels=label, values=value, hole=.3)])
        fig_pchart.update_traces(hoverinfo='label+percent', textinfo='label+value', textfont_size=20)
        return fig_pchart

    # ------------------------------------          A형 스타일카드 제작 (랭킹)          ---------------------------------------
    def make_cards_a(self, df, select, title):
        # 스타일카드 : FA, 파트너
        st.markdown('---')
        st.markdown(title)
        index_card = [['신청누계','수료율'], ['수료누계','수료율'], ['수료율','수료누계'], ['수료율','수료누계']]
        index_ascending = [False, False, False, True]
        index_columns = [3,5,8,8]
        index_units = ['회','회','%','%']
        # 랭킹 항목 4개씩 만들기
        for loop in range(4):
            st.write(select[loop])
            df = df.sort_values(by=[*index_card[loop]], ascending=[index_ascending[loop], False])
            # 카드 5개 씩 만들기
            sector = st.columns(5)
            for i in range(5):
                sector[i].metric(f"{df.iat[i,1]} ({df.iat[i, 0]})", f"{df.iat[i, index_columns[loop]]} ({index_units[loop]})")

    # ------------------------------------          B형 스타일카드 제작 (랭킹)          ---------------------------------------
    def make_cards_b(self, df, select, title):
        # 스타일카드 : 소속부문, 입사연차
        st.markdown('---')
        st.markdown(title)
        index_card = [['신청누계','수료율'], ['수료누계','수료율'], ['수료율','수료누계'], ['수료율','수료누계']]
        index_ascending = [False, False, False, True]
        index_column = [2,4,7,7]
        index_units = ['회','회','%','%']
        # 랭킹 항목 4개씩 만들기
        for loop in range(4):
            st.write(select[loop])
            df = df.sort_values(by=[*index_card[loop]], ascending=[index_ascending[loop], False])
            # 카드 5개 씩 만들기
            sector = st.columns(6)
            for i in range(6):
                sector[i].metric(df.iat[i, 0], f"{df.iat[i, index_column[loop]]} ({index_units[loop]})")

#########################################################################################################################
##############                        교육관리(메인페이지) 클래스 정의 : Charts 클래스 상속                        ################
#########################################################################################################################
class EduMain(Charts):
    def __init__(self):
        super().__init__()

    def call_data_main(self):
        # [매일] 시트 호출 ()
        # df_attend : | 과정명 | 소속부문 | 소속총괄 | 소속부서 | 파트너 | 사원번호 | 성명 | IMO신청여부 | 수료현황 | 비고
        df_main = call_sheets("month").drop(columns=['번호','비고']).rename(columns={'성함':'성명','날짜':'신청일자'}) # 시트 호출 & 컬럼 삭제 (번호) & 컬럼명 변경 (성함 ▶ 성명)
        df_main = df_main.drop(df_main[df_main['파트너'] == '인카본사'].index) # [파트너]에서 '인카본사' 삭제
        # 과정코드 정리
        df_main.insert(0, column='과정코드', value=None) # 첫번째 컬럼에 [과정코드] 컬럼 추가
        df_main['과정코드'] = [df_main.iloc[change,1].split(")")[0].replace('(','') for change in range(df_main.shape[0])] # [과정명]에서 '과정코드'만 추출하여 [과정코드] 컬럼에 추가
        df_main = df_main.drop(columns=['과정명']) # 기존 과정명 컬럼 삭제
        # 신청인원 컬럼 추가
        df_main = df_main.groupby(['신청일자','과정코드','소속부문','파트너','사원번호','성명'])['사원번호'].count().reset_index(name='신청인원')
        df_main['과정코드'] = df_main['과정코드'].astype(str) # df_main의 '과정코드' 열을 문자열로 변환
        # 입사연차 컬럼 추가
        df_main['입사연차'] = (datetime.now().year%100 + 1 - df_main['사원번호'].astype(str).str[:2].astype(int, errors='ignore')).apply(lambda x: f'{x}년차') # [입사연차] 컬럼 추가 및 데이터(입사연차) 삽입
        # ---------------------------------------------------------------------------------------------------------------
        df_course = call_sheets("course")
        df_course['과정명'] = '['+df_course['지역']+'] '+df_course['과정명']
        df_course['과정코드'] = df_course['과정코드'].astype(str) # df_course의 '과정코드' 열을 문자열로 변환
        # ---------------------------------------------------------------------------------------------------------------
        df_result = pd.merge(df_main, df_course[['과정코드','과정명','교육일자','목표인원']], on=['과정코드']) # 테이블 병합 (신청현황 + 과정현황)
        df_result = df_result.sort_values(by='신청일자', ascending=True) # df_apl: 신청일자 오름차순으로 정렬
        df_result['사원번호'] = df_result['사원번호'].astype(str)
        # df_result : | 신청일자 | 과정코드 | 소속부문 | 파트너 | 사원번호 | 성명 | 신청인원 | 과정명 | 교육일자 | 목표인원
        return df_result  

    def make_set_main(self, df, select):
        # df : | 신청일자 | 과정코드 | 소속부문 | 파트너 | 사원번호 | 성명 | 신청인원 | 과정명 | 교육일자 | 목표인원
        df_main = df.drop(df[df.iloc[:,0] != df.iloc[-1,0]].index) # 신청일자 가장 최근 데이터만 남기기
        df_main = df_main.groupby([select])['신청인원'].sum().reset_index(name='신청인원')
        return df_main

#########################################################################################################################
##############                        교육관리(하위페이지) 클래스 정의 : Charts 클래스 상속                        ################
#########################################################################################################################
class EduPages(Charts):
    def __init__(self):
        super().__init__()

    # -----------------------------------         월별 데이터 오름차순 정렬          ------------------------------------------
    def sort_month(self, column):
        return int(column[:-1])

    # -----------------------------------         재적인원 데이터 호출          ------------------------------------------
    def call_registered(self, theme):
        # [매월]재적인원 시트 호출 (https://docs.google.com/spreadsheets/d/1AG89W1nwRzZxYreM6i1qmwS6APf-8GM2K_HDyX7REG4/edit#gid=1608447947)
        # df_regist : | 월 | 구분 | 항목 | 재적인원
        df_regist = pd.read_csv(st.secrets["regist_url"].replace("/edit#gid=", "/export?format=csv&gid=")) # 시트호출
        df_regist = df_regist[df_regist['구분'] == theme] # [구분] 컬럼을 '소속부문' 또는 '입사연차'에 따라 분류
        df_regist.rename(columns={'항목':theme}, inplace=True) # [항목] 컬럼을 '소속부문' 또는 '입사연차'로 변경
        df_regist = df_regist.drop(columns='구분') # [구분] 컬럼 삭제
        # df_regist : | 월 | 소속부문/입사연차 | 재적인원
        return df_regist

    # --------------------         수료현황 테이블 정리 & 테이블 병합 (신청현황+과정현황)          -------------------------
    def call_data_pages(self):
        # [매월]교육과정수료현황 시트 호출 ()
        # df_attend : | 과정명 | 소속부문 | 소속총괄 | 소속부서 | 파트너 | 사원번호 | 성명 | IMO신청여부 | 수료현황 | 비고
        df_attend = call_sheets("attend").drop(columns=['번호','비고']).rename(columns={'성함':'성명'}) # 시트 호출 & 컬럼 삭제 (번호) & 컬럼명 변경 (성함 ▶ 성명)
        df_attend = df_attend.drop(df_attend[df_attend['파트너'] == '인카본사'].index) # [파트너]에서 '인카본사' 삭제
        # 과정코드 정리
        df_attend.insert(0, column='과정코드', value=None) # 첫번째 컬럼에 [과정코드] 컬럼 추가
        df_attend['과정코드'] = [df_attend.iloc[change,1].split(")")[0].replace('(','') for change in range(df_attend.shape[0])] # [과정명]에서 '과정코드'만 추출하여 [과정코드] 컬럼에 추가
        df_attend = df_attend.drop(columns=['과정명']) # 기존 과정명 컬럼 삭제
        # 데이터형식 정리
        df_attend['IMO신청여부'] = df_attend['IMO신청여부'].replace({'Y':1, 'N':0}) # IMO신청여부: Y ▶ 1
        df_attend['수료현황'] = pd.to_numeric(df_attend['수료현황'], errors='coerce') # 수료현황 : 텍스트 ▶ 숫자
        df_attend['입사연차'] = (datetime.now().year%100 + 1 - df_attend['사원번호'].astype(str).str[:2].astype(int, errors='ignore')).apply(lambda x: f'{x}년차') # [입사연차] 컬럼 추가 및 데이터(입사연차) 삽입
        # df_attend : | 과정코드 | 소속부문 | 소속총괄 | 소속부서 | 파트너 | 사원번호 | 입사연차 | 성명 | IMO신청여부 | 수료현황
        # ---------------------------------------------------------------------------------------------------------------
        # [매월]과정현황 시트 호출 및 [교육일자] 데이터 변경
        # df_course = | 과정코드 | 과정분류 | 과정명 | 보험사 | 교육일자 | 과정형태 | 수강료 | 지역 | 교육장소 | 정원 | 목표인원
        df_course = call_sheets("course").drop(columns=['번호']) # 시트 호출
        df_course.insert(4, column='월', value=None) # 네번째 컬럼에 [월] 컬럼 추가
        df_course['월'] = [f"{pd.to_datetime(df_course.at[short, '교육일자'], format='%Y. %m. %d').month}월" for short in range(df_course.shape[0])] # [교육일자]에서 '월' 데이터만 추출하여 [월] 컬럼에 추가
        df_course = df_course.drop(columns=['교육일자']) # 기존 교육일자 컬럼 삭제
        # df_course : | 과정코드 | 과정분류 | 과정명 | 보험사 | 월 | 과정형태 | 수강료 | 지역| 교육장소 | 정원 | 목표인원
        # ---------------------------------------------------------------------------------------------------------------
        # 테이블 병합 : df_attend(수료현황) + df_course(과정현황)
        df_attend['과정코드'] = df_attend['과정코드'].astype(str)
        df_course['과정코드'] = df_course['과정코드'].astype(str)
        df_merge = pd.merge(df_course, df_attend, on=['과정코드']) # [과정코드] 컬럼을 기준으로 두 데이터프레임 병합
        # df_merge : | 과정코드 | 과정분류 | 과정명 | 보험사 | 월 | 과정형태 | 수강료 | 지역 | 교육장소 | 정원 | 목표인원 | 소속부문 | 소속총괄 | 소속부서 | 파트너 | 사원번호 | 성명 | IMO신청여부 | 수료현황 | 입사연차
        return df_merge

    # ----------------------------          소속부문별 고유값 및 누계값 (상태값)          ---------------------------------
    def make_set_status(self, df, *columns): # *columns : '소속부문' 또는 '입사연차'
        # df : | 과정코드 | 과정분류 | 과정명 | 보험사 | 월 | 과정형태 | 수강료 | 지역 | 교육장소 | 정원 | 목표인원 | 소속부문 | 소속총괄 | 소속부서 | 파트너 | 사원번호 | 성명 | IMO신청여부 | 수료현황 | 입사연차
        # 신청인원 및 신청누계 구하기
        df_apply_total = df.groupby([*columns,'사원번호']).size().reset_index(name='신청누계') # 신청누계 : df를 *columns로 묶고, 사원번호의 누적개수 구하기
        df_apply_unique = df_apply_total.groupby([*columns])['사원번호'].nunique().reset_index(name='신청인원') # 신청인원 : df를 *columns로 묶고, 사원번호의 고유개수 구하기
        df_apply = pd.merge(df_apply_unique, df_apply_total.groupby([*columns])['신청누계'].sum().reset_index(name='신청누계'), on=[*columns]) # 신청인원과 신청누계 병합
        # ---------------------------------------------------------------------------------------------------------------
        # 수료인원, 수료누계, 수료율 및 IMO신청인원, IMO신청누계, IMO신청률
        index = [['수료현황', '수료인원', '수료누계', '수료율'], ['IMO신청여부', 'IMO신청인원', 'IMO신청누계', 'IMO신청률']]
        for i in range(len(index)):
            df_two_total = df.groupby([*columns])[index[i][0]].sum().reset_index(name=index[i][2]) # 수료현황 또는 IMO신청여부 : 전체 더하기 (수료누계 및 IMO신청누계)
            df_two_unique = pd.DataFrame(df[df[index[i][0]] != 0]).groupby([*columns])['사원번호'].nunique().reset_index(name=index[i][1]) # 수료현황 또는 IMO신청여부 : 값이 1인 사원번호의 개수 (수료인원 및 IMO신청인원)
            df_two = pd.merge(df_two_unique, df_two_total, on=[*columns]) # 수료인원+수료누계 & IMO신청인원+IMO신청누계
            df_apply = pd.merge(df_apply, df_two, on=[*columns]) # 신청+수료+IMO
        for i in range(len(index)):
            df_apply[index[i][3]] = (df_apply[index[i][2]]/df_apply['신청누계']*100).round(1) # 수료율 및 IMO신청률 구하기
        # df_apply : | 소속부문/입사연차 | 신청인원 | 신청누계 | 수료인원 | 수료누계 | 수료율 | IMO신청인원 | IMO신청누계 | IMO신청률
        return df_apply

    # ------------------------------          소속부문별 고유값 및 누계값 (월별추이)          ------------------------------------
    def make_set_trend(self, df, theme, *columns):
        # df_apply : | 소속부문/입사연차 | 신청인원 | 신청누계 | 수료인원 | 수료누계 | 수료율 | IMO신청인원 | IMO신청누계 | IMO신청률
        df_apply = self.make_set_status(df, *columns)
        # ---------------------------------------------------------------------------------------------------------------
        # 재적인원
        df_apply = pd.merge(df_apply, self.call_registered(theme), on=['월',theme]) # 기존 데이터프레임과 재적인원 데이터프레임 병합
        units_index = ['재적인원 대비 신청인원', '재적인원 대비 신청누계', '재적인원 대비 수료인원', '재적인원 대비 수료누계', '재적인원 대비 수료율', '재적인원 대비 IMO신청인원', '재적인원 대비 IMO신청누계', '재적인원 대비 IMO신청률']
        for c in range(len(units_index)):
            df_apply[units_index[c]] = (df_apply[units_index[c].split(" ")[2]] / df_apply['재적인원'] * 100).round(1) # 각 요소별 재적인원 대비 인원비율 구하기
        # ---------------------------------------------------------------------------------------------------------------
        df_apply = pd.merge(pd.DataFrame({'월' : sorted(df_apply['월'].unique(), key=self.sort_month)}), df_apply, on=['월'])
        # df_apply : | 월 | 소속부문/입사연차 | 신청인원 | 신청누계 | 수료인원 | 수료누계 | 수료율 | IMO신청인원 | IMO신청누계 | IMO신청률 | 재적인원 대비 신청인원 | 재적인원 대비 신청누계 | 재적인원 대비 수료인원 | 재적인원 대비 수료누계 | 재적인원 대비 IMO신청인원 | 재적인원 대비 IMO신청률'
        return df_apply

    # ------------------------------          현황요약 (수료율 & IMO신청률)          ------------------------------------
    def make_rates(self, df, item_a, item_b, reference, column):
        return pd.DataFrame({
            '구분':[item_a,item_b],
            column:[(df[reference].sum()/df.shape[0]*100).round(1), (100-df[reference].sum()/df.shape[0]*100).round(1)]
        })

    # ------------------------------          현황요약 (신청 & 수료)          ------------------------------------
    def make_summary_status(self, df):
        # df_summary : | 소속부문/입사연차 | 신청인원 | 신청누계 | 수료인원 | 수료누계 | 수료율 | IMO신청인원 | IMO신청누계 | IMO신청률
        df_summary = self.make_set_status(df, *['소속부문']) # 전체 현황 데이터 호출
        return pd.DataFrame({
            '구분':['신청','수료'],
            '고유인원':[df_summary['신청인원'].sum(), df_summary['수료인원'].sum()],
            '누계인원':[df_summary['신청누계'].sum(), df_summary['수료누계'].sum()]
        })
    
    # ------------------------------          요약추이 제작을 위한 내부함수          ------------------------------------
    def calculate_summary(self, df, columns, percentage):
        summary_data = df.groupby(['월'])[[columns,'재적인원']].sum() # df_all 데이터프레임으로 부터 신청인원 및 수료인원 관련 컬럼 추출
        summary_data['구분'] = columns # 새로 만든 데이터프레임의 [값] 컬럼에 '신청인원' 또는 '수료인원' 데이터를 계산하여 삽입
        if percentage == True:
            summary_data['값'] = (summary_data[columns] / summary_data['재적인원'] * 100).round(1) # 새로 만든 데이터프레임의 [값] 컬럼에 '재적인원 대비 신청인원' 또는 '재적인원 대비 수료인원' 데이터를 계산하여 삽입
        else:
            summary_data['값'] = summary_data[columns] # 새로 만든 데이터프레임의 [값] 컬럼에 '재적인원 대비 신청인원' 또는 '재적인원 대비 수료인원' 데이터를 계산하여 삽입
        summary_data.drop(columns=[columns,'재적인원'],inplace=True) # '신청인원' 또는 '수료인원' 컬럼과 '재적인원' 컬럼 삭제
        return summary_data
    
    # ------------------------------          현황요약 (신청인원 및 수료인원)          ------------------------------------
    def make_trend_all(self, df):
        # df_summary : | 월 | 소속부문/입사연차 | 신청인원 | 신청누계 | 수료인원 | 수료누계 | 수료율 | IMO신청인원 | IMO신청누계 | IMO신청률 | 재적인원 대비 신청인원 | 재적인원 대비 신청누계 | 재적인원 대비 수료인원 | 재적인원 대비 수료누계 | 재적인원 대비 IMO신청인원 | 재적인원 대비 IMO신청률'
        df_all = self.make_set_trend(df,'소속부문', *['월','소속부문'])
        # ---------------------------------------------------------------------------------------------------------------
        # 재적인원 대비 신청누계 및 재적인원 대비 수료누계
        df_trend_apply = self.calculate_summary(df=df_all, columns='신청누계', percentage=False)
        df_trend_attend = self.calculate_summary(df=df_all, columns='수료누계', percentage=False)
        # ---------------------------------------------------------------------------------------------------------------
        # 재적인원 대비 신청누계 및 재적인원 대비 수료누계 병합
        df_summary = pd.merge(pd.DataFrame({'월': sorted(df_trend_attend.index, key=self.sort_month)}), pd.concat([df_trend_apply, df_trend_attend], axis=0), on=['월'])
        return df_summary   
    
    # ------------------------------          현황요약 (재적인원 대비 신청인원 및 수료인원)          ------------------------------------
    def make_trend_people(self, df):
        # df_summary : | 월 | 소속부문/입사연차 | 신청인원 | 신청누계 | 수료인원 | 수료누계 | 수료율 | IMO신청인원 | IMO신청누계 | IMO신청률 | 재적인원 대비 신청인원 | 재적인원 대비 신청누계 | 재적인원 대비 수료인원 | 재적인원 대비 수료누계 | 재적인원 대비 IMO신청인원 | 재적인원 대비 IMO신청률'
        df_all = self.make_set_trend(df,'소속부문', *['월','소속부문'])
        # ---------------------------------------------------------------------------------------------------------------
        # 재적인원 대비 신청누계 및 재적인원 대비 수료누계
        df_summary_apply = self.calculate_summary(df=df_all, columns='신청누계', percentage=True)
        df_summary_attend = self.calculate_summary(df=df_all, columns='수료누계', percentage=True)
        # ---------------------------------------------------------------------------------------------------------------
        # 재적인원 대비 신청누계 및 재적인원 대비 수료누계 병합
        df_summary = pd.merge(pd.DataFrame({'월': sorted(df_summary_attend.index, key=self.sort_month)}), pd.concat([df_summary_apply, df_summary_attend], axis=0), on=['월'])
        return df_summary   

#########################################################################################################################
##############                        보장분석 클래스 정의 (차트제작) : MakeSet 상속                        ###############
#########################################################################################################################
class ServiceData:
    def __init__(self) -> None:
        pass
    
    def call_data_service(self):
        month_dict = {'jan':'1월','feb':'2월','mar':'3월','apr':'4월','may':'5월','jun':'6월','jul':'7월','aug':'8월','sep':'9월','oct':'10월','nov':'11월','dec':'12월'} # 반복문 실행을 위한 딕셔너리 선언
        df_service = pd.DataFrame() # 데이터 정리를 위한 데이터프레임 생성
        # 1월부터 12월까지 데이터 정리
        for month_key, month_name in month_dict.items():
            with st.spinner(f"{month_name} 데이터를 불러오는 중입니다."): # 로딩 화면 구현
                try: df_month = call_sheets(month_key).rename(columns={'컨설턴트ID':'사원번호','컨설턴트성명':'성명'}) # 각 월별 데이터 호출
                except: break # 아직 월별 데이터 생성 안 됐으면 반복문 탈출
                df_month = df_month.drop(df_month[df_month['파트너'] == '인카본사'].index) # [파트너]에서 '인카본사' 삭제
                df_month.insert(23, '약관조회', 0)
                df_month.insert(0, '월', month_name) # 기준일자 대신 월 항목 추가
                df_month['사원번호'] = df_month['사원번호'].astype(str) # 사번정리
                for i in range(df_month.shape[0]):
                    if len(df_month.iat[i,5]) < 6: df_month.iat[i,5] = f"16{df_month.iat[i,5]}"
                    else: pass
                df_service = pd.concat([df_service, df_month], axis=0) # 전월 데이터와 병합
        return df_service
    
    def make_set_summary(self, df):
        df_service = pd.DataFrame() # 데이터 정리를 위한 데이터프레임 생성
        columns_service = [
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
            '라이프사이클출력건수']
        # ---------------------------------------------------------------------------------------------------------------
        for month in df['월'].unique():
            try: df_month = df[df['월'].isin([month])].drop(columns=['기준일자','소속부문','소속총괄','소속부서','파트너','성명'])
            except: pass
            df_summary = pd.DataFrame()
            for columns in range(len(columns_service)):
                df_summary[columns_service[columns]] = [df_month[columns_service[columns]].astype(int).sum()] # 각 항목 합계 계산
            df_summary.insert(0, '월', month) # 기준일자 대신 월 항목 추가
            df_summary.insert(1, '사용자수', df_month['사원번호'].nunique()) # 사원번호 개수 구해서 사용자수 삽입
            df_service = pd.concat([df_service, df_summary], axis=0) # 전월 데이터와 병합
        # ---------------------------------------------------------------------------------------------------------------
        df_service['사용자수'] = df_service['사용자수'].astype(int)
        df_service.insert(2, '전월 대비 증감', '')
        for i in range(df_service.shape[0]):
            try: df_service.iloc[i+1,2] = df_service.iloc[i+1,1] - df_service.iloc[i,1]
            except: pass
        return df_service
    
    def make_set_branch(self, df):
        df_branch = pd.DataFrame(columns=['소속부문','소속총괄','소속부서'])
        for month in df['월'].unique():
            df_month = df[df['월'].isin([month])] # 해당 월에 해당하는 데이터만 추출
            df_month = df_month.groupby(['소속부문','소속총괄','소속부서'])['사원번호'].nunique().reset_index(name=month) # 사원번호 개수 카운트 (사용자수)
            df_branch = pd.merge(df_branch, df_month, on=['소속부문','소속총괄','소속부서'], how='outer').fillna(0) # 기존 데이터와 병합하고 빈 셀은 0으로 채워넣기
        # df_branch : | 소속부문 | 소속총괄 | 소속부서 | 1월 | 2월 | 3월 | 4월 | 5월 | 6월 | 7월 | 8월 | 9월 | 10월 | 11월 | 12월 |
        # ---------------------------------------------------------------------------------------------------------------
        df_branch_sum = pd.DataFrame()
        for part in df_branch['소속총괄'].unique():
            df_part = df_branch[df_branch['소속총괄'].isin([part])] # 해당 총괄에 해당하는 데이터만 추출
            if part in ['CA1총괄']: st.dataframe(df_part)
            else: pass
        # ---------------------------------------------------------------------------------------------------------------
            # 총괄별 합계
            df_sum = pd.DataFrame()
            df_part_sum = pd.DataFrame()
            for i in df_part.columns:
                if i in ['소속부문','소속총괄']: df_sum[i] = df_part[i]
                elif i in ['소속부서']: df_sum[i] = ''
                else: df_sum[i] = df_part[i].sum() # 컬럼별 합계
                if part in ['CA1총괄']: st.dataframe(df_sum)
                else: pass
            df_sum = df_sum.iloc[[0]]
            df_part_sum = pd.concat([df_part, df_sum], axis=0)
            if part in ['CA1총괄']: st.dataframe(df_part_sum)
            else: pass

            df_branch_sum = pd.concat([df_branch, df_part_sum], axis=0)
        return df_branch_sum
