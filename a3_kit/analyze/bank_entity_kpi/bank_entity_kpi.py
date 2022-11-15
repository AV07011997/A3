import pandas as pd
import numpy as np
import datetime

def bek(data):
  
  df=data

  df['debit'] = df['debit'].replace(0, np.nan)
  df['credit'] = df['credit'].replace(0, np.nan)
  df['entity'] = df['entity'].apply(lambda x : x.strip())
  df['txn_date'] = pd.to_datetime(df['txn_date'], format='%Y-%m-%d')
  df['month_year'] = df['txn_date'].dt.month.astype(str)+'-'+df['txn_date'].dt.year.astype(str)
  # df['debit'] = pd.to_numeric(df['debit'].str.replace(',',''),errors='coerce')
  # df['credit'] = pd.to_numeric(df['credit'].str.replace(',',''),errors='coerce')
  # df['balance'] = pd.to_numeric(df['balance'].str.replace(',',''),errors='coerce')

  start = df['txn_date'].min() #transactions_from
  end = df['txn_date'].max() #transactions_till
  tot_entities = df.entity.nunique() #count of entities transacted with

  df2 = df.copy()
  df2['entity'].fillna('Other Transactions', inplace=True)
  a = df2.groupby('entity', as_index=False)

  v1 = a.debit.count().rename(columns={'debit':'debits'}) #count debits
  v2 = a.credit.count().rename(columns={'credit':'credits'}) #count credits
  v3 = a.debit.sum().rename(columns={'debit':'debited_amt_total'}) #total debit (sum)
  v4 = a.credit.sum().rename(columns={'credit':'credited_amt_total'}) #total credit (sum)
  v5 = a.debit.max().rename(columns={'debit':'max_debit'}) #maximum debit
  v6 = a.credit.max().rename(columns={'credit':'max_credit'}) #maximum credit
  v7 = a.debit.min().rename(columns={'debit':'min_debit'}) #minimum debit
  v8 = a.credit.min().rename(columns={'credit':'min_credit'}) #minimum credit
  v9 = a.txn_date.min().rename(columns={'txn_date':'oldest_txn'}) #oldest transaction date
  v10 = a.txn_date.max().rename(columns={'txn_date':'latest_txn'}) #latest transaction date

  b = df2.loc[df.debit.notnull(),:].groupby('entity', as_index=False)
  v11 = b.month_year.nunique().rename(columns={'month_year':'months_with_debit'}) #count of months with debit
  c = df2.loc[df.credit.notnull(),:].groupby('entity', as_index=False)
  v12 = c.month_year.nunique().rename(columns={'month_year':'months_with_credit'}) #count of months with credit

  dfout = v1.merge(v2, on='entity', how='outer').merge(v3, on='entity', how='outer').merge(v4, on='entity', how='outer').merge(v5, on='entity', how='outer').merge(v6, on='entity', how='outer').merge(v7, on='entity', how='outer').merge(v8, on='entity', how='outer').merge(v9, on='entity', how='outer').merge(v10, on='entity', how='outer').merge(v11, on='entity', how='outer').merge(v12, on='entity', how='outer')

  try:
    idxother = dfout[dfout['entity']=='Other Transactions'].index.values.astype(int)[0]
    idx = dfout.index.tolist()
    idx.pop(idxother)
    dfout = dfout.reindex(idx+[idxother])
  except:
    l = pd.Series(np.repeat(np.nan, 13))
    l[0] = 'Other Transactions'
    dfout.loc[len(dfout)] = list(l)

  # m = pd.Series(np.repeat(np.nan, 13))
  # m[0] = 'Overall'
  # for i in [1,2,3,4]:
  #   m[i] = dfout.iloc[:,[i]].sum().iloc[0]
  # for i in [5,6,10]:
  #   m[i] = dfout.iloc[:,[i]].max().iloc[0]
  # for i in [7,8,9]:
  #   m[i] = dfout.iloc[:,[i]].min().iloc[0]
  # m[11] = df2.loc[df2.debit.notnull(),:].month_year.nunique()
  # m[12] = df2.loc[df2.credit.notnull(),:].month_year.nunique()

  # dfout.loc[len(dfout)] = list(m)

  dfout.loc[dfout.months_with_debit.notnull(),'debited_amt_mthly'] = dfout.debited_amt_total/dfout.months_with_debit #debited amount (monthly)
  dfout.loc[dfout.months_with_credit.notnull(),'credited_amt_mthly'] = dfout.credited_amt_total/dfout.months_with_credit #credited amount (monthly)
  
  return dfout