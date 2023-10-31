import time 
import datetime
import REGMonitor as REG_monitor
import TIPDRESSNofitier as TD_notifier

#REG_monitor.Registers_Checker()

# Lista de horários estabelecidos
horarios_Monitor = ["10:30:00","18:00:00","20:00:00","00:00:00"]
horarios_CheckerRobots = ["00:00:00"]
horarios_emails = ["06:00:00","15:00:00","00:00:00","14:26:00"]

while True:
    # Obtém o horário atual
    horario_atual = datetime.datetime.now().strftime("%H:%M:%S")

    # Verifica se o horário atual está na lista de horários estabelecidos
    #if datetime.datetime.today().weekday() in [5,6]:
       # if horario_atual in horarios_CheckerRobots:
          #  REG_monitor.Registers_Checker()

    if datetime.datetime.today().weekday() in [0,1,2,3,4]:
        if horario_atual in horarios_Monitor:
            REG_monitor.Registers_Monitor()
            
        if horario_atual in horarios_emails:
            REG_monitor.Registers_Monitor()
            TD_notifier.send_email()

    # Aguarda 1 segundo antes de verificar novamente
    time.sleep(1)





    

    

