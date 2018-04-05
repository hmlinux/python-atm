#/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import sys
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
BANKCARD_TATBLE = os.path.join(base_dir,"db","bankcard_table.json")

class BankcardBaseClass(object):
    def __init__(self,result=True):
        self.result = result

    def user_bankcard_info(self,username):
        with open(BANKCARD_TATBLE, "r") as bankcard_info:
            bankcard_info_dic = json.loads(bankcard_info.read())
            if username in bankcard_info_dic:
                user_bankcard = bankcard_info_dic[username]
            else:
                user_bankcard = None
            return user_bankcard

    def load_bankcard_table(self):
        with open(BANKCARD_TATBLE, "r") as bankcard_txns:
            bankcard_table_dic = json.loads(bankcard_txns.read())
            return bankcard_table_dic

    def update_bankcard_table(self,bankcard_data):
        with open(BANKCARD_TATBLE, "w") as bankcard_txns:
            bankcard_txns.write(json.dumps(bankcard_data))
            return self.result

    def check_bankcard_id(self,bankcard_id):
        with open(BANKCARD_TATBLE, "r") as bankcard_txns:
            bankcard_info_dic = json.loads(bankcard_txns.read())
            users = bankcard_info_dic.keys()
            for user in users:
                for i in bankcard_info_dic[user]:
                    if i == bankcard_id:
                        return self.result

userBankcard = BankcardBaseClass()
