import pymysql
db = pymysql.connect("localhost", "root", "aA_iul453_bB", "test0")


def loginer(uname,upass):
    if uname =='':
        print('no usrname')
        return 0
    cursor = db.cursor()
    sql = "SELECT password FROM users WHERE username='%s'" % uname
    #print(sql)

    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
    except:
        print('fetch password error')
    if result == ():
        return 0
    password = result[0][0]
    if str(upass) == str(password):
        print('ok')
        return 1
    else:
        print('bad')
        return 0



def signiner(uname,upass):
    cursor = db.cursor()
    sql = "SELECT username FROM users WHERE username='%s'" % uname
    cursor.execute(sql)
    if cursor.fetchall() == ():
        sql = "INSERT INTO users (username,password,validator) VALUES ('%s','%s',0)" % (uname,upass)
        #print(sql)
        try:
            cursor.execute(sql)
            print('sigin in ok')
            return 1
        except:
            print('signin database error')
        return 0
    else:
        print('username already exist')
        return -1


def getusertable(username):
    cursor = db.cursor()
    sql = """select * from users where username = '%s'"""%username
    try:
        cursor.execute(sql)
        print('get usertable ok')
    except Exception as exception:
        print(exception)
    result = cursor.fetchone()
    print(result)
    if result == None:
        return ['None']
    tables = str(result[5])
    #tableset = str(tables).split('&')
    print(tables)
    return tables


def updusertable(username,table):
    table = str(table)+'&'
    cursor = db.cursor()
    extable = getusertable(username)
    print('=====================',extable)
    if extable == 'None':
        extable = ''
    table = extable + str(table)
    print('-------------------',table)
    sql = """update users set tables = '%s' where username = '%s'"""%(table,username)
    print(sql)
    try:
        cursor.execute(sql)
        print('upd usertable ok')
        return 1
    except Exception as e:
        print(e)
        return 0


def popusertable(username,table):
    #print('received:',username,table)
    extable = getusertable(username)
    #print(extable)
    table = str(table)+'&'
    #print(table)
    table = extable.replace(table,'')
    #print('new usertable=================',table)
    cursor = db.cursor()
    sql = """update users set tables = '%s' where username = '%s'"""%(table,username)
    print(sql)
    try:
        cursor.execute(sql)
        print('pop usertable ok')
        return 1
    except Exception as e:
        print(e)
        return 0


def stopper(tableid):
	cursor = db.cursor()
	sql = """update tab1info set ENDTIME=19991001012359 where tableid = %d;"""%tableid
	#print(sql)
	#cursor.execute(sql)
	try:
		cursor.execute(sql)
		print('stop ok')
	except:
		print('stop fail')
		return 0
	return 1


def resumer(tableid):
	cursor = db.cursor()
	sql = """update tab1info set ENDTIME=20291001012359 where tableid = %d;"""%tableid
	print(sql)
	#cursor.execute(sql)
	try:
		cursor.execute(sql)
		print('resume ok')
	except:
		print('resume fail')
		return 0
	return 1
	

def saveip(ip,tablename):
    cursor = db.cursor()
    #先检查有没有已有记录
    sql = """select * from iptable where ip = '%s';"""%(ip)
    #print(sql)
    try:
        cursor.execute(sql)
    except:
        print('get existing ip fail')
        return 0
    result = cursor.fetchone()
    #print(result)
    if result == None:
        sql = """insert into iptable (ip,tables)values('%s','%s');"""%(ip,tablename+'&')	
        #print(sql)
        try:
            cursor.execute(sql)
            print('save ip ok')
        except:
            print('save ip fail')
            return 0
        return 1
    else:
        extab = str(result[2])
        extab += str(tablename)
        extab += str('&')
        sql = """update iptable set tables='%s' where ip = '%s';"""%(extab,ip)
        #print(sql)
        try:
            cursor.execute(sql)
            print('update ip ok')
        except:
            print('update ip fail')
            return 0


def checkip(ip,tablename):
    cursor = db.cursor()
    sql = """select * from iptable where ip = '%s';"""%(ip)
    try:
        cursor.execute(sql)
    except:
        print('get existing ip fail')
        return 0
    result = cursor.fetchone()
    #print(result)
    if result == None:
        return 1
    tables = str(result[2])
    if tables.find(str(tablename)+'&') == -1:
        return 1
    else:
        return 0
    return 0

	
	
def gettime(tableid,arg2):
    cursor = db.cursor()
    opt = int(arg2)
    if opt == 1:
        sql = """select STARTTIME from tab1info where tableid = %d;"""%tableid
    elif opt == 2:
        sql = """select ENDTIME from tab1info where tableid = %d;"""%tableid
    else:
        print('gettime error(arg2 invalid)')
        return 0
    #print(sql)
    try:
        cursor.execute(sql)
        print('try get time ok')
        result = cursor.fetchall()
        endtime = str(result[0][0])
        #print(endtime)
    except:
        print('get time error')
        return 0
    return endtime
	
	
	
def newtable(tablename):
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS %s"% tablename)

    sql = """CREATE TABLE %s (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY ,
            CANDIDATE VARCHAR(127) NOT NULL,
            DETAIL VARCHAR(255),
            GRADE INT DEFAULT 0,
            SEX CHAR(1) DEFAULT'm',
            CREATETIME TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            VOTES INT DEFAULT 0) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;"""% tablename 
    #print(sql)
    try :
        cursor.execute(sql)
        print('new table success')
    except:
        print('create table error')
        return -1
    return 1


def deletetable(tablename,id):
    cursor = db.cursor()
    sql = "DROP TABLE %s"% tablename
    try:
        cursor.execute(sql)
        print('drop table'+tablename+'success')
    except:
        print('drop table'+tablename+'fail')
        return -8
    sql = "DELETE FROM %s WHERE tableid=%d" % ('tab1info',int(id))
    #print(sql)
    try:
        cursor.execute(sql)
        print('remove info success')
    except:
        print('remove info fail')
        return -9
    return 0


def add1(tablename,candidate,detail,grade,sex,votes):
    #db = pymysql.connect("localhost", "root", "root", "test0")
    db = pymysql.connect("localhost", "root", "aA_iul453_bB", "test0")
    cursor = db.cursor()
    sql = "INSERT INTO %s (CANDIDATE,DETAIL,GRADE,SEX,VOTES) VALUES ('%s','%s','%d','%s','%d')" %(tablename,candidate,detail,grade,sex,votes)
    sql = str(sql)
    #print(sql)
    '''
    try:
        cursor.execute(sql)
        cursor.commit()
        print('add 1 success')
    except:
        print('add 1 error')
        return -7
    '''
    #cursor.execute(sql)
    return sql


def updatewhencreate(tableid,len,normal_acc,title,subtitle,starttime,endtime,minvote,maxvote):
    #db = pymysql.connect("localhost", "root", "root", "test0")
    cursor = db.cursor()
    sql ="INSERT INTO %s (tableid,len,normal_acc,Title,subtitle,STARTTIME,ENDTIME,minvote,maxvote) VALUES('%d','%d','%d','%s','%s','%d','%d','%d','%d')" \
          %('tab1info',tableid,len,normal_acc,title,subtitle,starttime,endtime,minvote,maxvote)
    #print(sql)
    try:
        cursor.execute(sql)
        print('updatewhencreate success')
    except:
        print('update on create error')
        return -6
    return 1


def getallinfo():
    #db = pymysql.connect("localhost", "root", "root", "test0")
    cursor = db.cursor()
    sql = "SELECT * FROM %s" % 'tab1info'
    # print(sql)
    tableidset = []
    tablelenset = []
    normal_accset = []
    titleset = []
    subtitleset = []
    starttimeset = []
    endtimeset=[]
    minvoteset = []
    maxvoteset = []
    allinfo = [tableidset,tablelenset,normal_accset,titleset,subtitleset,starttimeset,endtimeset,minvoteset,maxvoteset]
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        # print(results)
        resultlen = len(results)
        for i in range(0, resultlen):
            result = results[i]
            tableidset.append(result[0])
            tablelenset.append(result[1])
            normal_accset.append(result[2])
            titleset.append(result[3])
            subtitleset.append(result[4])
            starttimeset.append(result[5])
            endtimeset.append(result[6])
            minvoteset.append(result[7])
            maxvoteset.append(result[8])
        #print(allinfo)
        return allinfo
    except:
        print('getallinfo error')
        return -5


def gettableinfo(table):
    #db = pymysql.connect("localhost", "root", "root", "test0")
    cursor = db.cursor()
    sql = "SELECT * FROM %s" % (str(table))
    #print(sql)
    tableidset = []
    tablelenset = []
    normal_accset = []
    titleset = []
    subtitleset = []
    starttimeset = []
    endtimeset = []
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        #print(results)
        resultlen = len(results)
        for i in range(0,resultlen):
            result = results[i]
            tableidset.append(result[0])
            tablelenset.append(result[1])
            normal_accset.append(result[2])
            titleset.append(result[3])
            subtitleset.append(result[4])
            starttimeset.append(result[5])
            endtimeset.append(result[6])
        result = results[0]
        #print(result)
        tableid = result[0]
        tablelen = result[1]
        normal_acc = result[2]
        title = result[3]
        subtitle = result[4]
        #print(tableidset,tablelenset,normal_accset,titleset,subtitleset)
        return (tableidset,tablelenset,normal_accset,titleset,subtitleset,starttimeset,endtimeset)
    except:
        print('fetchallinfo error')
        return -1


def updtableinfo(table):
    #db = pymysql.connect("localhost", "root", "root", "test0")
    cursor = db.cursor()
    sql = "UPDATE %s SET len = len +1 WHERE Title = 'titlenumber2'" % (table)
    # print(sql)
    try:
        cursor.execute(sql)
    except:
        print('updtableinfo error')
        return -4

    return 0


def fetchidandvote2(tablename,arg):
    info = gettableinfo('tab1info')
    tableid = tablename.split('tab')
    tableid = str(tableid[1])
    #print('tableid',tableid)
    #print('info',info)
    idlist = info[0]
    #print(idlist)
    place = idlist.index(int(tableid))
    tablen = info[1][place]
    #print(tablen)
    candidates = []
    db = pymysql.connect("localhost", "root", "aA_iul453_bB", "test0")
    cursor = db.cursor()
    for i in range(1,tablen+1):
        sql = "SELECT %s FROM %s WHERE id = %s"% (arg,tablename,i)
        #print(sql)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            #print(results)
            result = results[0]
            result = result[0]
            #print(result)
            candidates.append(result)
        except:
            print("error: fetchids fail")
            return -2
        #print(str(candidates))
    return candidates


def upd1(tablename,value):
    #db = pymysql.connect("localhost", "root", "root", "test0")
    cursor = db.cursor()
    sql = "UPDATE %s SET votes = votes +1 WHERE CANDIDATE = '%s'" % (tablename,value)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        print('upd ok')
        return 1
    except:
        print("upd err")
        return -2


def fetchdetails(tablename):
    details = []
    info = gettableinfo('tab1info')
    tableid = tablename.split('tab')
    tableid = str(tableid[1])
    idlist = info[0]
    place = idlist.index(int(tableid))
    tablen = info[1][place]
    db = pymysql.connect("localhost", "root", "aA_iul453_bB", "test0")
    cursor = db.cursor()
    for i in range(1,tablen+1):
        sql = "SELECT DETAIL FROM %s WHERE id = %s" %(tablename,i)
        #print(i)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            result = results[0]
            result = result[0]
            details.append(result)
        except:
            print("bad fetch details")
            return -3
    #print(details)
    return details



db = pymysql.connect("localhost","root","aA_iul453_bB","test0")

if __name__ == '__main__':
    #fetchdetails('tab2')
    #getusertable('123')
    #updusertable('wtf','tab10')
    popusertable('hello','tab10')
    #newtable()
    #add1()
    #updtableinfo('tab1info')
    #fetch1()
    #upd1('timothee')
    #gettableinfo('tab1info')
    #fetchids()
    #fetchidandvote2('tab17','CANDIDATE')
    #voteinfo()
    #fetchdetails()
    #getallinfo()
    #newtable('tab2')
    #newtable('tab3')
    #add1('tab3','toppod','topodDETAILLLLLL',4,'m',0)
    #updatewhencreate(3,3,0,'to','io',0,0)
    #signiner('wut','rld')
    #loginer('hello','world')
    #saveip('13.123.123.123','tab9')

    exit()