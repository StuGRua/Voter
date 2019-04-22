import pymysql
db = pymysql.connect("localhost", "root", "aA_iul453_bB", "test0")

def write_in_info(sql):
    print('sql received================',sql)
    sql = str(sql.strip())
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        print('fix success')
    except:
        print('writeininfo error')

if __name__ == '__main__':
    exit()
    
    