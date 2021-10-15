# -*- coding: utf-8 -*-
import json
import re
import scrapy

from datetime import date

class FilipeflopShippingSpider(scrapy.Spider):
    name = "filipeflop_shipping"
    allowed_domains = ["filipeflop.com", "facebook.com"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOAD_DELAY": 1,
        "ROBOTSTXT_OBEY": False,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    zipcode = "88040401" # UFSC zipcode
    product_id = "486226" # product example
    qtt = 1

    start_urls = [f"https://www.filipeflop.com/wp-admin/admin-ajax.php?action=wc_shipping_simulator&zipcode={zipcode}&product_id={product_id}&global_product={product_id}&quantity={qtt}&_=1624885423849"]

    def parse(self, response):
        """Function to parse shipping information."""

        json_response = json.loads(response.body)

        if json_response:
            parsed_response = [
                {
                "type": json_response['rates'][key]['label'].split('-')[0],
                'deadline': re.findall('[0-9]+', json_response['rates'][key]['label'].split('-')[1])[0][0] + ' dias úteis',
                'price': 'R$ '+re.findall('(?<=span>)((.*?)(?=<))', json_response['rates'][key]['cost'])[0][0]
                } for key in json_response['rates'].keys() if 'local_pickup' not in key
            ]


            yield{
                "response": str(parsed_response),
                "execution_date": date.today().strftime("%Y/%m/%d"),
                "website_domain": "filipeflop",
                "website_url": "https://www.filipeflop.com/",
            }