import tabula
from pandas import DataFrame, to_datetime, isna, concat, notna, core, Series
from numpy import nan
from datetime import datetime as dt


# function to concatenate description in  different lines (email statements)
# list of keywords has been used to identify that a particular description is of the row above it or below it
def concat_desc(df):
    no_of_rows = len(df)
    keywords = ['NEF', 'BIL', 'ATM', 'ACH', 'UPI', 'VIN', 'IIN', 'VPS', 'IPS', 'MMT', 'NFS', 'ATD', 'CLG']
    # fill nan
    df['PARTICULARS'] = df['PARTICULARS'].ffill()
    j = 0
    while j < no_of_rows:
        if isna(df['DATE'][j]) and not isna(df['PARTICULARS'][j]):
            if j + 1 < no_of_rows and df['PARTICULARS'][j][:3] in keywords:
                if df['PARTICULARS'][j] not in df['PARTICULARS'][j + 1]:
                    df['PARTICULARS'][j + 1] = str(df['PARTICULARS'][j]) + str(df['PARTICULARS'][j + 1])
            elif j - 1 >= 0:
                df['PARTICULARS'][j - 1] = str(df['PARTICULARS'][j - 1]) + str(df['PARTICULARS'][j])
        j += 1
    df.dropna(subset=['DATE'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# function to align the dataframes into standardized form
def icici_digitization(pdf_path, out_path):
    # extracting file name from pdf_path
    file_name = pdf_path.split('\\')[-1][:-4]
    password = ''
    try:
        # if file is encrypted but with empty password
        decider = tabula.read_pdf(pdf_path, pages=1, password=password, area=[66, 338, 130, 806],
                                  pandas_options={'header': None})
    except:
        # password = input("Enter the Password : ")
        decider = tabula.read_pdf(pdf_path, pages=1, password=password, area=[66, 338, 130, 806],
                                  pandas_options={'header': None})
    if len(decider) == 0 or (decider[0].iloc[0, 0] != "DETAILED STATEMENT" and decider[0].iloc[0, 0] != "ENT"):
        # print("email_statements"+str(i))
        # code for email statements
        # differentiator for current and savings accounts
        decider = tabula.read_pdf(pdf_path, password=password, area=[270.0, 7.0, 586.2, 402], pages='1',
                                  pandas_options={'header': None})
        # return if the file is image based (scanned) pdf
        if len(decider) == 0:
            print("This is an image-based statement, hence, cannot be digitized here")
            return
        # snippet to recognise type of account
        current = False
        savings = False
        xx_format = False
        for i in range(len(decider[0].columns)):
            for j in range(len(decider[0])):
                if type(decider[0].iloc[j][i]) == str and decider[0].iloc[j][i].lower().find(
                        "Statement of Transactions in Savings Account Number:".lower()) != -1:
                    current = False
                    savings = True
                    no = decider[0].iloc[j][i].split(":")[1].split()[0]
                    acct_number = "'{}'".format(no)
                    if "XX" in acct_number:
                        xx_format = True
                    break
                if type(decider[0].iloc[j][i]) == str and decider[0].iloc[j][i].lower().find(
                        "Statement of Transactions in Savings Account".lower()) != -1:
                    current = False
                    savings = True
                    no = decider[0].iloc[j][i].split("Account")[1].split()[0]
                    acct_number = "'{}'".format(no)
                    if "XX" in acct_number:
                        xx_format = True
                    break
                if type(decider[0].iloc[j][i]) == str and decider[0].iloc[j][i].lower().find(
                        "Statement of transactions in Current account number:".lower()) != -1:
                    current = True
                    savings = False
                    no = decider[0].iloc[j][i].split(":")[1].split()[0]
                    acct_number = "'{}'".format(no)
                    break
        if current == True and savings == False:  # case for non-retail
            tables = tabula.read_pdf(pdf_path, password=password, pages='all',
                                     columns=[59.4, 238.1, 278.8, 345.3, 413.4, 466.6, 519.8, 602.0])
            info = tabula.read_pdf(pdf_path, guess=True, lattice=False, password=password,
                                   area=[95.1, 8.7, 179.0, 601.2], pages=1, pandas_options={'header': None})
            col_name = ['Date', 'Particulars', 'Chq.No.', 'Withdrawals', 'Deposits', 'Autosweep', 'Reverse', 'Balance']
            master_table = DataFrame()
            # removing extra columns and concatenating particulars spitted into different columns
            for i in range(1, len(tables)):
                if len(tables[i].columns) > 8:
                    tables[i].dropna(axis=1, how='all', inplace=True)
                if len(tables[i].columns) > 8:
                    col_date = tables[i].columns.get_loc('Date')
                    col_chq = tables[i].columns.get_loc('Chq.No.')
                    key_p = tables[i].columns[col_date + 1]
                    tables[i][key_p] = tables[i][key_p].apply(lambda x: str(x) if not isna(x) else "")
                    if col_chq - col_date != 2:
                        for j in range(col_date + 2, col_chq):
                            key_extra = tables[i].columns[j]
                            tables[i][key_extra] = tables[i][key_extra].apply(lambda x: x if not isna(x) else "")
                            tables[i][key_p] += tables[i][key_extra]
                            tables[i].drop([key_extra], inplace=True, axis=1)
                if len(tables[i].columns) == 8:
                    tables[i].columns = col_name
                elif i != 0:
                    print("check for tables[" + str(i) + "]")
            # removing unnecssary rows from end and concatenating into master_table
            for i in range(1, len(tables)):
                tables[i] = tables[i][['Date', 'Particulars', 'Withdrawals', 'Deposits', 'Balance']]
                for col in (tables[i].columns):
                    if tables[i][tables[i][col] == "Page Total:"].any()['Particulars']:
                        row = tables[i].index[tables[i][col] == "Page Total:"][0]
                        tables[i] = tables[i][:row]
                        break
                master_table = concat([master_table, tables[i]])
            master_table.reset_index(drop=True, inplace=True)
            # removing b\f
            if master_table[master_table['Particulars'] == "B/F"].any()['Particulars']:
                row = master_table.index[master_table[col] == "B/F"][0]
                master_table = master_table[row + 1:]
                master_table.reset_index(drop=True, inplace=True)
            # concatenating particulars split up into different rows
            for j in range(1, len(master_table)):
                if isna(master_table['Date'][j]):
                    master_table['Particulars'][j - 1] += master_table['Particulars'][j]
            master_table.dropna(subset=['Date'], inplace=True)
            master_table.reset_index(drop=True, inplace=True)
            # extracting account holder name; number is extracted along current and savings decider
            for i in range(len(info)):
                for j in range(len(info[i])):
                    for k in range(len(info[i].columns)):
                        if type(info[i].iloc[j, k]) == str and "Your Details With Us:" in info[i].iloc[j, k]:
                            name = info[i].iloc[j + 1, k]
                            break
            master_table2 = master_table
            master_table2['Balance'] = master_table['Balance'].apply(
                lambda x: x[:-3] if x[-2:] == "Cr" else ("-" + x[:-3]))
            master_table2.rename(columns={'Date': 'Txn Date', 'Withdrawals': 'Debit', 'Deposits': 'Credit',
                                          'Particulars': 'Description'}, inplace=True)
            master_table2 = master_table
            # standardising dataframe according to standard schema
            master_table2['Account Name'] = name
            master_table2['Account Number'] = acct_number
            master_table2 = master_table2[
                ['Txn Date', 'Description', 'Debit', 'Credit', 'Balance', 'Account Name', 'Account Number']]
            master_table2['Txn Date'] = [dt.strftime(to_datetime(x, dayfirst=True), "%d-%m-%Y") for x in
                                         master_table2['Txn Date']]
            last_trans_date = master_table2['Txn Date'].iat[-1]
            # master_table2.to_csv(r"{}\{}_{}_{}.csv".format(out_path,file_name, acct_number, last_trans_date),index=False)

        elif xx_format == True:
            tables1 = tabula.read_pdf(pdf_path, guess=True, lattice=False, password=password, area=[100, 30, 900, 600],
                                      pages='all', columns=[70, 130, 430, 350, 520])
            info1 = tabula.read_pdf(pdf_path, guess=True, lattice=False, password=password, area=[0, 0, 900, 600],
                                    pages='1', columns=[200, 200, 430, 350, 520])
            # extracting account information (name/number)
            for i in range(len(info1)):
                for j in range(len(info1[i])):
                    for k in range(len(info1[i].columns)):
                        if type(info1[i].iloc[j, k]) == str:
                            if info1[i].iloc[j, k].startswith('MR.') or info1[i].iloc[j, k].startswith('MRS.') or \
                                    info1[i].iloc[j, k].startswith('MS.'):
                                name = info1[i].iloc[j, k]
            for i in range(len(tables1)):
                tables1[i].columns = ['DATE', 'MODE**', 'PARTICULARS', 'DEPOSITS', 'WITHDRAWALS', 'BALANCE']
                len_bf = len(tables1[i])
                for j in range(len(tables1[i]['DATE'])):
                    if tables1[i]['DATE'][j] == 'DATE':
                        tables1[i] = tables1[i].iloc[j:]
                        tables1[i] = tables1[i].reset_index(drop=True)
                        break

            for i in range(len(tables1)):
                for j in range(len(tables1[i])):
                    if tables1[i]['PARTICULARS'][j] == 'Total:':
                        tables1[i] = tables1[i].iloc[:j]
                        break
                len_af = len(tables1[i])
                tables1[i] = tables1[i].iloc[1:]
                tables1[i] = tables1[i].reset_index(drop=True)
                if len_bf == len_af:
                    tables1.pop(i)
            master_table2 = DataFrame()
            for i in range(len(tables1)):
                tables1[i] = tables1[i][tables1[i]['PARTICULARS'] != "B/F"]
                tables1[i].reset_index(drop=True, inplace=True)
                tables1[i] = concat_desc(tables1[i])
                master_table2 = concat([master_table2, tables1[i]])
            # standardising dataframe according to standard schema
            master_table2 = master_table2[['DATE', 'PARTICULARS', 'DEPOSITS', 'WITHDRAWALS', 'BALANCE']]
            master_table2.rename(
                {'DATE': 'Txn Date', 'PARTICULARS': 'Description', 'DEPOSITS': 'Credit', 'WITHDRAWALS': 'Debit',
                 'BALANCE': 'Balance'}, inplace=True, axis=1)
            master_table2['Account Name'] = name
            master_table2['Account Number'] = acct_number
            master_table2 = master_table2[
                ['Txn Date', 'Description', 'Debit', 'Credit', 'Balance', 'Account Name', 'Account Number']]
            master_table2['Txn Date'] = [dt.strftime(to_datetime(x, dayfirst=True), "%d-%m-%Y") for x in
                                         master_table2['Txn Date']]
            last_trans_date = master_table2['Txn Date'].iat[-1]
            # master_table2.to_csv(r"{}\{}_{}_{}.csv".format(out_path,file_name, acct_number, last_trans_date),index=False)


        else:
            # savings=True
            # format 2; account number all digits
            tables = tabula.read_pdf(pdf_path, password=password, pages='all', area=[140.0, 14.5, 824.7, 593.2],
                                     columns=[72.8, 155.9, 350.3, 428.9, 506.7, 585.3])
            info_name = tabula.read_pdf(pdf_path, password=password, area=[153.2, 17.2, 250.4, 589.7], pages='1',
                                        pandas_options={'header': None})
            # extracting account name and number
            for i in range(len(info_name[0])):
                ele = info_name[0].iloc[i, 0]
                if type(ele) == str and (
                        ele.startswith("MR.") or ele.startswith("MRS.") or ele.startswith("MS.") or ele.startswith(
                        "M/S") or ele.startswith("Master")):
                    name = ele
                    break
            col_names = ['DATE', 'MODE**', 'PARTICULARS', 'DEPOSITS', 'WITHDRAWALS', 'BALANCE']
            # poping out last dataframe containing extra infrmation
            if not "DATE" in tables[-1].columns:
                tables.pop()
            # removing information part from tables[0]
            key0 = tables[0].columns[0]
            if tables[0][tables[0][key0] == "DATE"].any()[key0]:
                row = tables[0].index[tables[0][key0] == "DATE"][0]
                tables[0] = tables[0][row - 1:]
                tables[0].reset_index(drop=True, inplace=True)
                if len(tables[0].columns == 6):
                    tables[0].columns = col_names
                else:
                    print("handle extra column in tables[0]")
            # super dataframe which contains rows for all statements present in single file
            super_df = DataFrame()
            for i in range(len(tables)):
                super_df = concat([super_df, tables[i]])
            super_df.reset_index(drop=True, inplace=True)
            # splitters contains all the start index of all statements present
            splitters = super_df.index[super_df['DATE'] == "Statement o"]
            for i in range(len(splitters)):
                if i == len(splitters) - 1:
                    df = super_df[splitters[i]:]
                else:
                    df = super_df[splitters[i]:splitters[i + 1]]
                df.reset_index(drop=True, inplace=True)
                # extract the account number
                acct_number_string = df['PARTICULARS'][0].split(":")[1]
                acct_number = "'{}'".format(acct_number_string.split()[0])
                # drop extra rows:- first 3 lines (statement, date , "B\F") and after total
                df = df[3:]
                df.reset_index(drop=True, inplace=True)
                if df[df['PARTICULARS'] == "OTAL"].any()['PARTICULARS']:
                    row = df.index[df['PARTICULARS'] == "OTAL"][0]
                    df = df[:row]
                if df[df['PARTICULARS'] == "TOTAL"].any()['PARTICULARS']:
                    row = df.index[df['PARTICULARS'] == "TOTAL"][0]
                    df = df[:row]
                df.reset_index(drop=True, inplace=True)
                # concat desc
                df = concat_desc(df)
                # drop extra columns and add account  name and number
                df = df[['DATE', 'PARTICULARS', 'DEPOSITS', 'WITHDRAWALS', 'BALANCE']]
                df.rename(
                    {'DATE': 'Txn Date', 'PARTICULARS': 'Description', 'DEPOSITS': 'Credit', 'WITHDRAWALS': 'Debit',
                     'BALANCE': 'Balance'}, inplace=True, axis=1)
                df['Account Name'] = name
                df['Account Number'] = acct_number
                df['Txn Date'] = [dt.strftime(to_datetime(x, dayfirst=True), "%d-%m-%Y") for x in df['Txn Date']]
                last_trans_date = df['Txn Date'].iat[-1]
                # df.to_csv(r"{}\{}_{}_{}.csv".format(out_path,file_name, acct_number, last_trans_date),index=False)

    else:
        # print("net_banking"+str(i))
        tables2 = tabula.read_pdf(pdf_path, pages=1, password=password)
        if len(tables2) == 0:
            print("This is an image-based statement, hence, cannot be digitized here.")
            return
        if "No." in tables2[0].columns:
            # non retails
            tables = tabula.read_pdf(pdf_path, pages='all', stream=True, password=password,
                                     pandas_options=({'header': None}))
            cust_info = tabula.read_pdf(pdf_path, pages=1, stream=True, password=password, area=[171, 0, 221.4, 907.2],
                                        pandas_options=({'header': None}))
            col_names = ["No.", "Txn Id", "Value Date", "Txn Date", "Chq no", "Description", "Cr/Dr", "Amount",
                         "Balance"]
            master_table = DataFrame(columns=col_names)
            row = 0
            for i in range(len(tables)):
                # checking if description is split into multiple columns and merging
                if len(tables[i].columns) == 10:
                    for j in range(len(tables[i])):
                        if not isna(tables[i][tables[i].columns[5]][j]) and not isna(
                                tables[i][tables[i].columns[6]][j]):
                            tables[i][tables[i].columns[5]] = str(tables[i][tables[i].columns[5]][j]) + str(
                                tables[i][tables[i].columns[6]][j])
                    tables[i].drop(tables[i].columns[6], inplace=True, axis=1)
                # renaming columns to avoid non printable chars in column names
                tables[i].columns = col_names
                # concatenating description splited into multiple rows
                for j in range(len(tables[i])):
                    if not isna(tables[i]['No.'][j]) and tables[i]['No.'][j] != "No.":
                        if j > 0 and not isna(tables[i]['Description'][j - 1]) and isna(
                                tables[i]['Txn Date'][j - 1]) and str(tables[i]['Description'][j]) != str(
                                tables[i]['Description'][j - 1]):
                            if isna(tables[i]['Description'][j]):
                                tables[i]['Description'][j] = str(tables[i]['Description'][j - 1])
                            else:
                                tables[i]['Description'][j] = str(tables[i]['Description'][j - 1]) + str(
                                    tables[i]['Description'][j])
                        if j + 1 < len(tables[i]) and not isna(tables[i]['Description'][j + 1]) and isna(
                                tables[i]['Txn Date'][j + 1]) and str(tables[i]['Description'][j]) != str(
                                tables[i]['Description'][j + 1]):
                            if isna(tables[i]['Description'][j]):
                                tables[i]['Description'][j] = str(tables[i]['Description'][j + 1])
                            else:
                                tables[i]['Description'][j] = str(tables[i]['Description'][j]) + str(
                                    tables[i]['Description'][j + 1])
                        master_table.loc[row] = tables[i].loc[j]
                        row += 1
                # spliting amount column into debit and credit resp
                master_table['Debit'] = master_table.loc[master_table['Cr/Dr'] == "DR", 'Amount']
                master_table['Credit'] = master_table.loc[master_table['Cr/Dr'] == "CR", 'Amount']
            # dropping off uneccesary column and extracting account info
            master_table = master_table[["Txn Date", "Description", "Debit", "Credit", "Balance"]]
            info_string = cust_info[0].iloc[0, 1]
            account_name = info_string.split("-")[1][:-7].strip()
            account_no = "'{}'".format(info_string.split("-")[2].strip())

        elif "Sr No" in tables2[0].columns:
            # new format of 2020
            tables = tabula.read_pdf(pdf_path, lattice=True, pages='all', password=password,
                                     pandas_options={'header': None})
            cust_info = tabula.read_pdf(pdf_path, pages=1, stream=True, area=[73.7, 13.7, 250.4, 566.7],
                                        password=password, pandas_options=({'header': None}))
            # removing headers from 0th df
            tables[0] = tables[0].drop(tables[0].index[0])
            tables[0].reset_index(drop=True, inplace=True)
            master_table = DataFrame()
            # renaming columns and concatenating to master_table
            for i in range(len(tables)):
                tables[i].rename({0: "Sr. No.", 1: "Value Date", 2: "Txn Date",
                                  3: "ChequeNumber", 4: "Description", 5: "Debit", 6: "Credit", 7: "Balance"}, axis=1,
                                 inplace=True)
                tables[i].drop(tables[i].columns[[0, 1, 3]], axis=1, inplace=True)
                master_table = concat([master_table, tables[i]])
            # spliting amount column into debit and credit resp
            master_table.reset_index(drop=True, inplace=True)
            master_table['Debit'] = master_table['Debit'].replace('NA', nan)
            master_table['Credit'] = master_table['Credit'].replace('NA', nan)
            # extracting account information
            for i in range(len(cust_info[0])):
                ele = cust_info[0].iloc[i, 0]
                if type(ele) == str and (ele.startswith("Account Name:")):
                    account_name = ele.split(':', 1)[-1]
                    break
                account_no = "'{}'".format(cust_info[0].iloc[0, 0].split()[-1])
            # changing new date format
            master_table['Txn Date'] = [(i[:7] + i[10:]) for i in master_table['Txn Date']]
            master_table['Txn Date'] = [dt.strftime(to_datetime(x, dayfirst=True), "%d-%m-%Y") for x in
                                        master_table['Txn Date']]
            last_trans_date = master_table['Txn Date'].iloc[-1]

        else:
            # retails old formats
            tables = tabula.read_pdf(pdf_path, pages='all', stream=True, password=password)
            tables2 = tabula.read_pdf(pdf_path, pages='all', lattice=True, password=password)
            cust_info = tabula.read_pdf(pdf_path, pages=1, password=password, stream=True,
                                        area=[134.5, 28.2, 371.8, 983.1], pandas_options={'header': None})
            # to extract balance correctly with decimal points and then adding back to original tables
            for i in range(len(tables2)):
                tables2[i].dropna(subset=[tables2[i].columns[1]], inplace=True)
                tables2[i].reset_index(drop=True, inplace=True)
            temp_bal = Series(dtype=float)
            for i in range(len(tables2)):
                temp_bal = temp_bal.append(tables2[i][tables2[i].columns[-1]])
            temp_bal = temp_bal.reset_index()
            for i in range(len(tables)):
                tables[i].dropna(axis=0, how='all', inplace=True)
            # setting the header as standard wherever first row of table is taken as header by tabula
            for i in range(len(tables)):
                tables[i] = tables[i].append(Series([nan]), ignore_index=True)
                tables[i] = tables[i].shift(1, axis=0)
                tables[i].iloc[0] = tables[i].columns
                if tables[i].columns[-1] == 0:
                    del tables[i][0]
            # dropping extra columns
            for i in range(len(tables)):
                if len(tables[i].columns) > 8:
                    for j in range(len(tables[i])):
                        for k in range(1, (len(tables[i].columns) - 7)):
                            tables[i].iloc[j, 4] = tables[i].iloc[j, 4] + tables[i].iloc[j, 4 + k]
                            del tables[i][tables[i].columns[4 + k]]
                        if len(tables[i].columns) > 8:
                            tables[i].dropna(axis=1, how='all')
                        break
            # setting the header as standard wherever first row of table is taken as header by tabula
            for i in range(len(tables)):
                tables[i].columns = ['S No.', 'Value Date', 'Txn Date', 'Cheque Number', 'Description', 'Debit',
                                     'Credit', 'Balance']
            # appending all tables of a pdf
            master_table = tables[0]
            for i in range(len(tables) - 1):
                master_table = concat([master_table, tables[i + 1]])
            master_table = master_table[master_table['Description'] != 'Unnamed: 4']
            master_table = master_table[master_table['S No.'] != 'S No.']
            master_table = master_table.dropna(subset=['Description'])
            master_table = master_table.replace(nan, '')
            master_table.reset_index(drop=True, inplace=True)
            master_table['Description'] = list(map(str, master_table['Description']))
            # merging description
            for i in reversed(range(len(master_table))):
                if master_table['Value Date'][i] == '':
                    master_table['Description'][i - 1] = master_table['Description'][i - 1] + \
                                                         master_table['Description'][i]
                else:
                    continue
            # removing blank
            for i in range(len(master_table)):
                master_table = master_table.replace('', nan)
                master_table.dropna(subset=['Value Date'], inplace=True)
            master_table.reset_index(drop=True, inplace=True)
            # correcting date where .1 is there
            for i in range(len(master_table)):
                if len(master_table['Txn Date'][i]) > 10:
                    master_table['Txn Date'][i] = master_table['Txn Date'][i][0:10]
                else:
                    continue
            # we have to resolve the issue where Debit/Credit/Balance column have 2 decimals
            col1 = master_table.columns.get_loc('Debit')
            for i in range(len(master_table)):
                for j in range(col1, len(master_table.columns)):
                    if master_table.iloc[i, j].count('.') > 1:
                        master_table.iloc[i, j] = master_table.iloc[i, j][:-2]
            for i in range(len(master_table)):
                master_table['Balance'][i] = temp_bal[0][i + 1]
            del master_table['S No.']
            for i in range(len(cust_info[0])):
                for j in range(len(cust_info[0].columns)):
                    if type(cust_info[0].iloc[i, j]) == str and cust_info[0].iloc[i, j].find("Account Number") != -1:
                        info_string = cust_info[0].iloc[i, j].split('-', 2)
                        account_name = info_string[-1].strip()
                        account_no = "'{}'".format(info_string[0].split()[-1][:-5])
                        break
        ## adding the common parts
        master_table['Account Name'] = account_name
        master_table['Account Number'] = account_no

        master_table2 = master_table.reset_index(drop=True)
        master_table2['Txn Date'] = [dt.strftime(to_datetime(x, dayfirst=True), "%d/%m/%Y") for x in
                                     master_table2['Txn Date']]
        master_table2 = master_table2[
            ['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name',
             'Account Number']]
        last_trans_date = master_table2['Txn Date'].iat[-1]

        # exporting the master table to a csv - this is final having complete transactions table appended and essential account information
        # master_table2.to_csv("{}\\{}_{}_{}.csv".format(out_path,file_name,account_no, last_trans_date),index=False)

        ## NOW PERFORMING FEW LOGICAL CHECKS TO CHECK DIGITIZATION HAS NO ISSUE

        df = DataFrame(master_table2)
        column_names = ['Statement_name', 'Wrong Credit', 'Wrong Debit', 'Remark']
        result = DataFrame(index=[1], columns=column_names)

        if df['Credit'].dtype == 'O':
            df['Credit_changed'] = (df['Credit'].str.replace(',', '')).astype(float)
        else:
            df['Credit_changed'] = df['Credit'].astype(float)
        if df['Debit'].dtype == 'O':
            df['Debit_changed'] = (df['Debit'].str.replace(',', '')).astype(float)
        else:
            df['Debit_changed'] = df['Debit'].astype(float)
        if df['Balance'].dtype == 'O':
            df['Balance_changed'] = (df['Balance'].str.replace(',', '')).astype(float)
        else:
            df['Balance_changed'] = df['Balance'].astype(float)

        df['Balance_changed'] = df['Balance_changed'].replace(0, nan)
        df['Debit_changed'] = df['Debit_changed'].replace(0, nan)
        df['Credit_changed'] = df['Credit_changed'].replace(0, nan)

        col_credit = df.columns.get_loc('Credit_changed')
        col_debit = df.columns.get_loc('Debit_changed')
        col_bal = df.columns.get_loc('Balance_changed')
        col_desc = df.columns.get_loc('Description')

        for i in range(1, len(df)):
            # check 1 having, both debit and credit values
            if (isna(df.iloc[i, col_debit]) and isna(df.iloc[i, col_credit])) or (
                    notna(df.iloc[i, col_debit]) and notna(df.iloc[i, col_credit])):
                data = DataFrame({'Statement_name': file_name, 'Wrong Credit': (i + 2), 'Wrong Debit': (i + 2),
                                  'Remark': 'Only one of Debit/Credit should be filled'}, index=[0])
                result = concat([result, data])

                # check 2, balance check
            else:
                # debited
                if isna(df.iloc[i, col_credit]):
                    if df.iloc[i, col_debit] > 0:
                        if df.iloc[i - 1, col_bal] < df.iloc[i, col_bal]:
                            data = DataFrame({'Statement_name': file_name, 'Wrong Credit': nan, 'Wrong Debit': (i + 2),
                                              'Remark': 'Balance should be less than previous since debit>0'},
                                             index=[0])
                            result = concat([result, data])
                    else:
                        if df.iloc[i - 1, col_bal] > df.iloc[i, col_bal]:
                            data = DataFrame({'Statement_name': file_name, 'Wrong Credit': nan, 'Wrong Debit': (i + 2),
                                              'Remark': 'Balance should be more than previous since debit<0'},
                                             index=[0])
                            result = concat([result, data])


                # credited
                elif isna(df.iloc[i, col_debit]):
                    if df.iloc[i, col_credit] > 0:
                        if df.iloc[i - 1, col_bal] > df.iloc[i, col_bal]:
                            data = DataFrame([{'Statement_name': file_name, 'Wrong Credit': (i + 2), 'Wrong Debit': nan,
                                               'Remark': 'Balance should be more than previous since credit>0'}],
                                             index=[0])
                            result = concat([result, data])
                    else:
                        if df.iloc[i - 1, col_bal] < df.iloc[i, col_bal]:
                            data = DataFrame([{'Statement_name': file_name, 'Wrong Credit': (i + 2), 'Wrong Debit': nan,
                                               'Remark': 'Balance should be less than previous since credit<0'}],
                                             index=[0])
                            result = concat([result, data])

        result = result.dropna(how='all')

        # will continue only if 'result' is an empty dataframe
        if len(result) == 0:
            pass
        else:
            print(
                "\nThere are issues found after the Logical checks.\nThe digtitized output and the issues have been exported in CSVs.\n")
            return

        # NOW THE ENTITY EXTRACTION PART

        icici = DataFrame(master_table2)
        icici["Description"] = icici["Description"].str.lstrip()

        # Converting list to string
        def listToString(s):
            str1 = " "
            return (str1.join(s))

        try:
            df1 = icici[icici["Description"].str.startswith("IMPS")]
            df1['new'] = df1['Description'].str.split("-")
            df1["sub_mode"] = df1['new'].apply(lambda x: x[0])
            df1['source_of_trans'] = 'Self Initiated'
            # df1['entity_bank'] = df1['new'].apply(lambda x:x[3])
            # df1['entity_bank'] = df1['entity_bank'].apply(lambda x: 'icici' if x == 'icici' else 'Others')
            df1['mode'] = 'Net Banking'
            df1['entity'] = df1['new'].apply(lambda x: x[2])
            df1.drop(["new"], axis=1, inplace=True)

        except:
            pass

        # subsetting .IMPS
        try:
            df2 = icici[icici["Description"].str.startswith(".IMPS")]
            df2[['sub_mode', 'p2p', 'trans_id', 'MIR']] = df2.Description.str.split(" ", expand=True)
            df2['source_of_trans'] = 'Automated'
            df2['entity'] = 'NA'
            df2['mode'] = 'Charges'
            # df2['entity_bank']='NA'
            df2.drop(['trans_id', "p2p", "MIR"], axis=1, inplace=True)
        except:
            pass

        # subsetting UPI

        try:
            df3 = icici[icici["Description"].str.startswith("UPI")]
            df3['new'] = df3['Description'].str.split("-")
            df3['sub_mode'] = df3['new'].apply(lambda x: x[0])
            df3['entity'] = df3['new'].apply(lambda x: x[2])
            df3['source_of_trans'] = 'Self Initiated'
            df3['mode'] = 'Mobile App'
            # df3['entity_bank']=df3['entity'].str[:4]
            df3.drop('new', axis=1, inplace=True)
        except:
            pass

        # subsetting ATW
        try:
            df4 = icici[icici["Description"].str.startswith("ATW")]

            df4["sub_mode"] = "Cash Withdrawal"
            df4['new'] = df4['Description'].str.split("-")
            df4['source_of_trans'] = 'Self Initiated'
            df4['mode'] = 'Cash'
            # df4['entity_bank']='NA'
            df4['entity'] = 'NA'

            df4.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # subsetting 41005995TERMINAL
        try:
            df5 = icici[icici["Description"].str.contains(pat="TERMINAL 1 CARDS SETTL.")]
            df5['new'] = df5['Description'].str.split(" ")
            df5['x1'] = df5['new'].apply(lambda x: x[0] + ' ' + x[1])
            df5['sub_mode'] = df5['new'].apply(lambda x: x[2] + ' ' + x[3])
            df5['date'] = df5['new'].apply(lambda x: x[4])

            df5['source_of_trans'] = 'Automated'
            df5['mode'] = 'Card'
            # df5['entity_bank']='NA'
            df5['entity'] = 'NA'
            df5.drop(['x1', "date", "new"], axis=1, inplace=True)
        except:
            pass

        # subsetting ACH

        try:
            df6 = icici[icici["Description"].str.startswith("ACH")]
            df6['new'] = df6['Description'].str.split("-")
            df6['count'] = df6['new'].apply(lambda x: len(x))
        except:
            pass

        try:
            df6a = df6[df6['count'] != 1]
            df6a['sub_mode'] = df6a['new'].apply(lambda x: x[0])
            df6a['entity'] = df6a['new'].apply(lambda x: x[1])
            df6a['source_of_trans'] = 'Automated'
            df6a['mode'] = 'Loan'
            # df6a['entity_bank']='NA'
            df6a.drop(['new', 'count'], axis=1, inplace=True)
        except:
            pass

        try:
            df6b = df6[df6['count'] == 1]
            df6b['sub_mode'] = df6b['new'].apply(lambda x: x[0])
            df6b['entity'] = 'NA'
            df6b['source_of_trans'] = 'Automated'
            df6b['mode'] = 'Loan'
            # df6b['entity_bank']='NA'
            df6b.drop(['new', 'count'], axis=1, inplace=True)
        except:
            pass

        # subsetting AMB CHRG INCL GST
        try:
            df7 = icici[icici["Description"].str.startswith("AMB")]
            df7['new'] = df7['Description'].str.split(" ")
            df7['sub_mode'] = df7['new'].apply(lambda x: x[0] + ' ' + x[1] + ' ' + x[2] + ' ' + x[3])
            df7['source_of_trans'] = 'Automated'
            df7['mode'] = 'Charges'
            # df7['entity_bank']='NA'
            df7['entity'] = 'NA'
            df7.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # subsetting Cheque return

        try:
            df8 = icici[icici["Description"].str.startswith("CHQ DEP RET-")]
            df8['new'] = df8['Description'].str.split("-")
            df8['sub_mode'] = df8['new'].apply(lambda x: x[0])
            df8['source_of_trans'] = 'Automated'
            df8['mode'] = 'Cheque'
            # df8['entity_bank']='NA'
            df8['entity'] = 'NA'
            df8.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # subsetting Cheque return 2.0

        try:
            df50 = icici[icici["Description"].str.startswith("CHQ DEP RET")]
            df50 = df50[~df50["Description"].str.startswith("CHQ DEP RET-")]
            df50['new'] = df50['Description'].str.split("CHGS")
            df50['sub_mode'] = df50['new'].apply(lambda x: x[0])
            df50['source_of_trans'] = 'Automated'
            df50['mode'] = 'Cheque'
            # df50['entity_bank']='NA'
            df50['entity'] = 'NA'
            df50.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # subsetting Cheque paid
        try:
            df9 = icici[icici["Description"].str.startswith("CHQ PAID")]
            df9['new'] = df9['Description'].str.split("-")
            df9['sub_mode'] = df9['new'].apply(lambda x: x[0])
            df9['entity'] = df9['new'].apply(lambda x: x[-1])
            df9['source_of_trans'] = 'Automated'
            df9['mode'] = 'Cheque'
            # df9['entity_bank']='NA'
            df9.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # subsetting debit card fee
        try:
            df10 = icici[icici["Description"].str.startswith("DEBIT CARD ANNUAL")]
            df10['sub_mode'] = 'DEBIT CARD ANNUAL FEE'
            df10['source_of_trans'] = 'Automated'
            df10['mode'] = 'Charges'
            # df10['entity_bank']='NA'
            df10['entity'] = 'NA'
        except:
            pass

        # ATM Cash Fee
        try:
            df11 = icici[icici["Description"].str.startswith("FEE")]
            df11['sub_mode'] = 'ATM CASH FEE'
            df11['source_of_trans'] = 'Automated'
            df11['mode'] = 'Charges'
            # df11['entity_bank']='NA'
            df11['entity'] = 'NA'
        except:
            pass

        try:
            df12 = icici[icici["Description"].str.startswith("DEPOSITORY CHARGES")]
            df12['sub_mode'] = 'DEPOSITORY CHARGES'
            df12['source_of_trans'] = 'Automated'
            df12['mode'] = 'Charges'
            # df12['entity_bank']='NA'
            df12['entity'] = 'NA'
        except:
            pass

        try:
            df13 = icici[icici["Description"].str.startswith(".ACH")]
            df13['sub_mode'] = 'ACH DEBIT RETURN CHARGES'
            df13['source_of_trans'] = 'Automated'
            df13['mode'] = 'Charges'
            # df13['entity_bank']='NA'
            df13['entity'] = 'NA'
        except:
            pass

        try:
            df14 = icici[icici["Description"].str.startswith(".ECS")]
            df14['sub_mode'] = 'ECS DEBIT RETURN CHARGES'
            df14['source_of_trans'] = 'Automated'
            df14['mode'] = 'Charges'
            # df14['entity_bank']='NA'
            df14['entity'] = 'NA'

        except:
            pass

        # subsetting CHEQUE DEP
        try:
            df15 = icici[icici["Description"].str.startswith("CHQ DEP")]
            df15 = df15[~df15["Description"].str.startswith("CHQ DEP RET")]
            df15 = df15[~df15["Description"].str.startswith("CHQ DEP - REV")]
            df15['new'] = df15.Description.str.split("-")
            df15['sub_mode'] = df15['new'].apply(lambda x: x[0])
            df15['source_of_trans'] = 'Self Initiated'
            df15['mode'] = 'Cheque'
            # df15['entity_bank']='NA'
            df15['entity'] = df15['new'].apply(lambda x: x[0])
            df15.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # Credit Interest Capitalised
        try:

            df16 = icici[icici["Description"].str.startswith("CREDIT INTEREST CAPITALISED")]
            df16['sub_mode'] = 'CREDIT INTEREST CAPITALISED'
            df16['source_of_trans'] = 'Automated'
            df16['mode'] = 'Interest'
            # df16['entity_bank']='NA'
            df16['entity'] = 'NA'
        except:
            pass

        # Cash Dep
        try:
            df17 = icici[icici["Description"].str.startswith("CASH DEP")]
            df17 = df17[~df17["Description"].str.startswith("CASH DEPOSIT")]
            df17['new'] = df17.Description.str.split(" ")
            df17['sub_mode'] = df17['new'].apply(lambda x: x[0] + " " + x[1])
            df17['source_of_trans'] = 'Self Initiated'
            df17['mode'] = 'Cash'
            # df17['entity_bank']='NA'
            df17['entity'] = df17['new'].apply(lambda x: x[2:])
            df17['entity'] = df17["entity"].str.join(" ")
            df17.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # cASH DEPOSIT
        try:
            df17a = icici[icici["Description"].str.startswith("CASH DEPOSIT")]
            df17a['new'] = df17a.Description.str.split("-")
            df17a['sub_mode'] = df17a['new'].apply(lambda x: x[0])
            df17a['source_of_trans'] = 'Self Initiated'
            df17a['mode'] = 'Cash'
            # df17a['entity_bank']='NA'
            df17a['entity'] = df17a['new'].apply(lambda x: x[-1])
            df17a.drop(['new'], axis=1, inplace=True)
        except:
            pass

            # I/W Cheque Return

        try:
            df18 = icici[icici["Description"].str.startswith("I/W")]
            df18['new'] = df18['Description'].str.split("-")
            df18['source_of_trans'] = 'Automated'
            df18['sub_mode'] = 'Cheque Return'
            df18['mode'] = 'Cheque Bounce'
            # df18['entity_bank']='NA'
            df18['entity'] = 'NA'
            df18.drop(['new'], axis=1, inplace=True)

        except:
            pass

        # fund Transfer
        try:
            df19 = icici[icici["Description"].str.startswith("FT")]
            df19["new"] = df19['Description'].str.split("-")

            df19["sub_mode"] = "NA"
            df19['source_of_trans'] = 'Self Initiated'
            df19["entity"] = df19['new'].apply(lambda x: x[3])
            df19['mode'] = 'Fund Transfer'
            # df19['entity_bank']='NA'
            df19.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # NEFT
        try:
            df20 = icici[icici["Description"].str.startswith("NEFT")]
            df20 = df20[~df20["Description"].str.startswith("NEFT CHGS")]
            df20['new'] = df20["Description"].str.split("-")
            df20['sub_mode'] = df20['new'].apply(lambda x: x[0])
            df20['entity'] = df20['new'].apply(lambda x: x[2])
            df20['ifsc'] = df20['new'].apply(lambda x: x[1]).str[:4]
            df20['source_of_trans'] = 'Self Initiated'
            df20['mode'] = 'Net Banking'
            # df20['entity_bank'] = df20['ifsc'].apply(lambda x: 'icici' if x == 'icici' else 'Others')
            df20.drop(['new'], axis=1, inplace=True)
            df20.drop(['ifsc'], axis=1, inplace=True)
        except:
            pass

        # NEFT CHGS
        try:
            df20a = icici[icici["Description"].str.startswith("NEFT CHGS")]
            df20a['new'] = df20a["Description"].str.split(" ")
            df20a['sub_mode'] = df20a['new'].apply(lambda x: x[0:2]).str.join(" ")
            df20a['source_of_trans'] = 'Automated'
            df20a['mode'] = 'Charges'
            # df20a['entity_bank']='NA'
            df20a['entity'] = 'NA'
            df20a.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # NWD (icici)
        try:
            df21 = icici[icici["Description"].str.startswith("NWD")]
            df21['sub_mode'] = 'NWD (icici)'
            df21['source_of_trans'] = 'Self Initiated'
            df21['mode'] = 'Cash'
            # df21['entity_bank']='NA'
            df21['entity'] = 'NA'
        except:
            pass

        # EAW

        try:
            df22 = icici[icici["Description"].str.startswith("EAW")]
            df22['sub_mode'] = 'EAW'
            df22['source_of_trans'] = 'Self Initiated'
            df22['mode'] = 'Cash'
            # df22['entity_bank']='NA'
            df22['entity'] = 'NA'
        except:
            pass

        # ECS
        try:
            df23 = icici[icici["Description"].str.startswith("ECS")]
            df23['new'] = df23.Description.str.split("-")
            df23['sub_mode'] = 'ECS'
            df23['source_of_trans'] = 'Automated'
            df23['mode'] = 'Loan'
            # df23['entity_bank']='NA'
            df23['entity'] = df23['new'].apply(lambda x: x[1])
            df23.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # EMI
        try:
            df24 = icici[icici["Description"].str.startswith("EMI")]
            df24['new'] = df24.Description.str.split(" ")
            df24['sub_mode'] = 'EMI'
            df24['source_of_trans'] = 'Automated'
            df24['mode'] = 'Loan'
            # df24['entity_bank']='NA'
            df24['entity'] = "Loan A/C" + " - " + df24['new'].apply(lambda x: x[1])
            df24.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # CRV POS
        try:
            df25 = icici[icici["Description"].str.startswith("CRV POS")]
            df25['sub_mode'] = 'CRV POS'
            df25['source_of_trans'] = 'Automated'
            df25['mode'] = 'Refund'
            # df25['entity_bank']='NA'
            df25['entity'] = 'NA'
        except:
            pass

        # POS
        try:
            df26 = icici[icici["Description"].str.startswith("POS")]
            df26 = df26[~df26["Description"].str.startswith("POS REF")]
            df26 = df26[~df26["Description"].str.endswith("POS DEBIT")]
            df26 = df26[~df26["Description"].str.endswith("POSDEBIT")]
            df26['new'] = df26['Description'].str.split(" ")
            df26['sub_mode'] = df26['new'].apply(lambda x: x[0])
            df26['source_of_trans'] = 'Self Initiated'
            df26['mode'] = 'Card'
            # df26['entity_bank']='NA'
            df26['entity'] = df26['new'].apply(lambda x: x[2:])
            df26['entity'] = df26["entity"].str.join(" ")
            df26.drop(['new'], axis=1, inplace=True)
        except:
            pass

        try:
            df26a = icici[icici["Description"].str.endswith("POSDEBIT")]
            df26a['new'] = df26a['Description'].str.split(" ")
            df26a['sub_mode'] = df26a['new'].apply(lambda x: x[0])
            df26a['source_of_trans'] = 'Self Initiated'
            df26a['mode'] = 'Card'
            # df26a['entity_bank']='NA'
            df26a['entity'] = df26a['new'].apply(lambda x: x[2:-1])
            df26a['entity'] = df26a["entity"].str.join(" ")
            df26a.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # POS REF
        try:
            df27 = icici[icici["Description"].str.startswith("POS REF")]
            df27['new'] = df27['Description'].str.split(" ")
            df27['sub_mode'] = df27['new'].apply(lambda x: x[0] + ' ' + x[1])
            df27['entity'] = df27['new'].apply(lambda x: x[3])
            df27['source_of_trans'] = 'Self Initiated'
            df27['mode'] = 'Card'
            # df27['entity_bank']='NA'
            df27.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # Ends with POS DEBIT
        try:
            df45 = icici[icici["Description"].str.endswith("POS DEBIT")]
            df45['new'] = df45['Description'].str.split(" ")
            df45['sub_mode'] = df45['new'].apply(lambda x: x[0])
            df45['source_of_trans'] = 'Self Initiated'
            df45['mode'] = 'Card'
            # df45['entity_bank']='NA'
            df45['entity'] = df45['new'].apply(lambda x: x[2:-2])
            df45['entity'] = df45["entity"].str.join(" ")
            df45.drop(['new'], axis=1, inplace=True)
        except:
            pass

            # RTGS

        # RTGS
        try:
            df28 = icici[icici["Description"].str.startswith("RTGS")]
            df28 = df28[~df28["Description"].str.startswith("RTGS CHGS")]
            df28['new'] = df28['Description'].str.split("-")
            df28['ifsc'] = df28['new'].apply(lambda x: x[1][:4])
            # df28['entity_bank'] = df28['ifsc'].apply(lambda x: 'icici' if x == 'icici' else 'Others')
            df28['sub_mode'] = "RTGS"
            df28['entity'] = df28['new'].apply(lambda x: x[2])
            df28['source_of_trans'] = 'Self Initiated'
            df28['mode'] = 'Bank'
            df28.drop(['new'], axis=1, inplace=True)
            df28.drop(["ifsc"], axis=1, inplace=True)
        except:
            pass

        # RTGS Charges
        try:
            df28a = icici[icici["Description"].str.startswith("RTGS CHGS")]
            df28a['sub_mode'] = "RTGS Charges"
            df28a["entity_bank"] = "NA"
            df28a['entity'] = "NA"
            df28a['source_of_trans'] = 'Automated'
            # df28a["entity_bank"]="NA"
            df28a['mode'] = 'Charges'
        except:
            pass

        # Service Charge
        try:
            df29 = icici[icici["Description"].str.startswith("SERVICE CHARGES")]
            df29['sub_mode'] = 'SERVICE Charges'
            df29['source_of_trans'] = 'Automated'
            df29['mode'] = 'Charges'
            # df29['entity_bank']='NA'
            df29['entity'] = 'NA'
        except:
            pass

        # Settlement Charge
        try:
            df30 = icici[icici["Description"].str.startswith("SETTLEMENT CHARGE")]
            df30['sub_mode'] = 'SETTLEMENT CHARGE'
            df30['source_of_trans'] = 'Automated'
            df30['mode'] = 'Charges'
            # df30['entity_bank']='NA'
            df30['entity'] = 'NA'
        except:
            pass

        # MC CHARGES
        try:
            df31 = icici[icici["Description"].str.startswith("MC CHARGES")]
            df31['sub_mode'] = 'MC CHARGES'
            df31['source_of_trans'] = 'Automated'
            df31['mode'] = 'Charges'
            # df31['entity_bank']='NA'
            df31['entity'] = 'NA'
        except:
            pass

        # INST-ALERT CHARGES
        try:
            df32 = icici[icici["Description"].str.startswith("INST-ALERT")]
            df32['sub_mode'] = 'INST ALERT CHG CHARGES'
            df32['source_of_trans'] = 'Automated'
            df32['mode'] = 'Charges'
            # df32['entity_bank']='NA'
            df32['entity'] = 'NA'
        except:
            pass

        try:
            df33 = icici[icici["Description"].str.startswith("IB")]
            df33['new'] = df33['Description'].str.split("-")
            df33['sub_mode'] = df33['new'].apply(lambda x: x[0])
            df33['source_of_trans'] = 'Self Initiated'
            df33['mode'] = 'NA'
            # df33['entity_bank']='NA'
            df33['entity'] = 'NA'
            df33.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # TATASKY DTH

        try:
            df34 = icici[icici["Description"].str.startswith("TATASKY")]
            df34['sub_mode'] = 'TATASKY'
            df34['source_of_trans'] = 'NA'
            df34['mode'] = 'NA'
            # df34['entity_bank']='NA'
            df34['entity'] = 'NA'
        except:
            pass

        # BAJAJ FINEMI
        try:
            df35 = icici[icici["Description"].str.startswith("BAJAJ FINEMI")]
            df35['sub_mode'] = 'BAJAJ FINEMI'
            df35['source_of_trans'] = 'Automated'
            df35['mode'] = 'EMI'
            # df35['entity_bank']='NA'
            df35['entity'] = 'BAJAJ FINANCE'
        except:
            pass

        # CASH WITHDRAWAL
        try:
            df36 = icici[icici["Description"].str.startswith("CSH WD - CHQ PAID")]
            df36['sub_mode'] = 'CSH WD - CHQ PAID'
            df36['source_of_trans'] = 'Self Initiated'
            df36['mode'] = 'Cash'
            # df36['entity_bank']='NA'
            df36['entity'] = 'NA'
        except:
            pass

        ##HD
        try:
            df37 = icici[icici["Description"].str.startswith("HD0")]
            df37['new'] = df37['Description'].str.split("-")
            df37['sub_mode'] = df37['new'].apply(lambda x: x[0])
            df37['entity'] = df37['new'].apply(lambda x: x[1])
            df37['source_of_trans'] = 'Self Initiated'
            df37['mode'] = 'NA'
            # df37['entity_bank']='NA'
            df37.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # INTER-BRN CHARGES
        try:
            df38 = icici[icici["Description"].str.startswith("INTER-BRN")]
            df38['sub_mode'] = 'INTER-BRN CASH CHARGES'
            df38['source_of_trans'] = 'Automated'
            df38['mode'] = 'Charges'
            # df38['entity_bank']='NA'
            df38['entity'] = 'INTER-BRN CASH CHG'
        except:
            pass

        ##Manager's Cheque
        try:
            df39 = icici[icici["Description"].str.startswith("MC ISSUED")]
            df39['new'] = df39['Description'].str.split("-")
            df39['sub_mode'] = df39['new'].apply(lambda x: x[0])
            df39['entity'] = df39['new'].apply(lambda x: x[4])
            df39['source_of_trans'] = 'Self Initiated'
            df39['mode'] = 'cheque'
            # df39['entity_bank']='NA'
            df39.drop(['new'], axis=1, inplace=True)
        except:
            pass

            # TPT Third Party Transfer
        try:
            df40 = icici[icici["Description"].str.contains("TPT")]
            df40['new'] = df40['Description'].str.split("-")
            df40['sub_mode'] = 'TPT'
            df40['source_of_trans'] = 'Self Initiated'
            df40['mode'] = 'NA'
            # df40['entity_bank']='NA'
            df40['entity'] = df40['new'].apply(lambda x: x[-1])
            df40.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # REV
        try:
            df41 = icici[icici["Description"].str.contains("REV")]
            df41 = df41[~df41["Description"].str.startswith("IMPS")]
            df41['sub_mode'] = 'REV'
            df41['source_of_trans'] = 'Automated'
            df41['mode'] = 'Reversal'
            # df41['entity_bank']='NA'
            df41['entity'] = 'NA'
        except:
            pass

        # NET PI to HSL

        try:
            df42 = icici[icici["Description"].str.startswith("NET")]
            df42['new'] = df42['Description'].str.split(" ")
            df42['sub_mode'] = df42['new'].apply(lambda x: x[0] + " " + x[1] + " " + x[2] + " " + x[3] + " " + x[4])
            df42['source_of_trans'] = 'Automated'
            df42['mode'] = 'Trading'
            # df42['entity_bank']='NA'
            df42['entity'] = df42['new'].apply(lambda x: x[0] + " " + x[1] + " " + x[2] + " " + x[3] + " " + x[4])
            df42.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # SALARY
        try:
            df43 = icici[icici["Description"].str.startswith("SAL")]
            df43['new'] = df43['Description'].str.split(" ")
            df43['sub_mode'] = df43['new'].apply(lambda x: x[0])
            df43['source_of_trans'] = 'Automated'
            df43['mode'] = 'Salary'
            # df43['entity_bank']='NA'
            df43['entity'] = 'NA'
            df43.drop(['new'], axis=1, inplace=True)
        except:
            pass

        try:
            df44 = icici[icici["Description"].str.slice(1, 4, 1) == 'HDF']
            df44['new'] = df44['Description'].str.split("/")
            df44['sub_mode'] = df44['new'].apply(lambda x: x[0]).str[:4]
            df44['source_of_trans'] = 'Self Initiated'
            df44['mode'] = 'NA'
            # df44['entity_bank']='NA'
            df44['entity'] = df44['new'].apply(lambda x: x[1])
            df44.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # df45 exists

        # CC
        try:
            df46 = icici[icici["Description"].str.startswith("CC")]
            df46['new'] = df46['Description'].str.split(" ")
            df46['sub_mode'] = df46['new'].apply(lambda x: x[0])
            df46['source_of_trans'] = 'Automated'
            df46['mode'] = 'Card'
            # df46['entity_bank']='NA'
            df46['entity'] = df46['new'].apply(lambda x: x[-1])
            df46.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # MICRO ATM CASH DEP
        try:
            df47 = icici[icici["Description"].str.startswith("MICRO ATM CASH")]
            df47['new'] = df47['Description'].str.split("-")
            df47['sub_mode'] = df47['new'].apply(lambda x: x[0])
            df47['source_of_trans'] = 'Self Initiated'
            df47['mode'] = 'Cash'
            # df47['entity_bank']='NA'
            df47['entity'] = df47['new'].apply(lambda x: x[-1])
            df47.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # MICRO ATM CASH DEP
        try:
            df48 = icici[icici["Description"].str.startswith("PAYZAPP")]
            df48['new'] = df48['Description'].str.split("-")
            df48['sub_mode'] = df48['new'].apply(lambda x: x[0])
            df48['source_of_trans'] = 'Self Initiated'
            df48['mode'] = 'Mobile Apps'
            # df48['entity_bank']='NA'
            df48['entity'] = df48['new'].apply(lambda x: x[2])
            df48.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # LOAN MANUAL HOLD CHARGE
        try:
            df49 = icici[icici["Description"].str.contains("LOAN MANUAL HOLD")]
            df49['new'] = df49['Description'].str.split(" ")
            df49['sub_mode'] = df49['new'].apply(lambda x: x[1:])
            df49['source_of_trans'] = 'Automated'
            df49['mode'] = 'Charges'
            # df49['entity_bank']='NA'
            df49['entity'] = "Loan A/C" + " - " + df49['new'].apply(lambda x: x[0])
            df49['sub_mode'] = df49["sub_mode"].str.join(" ").str.extract('(.*)E') + "E"
            df49.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # SI HGA
        try:
            df51 = icici[icici["Description"].str.contains("SI HGA")]
            df51['new'] = df51['Description'].str.split(" ")
            df51['sub_mode'] = 'NA'
            df51['source_of_trans'] = 'Self Initiated'
            df51['mode'] = 'Card'
            # df51['entity_bank']='NA'
            df51['entity'] = df51['new'].apply(lambda x: x[2])
            df51.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # HGAIP
        try:
            df52 = icici[icici["Description"].str.startswith("HGA")]
            df52['new'] = df52['Description'].str.split("-")
            df52['sub_mode'] = 'NA'
            df52['source_of_trans'] = 'Automated'
            df52['mode'] = 'NA'
            # df52['entity_bank']='NA'
            df52['entity'] = df52['new'].apply(lambda x: x[1])
            df52.drop(['new'], axis=1, inplace=True)
        except:
            pass

        # LOw usage charges
        try:
            df53 = icici[icici["Description"].str.startswith("LOW USAGE CHARGES")]
            df53['new'] = df53['Description'].str.split("-")
            df53['sub_mode'] = 'NA'
            df53['source_of_trans'] = 'Automated'
            df53['mode'] = 'Charges'
            # df53['entity_bank']='NA'
            df53['entity'] = "NA"
            df53.drop(['new'], axis=1, inplace=True)
        except:
            pass

        t1 = concat(
            [df1, df2, df3, df4, df6a, df6b, df7, df8, df9, df10, df11, df12, df13, df14, df15, df16, df17, df17a, df18,
             df19, df20, df20a, df21, df22, df23, df24, df25, df26, df26a, df27, df28, df28a, df29, df30, df31, df32,
             df33, df34, df35, df36, df37, df38, df39, df40, df41, df42, df43, df44, df45, df46, df47, df48, df50, df49,
             df51, df52, df53], axis=0)  # axis =0 for vertically appending

        t2 = icici[~icici["Description"].isin(t1["Description"])]
        t2['mode'] = 'Others'
        t2['entity'] = 'NA'
        t2['source_of_trans'] = 'NA'
        # t2['entity_bank']='NA'
        t2['sub_mode'] = 'NA'

        final = concat([t1, t2], axis=0)

        try:
            final.drop(['new'], axis=1, inplace=True)
        except:
            pass

        final = final.sort_values(by=["Txn Date"])
        final = final.sort_index()
        final.rename(columns={'sub-mode': 'sub_mode'}, inplace=True)
        final = final[
            ['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name', 'Account Number',
             'mode', 'entity', 'source_of_trans', 'sub_mode']]
        final['entity'].fillna('Other', inplace=True)
        final['entity'].replace('NA', 'Other', inplace=True)
        final['entity'].replace('', 'Other', inplace=True)

        final['Debit'] = final['Debit'].astype('str')
        final['Debit'] = final['Debit'].apply(lambda x: x.replace(',', ''))
        final['Debit'] = final['Debit'].replace('nan', 0)
        final['Debit'] = final['Debit'].astype('float64')
        final['Debit'] = final['Debit'].apply(lambda x: round(x, 2))

        final['Credit'] = final['Credit'].astype('str')
        final['Credit'] = final['Credit'].apply(lambda x: x.replace(',', ''))
        final['Credit'] = final['Credit'].replace('nan', 0)
        final['Credit'] = final['Credit'].astype('float64')
        final['Credit'] = final['Credit'].apply(lambda x: round(x, 2))

        final['Balance'] = final['Balance'].astype('str')
        final['Balance'] = final['Balance'].apply(lambda x: x.replace(',', ''))
        final['Balance'] = final['Balance'].astype('float64')
        final['Balance'] = final['Balance'].apply(lambda x: round(x, 2))

        final.reset_index(drop=True, inplace=True)

        d = {}
        for i, j in enumerate(final['Balance']):
            if j < 0:
                d[i] = 'Overdrawn'
                if final.iloc[i]['Debit'] == final.iloc[i + 1]['Credit'] and final.iloc[i]['Txn Date'] == \
                        final.iloc[i + 1]['Txn Date'] and final.iloc[i]['entity'] == final.iloc[i + 1]['entity']:
                    d[i] = 'Bounced'
                    d[i + 1] = 'Bounced'

            else:
                if i not in d.keys():
                    if final.iloc[i]["source_of_trans"] == "Automated" and final.iloc[i]["Credit"] != 0 and \
                            final.iloc[i]["Debit"] == 0:
                        d[i] = "Auto Credit"
                    elif final.iloc[i]["source_of_trans"] == "Automated" and final.iloc[i]["Credit"] == 0 and \
                            final.iloc[i]["Debit"] != 0:
                        d[i] = "Auto Debit"
                    elif final.iloc[i]["source_of_trans"] == "Self Initiated" and final.iloc[i]["Credit"] != 0 and \
                            final.iloc[i]["Debit"] == 0:
                        d[i] = "Self Credit"
                    elif final.iloc[i]["source_of_trans"] == "Self Initiated" and final.iloc[i]["Credit"] == 0 and \
                            final.iloc[i]["Debit"] != 0:
                        d[i] = "Self Debit"
                    else:
                        d[i] = "Not available"

        final["Transaction_Type"] = final.index.map(d)

        final['bank_name'] = 'ICICI'

        final['lid'] = file_name.split('_')[0]
        #final.rename(columns={'Txn Date': 'Txn_Date','Cheque Number':'Cheque_Number','Account Name':'Account_Name','Account Number':'Account_Number'}, inplace=True)
        print(final)
        final.to_csv(r'D:\digitizedfiles\{}_b.csv'.format(file_name), index=False)

        return r'D:\digitizedfiles\{}_b.csv'.format(file_name)


#icici_digitization("D:\\bank\\765606_4_aaditya banking.pdf", "")


