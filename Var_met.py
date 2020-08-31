import json
import requests
import sys

def main():
    resp = requests.get('http://104.248.53.140/SeverGet.php/?hour=1')
    data=json.loads(resp.content)

    print(data[-1])

    



if __name__ == '__main__':
    main()
 
sys.exit(0)
