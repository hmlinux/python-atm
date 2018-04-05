#/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import sys
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
SUPPER_USER_TATBLE = os.path.join(base_dir,"db","supper_user_table.json")

def load_supper_user():
    with open(SUPPER_USER_TATBLE, "r") as supper_user_txns:
        supper_user_dic = json .loads(supper_user_txns.read())
        return supper_user_dic
