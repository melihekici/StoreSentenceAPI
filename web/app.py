"""
Registration of a user (0 token cost)
Each user gets 10 tokens
Store a sentence on our database for 1 token
Retrieve his stored sentence on out database for 1 token
"""

import bcrypt
from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

dbClient = MongoClient("mongodb://db:27017")
db = dbClient.SentencesDatabase
users = db['Users']


class Register(Resource):
    def post(self):
        # Read posted data by the user
        postData = request.get_json()
        
        # Check posted data, if OK extract username and password
        if(self.register_check(postData)==200):
            userName = postData['username']
            password = postData['password']
            hashedPW = self.hashPW(password)

            users.insert({
                'Username': userName,
                'Password': hashedPW,
                'Sentence': "",
                'Tokens': 6231231
            })

            retJson = {
                "status": 200,
                "msg": "You have successfully signed up to API"
            }

            return jsonify(retJson)

        else:
            retJson = {
                "status": 301,
                "msg": "Username or Password is missing"
            }
            return jsonify(retJson)
        

    def register_check(postData):
        if('username' in postData and 'password' in postData):
            return 200
        else:
            return 301

    def hashPW(self, password):
        hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        return hashed

def verifyPW(username,password):
    hashedPW = users.find({"Username":username})[0]["Password"]
    if(bcrypt.hashpw(password.encode("utf8"), hashedPW) == hashedPW):
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({'Username':username})[0]['Tokens']
    return tokens

class Store(Resource):
    def post(self):
        postData = request.get_json()
        sentenceCheck = self.sentence_check(postData)

        if(sentenceCheck == 200):
            username = postData['username']
            password = postData['password']
            sentence = postData['sentence']

            if(not verifyPW(username, password)):
                retJson = {
                    "status": 302,
                    "msg": "Wrong authentication information"
                }
                return jsonify(retJson)
            
            print(countTokens(username))
            if(countTokens(username) == 0):
                retJson = {
                    "status": 301,
                    "message": "Out of tokens"
                }
                return jsonify(retJson)

            users.update(
                {"Username": username},
                {"$set":{
                    "Sentence": sentence,
                    "Tokens": countTokens(username) - 1
                    }
                }
                )
            
            retJson = {
                "status": 200,
                "msg": "Sentence saved successfully"
            }
            return jsonify(retJson)


        else:
            retJson = {
                "status": sentenceCheck
            }

    def sentence_check(self, postData):
        if('username' in postData and 'password' in postData and 'sentence' in postData):
            return 200
        elif('sentence' in postData):
            return 301
        else:
            return 401

class GetSentence(Resource):
    def post(self):
        postedData = request.get_json()

        if(.register_check(postedData) != 200):
            retJson = {
                "status":301,
                "msg": "Username or Password is missing"
            }
            return jsonify(retJson)
        
        username = postedData['username']
        password = postedData['password']

        if(not verifyPW(username, password)):
            retJson = {
                "status":302,
                "msg": "Wrong username or password"
            }
            return jsonify(retJson)

        if(countTokens(username) > 0):
            userInfo = users.find({'Username':username})[0]
            tokenNum = userInfo['Tokens']
            userSentence = userInfo['Sentence']

            retJson = {
                "status":200,
                "sentence":userSentence,
                "tokens":tokenNum-1
            }

            users.update({'Username':username}, 
                         {"$set":{'Tokens':tokenNum-1}})

            return jsonify(retJson)
        
        else:
            retJson = {
                "status":301,
                "msg": "Not enough Tokens"
            }
            return jsonify(retJson)

api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(GetSentence, "/getsentence")


if __name__ == '__main__':
    app.run(host='0.0.0.0')


"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

dbClient = MongoClient("mongodb://db:27017")
db = dbClient.aNewDB
userNum = db['userNum']

userNum.insert(
    {
        'Number of Visitors':0
    }
)

class Visitors(Resource):
    def get(self):
        prevNum = userNum.find({})[0]['Number of Visitors']
        userNum.update({}, {"$set":{'Number of Visitors':prevNum+1}})
        return str("Hello user Number:" + str(prevNum+1))

def checkPostedData(postedData):
    if "x" not in postedData or "y" not in postedData:
        return 301 # x or y does not exist
    else:
        return 200


def readXY(postedData):
    x = postedData['x']
    y = postedData['y']
    x = int(x)
    y = int(y)
    return x,y


class Add(Resource):
    def post(self):
        postedData = request.get_json()
        dataCheck = checkPostedData(postedData)

        if (dataCheck == 200):
            x,y = readXY(postedData)
            result = x + y
        else:
            result = "Error"

        response = {
            'Result': result,
            'Status Code': dataCheck
        }
        return jsonify(response)


class Substract(Resource):
    def post(self):
        postedData = request.get_json()
        dataCheck = checkPostedData(postedData)

        if (dataCheck == 200):
            x,y = readXY(postedData)
            result = x - y
        else:
            result = "Error"

        response = {
            'Result': result,
            'Status Code': dataCheck
        }
        return jsonify(response)

class Multiply(Resource):
    def post(self):
        postedData = request.get_json()
        dataCheck = checkPostedData(postedData)

        if (dataCheck == 200):
            x,y = readXY(postedData)
            result = x * y
        else:
            result = "Error"

        response = {
            'Result': result,
            'Status Code': dataCheck
        }
        return jsonify(response)

class Divide(Resource):
    def post(self):
        postedData = request.get_json()
        dataCheck = checkPostedData(postedData)

        if (dataCheck == 200):
            x,y = readXY(postedData)
            if(y==0):
                dataCheck = 302
                result = "Error: Division by zero"
            else:
                result = x / y
        else:
            result = "Error"

        response = {
            'Result': result,
            'Status Code': dataCheck
        }
        return jsonify(response)

api.add_resource(Add, "/add")
api.add_resource(Substract, "/substract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/divide")
api.add_resource(Visitors, "/hello")



# @app.route('/add_two_nums', methods=['POST'])
# def add_two_nums():
#     #Get x and y from POST request
#     dataDict = request.get_json()
#     x = dataDict["x"]
#     y = dataDict["y"]
    
#     #Add x + y and store in z
#     z = x + y
    
#     #Prepare a JSON with field z in it. 'z':z
#     response = {
#         "z":z
#     }

#     #Return jsonify(prepared map)
#     return jsonify(response), 200

# @app.route('/hithere')
# def hithere():
#     return "Hello"


# @app.route('/')
# def mainPage():
#     return "Hello World!"

# @app.route('/bye')
# def bye():
#     return "See you later"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
"""
