#/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import sys
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
USER_ACCOUNTS_TABLE = os.path.join(base_dir,"db","users_table.json")

def load_account_data():    #加载用户信息数据库
    with open(USER_ACCOUNTS_TABLE, "r") as accounts_info:
        user_accounts_dic = json.loads(accounts_info.read())
        return user_accounts_dic

def update_account_data(accounts_data):  #更新用户信息数据库
    with open(USER_ACCOUNTS_TABLE, "w") as accounts_info:
        accounts_info.write(json.dumps(accounts_data))
        return True

def check_account_id(account_id):   #帐号检测
    user_accounts_dic = load_account_data()
    if account_id in user_accounts_dic:
        return True

