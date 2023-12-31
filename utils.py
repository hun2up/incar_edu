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
##############                                  차트제작 클래스 정의                                      ################
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

    # -----------------------------------          수평막대그래프 제작 (Grouped)          ------------------------------------
    def make_vbarchart_group(self, df, category, axis_a, axis_b, title, caption=True):
        if caption == True: caption_text = '색상 차트는 누적인원(중복포함), 회색 차트는 고유인원(중복제거)'
        else: caption_text = None
        # axis_a: 고유값 (신청인원, 수료인원) / axis_b: 누계값 (신청누계, 수료누계)
        fig_a = pl.graph_objs.Bar(
            x=df[category],
            y=df[axis_a],
            name=axis_a,
            text=df[axis_a],
            marker={'color':'grey'},
            orientation='v'
        )
        fig_b = pl.graph_objs.Bar(
            x=df[category],
            y=df[axis_b],
            name=axis_b,
            text=df[axis_b],
            marker={'color':self.generate_chart_colors(df)},
            orientation='v'
        )
        layout_chart = pl.graph_objs.Layout(title=title,xaxis={'categoryorder':'array', 'categoryarray':self.generate_barchart_orders(df,category)}, annotations=[dict(text=caption_text,showarrow=False,xref='paper',yref='paper',x=-0.1,y=1.1)])
        return_chart = pl.graph_objs.Figure(data=[fig_a, fig_b],layout=layout_chart)
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
    def make_piechart(self, label, value, title=None, font=20):
        fig_pchart = pl.graph_objs.Figure(data=[pl.graph_objs.Pie(labels=label, values=value, hole=.3)])
        fig_pchart.update_traces(hoverinfo='label+percent', textinfo='label+value', textfont_size=font, showlegend=False)
        if title:
            fig_pchart.update_layout(title=title)
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
            sector = st.columns(5)
            [sector[i].metric(f"{df.iat[i,1]} ({df.iat[i, 0]})", f"{df.iat[i, index_columns[loop]]} ({index_units[loop]})") for i in range(5)] # 카드 5개 씩 만들기

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
            sector = st.columns(6)
            [sector[i].metric(df.iat[i,0], f"{df.iat[i, index_column[loop]]} ({index_units[loop]})") for i in range(5)] # 카드 5개 씩 만들기

#########################################################################################################################
##############                   교육관리(메인페이지) 클래스 정의 : Charts 클래스 상속                      ################
#########################################################################################################################
class EduMain(Charts):
    def __init__(self):
        super().__init__()

    # ----------------------------------------          신청현황 시트 호출          -------------------------------------------
    def call_data_main(self):
        # [매일]신청현황 시트 호출 (https://docs.google.com/spreadsheets/d/1AG89W1nwRzZxYreM6i1qmwS6APf-8GM2K_HDyX7REG4/edit#gid=216302834)
        #df_attend : | 과정명 | 소속부문 | 소속총괄 | 소속부서 | 파트너 | 사원번호 | 성명 | IMO신청여부 | 수료현황 | 비고
        df_main = call_sheets("apply").drop(columns=['번호','비고']).rename(columns={'성함':'성명','날짜':'신청일자'}) # 시트 호출 & 컬럼 삭제 (번호) & 컬럼명 변경 (성함 ▶ 성명)
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

    # ------------------------------------------          전체 교육신청          ---------------------------------------------
    def make_set_main(self, df, select):
        # df : | 신청일자 | 과정코드 | 소속부문 | 파트너 | 사원번호 | 성명 | 신청인원 | 과정명 | 교육일자 | 목표인원
        df_main = df.drop(df[df.iloc[:,0] != df.iloc[-1,0]].index) # 신청일자 가장 최근 데이터만 남기기
        df_main = df_main.groupby([select])['신청인원'].sum().reset_index(name='신청인원')
        return df_main
    
    # ------------------------------------------          신규 교육신청          ---------------------------------------------
    def make_set_new(self, df):
        df_before = df.drop(df[df.iloc[:,0] == df.iloc[-1,0]].index)
        df_before = df_before.drop(df_before[df_before.iloc[:,0] != df_before.iloc[-1,0]].index)
        df_today = df.drop(df[df.iloc[:,0] != df.iloc[-1,0]].index)
        df_today = df_today[~df_today['사원번호'].isin(df_before['사원번호'])][['신청일자','교육일자','과정명','소속부문','파트너','사원번호','성명','입사연차']].reset_index(drop=True)
        return df_today

    # ------------------------------------------          홍보효과 분석을 위한 신청현황 데이터 호출 및 정리          ---------------------------------------------
    def target_set_apply(self, df):
        df_apply = df.drop(df[df.iloc[:,0] != df.iloc[-1,0]].index)[['교육일자','과정코드','과정명','소속부문','파트너','사원번호','성명','입사연차']] # 마지막 신청일자 제외한 나머지 신청내역 삭제
        df_apply['사원번호'] = df_apply['사원번호'].astype(str)
        return df_apply

    # ------------------------------------------          홍보효과 분석을 위한 타겟홍보 데이터 호출 및 정리          ---------------------------------------------
    def target_set_target(self):
        df_target = call_sheets("target").drop(columns=['번호','소속총괄','소속부서','IMO신청여부','수료현황']).rename(columns={'성함':'성명'}).reset_index(drop=True)
        df_target = df_target.drop(df_target[df_target['파트너'] == '인카본사'].index)
        df_target.insert(0, column='타겟명', value=None)
        df_target['타겟명'] = df_target['과정명'].str.split(']').str[1]
        df_target = df_target.drop(columns='과정명')
        df_target['사원번호'] = df_target['사원번호'].astype(str)     
        # 입사연차 컬럼 추가
        df_target['입사연차'] = (datetime.now().year%100 + 1 - df_target['사원번호'].astype(str).str[:2].astype(int, errors='ignore')).apply(lambda x: f'{x}년차') # [입사연차] 컬럼 추가 및 데이터(입사연차) 삽입   
        return df_target
    
    # ------------------------------------------          홍보효과 분석을 위한 신청현황 및 타겟홍보 데이터 병합          ---------------------------------------------
    def make_set_target(self, apply, target, data_type):
        label_data = [['과정명','신청인원','유입인원'],['타겟명','타겟인원','반응인원']]
        df_apply = apply
        df_target = target
        # -------------------------------------------------------------------------------------------------------------------
        if data_type == '신청':
            number = 0
            df_left = df_apply
            df_right = df_target
        elif data_type =='타겟': 
            number = 1
            df_left = df_target
            df_right = df_apply
        # -------------------------------------------------------------------------------------------------------------------
        df_all = df_left.groupby([label_data[number][0]])['사원번호'].nunique().reset_index(name=label_data[number][1])
        df_selected = df_left[df_left['사원번호'].isin(df_right['사원번호'])].groupby([label_data[number][0]])['사원번호'].nunique().reset_index(name=label_data[number][2])
        return pd.merge(df_all, df_selected, on=label_data[number][0])

    # ------------------------------------------          원형차트 제작          ---------------------------------------------
    def make_pie_target(self, apply, target, data_type):
        self.make_set_target(apply=apply,target=target,data_type=data_type)
        # -------------------------------------------------------------------------------------------------------------------
        if data_type == '신청': label_chart = ['타겟유입','직접신청','유입인원','신청인원']
        elif data_type =='타겟': label_chart = ['타겟반응','반응없음','반응인원','타겟인원']
        # -------------------------------------------------------------------------------------------------------------------
        return pd.DataFrame({
            '구분':[label_chart[0],label_chart[1]],
            '인원':[self.make_set_target(apply=apply,target=target,data_type=data_type)[label_chart[2]].sum(), self.make_set_target(apply=apply,target=target,data_type=data_type)[label_chart[3]].sum() - self.make_set_target(apply=apply,target=target,data_type=data_type)[label_chart[2]].sum()]
        })

    # ------------------------------------------          원형차트 제작          ---------------------------------------------
    def make_bar_target(self, apply, target, select):
        df_apply = apply
        df_target = target
        # -------------------------------------------------------------------------------------------------------------------
        df_apply_all = df_apply.groupby([select])['사원번호'].count().reset_index(name='신청인원')
        df_apply_isin = df_apply[df_apply['사원번호'].isin(df_target['사원번호'])].groupby([select])['사원번호'].count().reset_index(name='유입인원')
        df_apply_all = pd.merge(df_apply_all, df_apply_isin, on=select)
        df_apply_all['유입률'] = (df_apply_all['유입인원']/df_apply_all['신청인원']*100).round(1) # 수료율 및 IMO신청률 구하기
        # -------------------------------------------------------------------------------------------------------------------
        df_target_all = df_target.groupby([select])['사원번호'].count().reset_index(name='타겟인원')
        df_target_isin = df_target[df_target['사원번호'].isin(df_apply['사원번호'])].groupby([select])['사원번호'].count().reset_index(name='반응인원')
        df_target_all = pd.merge(df_target_all, df_target_isin, on=select)
        df_target_all['반응률'] = (df_target_all['반응인원']/df_target_all['타겟인원']*100).round(1)
        # -------------------------------------------------------------------------------------------------------------------
        # | 소속부문/입사연차 | 신청인원 | 유입인원 | 유입률 | 타겟인원 | 반응인원 | 반응률
        return pd.merge(df_apply_all, df_target_all, on=select)

    # ------------------------------------------          홍보효과 데이터프레임 제작          ---------------------------------------------
    def make_dataframe_target(self, apply, target, data_type):
        df_apply = apply
        df_target = target
        # -------------------------------------------------------------------------------------------------------------------
        if data_type == '신청':
            df_left = df_apply
            df_right = df_target
            label_dataframe = ['과정명','유입여부','타겟유입']
        elif data_type =='타겟': 
            df_left = df_target
            df_right = df_apply
            label_dataframe = ['타겟명','반응여부','타겟반응']
        # -------------------------------------------------------------------------------------------------------------------
        df_isin = df_left[df_left['사원번호'].isin(df_right['사원번호'])]
        df_isin[label_dataframe[1]] = label_dataframe[2]
        df_notin = df_left[~df_left['사원번호'].isin(df_right['사원번호'])]
        df_notin[label_dataframe[1]] = ''
        df_result = pd.concat([df_isin,df_notin], axis=0)[[label_dataframe[0],'소속부문','파트너','사원번호','성명','입사연차',label_dataframe[1]]].sort_values(by=label_dataframe[0],ascending=True).reset_index(drop=True)
        return df_result

#########################################################################################################################
##############                   교육관리(하위페이지) 클래스 정의 : Charts 클래스 상속                      ################
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
        # [매월]교육과정수료현황 시트 호출 (https://docs.google.com/spreadsheets/d/1AG89W1nwRzZxYreM6i1qmwS6APf-8GM2K_HDyX7REG4/edit#gid=0)
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
        df_course['년도'] = [f"{pd.to_datetime(df_course.at[short, '교육일자'], format='%Y. %m. %d').year}년" for short in range(df_course.shape[0])]
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