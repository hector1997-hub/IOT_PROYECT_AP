import sys
from time import sleep
import signal
from gpiozero import LED, Button
from threading import Thread
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import ssl
import paho.mqtt.client

###############FLAGS##################################

FLAGS_VALVS = {"VALVI":"FALSE","VALVR":"FALSE","LIGTH":"FALSE"}




#########VARIABLES FIREBASE ###########################
PAHT_CRED = '/home/pi/Desktop/IOT/culterapp.json'
URL_DB = 'https://culterapp.firebaseio.com/'
REF_CULT='CULTIVO'
REF_LUZ = 'LUCES'
REF_TIPO='TIPO'
REF_SENS = 'SENSORES'
REF_SENSOR1= 'SENSOR1'
REF_SENSOR2='SENSOR2'
REF_SENSOR3='SENSOR3'
REF_SENS_N = 'SENSORES_NIVEL'
REF_SN1='S_N1'
REF_SN2='S_N2'
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

        cred = credentials.Certificate(PAHT_CRED)

        firebase_admin.initialize_app(cred, {

            'databaseURL': URL_DB

        })

        self.refcultivo=db.reference(REF_CULT)

        self.refluz = self.refcultivo.child(REF_LUZ)
        self.reftipo = self.refluz.child(REF_TIPO)

        self.refsens=self.refcultivo.child(REF_SENS)
        self.refsens1=self.refsens.child(REF_SENSOR1)    
        self.refsens2=self.refsens.child(REF_SENSOR2) 
        self.refsens3=self.refsens.child(REF_SENSOR3) 

        self.refsens_niv=self.refcultivo.child(REF_SENS_N)
        self.refsn1=self.refsens_niv.child(REF_SN1)
        self.refsn2=self.refsens_niv.child(REF_SN2)

        self.refuser=self.refcultivo.child(REF_USER)
        self.refp_1=self.refsens_niv.child(REF_PASS1)
        self.refu_1=self.refuser.child(REF_USER1)
        
        self.refvalvsi=self.refcultivo.child(REF_VALVSI) 
        self.refvali=self.refvalvsi.child(REF_VAL1)

        self.refvalvsr=self.refcultivo.child(REF_VALVSR) 
        self.refvalr=self.refvalvsr.child(REF_VAL2)


        client =paho.mqtt.client.Client(client_id='ESTACION_P', clean_session=False)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(host='192.168.1.64', port=1883)
        client.loop_start()


    def LUCES(self):
        estado_anterior = self.reftipo.get()

        while True:
            estado_actual = self.reftipo.get() #peticion
            if estado_actual!= estado_anterior:
                print('luces = '+ str(estado_actual)) 
                
            estado_anterior=estado_actual    
            sleep(0.4)


    def VALVULAS(self):
        prev_S_VI = self.refvali.get()
        prev_S_VR = self.refvalr.get()
        while True:
            act_S_VI = self.refvali.get() #peticion
            act_S_VR = self.refvalr.get()

            if prev_S_VI != act_S_VI:
                print('VALVI = '+ str(act_S_VI))  
                FLAGS_VALVS["VALVI"]=act_S_VI
            if prev_S_VR != act_S_VR:  
                print('VALVR = '+ str(act_S_VR))
                FLAGS_VALVS["VALVR"]=act_S_VI               
            prev_S_VI=act_S_VI
            prev_S_VR=act_S_VR 
            sleep(0.4)

    def on_connect(self,client, userdata, flags, rc):
        print('connected (%s)' % client._client_id)
        client.subscribe(topic='SENSOR1', qos=2)

    def on_message(self,client, userdata, message):
        print('------------------------------')
        print('topic: %s' % message.topic)
        print('payload: %s' % message.payload)
        print('qos: %d' % message.qos)   
        if(message.topic=="SENSOR1"):
            print("llego", str(message.payload))
            self.sen=str(message.payload)
            self.refsens1.set(self.sen[2:len(self.sen)-1])





def main():
    print ('START !')
    FB = FIREB()

    subproceso_valvs = Thread(target=FB.VALVULAS)
    subproceso_valvs.daemon = True
    subproceso_valvs.start()
    

    subproceso_luces = Thread(target=FB.LUCES)
    subproceso_luces.daemon = True
    subproceso_luces.start()
    signal.pause()

    

    



if __name__ == '__main__':
    main()
 
sys.exit(0)



