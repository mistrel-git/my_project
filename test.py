# 한국 거래소 데이터 => 종목코드

# 네이버 금융에 특정 기업을 분석한다. 분석 대상은 신라젠이라는 기업.

# jupyter notebook은 반드시 크롬에서 실행한다.


import pandas as pd

# html에 있는 정보를 읽어온다.

# header = 0 으로 맨 윗줄의 데이터를 헤더로 사용하고 얻은 자료를 리스트 형태로 이용하기 위해 뒤에 [0] 을 붙여준다.

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]

# 타입을 확인

print(type(code_df))  # <class 'pandas.core.frame.DataFrame'>

print(code_df.head())  # 데이터를 확인

# code_df에 있는 '종목코드' 컬럼을 0을 채운 6자리 포멧으로 맞춰준다.

code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)

# code_df를 회사명과 종목코드 컬럼만 뽑아낸다.

#    ***참고*** pandas에서 컬럼을 선택 할 때

#                   단일개 선택: df['컬럼명']   or   df.컬럼명

#                   여러개 선택: df[['컬럼명', ... ,'컬럼명']]

code_df = code_df[['회사명', '종목코드']]

print(code_df)  # 데이터를 확인

# 한글로된 컬럼명을 영어로 바꿔준다.

code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})


# 신라젠 네이버 금융 주소.   http://finance.naver.com/item/main.nhn?code=215600

# 함수 생성 => 특정한 업체만 코드를 가져오기 위해서

def get_url(item_name, code_df):
    # 코드를 가져오기 위한 처리.

    # 먼저 .query("name=='{}'".format(item_name))['code']는 name 컬럼에 item_name과 동일한 값의 code값을 반환한다는 뜻.

    # 즉, .query("쿼리".format(쿼리에 넣을 데이터))[얻을 자료]

    # .to_string(index = False)로 위에서 얻어진 값에 index를 빼고 string타입으로 바꿔준다.

    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)

    # url은 일일 종가 시가 고가 저가 거래량을 보여주는 표이다.

    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)

    print("요청 URL = {}".format(url))

    return url


# 신라젠 정보 가져오기

item_name = '신라젠'

url = get_url(item_name, code_df)

df = pd.DataFrame()

# 크롤링. 페이지 20까지 크롤링을 한다.

for page in range(1, 21):
    # 위에서 얻은 url에 page를 붙여줘서 url 포멧을 만들어준다.

    pg_url = '{url}&page={page}'.format(url=url, page=page)

    # pandas의 df에 위에서 얻은 url을 넣어줘서 우리가 구하고자 하는 데이터프레임을 만든다.

    # 데이터프레임을 만들 때 리스트에 [0]을 붙여줘서 만들 수 있음을 다시 확인.

    df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)

# df.dropna()를 이용해 결측값(NaN) 있는 행을 제거한다.

df = df.dropna()

# 상위 5개 데이터 확인하기

print(df.head())

# 한글로 된 컬럼명을 영어로 바꿔준다.

df = df.rename(columns={'날짜': 'date', '종가': 'close', '전일비': 'diff',

                        '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'})

# 데이터의 타입을 int형으로 바꿔줌. \(역슬래쉬)는 뒤에 데이터가 이어진다는 의미이다. 한줄로 쓰면 \ 필요없음.

df[['close', 'diff', 'open', 'high', 'low', 'volume']] \
 \
    = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)

# 컬럼명 'date'의 타입을 date로 바꿔줌

df['date'] = pd.to_datetime(df['date'])

#  일자(date)를 기준으로 오름차순 정렬

df = df.sort_values(by=['date'], ascending=True)

# 상위 5개 데이터 확인

print(df.head())

# 시각화 파트


# jupyter notebook 에서 출력. 꼭 jupyter notebook에서 해야한다.

# 만약 jupyter notebook에서 출력하기 싫다면 아래에 적어놓는 방법을 이용하자.


import plotly.offline as offline

import plotly.graph_objs as go

# plotly 접속

offline.init_notebook_mode(connected=True)

# 그래프를 생성. x축에는 날짜, y축에는 종가, 그래프 이름은 item_name에서 가져온다.

trace = go.Scatter(x=df.date, y=df.close, name=item_name)

# 위에 데이터 정보를 data라는 객체의 리스트로 담아준다.

data = [trace]

# 레이아웃 잡기

layout = dict(title='{}의 종가(close) Time Series'.format(item_name),  # 타이틀 생성.

              xaxis=dict(

                  rangeselector=dict(

                      buttons=list([  # 한 달, 세 달, 6달, 전체 종가를 보여주는 버튼을 만든다.

                          dict(

                              count=1,  # 1개씩 센다. 여기서는 step='month'이기 때문에 1달이 된다.

                              label='1m',  # 라벨 이름. 그래프에 1m이라는 버튼을 만든다.

                              step='month',  # 한 달을 기준으로 잡아서 count를 센다.

                              stepmode='backward'),  # 가장 최근 데이터부터 센다. forward는 가장 오래된 데이터부터 센다.

                          dict(

                              count=3,

                              label='3m',

                              step='month',

                              stepmode='backward'),

                          dict(

                              count=6,

                              label='6m',

                              step='month',

                              stepmode='backward'),

                          dict(

                              step='all')])),  # 전체 데이터를 출력한다. step='all'은 label을 설정할 수 없다.

                  rangeslider=dict(),

                  type='date'

              )

              )

# graph object에 data, layout을 저장한다.

fig = go.Figure(data=data, layout=layout)

# 플롯을 출력한다.

offline.iplot(fig)

# jupyter notebook 에서 출력하기 싫을 때 사용하는 방법.

# html로 만든다.


import plotly.offline as offline

import plotly.graph_objs as go

# # plotly 접속

# offline.init_notebook_mode(connected=True)

# 그래프를 생성. x축에는 날짜, y축에는 종가, 그래프 이름은 item_name에서 가져온다.

trace = go.Scatter(x=df.date, y=df.close, name=item_name)

# 위에 데이터 정보를 data라는 객체의 리스트로 담아준다.

data = [trace]

# 레이아웃 잡기

layout = dict(title='{}의 종가(close) Time Series'.format(item_name),  # 타이틀 생성.

              xaxis=dict(

                  rangeselector=dict(

                      buttons=list([  # 한 달, 세 달, 6달, 전체 종가를 보여주는 버튼을 만든다.

                          dict(

                              count=1,  # 1개씩 센다. 여기서는 step='month'이기 때문에 1달이 된다.

                              label='1m',  # 라벨 이름. 그래프에 1m이라는 버튼을 만든다.

                              step='month',  # 한 달을 기준으로 잡아서 count를 센다.

                              stepmode='backward'),  # 가장 최근 데이터부터 센다. forward는 가장 오래된 데이터부터 센다.

                          dict(

                              count=3,

                              label='3m',

                              step='month',

                              stepmode='backward'),

                          dict(

                              count=6,

                              label='6m',

                              step='month',

                              stepmode='backward'),

                          dict(

                              step='all')])),  # 전체 데이터를 출력한다. step='all'은 label을 설정할 수 없다.

                  rangeslider=dict(),

                  type='date'

              )

              )

# graph object에 data, layout을 저장한다.

fig = go.Figure(data=data, layout=layout)

# 플롯을 출력한다.

offline.iplot(fig)

# 여기까지 끝나면 temp-plot.html이 생성되는데 이걸 출력하면 jupyter에서 출력되는 것과 동일한 그래프가 나온다.

# 경로와 이름을 지정하고 싶으면 offline.plot(fig, filename = '원하는 경로/원하는 이름.html')을 하면 된다.
