import pandas as pd
import pymssql
import os
import win32com.client as win32

#Path html_files to send email:
os.chdir(r"C:\REG_Monitor\Register_Monitor\data_html")

def send_email():
    
    connection = pymssql.connect(server='BRSCTWDCS2403BK\SQLEXPRESS01',database='REG_TIPDRESS',user='sa',password='1234')
    cursor = connection.cursor()
    dfREG_VALUES = pd.read_sql_query("SELECT* FROM TB_REG_VALUES", connection)
    IPS = pd.read_sql_query("SELECT* FROM TB_ROBOTS_MONITORED",connection)

    #Gerando a tabela do preset <0.01
    dfPreset = dfREG_VALUES[['robot_name', 'WEAR_MEM', 'RESULT', 'PRESET']]
    dfResult = dfPreset[['robot_name' , 'RESULT']]
    dfPreset = dfPreset.loc[(dfPreset['PRESET'] < 0.01) & (dfPreset['WEAR_MEM'] != 0) & (dfPreset['RESULT'] != 0)]
    dfPreset = pd.merge(dfPreset,IPS, how = 'left' , on= 'robot_name')
    dfPreset.rename(columns={'robot_name':'name' , 'PRESET':'valor'} , inplace= True)
    del dfPreset['WEAR_MEM']
    del dfPreset['RESULT']
    dfPreset = dfPreset[['name', 'reg', 'valor']]
    dfPreset['comentario'] = 'G1GN PRESET'
    dfPreset.sort_values(by=['name'], inplace= True)

    #Gerando a tabela do Result <0.01.
    dfResult = dfResult.loc[(dfResult['RESULT'] <0.01)]
    dfResult = pd.merge(dfResult,IPS, how = 'left' , on= 'robot_name' )
    dfResult = dfResult.loc[(dfResult['reg'] != 'Não encontrado')]
    dfResult.rename(columns={'robot_name':'name' , 'RESULT':'valor'} , inplace= True)
    dfResult['comentario'] = 'RESULT'
    dfResult.sort_values(by=['name'], inplace = True)
    del dfResult['robot_ip']
    dfResult = dfResult[['name', 'reg', 'valor', 'comentario']]
    #Gerando a tabela do Current inc <3
    dfCurrentINC = dfREG_VALUES[['robot_name', 'CURRNT_INC']]
    dfCurrentINC = dfCurrentINC.loc[dfCurrentINC['CURRNT_INC'] < 3]
    dfCurrentINC.sort_values(by=['robot_name'], inplace= True)
    dfCurrentINC.rename(columns={'robot_name':'name' , 'CURRNT_INC':'valor'} , inplace= True)
    dfCurrentINC['comentario'] = 'CURRENT INC'
    dfCurrentINC['reg'] = '79'
    dfCurrentINC = dfCurrentINC[['name', 'reg', 'valor', 'comentario']]

    outlook = win32.Dispatch('outlook.application')
    email = outlook.CreateItem(0)

    to_email = []

    with open('HTML_header.txt') as header:
        htmlHeader = header.read()
    with open('HTML_footer.txt') as footer:
        htmlFooter = footer.read()
    with open('emails.txt') as emails:
        emailslist = emails.read()

    to_email.append(htmlHeader)

    if dfResult.shape[0] > 0:
        with open('HTML_Title03.txt') as title03:
            htmlTitle03 = title03.read()
        tableResult = dfResult.to_html(index = False ,col_space= 5 )
        to_email.append(htmlTitle03)
        to_email.append(tableResult)
        
    if dfPreset.shape[0]> 0:
        with open('HTML_Title01.txt') as title01:
            htmlTitle01 = title01.read()
        tablePreset = dfPreset.to_html(index = False, col_space=5)
        to_email.append(htmlTitle01)
        to_email.append(tablePreset)

    if dfCurrentINC.shape[0] > 0:
        with open('HTML_Title02.txt') as title02:
            htmlTitle02 = title02.read()
        tableCurrentINC = dfCurrentINC.to_html(index= False, col_space= 5)
        to_email.append(htmlTitle02)
        to_email.append(tableCurrentINC)


    to_email.append(f"""<p style="color:black;font-size:14px;text-align:left;">
    O sistema esta monitorando {IPS.shape[0]} Robos<br/>
    <br/>
    </p>""")

    to_email.append(htmlFooter)

    email.HTMLbody = ''.join(to_email)
    email.Subject = "ATENÇÃO! Registradores com valores diferentes do padrão"
    email.To = emailslist
    email.Send()

    cursor.close()
    connection.close()