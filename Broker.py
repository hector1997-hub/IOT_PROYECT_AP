import sys
from time import sleep
import signal
from threading import Thread
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime 
import ssl
import paho.mqtt.client

###############FLAGS##################################

FLAGS_C = {"VALVI":"FALSE","VALVR":"FALSE","LIGTH":"FALSE","RIEGO":"ON"}
HORA_RIEGO="00:00"
RIEGO_A=0.0
FLUJO=20  #M/S
MENS_VALI=""
MENS_VALR=""
#########VARIABLES FIREBASE ###########################
PAHT_CRED = '/home/pi/IOT_PROYECT_AP/culterapp.json'
URL_DB = 'https://culterapp.firebaseio.com/'
REF_CULT='CULTIVO'
REF_LUZ = 'LUCES'
REF_TIPO1='TIPO1'
REF_TIPO2='TIPO2'
REF_TIPO3='TIPO3'

REF_SENS = 'SENSORES'
REF_SENSOR1= 'SENSOR1'
REF_SENSOR2='SENSOR2'
REF_SENSOR3='SENSOR3'
REF_SENS_N = 'SENSORES_NIVEL'
REF_SN1='S_N1'
REF_SN2='S_N2'

REF_TIME='TIEMPO'
REF_ACTP='PREESCRIBIR'

REF_HORA="HORA"

REF_TIME2='TIEMPO2'
REF_PRES='PRIEGO'
REF_HOA='HORA_ANTERIOR'
REF_FECHA='FECHA_RIEGO'

REF_USER = 'USERS'
REF_PASS1='PASSWORD1'
REF_USER1='USER1'
REF_VALVSI = 'VALVULAS_I'
REF_VALVSR= 'VALVULAS_R'
REF_VAL1='VALVULA_I'
REF_VAL2='VALVULA_R'
#############################################################







 
class FIREB():

    def __init__(self):
        global HORA_RIEGO
        global FLAGS_C
        cred = credentials.Certificate(PAHT_CRED)

        firebase_admin.initialize_app(cred, {

            'databaseURL': URL_DB

        })

        self.refcultivo=db.reference(REF_CULT)

        self.refluz = self.refcultivo.child(REF_LUZ)
        self.reftipo1 = self.refluz.child(REF_TIPO1)
        self.reftipo2 = self.refluz.child(REF_TIPO2)
        self.reftipo3 = self.refluz.child(REF_TIPO3)

        self.refsens=self.refcultivo.child(REF_SENS)
        self.refsens1=self.refsens.child(REF_SENSOR1)    
        self.refsens2=self.refsens.child(REF_SENSOR2) 
        self.refsens3=self.refsens.child(REF_SENSOR3) 

        self.refsens_niv=self.refcultivo.child(REF_SENS_N)
        self.refsn1=self.refsens_niv.child(REF_SN1)
        self.refsn2=self.refsens_niv.child(REF_SN2)

        self.reftime=self.refcultivo.child(REF_TIME)
        self.refhora=self.reftime.child(REF_HORA)
        self.refactp=self.reftime.child(REF_ACTP)

        self.reftriego=self.refcultivo.child(REF_TIME2)
        self.refpres=self.reftriego.child(REF_PRES)
        self.refhprog=self.reftriego.child(REF_HOA)
        self.refferieg=self.reftriego.child(REF_FECHA)

        self.refuser=self.refcultivo.child(REF_USER)
        self.refp_1=self.refsens_niv.child(REF_PASS1)
        self.refu_1=self.refuser.child(REF_USER1)
        
        self.refvalvsi=self.refcultivo.child(REF_VALVSI) 
        self.refvali=self.refvalvsi.child(REF_VAL1)

        self.refvalvsr=self.refcultivo.child(REF_VALVSR) 
        self.refvalr=self.refvalvsr.child(REF_VAL2)


        self.client =paho.mqtt.client.Client(client_id='ESTACION_P', clean_session=False)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host='192.168.1.64', port=1883)
        self.client.loop_start()

        #INIT VARIABLES 
        HORA_RIEGO= self.refhora.get()
        FLAGS_C["RIEGO"] = self.refactp.get()
           

    def LUCES(self):
        estado_ant1 = self.reftipo1.get()
        estado_ant2 = self.reftipo2.get()
        estado_ant3 = self.reftipo3.get()
        while True:
            estado_act1 = self.reftipo1.get() #peticion
            estado_act2 = self.reftipo2.get() #peticion
            estado_act3 = self.reftipo3.get() #peticion
            if estado_act1!= estado_ant1:
                self.client.publish('LUCES/TIPO1',estado_act1)
            elif estado_act2!= estado_ant2:
                 self.client.publish('LUCES/TIPO2',estado_act1)
            elif estado_act3!= estado_ant3:
                self.client.publish('LUCES/TIPO3',estado_act1)
            else:
                pass
            estado_ant1=estado_act1    
            estado_ant2=estado_act2   
            estado_ant3=estado_act3   
            sleep(0.1)


    def VALVULAS(self):
        prev_S_VI = self.refvali.get()
        prev_S_VR = self.refvalr.get()
        while True:
            act_S_VI = self.refvali.get() #peticion
            act_S_VR = self.refvalr.get()
            if prev_S_VI != act_S_VI:
                print('VALVI = '+ str(act_S_VI))  
                FLAGS_C["VALVI"]=act_S_VI
            if prev_S_VR != act_S_VR:  
                print('VALVR = '+ str(act_S_VR))
                FLAGS_C["VALVR"]=act_S_VI               
            prev_S_VI=act_S_VI
            prev_S_VR=act_S_VR 
            sleep(0.1)

    def prescripcion(self):
        global HORA_RIEGO
        global FLAGS_C
        global RIEGO_A
        A_presc = self.refactp.get()
        Haplic = self.refhora.get()
        while True:
            A_presc_a = self.refactp.get()
            Haplic_a = self.refhora.get()
            if Haplic_a != Haplic :
                if len(str(Haplic_a))>0 :
                   HORA_RIEGO=Haplic_a

            if A_presc_a != A_presc:  
                  FLAGS_C["RIEGO"]=A_presc_a  
                  if A_presc_a=="ON":
                      arch_met=open("/home/pi/IOT_PROYECT_AP/data_meterorologica.txt","r")
                      var_met=arch_met.readlines()
                      arch_met.close()
                      var_met=var_met[len(var_met)-1]
                      var_met=var_met.split(";")
                      EVT=float(var_met[1])
                      Rain=float(var_met[2])
                      RIEGO_A=25-EVT
                      self.refpres.set(str(RIEGO_A))  

            self.refhprog.set(HORA_RIEGO)
            Haplic= Haplic_a
            A_presc= A_presc_a
            sleep(0.5)   

    def RIEGO_APLICATION(self):
        global HORA_RIEGO
        global FLAGS_C
        global RIEGO_A
        while True:
            now_time=str(datetime.now().hour)+":"+str(datetime.now().minute)

            if HORA_RIEGO=="18:25" :  
                #print(HORA_RIEGO)
                #print(FLAGS_C["RIEGO"])
                if FLAGS_C["RIEGO"]=="ON":
                    sens_niv1= self.refsn1.get() #peticion
                    sens_niv2 = self.refsn2.get() #peticion
                    if  FLAGS_C["VALVI"]=="ENABLE": 
                        if float(sens_niv1)>=25:
                            print(RIEGO_A)
                            self.client.publish('VALV/VALV1',"ON;"+str(RIEGO_A))
                            FLAGS_C["VALVI"]="BUSSY"
                        else:
                            if float(sens_niv2>50):
                                self.client.publish('VALV/VALV2',"ON;"+str(RIEGO_A))
                                FLAGS_C["VALVR"]="BUSSY"
                                delay(3)
                                self.client.publish('VALV/VALV1',"ON;"+str(RIEGO_A))
                                FLAGS_C["VALVI"]="BUSSY"
                            else:
                                self.REF_FECHA.set("no agua")                        
            sleep(1)  


    def on_connect(self,client, userdata, flags, rc):
        print('connected (%s)' % client._client_id)
        client.subscribe(topic='cultivo/humedad_1', qos=0)
        client.subscribe(topic='cultivo/humedad_2', qos=0)
        client.subscribe(topic='cultivo/humedad_3', qos=0)
        client.subscribe(topic='tanque/sens_1', qos=0)
        client.subscribe(topic='tanque/sens_2', qos=0)
        client.subscribe(topic='tanque/valvi', qos=0)
        client.subscribe(topic='tanque/valvr', qos=0)

    def on_message(self,client, userdata, message):
        global MENS_VALI
        if(message.topic=="cultivo/humedad_1"):
           # print("llego", str(message.payload))
            self.sen=str(message.payload)
            self.refsens1.set(self.sen[2:len(self.sen)-1])
        elif message.topic=="cultivo/humedad_1":
            self.sen=str(message.payload)
            self.refsens2.set(self.sen[2:len(self.sen)-1])
        elif message.topic=="cultivo/humedad_2":
            self.sen=str(message.payload)
            self.refsens3.set(self.sen[2:len(self.sen)-1])
        elif message.topic=="tanque/sens_1":
            self.sen=str(message.payload)
            self.refsn1.set(self.sen[2:len(self.sen)-1])
        elif message.topic=="tanque/sens_2":
            self.sen=str(message.payload)
            self.refsn2.set(self.sen[2:len(self.sen)-1])
        elif message.topic=="tanque/valvi":
            mens_c=str(message.payload)
            MENS_VALI=mens_c[2:(len(mens_c)-1)]
            FLAGS_C["VALVI"]="WR"



    def final_riego(self):
        global FLAGS_C,MENS_VALI
        while True:
            if FLAGS_C["VALVI"]=="WR":
                arch_riego=open("/home/pi/IOT_PROYECT_AP/data_riego.txt","a")
                mens_i=MENS_VALI.split(";")
                arch_riego.write(mens_i[0]+";"+datetime.now().day+';\n')
                arch_riego.close
                FLAGS_C["VALVI"]="ENABLE"
            delay(0.2)    

    def LUCES(self):
        estado_ant1 = self.reftipo1.get()
        estado_ant2 = self.reftipo2.get()
        estado_ant3 = self.reftipo3.get()
        while True:
            estado_act1 = self.reftipo1.get() #peticion
            estado_act2 = self.reftipo2.get() #peticion
            estado_act3 = self.reftipo3.get() #peticion
            if estado_act1!= estado_ant1:
                self.client.publish('LUCES/TIPO1',estado_act1)
            elif estado_act2!= estado_ant2:
                 self.client.publish('LUCES/TIPO2',estado_act1)
            elif estado_act3!= estado_ant3:
                self.client.publish('LUCES/TIPO3',estado_act1)
            else:
                pass
            estado_ant1=estado_act1    
            estado_ant2=estado_act2   
            estado_ant3=estado_act3   
            sleep(0.4)       


def main():
    print ('START !')
    FB = FIREB()

    subproceso_preps = Thread(target=FB.prescripcion)
    subproceso_preps.daemon = True
    subproceso_preps.start()
    
    subproceso_RIEGO = Thread(target=FB.RIEGO_APLICATION)
    subproceso_RIEGO.daemon = True
    subproceso_RIEGO.start()
    

    subproceso_valvs = Thread(target=FB.VALVULAS)
    subproceso_valvs.daemon = True
    subproceso_valvs.start()
    


    subproceso_luces = Thread(target=FB.LUCES)
    subproceso_luces.daemon = True
    subproceso_luces.start()


    signal.pause()

    print

    



if __name__ == '__main__':
    main()
 
sys.exit(0)



