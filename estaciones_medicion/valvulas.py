#Librerias
import time
import ubinascii
from umqttsimple import MQTTClient
from machine import unique_id,Pin
import machine
from machine import Timer
import micropython
import network
import boot
import utime


ssid = 'UNE_HFC_2203'  #Nombre de la Red
password = 'P4BK0PJ2' #Contrasena de la red
wlan = network.WLAN(network.STA_IF)

wlan.active(True) #Activa el Wifi
wlan.connect(ssid, password) #Hace la conexi鐠愮珱

while wlan.isconnected() == False: #Espera a que se conecte a la red
    pass

#print('Conexion con el WiFi %s establecida' % ssid)
#print(wlan.ifconfig()) #Muestra la IP y otros datos del Wi-Fi
#Entradas y salidas
led = Pin(2, Pin.OUT)
RELE=Pin(23, Pin.OUT)
rojo1=Pin(13,Pin.OUT)
verde1=Pin(12,Pin.OUT)
azul1=Pin(14,Pin.OUT)
rojo2=Pin(27,Pin.OUT)
verde2=Pin(26,Pin.OUT)
azul2=Pin(25,Pin.OUT)
rojo3=Pin(33,Pin.OUT)
verde3=Pin(32,Pin.OUT)
azul3=Pin(23,Pin.OUT)
rele_p=Pin(15,Pin.OUT)
act_pa=Pin(22,Pin.OUT)
act_pb=Pin(23,Pin.OUT)
rele_p.on()
act_pb.off()
act_pa.off() 
triggerPort = 32
echoPort = 33
FLAG_V=False
timer_a=Timer(0)
interruptCounter=0
time_irrg=0

def valv_actd(action):
    if action=="ON":
        led.on()
        RELE.off()
                
    elif action=="OFF":
        led.off() 
        RELE.off()

    act_pb.off()
    act_pa.off()  
    
def ultrasonido():
    trigger = machine.Pin(15, machine.Pin.OUT)
    echo = machine.Pin(14, machine.Pin.IN)
    print("Ultrasonic Sensor. Trigger Pin=%d and Echo Pin=%d" % (triggerPort, echoPort))
    trigger.off()
    while True:
      # short impulse 10 microsec to trigger
      trigger.on()
      time.sleep_us(10)
      trigger.off()
      count = 0
      start = time.ticks_us() # get time in usec
      # Now loop until echo goes high
      while echo.value() == 0:
          pass
      t1 = utime.ticks_us()
      while echo.value() == 1:
          pass
      t2 = utime.ticks_us()      
      duration=t2-t1
      #duration = time.ticks_diff(time.ticks_us(),start) # compute time difference
      print("Duration: %f" % duration)

      # After 38ms is out of range of the sensor
      if duration > 38000 :
          print("Out of range")
          continue

      # distance is speed of sound [340.29 m/s = 0.034029 cm/us] per half duration
      distance = duration/58
      print("Distance: %f cm" % distance)
      time.sleep(2)
      return distance
def handleInterrupt(timer):
  global interruptCounter,time_irrg,FLAG_V
  if time_irrg>0 and interruptCounter>=time_irrg :
        timer_a.deinit()
        client.publish(b'tanque/valvr', b''+"OK;"+str(interruptCounter))
        valv_actd("OFF")
        time_irrg=0
        interruptCounter=0
        FLAG_V=False
        
  else:      
      interruptCounter = interruptCounter+1             

def form_sub(topic, msg):
    global time_irrg,FLAG_V,timer_a,interruptCounter
    if topic.decode() == "VALV/VALV2":
        #print ('message received: ' , msg.decode())
        mens=msg.decode()
        if mens=="OFF" and FLAG_V==True:
            timer_a.deinit()
            client.publish(b'tanque/valvr', b''+"OK;"+str(interruptCounter))
            valv_actd("OFF") 
            time_irrg=0
            interruptCounter=0
            FLAG_V=False
        elif mens=="ON_A" and FLAG_V==False:
            valv_actd("ON") 
            time_irrg=0
            interruptCounter=0
            FLAG_V=True          
        else:
            mens=mens.split(";")
            #print(mens)
            if mens[0]=="ON":
                #print("time:"+str(mens[1]))
                time_irrg=float(str(mens[1]))
                FLAG_V=True
                valv_actd("ON")
                timer_a.init(period=1, mode=machine.Timer.PERIODIC, callback=handleInterrupt)
                
    elif topic.decode() == "LUCES/TIPO1":
      mens=msg.decode()
      if mens=="ROJO":
          print("topico luces/1 color rojo")
          rojo1.off()
          verde1.on()
          azul1.on()
      elif mens=="AZUL":
          print("topico luces/1 color AZUL")
          rojo1.on()
          verde1.on()
          azul1.off()
      elif mens=="AMARILLO":
          print("topico luces/1 color AMARILLO")
          rojo1.off()
          verde1.off()
          azul1.on()  
      else:
          print("topico luces/1 color apagado")
          rojo1.on()
          verde1.on()
          azul1.on()  
    elif topic.decode() == "LUCES/TIPO2":
      mens=msg.decode()
      if mens=="ROJO":
          print("topico luces/2 color rojo")
          rojo2.off()
          verde2.on()
          azul2.on()
      elif mens=="AZUL":
          print("topico luces/2 color AZUL")
          rojo2.on()
          verde2.on()
          azul2.off()
      elif mens=="AMARILLO":
          print("topico luces/2 color AMARILLO")
          rojo2.off()
          verde2.off()
          azul2.on()  
      else:
          print("topico luces/2 color apagado")
          rojo2.on()
          verde2.on()
          azul2.on()
    elif topic.decode() == "LUCES/TIPO3":
      mens=msg.decode()
      if mens=="ROJO":
          print("topico luces/3 color rojo")
          rojo3.off()
          verde3.on()
          azul3.on()
      elif mens=="AZUL":
          print("topico luces/3 color AZUL")
          rojo3.on()
          verde3.on()
          azul3.off()
      elif mens=="AMARILLO":
          print("topico luces/3 color AMARILLO")
          rojo3.off()
          verde3.off()
          azul3.on()  
      else:
          print("topico luces/1 color apagado")
          rojo3.on()
          verde3.on()
          azul3.on()

#Funcion que conecta y se suscribe a MQTT
def Conexion_MQTT():
    client_id = ubinascii.hexlify(unique_id())
    mqtt_server = '192.168.1.64'
    port_mqtt = 1883
    user_mqtt = None 
    pswd_mqtt = None
    client = MQTTClient(client_id, mqtt_server,port_mqtt,user_mqtt,pswd_mqtt) 
    client.set_callback(form_sub)
    client.connect()
    client.subscribe(b'VALV/VALV2')
    client.subscribe(b'LUCES/TIPO1')
    client.subscribe(b'LUCES/TIPO2')
    client.subscribe(b'LUCES/TIPO3')
    #print('Conectado a %s' % mqtt_server)
    return client

#Reinicia la conexion de MQTT
def Reinciar_conexion():
    #print('Fallo en la conexion. Intentando de nuevo...')
    time.sleep(10)
    machine.reset()

def sens_capture(sens_h): 
    sens_h.atten(machine.ADC.ATTN_11DB)
    hum=(4.93*sens_h.read())/4095 
    return hum
    
try:
    client = Conexion_MQTT()
except OSError as e:
    Reinciar_conexion()

  
def main():
    t=0
    global interruptCounter,time_irrg
    
    
    while True:
        try:
            if(t==60):
             print(".")
             #sens_h1= machine.ADC(machine.Pin(32))
             #sens_h2= machine.ADC(machine.Pin(32))
             #sens_h3= machine.ADC(machine.Pin(35))
             #hum_1 =sens_capture(sens_h1)
             #hum_2 =sens_capture(sens_h2)
             #hum_3 =sens_capture(sens_h3)
             #client.publish(b'cultivo/humedad_1', b''+str(hum_1))
             #client.publish(b'cultivo/humedad_2', b''+str(hum_2))
             #client.publish(b'cultivo/humedad_3', b''+str(hum_3))
             
            # distancia=ultrasonido()
             #nivel=100-distancia
             #print(nivel)
             #if(nivel<0):
             # nivel=0
             #else:
             # nivel=nivel
             # client.publish(b'tanque/sens_1', b''+str(nivel))
             #t=0
            else:     
             client.check_msg()
             t+=1
             time.sleep(1) 
            
            #time.sleep(1)         
        except OSError as e:
         Reinciar_conexion()
         
if __name__ == '__main__':
    main()
 
sys.exit(0)


