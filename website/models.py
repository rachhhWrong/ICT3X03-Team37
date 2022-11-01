from flask import Flask, jsonify, request
from passlib.hash import pbkdf2_sha256
import uuid

from website.auth import *

class User:
    def signup(self):
        print(request.form)
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password')
        }

        # Encrypt Password
        #user['password'] = pbkdf2_sha256.encrypt(user['password'])
        #account_db.users.insert_one(user)


        return jsonify(user), 200



