# -- coding: utf-8 --
import re

def get_info(response, field, value):
    """
    Function to help find informations on product page.
    """
    return re.findall("(?<=content=\")((.*?)+(?=\"))", response.xpath(f"//meta[@{field}='{value}']").get())[0][0]