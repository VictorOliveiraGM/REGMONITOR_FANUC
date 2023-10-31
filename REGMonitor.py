import pandas as pd 
import requests as re
from datetime import datetime
import datetime
import pymssql

# Essa função recebe uma string no tipo Hostname: HA010R01B13 <br> e retorna apenas o nome do robo. 
def getName(data):
    index= 0
    indNome_fim = 0
    indNome_flag_final = 0
    for y in data:
        if y == '<'  and indNome_flag_final == 0:
            indNome_fim = index
            indNome_flag_final = 1
        index = index + 1
    return data[1:indNome_fim]
# Retorna o valor do registrador da pagina html robo.  
def GetRegValue(html , reg):      
        posReg = html.find(reg)
        html = html[posReg:posReg+39] 
        index = 0
        indComment_inicio  = 0
        indComment_flag_inicio = 0
        indValue_inicio = 0
        indValue_inicio_flag = 0           
 ##Pega os indexadores dos valores desejados para separar a linha em comentario valor e numero do registrador. 
        for x in html :
                if x == "'" and indComment_flag_inicio == 0 :
                        indComment_inicio = index
                        indComment_flag_inicio = 1
                        break                     
                if x == "=" and indValue_inicio_flag == 0:
                        indValue_inicio = index + 2
                        indValue_inicio_flag = 1
                index = index + 1
        #Definindo Valores.   
        valueReg =float(html[indValue_inicio:indComment_inicio-2])
        return valueReg
# Retorna o comentario do registrador
def get_Comentario(data):
    index = 0
    indComment_inicio  = 0
    indComment_flag_inicio = 0
    indComment_fim = 0
    indComment_flag_final = 0
        
    ##Pega os indexadores dos valores desejados para separar a linha em comentario valor e numero do registrador. 
    for x in data:
        if x == "'" and indComment_flag_inicio == 0 :
                indComment_inicio = index + 1
                indComment_flag_inicio = 1  
        elif x == "'" and indComment_flag_inicio == 1 and indComment_flag_final == 0 :
                indComment_fim = index 
                indComment_flag_final = 1             
        index += 1
    return data[indComment_inicio:indComment_fim]
# Retorna o numero do registrador de acordo com o seu comentario
def getReg_Num(data):
    index = 0
    indReg_inicio = 0
    indReg_fim = 0
    indReg_flag_inicio = 0 
    indReg_flag_final = 0
        
    for x in data:     
        if x == "[" and indReg_flag_inicio == 0 :
                indReg_inicio = index + 1
                indReg_flag_inicio = 1
                
        if x == "]" and indReg_flag_inicio == 1 and indReg_flag_final == 0  :
                indReg_fim = index
                indReg_flag_final = 1
        index += 1
        #Definindo Valores.   
         
    return data[indReg_inicio:indReg_fim]
# Retorna o valor do registrador de uma substring.
def getReg_Value(data):
    index = 0
    indValue_inicio = 0
    indValue_final = 0
    indValue_flag_inicio = 0 
    indValue_flag_final = 0
        
    for x in data:     
        if x == "=" and indValue_flag_inicio == 0 :
                indValue_inicio = index + 2
                indValue_flag_inicio = 1
                
        if x == "'" and indValue_flag_inicio == 1 and indValue_flag_final == 0  :
                indValue_final = index - 2
                indValue_flag_final = 1
                break
        index += 1
         
    return data[indValue_inicio:indValue_final]

def Registers_Monitor(): 
    # Guardar date_time do inicio da execucao
    start_date_time  = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    print('Inicio', start_date_time) 

    error_counter = 0
    currntinc_counter = 0
    preset_counter = 0 
    
    connection = pymssql.connect(server='BRSCTWDCS2403BK\SQLEXPRESS01',database='REG_TIPDRESS',user='sa',password='1234')

    cursor = connection.cursor()

    IPS = pd.read_sql_query("SELECT* FROM TB_ROBOTS_MONITORED",connection)

    # Limpar os dados da tabela para atualizar
    cursor.execute('DELETE FROM TB_REG_VALUES')
    connection.commit()


    # Lista para buscar entre os diferentes ranges de registradores utilizados:
    TDRegList = [['[470]', '[471]', '[472]', '[474]','[475]'],
               ['[490]', '[491]', '[492]', '[494]','[495]'],
               ['[131]', '[132]', '[133]', '[134]','[135]']]

    CURRNTRegList = ['[79]','[82]','[83]', '[92]']
    
    # Percorrendo as linhas dos Endereços.
    for i in range(len(IPS)):
        if IPS.iloc[i, 2] == '470':
            selector = 0
        elif IPS.iloc[i, 2] == '490':
            selector = 1
        elif IPS.iloc[i, 2] == '131':
            selector = 2
        else:
            selector = 3

        try:
            response = re.get('http://' + IPS.iloc[i, 1] + '/MD/NUMREG.VA')
        except:
            print(IPS.iloc[i, 1], 'Get Error')
            error_counter += 1 
        else:
            html = response.text
            posName = html.find("Hostname")
            robot_name = getName(html[posName+9:posName+25])
            robot_date = datetime.datetime.now().strftime('%m/%d/%Y')
            robot_time = datetime.datetime.now().strftime('%H:%M:%S')
            
            if selector != 3:
                wear_mem = GetRegValue (html , TDRegList[selector][0])
                result = GetRegValue (html , TDRegList[selector][1])
                preset = GetRegValue (html , TDRegList[selector][2])
                retrypreset = GetRegValue(html , TDRegList[selector][3])
                dresscount = GetRegValue(html, TDRegList[selector][4])
                currntinc_counter += 1
                preset_counter += 1
            
            if selector == 3:
                wear_mem = 0
                result = 0
                preset = 0
                retrypreset = 0
                dresscount = 0
                currntinc_counter += 1

            currentinc = GetRegValue (html , CURRNTRegList[0])
            currentfree = GetRegValue(html , CURRNTRegList[1])
            currentload = GetRegValue(html , CURRNTRegList[2])
            currentmax = GetRegValue (html,  CURRNTRegList[3])
             
            if selector != 2:
                SGcurrent = GetRegValue(html, '[488]')
            else:
                 SGcurrent = 0 
                 
            insert = f"""INSERT INTO TB_REG_VALUES(robot_date, robot_time, robot_name,WEAR_MEM, RESULT, PRESET,RETRY_PRESET,DRESS_COUNT,
            CURRNT_INC, CURRNT_FREE, CURRNT_LOAD, CURRNT_MAX,
            SG_CURRNT)
                VALUES('{robot_date}','{robot_time}','{robot_name}',{wear_mem},{result},{preset},{retrypreset},{dresscount}, 
                        {currentinc},{currentfree},{currentload},{currentmax},
                        {SGcurrent})"""
            
            insert_history = f"""INSERT INTO TB_REG_VALUES_HISTORY(robot_date, robot_time, robot_name,WEAR_MEM, RESULT, PRESET,RETRY_PRESET,DRESS_COUNT,CURRNT_INC, CURRNT_FREE, CURRNT_LOAD, CURRNT_MAX,
            SG_CURRNT)
                VALUES('{robot_date}','{robot_time}','{robot_name}',{wear_mem},{result},{preset},{retrypreset},{dresscount}, 
                        {currentinc},{currentfree},{currentload},{currentmax},
                        {SGcurrent})"""

            cursor.execute(insert_history)
            connection.commit()
            cursor.execute(insert)
            connection.commit()

    end_date_time  = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') 
    print ('Final' ,end_date_time)

    insert_status_datetime = f"""INSERT INTO TB_STATUS(start_datetime, end_datetime, error_counter, preset_counter, currntinc_counter)
        VALUES('{start_date_time}' ,'{end_date_time}' ,{error_counter},{preset_counter},{currntinc_counter})"""

    cursor.execute(insert_status_datetime)
    connection.commit()
    cursor.close()
    connection.close()

def Registers_Checker():
    
  
    df_AllRobots = pd.read_csv('RobotsIp.csv' , sep =';', index_col= False)


    connection = pymssql.connect(server='BRSCTWDCS2403BK\SQLEXPRESS01',database='REG_TIPDRESS',user='sa',password='1234')
    cursor = connection.cursor()


    error_counter = 0
    robots_counter = 0
    weld_counter = 0
    update_counter = 0
    insert_counter = 0
    delete_counter = 0

    comments = ['G1GN WEAR MEM','G1GN WEAR RESULT', 'G1GN WEAR MEMO','G1GN Wear Mem']

    start_datetime  = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    print('Start Checker', start_datetime)
    
    for i in range(len(df_AllRobots)):
        robot_ip = df_AllRobots.iloc[i,1]
        try:
            response = re.get('http://' + robot_ip + '/MD/NUMREG.VA')
            html = response.text
        except:
            error_counter += 1
            continue
        else:
            #Verifica se o e robo e de solda
            robots_counter += 1

            posReg = html.find('[1]')
            data = html[posReg:posReg+39]
            
            get_line = f"""SELECT* FROM TB_ROBOTS_MONITORED WHERE robot_ip = '{robot_ip}'"""
            cursor.execute(get_line)
            line = cursor.fetchone()
            
            #Criterio para verificar se o robo e de solda.
            if get_Comentario(data) == 'Spot Count G1': 
                weld_counter += 1
                #Tenta buscar comentarios iguais o da lista de comments
                for s in range(len(comments)):
                    posReg = html.find(comments[s])
                    data= html[posReg-20:posReg]
                    reg = getReg_Num(data)
                    if reg == '131' or reg == '490' or reg == '470' :
                        break
                if reg != '131' and reg != '490' and reg != '470':
                    reg = 'Não encontrado'
        
                posName = html.find("Hostname")
                robot_name = getName(html[posName+9:posName+25])
                

                if line is None :
                    #Incluir no banco de dados 
                    insert_robot = f"""INSERT INTO TB_ROBOTS_MONITORED(robot_name, robot_ip, reg)
                    VALUES('{robot_name}' ,'{robot_ip}' ,'{reg}')"""
                    cursor.execute(insert_robot)
                    connection.commit()
                    insert_counter += 1
                else:
                    if line[0] != robot_name:
                        update_name = f"""UPDATE TB_ROBOTS_MONITORED SET robot_name = '{robot_name}' WHERE robot_ip = '{robot_ip}'"""
                        cursor.execute(update_name)
                        connection.commit()
                        
                        update_name_History = f"""UPDATE TB_REG_VALUES_HISTORY SET robot_name = '{robot_name}' WHERE robot_name = '{line[0]}'"""
                        cursor.execute(update_name_History)
                        connection.commit()
                        update_counter += 1

                    if line[2] != reg :
                        #Atualiza registro do robo
                        update_robot = f"""UPDATE TB_ROBOTS_MONITORED SET reg = '{reg}' WHERE robot_name = '{robot_name}'"""
                        cursor.execute(update_robot)
                        connection.commit()
                        update_counter += 1
                    else:
                        continue
                    
            elif line != None :
                delete_robot = f"""DELETE FROM TB_ROBOTS_MONITORED WHERE robot_ip='{robot_ip}'"""
                cursor.execute(delete_robot)
                connection.commit()
                delete_counter += 1
                continue
    
    end_datetime  = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    print('end Checker', end_datetime)
    print('Error: ', error_counter, 'Inserts: ', insert_counter,'Deleted: ', delete_counter ,'Atualizados: ', update_counter, 'TotalWeld: ', weld_counter, 'Total Robots', robots_counter)
    insert_status_datetime = f"""INSERT INTO TB_STATUS_INSTALLATION(start_datetime, end_datetime, insert_counter,update_counter,robots_counter,error_counter,weld_counter,delete_counter)
                VALUES('{start_datetime}' ,'{end_datetime}' ,{insert_counter},{update_counter},{robots_counter},{error_counter},{weld_counter},{delete_counter})"""

    cursor.execute(insert_status_datetime)
    connection.commit()

    cursor.close()
    connection.close()

