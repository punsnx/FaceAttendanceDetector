import pymongo

myclient = pymongo.MongoClient("mongodb+srv://skdev:skdev123456789@skmongocluster.skdn9.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["FaceAttendance"]
workcol = mydb["Attendance"]
mycol = mydb["users"]

http = "http://skpcxv.thddns.net:7880"
checkin = {"ID": "อย่าอ้วนดิ้","Stamp":"3 วันที่แล้ว"}
#workcol.insert_one(checkin)
"""
for x in mycol.find({},{ "_id": 0, "name": 1, "profileFile": 1 }):
    try:
        print(x["name"], x["profileFile"])
        #print(http +x["profileFile"])
        if
    except:
        print("error", x["name"])
"""
mydoc = mycol.find({ "studentID" : "47574" },{ "_id": 0, "name": 1,})
for x in mydoc:
  saidname = x["name"]
  print(saidname)