#/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import sys
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
USER_CREDITCARD_TATBLE = os.path.join(base_dir,"db","user_creditcard_table.json")
BANK_CREDITCARD_TATBLE = os.path.join(base_dir,"db","bank_creditcard_table.json")

def load_user_creditcard(account_id):
    with open(USER_CREDITCARD_TATBLE, "r") as creditcard_info:
        creditcard_info_dic = json.loads(creditcard_info.read())
        if account_id in creditcard_info_dic:
            user_creditcard = creditcard_info_dic[account_id]
        else:
            user_creditcard = []
        return user_creditcard

def load_bind_creditcard_table():
    with open(USER_CREDITCARD_TATBLE, "r") as creditcard_txns:
        bind_creditcard_data_dic = json.loads(creditcard_txns.read())
        return bind_creditcard_data_dic

def update_bind_creditcard_table(bind_creditcard_data):
    with open(USER_CREDITCARD_TATBLE, "w") as creditcard_txns:
        creditcard_txns.write(json.dumps(bind_creditcard_data))
        return True

def check_creditcard_bind(account_id, creditcard_id):
    user_creditcard_list = load_user_creditcard(account_id)
    for user_creditcard_id in user_creditcard_list:
        if creditcard_id == user_creditcard_id:
            return True

def load_bank_creditcard_table():
    with open(BANK_CREDITCARD_TATBLE, "r") as creditcard_txns:
        bank_creditcard_data_dic = json.loads(creditcard_txns.read())
        return bank_creditcard_data_dic

def update_bank_creditcard_table(bank_creditcard_data):
    with open(BANK_CREDITCARD_TATBLE, "w") as creditcard_txns:
        creditcard_txns.write(json.dumps(bank_creditcard_data))
        return True

