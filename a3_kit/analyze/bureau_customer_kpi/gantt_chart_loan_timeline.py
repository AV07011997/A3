import plotly.express as px
import plotly
import pandas as pd
import plotly.figure_factory as ff
from datetime import datetime
import numpy as np

df=pd.read_excel(r"/home/pratyush/Downloads/bureau_account_segment_tl.xlsx")
df=df.sort_values('HIGH_CREDIT_AMOUNT')
# df['DATE_CLOSED']=pd.to_datetime(df['DATE_CLOSED'])

df['DATE_CLOSED'] = (pd.to_datetime(df['DATE_CLOSED']))
df['DATE_CLOSED'] =df['DATE_CLOSED'].apply(lambda x: x.date())
df['PAYMENT_HST_1']=df['PAYMENT_HST_1'].astype(str)




df['status_check']=0

for i in range(len(df)):

    if (pd.isnull(df['DATE_CLOSED'][i])):

        if ((df['PAYMENT_HST_1'][i][1:4] == '000') or (df['PAYMENT_HST_1'][i][1:4] == 'XXX') or (
            df['PAYMENT_HST_1'][i] == 'nan')):
            df['status_check'][i] = "Active Non Delinquent"
        else:
            df['status_check'][i] = "Active Delinquent"


    else:
        df['status_check'][i] = "Closed Loan"






###########

df['DATE_CLOSED'] = (pd.to_datetime(df['DATE_CLOSED']))




start_dates=[i.date() for i in df['DATE_AC_DISBURSED']]

for j in range(len(df)):
    if(pd.isnull(df['DATE_CLOSED'][j])):
        df['DATE_CLOSED'][j]=datetime.now()
        df['DATE_CLOSED'][j]=df['DATE_CLOSED'][j].date()
    else:
        df['DATE_CLOSED'][j]=df['DATE_CLOSED'][j].date()




amt=df['HIGH_CREDIT_AMOUNT']
start_dates=df['DATE_AC_DISBURSED']
end_dates=df['DATE_CLOSED']
types=df['status_check']

df_chart=pd.DataFrame()
df_chart['Task']=amt
df_chart['Start']=start_dates
df_chart['Finish']=end_dates
df_chart['Resource']=types
colors = {"Active Non Delinquent": 'rgb(0, 255, 100)',
          "Active Delinquent": 'rgb(255, 191, 0)',
          "Closed Loan": 'rgb(255,0,0)'}

fig = ff.create_gantt(df_chart,  index_col='Resource', colors=colors,
                      showgrid_x=True, showgrid_y=False,title='Loan Timeline',
                      show_colorbar=True, bar_width=0.25,)
fig.layout.xaxis.tickformat = '%Y-%m-%d'
fig.layout.yaxis.title="Disbursed Amount"



plotly.offline.plot(fig,filename=r"/home/pratyush/liveserverproject/a3_kit/templates/test.html")