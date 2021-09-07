# -*- coding: utf-8 -*-
import json
import scrapy

from datetime import date

class BaudaeletronicaShippingSpider(scrapy.Spider):
    name = "baudaeletronica_shipping"
    allowed_domains = ["baudaeletronica.com.br/"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOAD_DELAY": 1,
        "ROBOTSTXT_OBEY": False,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    zipcode = "88040401" # UFSC zipcode
    product_id = "948" # product example
    qtt = 1

    start_urls = [f"https://www.baudaeletronica.com.br/freteproduto/index/index?product_id={product_id}&postcode={zipcode}&qty=1"]

    def parse(self, response):
        """Function to parse shipping information."""

        yield{
            "response": str(json.loads(response.body)),
            "execution_date": date.today().strftime("%Y/%m/%d"),
            "website_domain": "baudaeletronica",
            "website_url": "https://www.baudaeletronica.com.br/",
        }