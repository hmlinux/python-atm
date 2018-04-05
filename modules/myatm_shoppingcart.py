#/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import sys
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
PRODUCT_TATBLE = os.path.join(base_dir,"db","product_table.json")
SHOPPINGCART_TATBLE = os.path.join(base_dir,"db","shoppingcart_table.json")
purchased_product_table = os.path.join(base_dir,"db","shopping_history.json")

def load_product_table():
    with open(PRODUCT_TATBLE, "r", encoding='utf-8') as shopping_list_txns:
        shopping_list = json.loads(shopping_list_txns.read())
        return shopping_list

def load_shopping_cart():
    with open(SHOPPINGCART_TATBLE, "r", encoding='utf-8') as shopping_cart_txns:
        shopping_cart = json.loads(shopping_cart_txns.read())
        return shopping_cart

def update_shopping_cart(shopping_cart):
    with open(SHOPPINGCART_TATBLE, "w", encoding='utf-8') as shopping_cart_txns:
        shopping_cart_txns.write(json.dumps(shopping_cart))
        return True

def load_user_purchased_product(user):
    with open(purchased_product_table, "r", encoding='utf-8') as user_purchased_product_txns:
        user_purchased_product_dict = json.loads(user_purchased_product_txns.read())
        user_purchased_product_list = user_purchased_product_dict[user]
        return user_purchased_product_list

def load_purchased_product():
    with open(purchased_product_table, "r", encoding='utf-8') as user_purchased_product_txns:
        purchased_product_dict = json.loads(user_purchased_product_txns.read())
        return purchased_product_dict


def update_purchased_product(purchased_product_dict):
    with open(purchased_product_table, "w", encoding='utf-8') as user_purchased_product_txns:
        user_purchased_product_txns.write(json.dumps(purchased_product_dict))