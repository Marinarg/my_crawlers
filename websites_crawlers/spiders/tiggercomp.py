# -*- coding: utf-8 -*-
import re
from datetime import date

import scrapy

from websites_crawlers.utils import get_info


class TiggerCompSpider(scrapy.Spider):
    name = "tiggercomp"
    allowed_domains = ["www.tiggercomp.com.br"]
    start_urls = ["https://tiggercomp.com.br/novaloja2/index.php?route=product/category&path=277"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 64,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 64,
        "DOWNLOAD_DELAY": 1,
        "ROBOTSTXT_OBEY": False,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def parse(self, response):
        """Function to get all category URLs."""

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Host": "www.tiggercomp.com.br",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
        }

        categories_urls = [
            cat for cat in
            response.xpath('//div[@class="row"]/aside/div/a/@href').getall()

        ]

        for i, url in enumerate(categories_urls):
            yield scrapy.Request(
                url,
                method="GET",
                headers=headers,
                meta={"cookiejar": i},
                callback=self.parse_products,
                dont_filter=True,
            )


    def parse_products(self, response, **kwargs):
        """Function to get all products from a specific category."""

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "www.tiggercomp.com.br",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
        }

        if 'Subcategoria' not in response.text:
            products_urls = [
                prod for prod in response.xpath('//div[@class="row"]/div/div/div/a/@href').getall()
            ]

            for url in products_urls:
                yield scrapy.Request(
                    url,
                    method="GET",
                    headers=headers,
                    meta=response.meta,
                    callback=self.parse_each_product,
                    dont_filter=True,
                )

            if (
                    'total de 1 ' not in response.xpath('//div[@class="col-sm-6 text-right"]')
                    and response.xpath('//div[@class="col-sm-6 text-left"]/ul[@class="pagination"]')
            ):

                next_urls = [next_url for next_url in
                 set(response.xpath('//div[@class="col-sm-6 text-left"]/ul[@class="pagination"]/li/a/@href').getall())]

                for i, url in enumerate(next_urls):
                    yield scrapy.Request(
                        url,
                        method="GET",
                        headers=headers,
                        meta={"cookiejar": i},
                        callback=self.parse_products,
                        dont_filter=True,
                    )

        else:
            sub_categories_urls = [
                sub_cat for sub_cat in response.xpath('//div[@class="col-sm-3"]/ul/li/a/@href').getall()
                if 'route=product/category&path' in sub_cat
            ]

            for i, url in enumerate(sub_categories_urls):
                yield scrapy.Request(
                    url,
                    method="GET",
                    headers=headers,
                    meta={"cookiejar": i},
                    callback=self.parse_products,
                    dont_filter=True,
                )


    def parse_each_product(self, response, **kwargs):
        """Function to parse each product."""

        # Product name
        product_name = re.findall("(?<=title>)((.*?)+(?=</))", response.text)[0][0]

        # Product description
        product_description = "" # not using this

        # Product id
        product_id = response.url.split("=")[-1]

        # Product image
        if response.xpath('//div[@class="col-sm-8"]/ul[@class="thumbnails"]'):
            product_image = response.xpath('//div[@class="col-sm-8"]/ul[@class="thumbnails"]/li/a/@href').get()
        else:
            product_image = None

        # Product currency
        currency_symbol = response.xpath('//div[@class="col-sm-4"]/ul[@class="list-unstyled"]/li/h2/text()').getall()[0][0:2]

        if currency_symbol == "R$":
            currency_iso = "BRL"
        elif currency_symbol == "$":
            currency_iso = "USD"

        # Product in stock
        if "Em estoque" in response.xpath('//div[@class="col-sm-4"]/ul[@class="list-unstyled"]/li/text()').getall()[1]:
            in_stock= True
        else:
            in_stock = False

        # Product price
        product_price = re.findall('\d*\.*\d+,*\d*', response.xpath('//div[@class="col-sm-4"]/ul[@class="list-unstyled"]/li/h2/text()').getall()[0])[0]

        if product_name:
            yield {
                "product_name": product_name.lower().replace(",", "."),
                "product_description": product_description,
                "product_labels": None,
                "product_id": product_id,
                "product_price": product_price.replace(".", ",").replace(",", "."),
                "product_image": product_image,
                "product_url": response.url,
                "currency_iso": currency_iso,
                "currency_symbol": currency_symbol,
                "in_stock": in_stock,
                "execution_date": str(date.today().strftime("%Y/%m/%d")),
                "website_domain": "tiggercomp",
                "website_url": "http://www.tiggercomp.com.br/novaloja/",
            }
