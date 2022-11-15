import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
import os
import squarify
from django.conf import settings
from babel.numbers import format_currency

def bck(data):
  df = data
  df['txn_date'] = pd.to_datetime(df['txn_date'], format='%Y-%m-%d')
  df['month_year'] = df['txn_date'].dt.month.astype(str)+'-'+df['txn_date'].dt.year.astype(str)
  # df['debit'] = [float(str(i).replace(',','')) for i in df['debit']]
  df.debit = df.debit.replace(0,np.nan)
  # df['credit'] = [float(str(i).replace(',','')) for i in df['credit']]
  # df['balance'] = [float(str(i).replace(',','')) for i in df['balance']]
  df.credit = df.credit.replace(0,np.nan)
  df.sort_values('txn_date', ascending=True, inplace=True)
  print('output from python code')
  print(df['account_number'])
  start = df['txn_date'].min()
  end = df['txn_date'].max()
  start1 = start.date()
  start1 = str(start1)
  end1 = end.date()
  end1 = str(end1)

  opening_bal = df.balance[df.first_valid_index()]
  closing_bal = df.balance[df.last_valid_index()]

  table4 = pd.DataFrame({'Start_Date':[start1], 'End_Date':[end1], 'Opening_Balance':[opening_bal], 'Closing_Balance':[closing_bal]})

  df2 = pd.DataFrame(data={'date':pd.date_range(start,end-timedelta(days=0),freq='d').tolist()})
  
  df2 = df2.merge(df[['txn_date', 'balance']], left_on='date', right_on='txn_date', how='left')
  df2.drop(columns=['txn_date'], inplace=True)
  df2 = df2[df2['balance'].notna()]
  df2['balance'].fillna(method='ffill', inplace=True)
  df2['month_year'] = df2['date'].dt.month.astype(str)+'-'+df2['date'].dt.year.astype(str)
  
  a = df2.groupby('month_year').balance.mean()
  avg_mthly_bal = a.sum()/a.shape[0]


  a=df.loc[df.debit.notnull(),:].groupby('month_year').debit.mean()
  avg_mthly_debit = (a.sum()/a.shape[0])


  a=df.loc[df.credit.notnull(),:].groupby('month_year').credit.mean()
  avg_mthly_credit = (a.sum()/a.shape[0])


  max_bal = df.balance.max()

  min_bal = df.balance.min()

  table = pd.DataFrame({'Average_Monthly_Balance':[avg_mthly_bal],'Average_Monthly_Debit':[avg_mthly_debit],'Average_Monthly_Credit':[avg_mthly_credit],'Maximum_Balance':[max_bal],'Minimum_Balance':[min_bal]})

  ratio_deb_cr = df.debit.sum()/df.credit.sum()
  ratio_cash_tot_cr = df.loc[(df['mode'].str.lower().str.strip()=='cash'),'credit'].sum()/df.credit.sum()

  if pd.notna(df.credit.idxmax()):
    mode_str = df.loc[df.credit.idxmax(),'mode']
    if pd.isna(mode_str):
      mode_str=''
    hi_cr_amt = format_currency(df.loc[df.credit.idxmax(), 'credit'], 'INR', locale='en_IN') + ' ('+mode_str+')'
  else:
    mode_str = ''
    hi_cr_amt = u"\u20B9"+str(np.nan) + ' ('+mode_str+')'
  hi_cr_amt_org = hi_cr_amt.replace(',','').replace('₹','').split(' ')[0]
  
  if pd.notna(df.debit.idxmin()):
    mode_str = df.loc[df.debit.idxmin(),'mode']
    if pd.isna(mode_str):
      mode_str=''
    low_deb_amt = format_currency(df.loc[df.debit.idxmin(), 'debit'], 'INR', locale='en_IN') + ' ('+mode_str+')'
  else:
    mode_str = ''
    low_deb_amt = u"\u20B9"+str(np.nan) + ' ('+mode_str+')'  
  low_deb_amt_org = low_deb_amt.replace(',','').replace('₹','').split(' ')[0]
  
  table2 = pd.DataFrame({'Ratio_Debit_Credit':[ratio_deb_cr], 'Ratio_Cash_Total_Credit':[ratio_cash_tot_cr], 'Lowest_Debit_Amount':[low_deb_amt], 'Highest_Credit_Amount':[hi_cr_amt], 'Lowest_Debit_Amount_Org':[low_deb_amt_org], 'Highest_Credit_Amount_Org':[hi_cr_amt_org]})
  table2['Lowest_Debit_Amount_Source'] = table2['Lowest_Debit_Amount'].apply(lambda x:x.split(' ')[1])
  table2['Highest_Credit_Amount_Source'] = table2['Highest_Credit_Amount'].apply(lambda x:x.split(' ')[1])
  
  number_cheque_bounce = int(df[df['transaction_type'] == 'Bounced']['transaction_type'].count()/2)
  
  min_amt_cheque_bounce = np.nan
  latest_cheque_bounce = np.nan
  df2.sort_values(['date','balance'], ascending=[True,False], inplace=True)
  df2.drop_duplicates(['date'], keep='last', inplace=True)
  df2.reset_index(drop=True, inplace=True)
  days_with_bal_0_neg = df2.loc[df2.balance<=0,:].shape[0]
  entries_0_neg_bal = df.loc[df['balance']<=0].shape[0]


  
  #number_charges_levied = int(df[df['transaction_type'] == 'Bounced']['transaction_type'].count()/2)
  number_charges_levied = np.nan

  table3 = pd.DataFrame({'Num_Chq_Bounce':[number_cheque_bounce], 'Min_Amt_Chq_Bounce':[min_amt_cheque_bounce], 'Latest_Chq_Bounce':[latest_cheque_bounce], 'Entries_Zero_Neg_Bal':[entries_0_neg_bal], 'Num_Charges_Levied':[number_charges_levied], 'Days_with_bal_0_neg':[days_with_bal_0_neg]})
  print('table3 =', table3)
  
  count_deb_txn = df.debit.count()
  
  
  count_cr_txn = df.credit.count()
  table1 = pd.DataFrame({'Num_Credit_Tnx':[count_cr_txn],'Num_Debit_Tnx':[count_deb_txn]})

  df3 = df2.copy()
  df3.drop_duplicates('month_year', keep='last', inplace=True)
  df3.rename(columns={'balance':'Closing Balance', 'month_year':'Month'}, inplace=True)
  df3.sort_values('date', inplace=True)
  df3.drop(columns='date', inplace=True)
  df3.reset_index(drop=True, inplace=True)
  df3['Month'] = pd.to_datetime(df3['Month'], format='%m-%Y')
  df3['Month'] = [i.strftime(format='%b-%y') for i in df3['Month']]
  df3['Closing Balance'] = df3['Closing Balance'].apply(lambda x : round(x))
  # df3['Closing Balance'] = df3['Closing Balance'].apply(lambda x : format_currency(x, 'INR', locale='en_IN'))
  # df3['Closing Balance'] = df3['Closing Balance'].astype('str')
  # df3['Closing Balance'] = df3['Closing Balance'].apply(lambda x : x.split('.')[0])

  #Old code of graph
  #def annotate_plot(frame, plot_col, label_col, **kwargs):
  #  for label, x, y in zip(frame[label_col], frame.index, frame[plot_col]):
  #    plt.annotate(format_currency(label, 'INR', locale='en_IN').split('.')[0], xy=(x, y), **kwargs, weight='bold')

  #plt.figure(figsize=(12,6))
  #plt.plot(df3['Month'],df3['Closing Balance'], color='#ee8a11', marker='o', linewidth=3)
  #annotate_plot(df3, 'Closing Balance', 'Closing Balance')
  #plt.title('Closing Balance Monthly Trend')
  #plt.xlabel('Month-Year', fontsize=14)
  #plt.ylabel('Closing Balance', fontsize=14)
  #plt.grid(True)

  # New code of graph
  plt.switch_backend('Agg')
  def annotate_plot(frame, plot_col, label_col, **kwargs):
    for label, x, y in zip(frame[label_col], frame.index, frame[plot_col]):
      plt.annotate(format_currency(label, 'INR', locale='en_IN').split('.')[0], xy=(x, y), **kwargs, weight='bold')

  plt.figure(figsize=(12, 6))

  # plt.yticks(range(min(df3['Closing Balance']), max(df3['Closing Balance'])+1))
  plt.plot(df3['Month'], df3['Closing Balance'], color='#ee8a11', marker='o', linewidth=3)
  ax = plt.gca()
  ax.set_yticklabels([])
  # ax.get_yaxis().get_major_formatter().set_scientific(False)
  annotate_plot(df3, 'Closing Balance', 'Closing Balance')
  plt.title('Closing Balance Monthly Trend')
  plt.xlabel('Month-Year', fontsize=14)
  plt.ylabel('Closing Balance', fontsize=14)
  plt.grid(True)
  #plt.show()
  plt.savefig(settings.STATICFILES_DIRS[0] + '/assets/images/saved_figure.png')


  debit_cash = df.loc[(df.debit.notnull()) & (df['mode'].str.lower().str.strip()=='cash'),:].shape[0]
  credit_cash = df.loc[(df.credit.notnull()) & (df['mode'].str.lower().str.strip()=='cash'),:].shape[0]
  debit_cheque = df.loc[(df.debit.notnull()) & (df['mode'].str.lower().str.strip()=='cheque'),:].shape[0]
  credit_cheque = df.loc[(df.credit.notnull()) & (df['mode'].str.lower().str.strip()=='cheque'),:].shape[0]
  debit_net = df.loc[(df.debit.notnull()) & (df['mode'].str.lower().str.strip().str.replace(' ', '')=='netbanking'),:].shape[0]
  credit_net = df.loc[(df.credit.notnull()) & (df['mode'].str.lower().str.strip().str.replace(' ', '')=='netbanking'),:].shape[0]

  data = {'debit': [debit_cheque, debit_cash, debit_net],
          'credit': [credit_cheque, credit_cash, credit_net]
          }
  df10 = pd.DataFrame(data,columns=['debit','credit'], index = ['Cheque', 'Cash', 'Net Banking'])
  print(df10)
  df10.plot.barh(figsize=(12,6))
  plt.title('Frequency & Mode of Transactions')
  #plt.show()
  plt.savefig(settings.STATICFILES_DIRS[0] + '/assets/images/saved_figure_1.png')

    

  df['flag2'] = ['Cash' if str(i).lower()=='cash' else 'Non-Cash' for i in df['mode']]
  df['flag1'] = ['Credit' if pd.notna(i) else 'Debit' for i in df['credit']]
  df['value'] = [i if pd.notna(i) else j for i,j in zip(df['debit'], df['credit'])]

  df1 = df.groupby(['flag1', 'flag2'], as_index=False).value.sum()

  fig1 = plt.figure()
  ax = fig1.add_subplot()
  fig1.set_size_inches(16, 5)

  labels = ["%s %s\n{}".format(format_currency(k, 'INR', locale='en_IN').split('.')[0]) % (i,j) for (i,j,k) in zip(df1.flag2, df1.flag1, df1.value)]

  squarify.plot(sizes=df1['value'], label=labels, color=['#1e90ff', '#1e90ff', '#ff6600', '#ff6700'], alpha=.8, bar_kwargs=dict(linewidth=2, edgecolor="#f2f0f0"),text_kwargs={'fontsize':14,'weight':'bold', 'color':'white','wrap':True})
  plt.title('Inflow & Outflow',fontsize=18)
  plt.axis('off')
  #plt.show()
  plt.savefig(settings.STATICFILES_DIRS[0] + '/assets/images/saved_figure_2.png')

  return table,table1,table2,table3,table4