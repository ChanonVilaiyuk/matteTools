import sqlite3 
import sys, os 

# conn = sqlite3.connect('C:/Users/Ta/Documents/test/ta.db')
# conn = sqlite3.connect(':memory:')
# queryCurs = conn.cursor()


def dbPath(project) : 
    path = 'P:/%s/.local/vrayMatteID.db' % project
    return path 

def dbPathCustom(project, dbName) : 
    path = 'P:/%s/.local/%s.db' % (project, dbName)
    return path 

def readDatabase(project, dbName='') : 
    path = dbPath(project)
    
    if dbName: 
        path = dbPathCustom(project, dbName)
        
    dbDir = os.path.dirname(path)

    if not os.path.exists(dbDir) : 
        os.makedirs(dbDir)

    if not os.path.exists(path) : 
        # create db 
        sql = sqlite3.connect(path)
        createTable(sql)
        print 'DB created'

    else : 
        sql = sqlite3.connect(path)
        print 'Reading db' 

    result = queryObjectIDTable(sql)
    result = captureData(result)
    sql.close()

    return result


def captureData(data) : 
    dbData = []

    for each in data : 
        dbData.append(each)

    return dbData


def createTable(sql) : 
    sql.execute('''CREATE TABLE ObjectID
            (ID                 INTEGER PRIMARY KEY AUTOINCREMENT,
            oID                 INTEGER,
            AssetName           TEXT,
            AssetPath           TEXT,
            User                TEXT,
            mID                 TEXT);''')

    sql.execute('''CREATE TABLE MatteID
            (ID                 INTEGER PRIMARY KEY AUTOINCREMENT,
            mID                 INTEGER,
            Color               TEXT,
            MultiMatte          TEXT,
            VrayMtl             TEXT);''')



def addObjectIDValue(sql, oID, AssetName, AssetPath, User, mID) : 
    sql.execute('''INSERT INTO ObjectID (oID, AssetName, AssetPath, User, mID) VALUES(?,?,?,?,?)''', (oID, AssetName, AssetPath, User, mID))

def addMatteIDValue(sql, mID, Color, MultiMatte, VrayMtl) : 
    sql.execute('''INSERT INTO MatteID (mID, Color, MultiMatte, VrayMtl) VALUES(?,?,?,?)''', (mID, Color, MultiMatte, VrayMtl))

def updateObjectIDValue(sql, ID, oID, assetName, assetPath, User, mID) : 
    # sql.execute('''INSERT INTO ObjectID (oID, AssetName, AssetPath, User, mID) VALUES(?,?,?,?,?)''', (oID, AssetName, AssetPath, User, mID))
    sql.execute('''UPDATE ObjectID SET oID = ? WHERE id = ? ''', (oID, ID))
    sql.execute('''UPDATE ObjectID SET assetName = ? WHERE id = ? ''', (assetName, ID))
    sql.execute('''UPDATE ObjectID SET assetPath = ? WHERE id = ? ''', (assetPath, ID))
    sql.execute('''UPDATE ObjectID SET User = ? WHERE id = ? ''', (User, ID))
    sql.execute('''UPDATE ObjectID SET mID = ? WHERE id = ? ''', (mID, ID))


def updateMatteIDValue(sql, ID, mID, Color, MultiMatte, VrayMtl) : 
    # sql.execute('''INSERT INTO ObjectID (oID, AssetName, AssetPath, User, mID) VALUES(?,?,?,?,?)''', (oID, AssetName, AssetPath, User, mID))
    sql.execute('''UPDATE MatteID SET mID = ? WHERE id = ? ''', (mID, ID))
    sql.execute('''UPDATE MatteID SET Color = ? WHERE id = ? ''', (Color, ID))
    sql.execute('''UPDATE MatteID SET MultiMatte = ? WHERE id = ? ''', (MultiMatte, ID))
    sql.execute('''UPDATE MatteID SET VrayMtl = ? WHERE id = ? ''', (VrayMtl, ID))


def queryObjectIDTable(sql) : 
    result = sql.execute('SELECT * FROM ObjectID')
    return result

def getObjectID(sql, oID) : 
    result = sql.execute('SELECT * FROM ObjectID WHERE oID = %s' % oID)
    return result 

def getAssetName(sql, assetName) : 
    result = sql.execute('SELECT * FROM ObjectID WHERE AssetName = "%s"' % assetName)
    return result 

def getRecordFromPath(sql, path) : 
    result = sql.execute('SELECT * FROM ObjectID WHERE AssetPath = "%s"' % path)
    return result 

def getMatteID(sql, mID) : 
    result = sql.execute('SELECT * FROM MatteID WHERE mID = %s' % mID)
    return result 

def deleteMatteID(sql, mIDs) : 
    for mID in mIDs : 
        sql.execute('DELETE FROM matteID WHERE mID=%s' % mID)
    return True

def deleteObjectID(sql, oIDs) : 
    for oID in oIDs : 
        sql.execute('DELETE FROM objectID WHERE oID=%s' % oID)
    return True

def getAllMID(sql) : 
    result = sql.execute('SELECT mID FROM MatteID')
    return result

def getAllOID(sql) : 
    result = sql.execute('SELECT oID FROM ObjectID')
    return result



# conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#       VALUES (1, 'Paul', 32, 'California', 20000.00 )");

# conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#       VALUES (2, 'Allen', 25, 'Texas', 15000.00 )");

# conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#       VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )");

# conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#       VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 )");