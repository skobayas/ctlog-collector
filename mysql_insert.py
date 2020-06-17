# 見通しが悪いなぁ
# ファイル分割の方針を貫かないといかんな

# 別途flask化するか

# https://qiita.com/valzer0/items/2f27ba98397fa7ff0d74

import requests
import mysql.connector as mydb
import mysql
import datetime
import json

from get_ctlog import get_ctlog_sub,get_domain_last_update

def to_csv_str(arr):
    return (',').join(arr)

def get_ctlog(domain,prod=False,force=False):

    # まだ見通しが悪いな

    #    入力：domain
    #    出力："no need update" or "結果"

    # 日付を確認
    if force == True:
        # 本当であればreturnせずにファイルに書くべき
        # さらに言えばdbに書くべき
        # と思ったが、dbに書くのは別ルーチンなので、これはこれで単にreturnすればいい
        prod=prod
        return get_ctlog_sub(domain,prod=prod,force=True)
    else:
        last_update = get_domain_last_update(domain)
        if last_update < -7:
            print('outdated or not found record for such domain, need to update')
            # 本当であればreturnせずにファイルに書くべき
            # さらに言えばdbに書くべき
            # と思ったが、dbに書くのは別ルーチンなので、これはこれで単にreturnすればいい
            return get_ctlog_sub(domain,prod=True,force=False)
            #
        else:
            # json-stringで返す
            # {[]}
            return json.dumps([{'message':'No need to update'}])

def insert_ctlog(ctlog):
    #    入力：res
    #    出力：OK/NG

    #   table:
    #       domain_update
    #       certs
    # ctlog = json.loads(ctlog_json)

    connection = mydb.connect(
        host='127.0.0.1',
        port='3306',
        user='root',
        password='mysql',
        database='ctlog_certs'
    )

    connection.ping(reconnect=True)
    cursor = connection.cursor()

    # domain更新日付の更新
    domain = ctlog[-1]['domain']

    cursor.execute("SELECT last_update FROM domain_update WHERE domain=%s", (domain,))
    result = cursor.fetchone()

    if result == None:
        cursor.execute("INSERT INTO certs.domain_update VALUE (%s, %s)",(domain,datetime.date.today()))
    else:
        cursor.execute("UPDATE domain_update SET last_update=%s WHERE domain=%s", (datetime.date.today(), domain))

    # Need update
    # domainカラムの追加と、このrecord追加処理の追加

    # 実質の処理
    for item in ctlog:
        try:
            cursor.execute(
                "INSERT INTO certs VALUES (%s,%s,%s,%s,%s,%s,%s)", (item['id'],to_csv_str(item['dns_names']),item['issuer']['name'],item['not_before'],item['not_after'],item["cert"]["data"],domain)
            )
        except mysql.connector.errors.IntegrityError as e:
            print ('The record {0} exits already, pass it'.format(item['id']))

    # cursor.execute("SELECT * FROM certs")
    # rows = cursor.fetchall()

    connection.commit()
    cursor.close()
    connection.close()

def upsert_ctlog(domain, prod=False,force=False):
    # ctlog_json = get_ctlog('amazon.co.jp')
    # ctlog_json = get_ctlog('facebook.com')
    prod=prod
    force=force
    ctlog_json = get_ctlog(domain,prod=prod,force=force)
    ctlog = json.loads(ctlog_json)

    # debugとキャッシュファイル作成用
    # print(ctlog)

    if ctlog == []:
        print ('does not get ctlog')
    elif 'message' in ctlog[-1]:
        print (ctlog[-1]['message'])
    else:
        insert_ctlog(ctlog)

upsert_ctlog('appfw.net',prod=True,force=True)
# upsert_ctlog('',prod=False,force=True)

# force=Trueが期待通り動かんね
# 詰めないといかん
# ひとまず何とかなったかな？