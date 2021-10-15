# -*- coding: utf-8 -*-
import re
from datetime import date

import scrapy


class BaudaeletronicaSpider(scrapy.Spider):
    name = "baudaeletronica"
    allowed_domains = ["baudaeletronica.com.br"]
    start_urls = ["https://www.baudaeletronica.com.br/"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 24,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 24,
        "DOWNLOAD_DELAY": 1,
        "ROBOTSTXT_OBEY": False,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def parse(self, response):
        """Function to get all category URLs."""

        headers = {
            "authority": "www.baudaeletronica.com.br",
            "method": "GET",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "referer": "https://www.baudaeletronica.com.br/",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
        }

        categories_urls = [
            cat[0]
            for cat in re.findall(
                '(?<=href=")(https:\/\/www.baudaeletronica.com.br\/(.*?)(?=">))',
                response.xpath("//div[@class='container']/nav/ul").get(),
            )
        ]
        
        for i, url in enumerate(categories_urls):
            yield scrapy.Request(
                url,
                method="GET",
                headers=headers,
                meta={"cookiejar": i},
                callback=self.parse_products,
                cb_kwargs={"category": url.split('/')[-1]}
            )

    def parse_products(self, response, **kwargs):
        """Function to get all products from a specific category."""

        headers = {
            "authority": "www.baudaeletronica.com.br",
            "method": "GET",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua": 'Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
        }

        products_urls = [
            prod[0]
            for prod in re.findall(
                '(?<=href=")((https:\/\/www\.baudaeletronica\.com\.br\/(.*?)\.html)(?="))',
                response.xpath(
                    "//ul[@class='products-grid category-products-grid itemgrid itemgrid-adaptive itemgrid-4col ']"
                ).get(),
            )
        ]

        for url in products_urls:
            yield scrapy.Request(
                url,
                method="GET",
                headers=headers,
                meta=response.meta,
                callback=self.parse_each_product,
                cb_kwargs=kwargs
            )

        if (
            response.xpath("//div[@class='toolbar']/ul/li[@class='pager']")
            and response.xpath("//li[@class='next']/a/@href").get()
        ):
            # Checking if there are more pages and if we are not on the last one

            next_page_url = response.xpath("//li[@class='next']/a/@href").get()

            yield scrapy.Request(
                next_page_url,
                method="GET",
                headers=headers,
                meta=response.meta,
                callback=self.parse_products,
                cb_kwargs=kwargs
            )

    def parse_each_product(self, response, **kwargs):
        """Function to parse each product."""

        # Product name
        product_name = response.xpath(
            "//div[@class='product-shop']/form/div[@class='product-name']/h1/text()"
        ).get()

        # Product id
        try:
            product_id = re.findall(
                '(?<=value=")((.*?)(?="))',
                response.xpath("//input[@class='product-id']").get(),
            )[0][0]
        except:
            product_id = response.xpath("//span[@class='title-rating']/text()").get()

        # Product price
        product_price = response.xpath(
            "//span[@class='regular-price']/span[@class='price']/text()"
        ).get()

        # Product image
        product_image = response.xpath("//div[@class='img-box']/figure/a/@href").get()

        # Product currency
        currency_iso = re.findall(
            '(?<=content=")((.*?)(?="))',
            response.xpath(
                "//div[@itemprop='offers']/meta[@itemprop='priceCurrency']"
            ).get(),
        )[0][0]

        if currency_iso == "BRL":
            currency_symbol = "R$"
        elif currency_iso == "USD":
            currency_symbol = "$"
            
        # Product in stock
        if response.xpath(
            "//div[@class='availability in-stock']/span[@class='disponivel']/text()"
        ):
            in_stock = True
        elif response.xpath(
            "//div[@class='availability out-of-stock']/span[@class='indisponivel']/text()"
        ):
            in_stock = False
        else:
            in_stock = None

        # Product description
        product_description = response.xpath("//div[@class='texto']/p").get()

        if product_name:
            yield {
                "product_name": product_name.lower(),
                "product_description": product_description,
                "product_labels": kwargs["category"],
                "product_id": product_id,
                "product_price": product_price,
                "product_image": product_image,
                "product_url": response.url,
                "currency_iso": currency_iso,
                "currency_symbol": currency_symbol,
                "in_stock": in_stock,
                "execution_date": date.today().strftime("%Y/%m/%d"),
                "website_domain": "baudaeletronica",
                "website_url": "https://www.baudaeletronica.com.br/",
            }
