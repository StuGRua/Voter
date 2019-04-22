from flask import Flask,render_template,request,url_for,make_response,session,redirect,jsonify
from sqlcon import upd1,fetchidandvote2,gettableinfo,fetchdetails,getallinfo,updatewhencreate,newtable,add1,deletetable\
    ,signiner,loginer,stopper,gettime,resumer,saveip,checkip,getusertable,updusertable,popusertable
import pymysql
import os
import re
import shutil
from fixer import write_in_info
from io import BytesIO
from flask import flash
import json
import random
import time,datetime
from validation import validate_picture

db = pymysql.connect("localhost", "root", "aA_iul453_bB", "test0")
voter = Flask(__name__)
voter.secret_key = 'some_secret'
namelist = str(fetchidandvote2('tab1','CANDIDATE'))
if namelist == -1:
    print('namelist error')
    exit(-1)

def makekey(length):
    key=''
    for i in range(0,length):
        temp = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
        key = key+str(temp)
    print(key)
    return str(key)


def nameli(tablename):
    namelist = str(fetchidandvote2(tablename,'CANDIDATE'))
    return namelist


def namelistlist(tablename):
    namelist = fetchidandvote2(tablename,'CANDIDATE')
    return namelist


tableinfo = gettableinfo('tab1info')
tableid = tableinfo[0]
tablelen = tableinfo[1]
normal_acc = tableinfo[2]
tabletitle = tableinfo[3]
subtitle = tableinfo[4]
#print(getallinfo())
#1 = can view; 0 = cannot view
#print(normal_acc)


def stripit(string):
    string = string.strip()
    string = re.sub('[\r\n\t]', '', string)
    string = re.sub('[#$%^@&*/<>.,|\]\[{}()=-?`;:]', '', string)
    string = string.replace(' ','')
    string = string.replace('\'','')
    string = string.replace('\"','')
    #print(string)
    return string



@voter.route('/')
def home():
    db = pymysql.connect("localhost", "root", "aA_iul453_bB", "test0")
    ip = request.remote_addr
    svtime = datetime.datetime.now()
    nologin = 0
    logout = 0
    if str(request.values.get('logout')) == '1':
        logout = 1
    if str(request.values.get('nologin')) == '1':
        nologin = 1
    return render_template("choose_main.html",userip = ip,datetime=svtime,nologin=nologin,\
        logout = logout)


@voter.route('/timeapi',methods=["GET","POST"])
def timeapi():
    svtime = str(datetime.datetime.now())
    return jsonify({"result":svtime})
    

@voter.route('/validator/<id>',methods=["GET","POST"])
def captcha_make(id):
    image, str = validate_picture()
    print(str)
    print(id)
    # 将验证码图片以二进制形式写入在内存中，防止将图片都放在文件夹中，占用大量磁盘
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把二进制作为response发回前端，并设置首部字段
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # 将验证码字符串储存在session中
    session['image'] = str
    return response


@voter.route('/sjoke')
def sjoke():
    return render_template('sjoke.html')

    
@voter.route('/notepad',methods=["GET","POST"])
def notepad():
    db = pymysql.connect("localhost", "root", "aA_iul453_bB", "test0")
    cursor = db.cursor()
    result = []
    if request.method == 'post':
        text = request.values.get('texts')
        sql = """INSERT INTO notepad (TEXTS) values (%s)"""%text
        print(sql)
        try:
            cursor.execute(sql)
            print('add ok')
        except:
            print('fuck up')
    sql2 = """select * from notepad"""
    print('sql2',sql2)
    try:
        cursor.execute('sql2')
        result = cursor.fetchall()
        print(result)
    except:
        print('fail')
    return render_template('notepad.html',result = result)


@voter.route('/login',methods=["GET","POST"])
def login():
    name = stripit(str(request.values.get('name')))
    psw = stripit(str(request.values.get('pass')))
    print(name,psw)
    if name == '' or name == None or psw == '' or psw == None:
        return render_template('choose_main.html')
    if str(name) == 'admin' and str(psw) == 'admin':
        tableset = getusertable(name)
        session['tableset'] = tableset
        return redirect(url_for('view'))
    elif loginer(name,psw) == 1:
        #session['key'] = makekey(24)
        session['username'] = name
        tableset = getusertable(name)
        #print(tableset)
        session['tableset'] = tableset
        return redirect(url_for('view'))
    else:
        return render_template('choose_main.html',wrongpsw=1)
    return 0


@voter.route('/signin' ,methods=["GET","POST"])
def signin():
    name = stripit(str(request.values.get('name')))
    psw = stripit(str(request.values.get('pass')))
    if name == '' or name == None or psw == '' or psw == None:
        return render_template('choose_main.html',wrongpsw=1)
    value = signiner(name,psw)
    if value==1:
        #session['key'] = makekey(24)
        session['username'] = name
        tableset = getusertable(name)
        session['tableset'] = tableset
        return redirect(url_for('view'))
    elif value==0:
        return render_template('choose_main.html',dberror=1)
    elif value== -1:
        return render_template('choose_main.html',duplicate=1)
    return 0


@voter.route('/view')
def view():
    username = session.get('username')
    abc = session.get('abcdefg')
    #print(type(username),type(abc))
    if type(username) == type(abc):
        return redirect(url_for('home',nologin = 1))
    resumeid = request.values.get('resumeid')
    stopid = request.values.get('stopid')
    tableset = session.get('tableset')
    #print('username is',username)
    #print('view tableset is',tableset)
    #print(type(tableset))
    if tableset == 'None':
        zero = [0,0]
        #print('we go here')
        return render_template('view.html', info=zero,notable = 1)
    tableset = tableset.replace('tab','')
    tableset = tableset.split('&')
    if tableset[-1] == '':
        tableset.remove('')
    #print('asdfasdf============',tableset)
    if tableset != ['None']:
        for item in tableset:
            item = int(item)
    #print('tableset received is ',tableset)
    allinfo = getallinfo()
    idlist = allinfo[0]
    if resumeid is not None:
        resumeid = int(resumeid)
    if stopid is not None:
        stopid = int(stopid)
    #print(resumeid,stopid)
    href = []
    delhref=[]
    managehref=[]
    stophref=[]
    resumehref=[]
    length = len(allinfo[0])
    #allinfo.append(length)
    localtime = time.time()
    starttimeset = []
    endtimeset = []
    newallinfo = []
    indexset = []
    addedset = []
    #print(allinfo)
    for i in range(0,len(allinfo[5])):
        if str(allinfo[0][i]) in tableset:
            stamp = time.mktime(allinfo[5][i].timetuple())
            starttimeset.append(stamp)
    #print(allinfo)
    for i in range(0,len(allinfo[6])):
        if str(allinfo[0][i]) in tableset:
            stamp = time.mktime(allinfo[6][i].timetuple())
            endtimeset.append(stamp)
    # print(allinfo)
    #print(starttimeset,endtimeset)
    #print(allinfo[5])
    for i in allinfo[0]:
        if str(i) in tableset:
            string = 'viewgen/' + '%s' % i
            href.append(string)
            string = 'delete?id=' + '%s' %i
            delhref.append(string)
            string = 'manage?id=' + '%s' %i
            managehref.append(string)
            string = 'stop?id=' + '%s' %i
            stophref.append(string)
            string = 'resume?id=' + '%s' %i
            resumehref.append(string)
    for i in range(0,len(allinfo)):
        newallinfo.append([])
        for j in range(0,len(tableset)):
            newallinfo[i].append([])
    for i in allinfo[0]:
        if str(i) in tableset:
            indexset.append(allinfo[0].index(i))
    #print('aaaaaaaaaaaaaaaaaa ',newallinfo)
    for i in range(0,len(allinfo)):
        for j in range(0,len(indexset)):
            m = int(indexset[j])
            #print('-----------------------',allinfo[i])
            newallinfo[i][j] = allinfo[i][m]
    
    newlength = len(indexset)
    newallinfo.append(newlength)
    #print('allinfo',allinfo)
    #print('newallinfo',newallinfo)
    return render_template('view.html', info=newallinfo,href = href,delhref = delhref,stophref=stophref,\
            managehref=managehref,resumehref=resumehref,resumeid = resumeid,stopid = stopid,localtime=localtime,\
                starttimeset = starttimeset,endtimeset = endtimeset,username = username)


@voter.route('/logout')
def logout():
    session.clear()
    name = session.get('username')
    print('clear?',name)
    return redirect(url_for('home',logout=1))


@voter.route('/manage')
def manage():
    
    if request.method=="post":
        return redirect(url_for('view'))
    id = int(request.values.get('id'))
    tablename = 'tab'+str(id)
    #print(tablename)
    allinfo = gettableinfo('tab1info')
    candidate = fetchidandvote2(tablename,'CANDIDATE')
    vote = fetchidandvote2(tablename,'VOTES')
    length = len(candidate)
    idset = allinfo[0]
    index = idset.index(int(id))
    title = allinfo[3][index]
    subtitle = allinfo[4][index]
    starttime = allinfo[5][index]
    endtime = allinfo[6][index]
    details = fetchdetails(tablename)
    return render_template('changegen.html',candidate = candidate,vote=vote,\
                           length=length,title = title,subtitle = subtitle,starttime = starttime,endtime=endtime,details = details)
                           
                           
@voter.route('/resume')
def resume():
    id = int(request.values.get('id'))
    #print(id)
    a = resumer(id)
    if a == 1:
        return redirect(url_for('view',resumeid=id))
    else:
        return render_template('hello.html')
		
		
@voter.route('/stop')
def stop():
    id = int(request.values.get('id'))
    #print(id)
    a = stopper(id)
    if a == 1:
        return redirect(url_for('view',stopid=id))
    else:
        return render_template('hello.html')


@voter.route('/viewgen/<id>')
def viewgen(id):
    username = session.get('username')
    abc = session.get('abcdefg')
    print(type(username),type(abc))
    if type(username) == type(abc):
        return redirect(url_for('home',nologin = 1))
    id = int(id)
    allinfo = getallinfo()
    if id not in allinfo[0]:
        return redirect(url_for('view'))
    tablename = 'tab'+str(id)
    print(tablename)
    allinfo = gettableinfo('tab1info')
    candidate = fetchidandvote2(tablename,'CANDIDATE')
    vote = fetchidandvote2(tablename,'VOTES')
    length = len(candidate)
    idset = allinfo[0]
    index = idset.index(int(id))
    title = allinfo[3][index]
    subtitle = allinfo[4][index]
    starttime = allinfo[5][index]
    endtime = allinfo[6][index]
    details = fetchdetails(tablename)
    return render_template('viewgen.html',candidate = candidate,vote=vote,\
                           length=length,title = title,subtitle = subtitle,starttime = starttime,endtime=endtime,details = details)


@voter.route('/delete')
def delete():
    username = session.get('username')
    abc = session.get('abcdefg')
    if type(username) == type(abc):
        return render_template('hello.html')
    id = request.values.get('id')
    tablename = 'tab'+str(id)
    deletetable(tablename,id)
    popusertable(username,tablename)
    return redirect(url_for('view'))


@voter.route('/create',methods=["GET","POST"])
def create():
    username = session.get('username')
    abc = session.get('abcdefg')
    print(type(username),type(abc))
    if type(username) == type(abc):
        return redirect(url_for('home',nologin = 1))
    return render_template('creator.html',username = username)


@voter.route('/createpost',methods=['GET','POST'])
def receive_create():
    username = session.get('username')
    abc = session.get('abcdefg')
    print(type(username),type(abc))
    if type(username) == type(abc):
        print('w are fucked')
        return render_template('hello.html')
    candidate = []
    details = []
    title = stripit(str(request.values.get('title')))
    subtitle = stripit(str(request.values.get('subtitle')))
    length = int(request.values.get('length'))
    starttime = int(request.values.get('starttime'))
    endtime = int(request.values.get('endtime'))
    minvote = int(request.values.get('minvote'))
    maxvote = int(request.values.get('maxvote'))
    for i in range(0,length):
        candidate.append(stripit(str(request.values.get(str('candidate'+str(i+1))))))
        details.append(stripit(str(request.values.get(str('detail'+str(i+1))))))
    #print(title,subtitle,candidate,details,starttime,endtime)
    info = getallinfo()
    print(info)
    idlist = info[0]
    idlist.sort()
    print(type(idlist))
    newid = int(idlist[-1])+1
    newtablename = 'tab'+str(newid)
    print(newtablename)
    try:
        if newtable(newtablename) != -1:
            for i in range(0, length):
                try:
                    if candidate[i] == None:
                        candidate[i] = 'none'
                    if details[i] == None:
                        details[i] = 'none'
                    write_in_info(add1(newtablename, candidate[i], details[i], grade=0, sex='m', votes=0))
                except:
                    print('error add1')

                try:
                    fname = 'f' + str(i + 1)
                    f = request.files[fname]
                    # filename = f.filename
                    filename = str(i + 1) + '.png'
                    print(filename)
                    # f.save(os.path.join('app/static',filename)
                    try:
                        os.mkdir('static/upload_pic/' + str(title))
                    except:
                        pass
                    if f.filename != '':
                        f.save('static/upload_pic/' + title + '/' + str(filename))
                        print('file saved', filename)
                    else:
                        shutil.copy('static/upload_pic/default.png', 'static/upload_pic/' + title + '/' + str(filename))
                        print('default img used')

                except:

                    print('file save fail')

            try:
                updatewhencreate(int(newid), length, 0, title, subtitle, starttime, endtime,minvote,maxvote)
            except:
                print('error updatewhencreate')
            try:
                updusertable(username,newtablename)
            except:
                print('error updating usertable')
            try:
                tableset = getusertable(username)
                session['tableset'] = tableset
            except:
                print('error getting new usertable')
            return redirect(url_for('view'))
        else:
            print('error creating  new table')
            return render_template('hello.html')
    except:
        deletetable(newtablename,newid)
        print('total fuck up')
        return render_template('hello.html')
    
    
    return render_template('hello.html')


@voter.route('/votegen/<id>',methods=["GET","POST"])
def votegen(id):
    if request.method != "GET":
        return render_template("hello.html")
    else:
        #id = int(request.values.get('id'))
        id = int(id)
        allinfo = getallinfo()
        if id not in allinfo[0] :
            return render_template('hello.html')
        if request.values.get('captcha') is not None:
            captcha = 0
        else:
            captcha = 1
        ip = str(request.remote_addr)
        tablename = 'tab'+str(id)
        svtime1 = gettime(id,1)
        svtime2 = gettime(id,2)
        timeArray = time.strptime(svtime1, "%Y-%m-%d %H:%M:%S")
        svstarttimestamp = time.mktime(timeArray)
        timeArray = time.strptime(svtime2, "%Y-%m-%d %H:%M:%S")
        svendtimestamp = time.mktime(timeArray)
        #print('svtime1:',svstarttimestamp)
        #print('svtime2:',svendtimestamp)
        nowtimestamp = time.time()
        #print('localtime',nowtimestamp)
        if checkip(ip,tablename) != 1:
            candidates=fetchidandvote2(tablename,'CANDIDATE')
            return render_template("vote_succ.html",candidates=fetchidandvote2(tablename,'CANDIDATE'),\
                   votes=fetchidandvote2(tablename,'VOTES'),length=len(candidates),voted=1)
        if svendtimestamp <= nowtimestamp:
            candidates=fetchidandvote2(tablename,'CANDIDATE')
            return render_template("vote_succ.html",candidates=fetchidandvote2(tablename,'CANDIDATE'),\
                   votes=fetchidandvote2(tablename,'VOTES'),length=len(candidates),timeout=1)
        
        
        if nowtimestamp <= svstarttimestamp:
            candidates=fetchidandvote2(tablename,'CANDIDATE')
            return render_template("vote_succ.html",candidates=fetchidandvote2(tablename,'CANDIDATE'),\
                   votes=fetchidandvote2(tablename,'VOTES'),length=len(candidates),notyet=1)
        #print(tablename)
        allinfo = getallinfo()
        #print(len(allinfo))
        idset = allinfo[0]
        #print(idset)
        if id not in idset:
            return render_template("hello.html")
        idindex = idset.index(id)
        title = allinfo[3][idindex]
        subtitle = allinfo[4][idindex]
        minvote = allinfo[7][idindex]
        maxvote = allinfo[8][idindex]
        candidates = fetchidandvote2(tablename,'CANDIDATE')
        votes = fetchidandvote2(tablename,'VOTES')
        details = fetchdetails(tablename)
        length = len(candidates)
        return render_template("generate.html",tablename=tablename,title=title,subtitle=subtitle,\
                               candidates=candidates,details=details,length = length,getnames = getnames(length),votes = votes,\
                                minvote = minvote,maxvote = maxvote,captcha=captcha)


@voter.route('/posted',methods=["POST"])
def posted():
    ip = request.remote_addr
    length = int(request.values.get('length'))
    captcha = stripit(request.values.get('image')).upper()
    sourcestr = session['image'].upper()
    print(captcha,sourcestr)
    tablename = stripit(str(request.values.get('id')))
    id = tablename.replace('tab','')
    if captcha != sourcestr:
        return redirect(url_for('votegen',id=id,captcha=0))
    candidates=fetchidandvote2(tablename,'CANDIDATE')
    if checkip(ip,tablename) !=1:
        return render_template("vote_succ.html",candidates=fetchidandvote2(tablename,'CANDIDATE'),\
                   votes=fetchidandvote2(tablename,'VOTES'),length=len(candidates),voted=1)
    saveip(ip,tablename)
    id = int(tablename.replace("tab",''))
    #print("id is",id)
    allinfo = getallinfo()
    #print(len(allinfo))
    idset = allinfo[0]
    #print(idset)
    if id not in idset:
        return render_template("hello.html",candidates=fetchidandvote2(tablename,'CANDIDATE'),\
                   votes=fetchidandvote2(tablename,'VOTES'),length=len(candidates),voted=1)
    idindex = idset.index(id)
    title = allinfo[3][idindex]
    subtitle = allinfo[4][idindex]
    minvote = allinfo[7][idindex]
    maxvote = allinfo[8][idindex]
    namelists = namelistlist(tablename)
    d = request.form
    d = d.to_dict()
    #print('d is =====',d)
    print(tablename)
    getnames = []
    #getform = []
    for i in range(1, length + 1):
        string = 'cond_' + str(i)
        getnames.append(string)
    sum =0
    for i in range(0,length):
        sum += int(d[str(getnames[i])])
    if sum < minvote or sum>maxvote:
        return render_template("hello.html")
    for i in range(0, length):
        if int(d[str(getnames[i])]) == 1:
            upd1(tablename,str(namelists[i]))
            print('updated:',namelists[i])
    return render_template("vote_succ.html",candidates=fetchidandvote2(tablename,'CANDIDATE'),\
                           votes=fetchidandvote2(tablename,'VOTES'),length=length)


def getnames(tablelen):
    getnames = []
    for i in range(1, tablelen + 1):
        string = 've' + str(i)
        getnames.append(string)
    return getnames



@voter.route('/choose_vote')
def choose_vote():
    allinfo = getallinfo()
    href = []
    length = len(allinfo[0])
    allinfo.append(length)
    #print(allinfo)
    for i in allinfo[0]:
        string = 'votegen/'+'%s'%i
        #print(string)
        href.append(string)
    return render_template("choose_vote.html",info = allinfo,href = href)


if __name__ == '__main__':
    voter.run(host='0.0.0.0', port=8080,debug='True')
