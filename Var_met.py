import json
import requests
import sys

def main():
    resp = requests.get('http://104.248.53.140/SeverGet.php/?hour=1')
    data=json.loads(resp.content)
    met_dat=open("/home/pi/IOT_PROYECT_AP/data_meterorologica.txt","a")
    met_dat.write(data[-1]['Date_Time']+";"+data[-1]['Rain_daily']+";"+data[-1]['ET_daily']+";\n")
    met_dat.close()
    #print(data[-1])


if __name__ == '__main__':
    main()
 
sys.exit(0)
