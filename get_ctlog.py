import requests
import json
from certspotter.api import CertSpotter
import mysql.connector as mydb
import mysql
import datetime

with open('.cred') as CRED:
    API_KEY = CRED.read()

def update_domain_last_update(domain):

    connection = mydb.connect(
        host='127.0.0.1',
        port='3306',
        user='root',
        password='mysql',
        database='certs'
    )

    connection.ping(reconnect=True)
    cursor = connection.cursor()
    # cursor.execute("UPDATE domain_update SET last_update=%s WHERE domain=%s", (datetime.date.today(),domain))
    # cursor.execute("UPDATE domain_update SET last_update=%s", (datetime.date.today(),))
    # またしてもうまくないな
    # バッククォートかと思ったが、それはないっぽい
    # ただ、考えたくないからアンダースコアは使用禁止だな
    # と思ったが、単にcommitしてないだけ？
    # そのようで
    #

    cursor.execute("UPDATE domain_update SET last_update=%s WHERE domain=%s", (datetime.date.today(),domain))

    cursor.execute("SELECT * FROM domain_update")

    results = cursor.fetchall()
    for item in results:
        print (item)

    connection.commit()
    cursor.close()
    connection.close()

def get_domain_last_update(domain):

    connection = mydb.connect(
        host='127.0.0.1',
        port='3306',
        user='root',
        password='mysql',
        database='certs'
    )

    connection.ping(reconnect=True)
    cursor = connection.cursor()
    cursor.execute("SELECT last_update FROM domain_update WHERE domain=%s", (domain,))
    result = cursor.fetchone()

    if result == None:
        return -999

    return (result[0] - datetime.date.today()).days

def get_ctlog_api(domain):
    api = CertSpotter(API_KEY)

    # rate-limitが収まってからテストして
    # loopを追記すべき
    # Done

    subdomains, retryinsec = api.getdomains(domain)

    #
    results=[]
    while len(subdomains)!=0:
        results+=subdomains
        after_id=subdomains[-1]['id']
        subdomains, retryinsec = api.getdomains(domain,after=after_id)
    #

    for item in results:
        item['domain'] = domain
    return json.dumps(results)


def get_ctlog_sub(domain,prod=False,force=False):
    if prod==True:
        return get_ctlog_api(domain)
    else:
        print ('return from file')
        # s3から取得するのではなくローカルファイルから取得するように
        try:
            with open(domain + '.json') as f:
                results = json.load(f)
        except FileNotFoundError:
            if prod==True:
                print ('File not found! try to get online')
                api_results = get_ctlog_api(domain)
                #
                # print (api_results)
                return api_results
            else:
                print('File not found!')
                print('To get via API, call with prod=True')
                exit(1)

        for item in results:
            if not ('domain' in item):
                item['domain'] = domain

        return json.dumps(results)

def get_ctlog(domain,prod=False,force=False):
    # 日付を確認
    if force==True:
        # 本当であればreturnせずにファイルに書くべき
        # さらに言えばdbに書くべき
        # と思ったが、dbに書くのは別ルーチンなので、これはこれで単にreturnすればいい
        return get_ctlog_sub(domain,prod=True,force=True)
    else:
        last_update = get_domain_last_update(domain)
        if last_update < -7:
            print ('outdated or not found record for such domain, need to update')
            # 本当であればreturnせずにファイルに書くべき
            # さらに言えばdbに書くべき
            # と思ったが、dbに書くのは別ルーチンなので、これはこれで単にreturnすればいい
            return get_ctlog_sub(domain,prod=prod,force=False)
            #
        else:
            return 'No need to update'


# print (get_ctlog('amazon.co.jp',force=True))

# print (get_ctlog('facebook.com'))

# print (get_ctlog('vsdj.jp'))

# update_domain_last_update("amazon.com")

if __name__ == '__main__':
    print (get_ctlog('appfw.net',prod=True))

