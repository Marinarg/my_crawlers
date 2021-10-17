# -*- coding: utf-8 -*-
import re
from datetime import date

import goslate
import scrapy


class DigikeySpider(scrapy.Spider):
    name = "digikey"
    allowed_domains = ["digikey.com/"]
    start_urls = ["https://www.digikey.com"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 24,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 24,
        "DOWNLOAD_DELAY": 1,
        "ROBOTSTXT_OBEY": False,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def parse(self, response):
        """Function to get sitemap page."""

        url = "https://www.digikey.com/product-detail/sitemap.xml"

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Host": "www.digikey.com",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0(X11; Ubuntu; Linuxx86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
        }

        yield scrapy.Request(
            url,
            headers=headers,
            method="GET",
            callback=self.parse_sitemap,
            dont_filter=True,
        )

    def parse_sitemap(self, response):
        """Function to get all submaps that correlates with some product URL."""

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Host": "www.digikey.com",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0(X11; Ubuntu; Linuxx86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
        }

        sitemap_urls = [
            sitemap[0]
            for sitemap in re.findall(
                "(?<=<loc>)((https:\/\/www\.digikey\.com\/[a-z]+\/product-detail\/submap\/(.*?)\.xml)(?=<\/loc>))",
                response.text,
            )
        ]

        for i, url in enumerate(sitemap_urls):
            yield scrapy.Request(
                url,
                headers=headers,
                method="GET",
                meta={"cookiejar": i},
                callback=self.parse_products,
                dont_filter=True,
            )

    def parse_products(self, response):
        """Function to get all products URLs."""

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Host": "www.digikey.com",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0(X11; Ubuntu; Linuxx86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
        }

        products_urls = [
            prod[0].replace(".pt/", ".com/")
            for prod in re.findall(
                '(?<=href=")((https:\/\/www\.digikey\.pt\/product-detail\/en\/(.*?)\/(.*?))(?="\s\/>))',
                response.text,
            )
        ]

        for url in products_urls:
            yield scrapy.Request(
                url,
                headers=headers,
                method="GET",
                meta=response.meta,
                callback=self.parse_each_product,
                dont_filter=True,
            )

    def parse_each_product(self, response):
        """Function to parse each product."""

        product_status = "".join(
            response.xpath(
                "//table[@id='product-attributes']/tbody/tr/td[@class='MuiTableCell-root MuiTableCell-body jss149']/div/div[@class='jss141']"
            ).getall()
        )

        if (
            "Obsolete" not in product_status
            and "Discontinued at Digi-Key" not in product_status
        ):

            # Product name
            product_name = response.xpath(
                "//th[@class='MuiTableCell-root MuiTableCell-head jss127']/h1/text()"
            ).get()

            # Product description
            product_description = "".join(
                response.xpath(
                    "//tbody[@class='MuiTableBody-root']/tr[@class['MuiTableRow-root jss128']]/td[@class='MuiTableCell-root MuiTableCell-body jss121']/div[@class='jss123']/text()"
                ).getall()
            )

            # Product id
            product_id = response.xpath(
                "//tbody[@class='MuiTableBody-root']/tr[@class['MuiTableRow-root jss128']]/td[@class='MuiTableCell-root MuiTableCell-body jss121']/div[@class='jss123']/div/text()"
            ).get()

            # Product image
            product_image = (
                "https:" + response.xpath("//div[@class='jss89 jss113']/img/@src").get()
                if response.xpath("//div[@class='jss89 jss113']/img/@src")
                else None
            )

            # Product currency
            currency_symbol = "$"
            currency_iso = "USD"  # I had to get it manually

            # Product in stock
            if re.findall("0 In Stock", response.text):
                in_stock = False
            else:
                in_stock = True

            # Product price
            product_price = (
                re.findall('(?<=unitPrice":"\$)((.*?)(?="))', response.text)[0][0]
                if re.findall('(?<=unitPrice":"\$)((.*?)(?="))', response.text)
                else None
            )

            # Product labels
            product_labels = [
                label[0]
                for label in re.findall(
                    '(?<=label":")(([A-Z]*[a-z]*)(?="))', response.text
                )
            ]

            if product_name:
                gs = goslate.Goslate()
                yield {
                    "product_name": gs.translate(product_name.lower(), 'pt'),
                    "product_description": product_description,
                    "product_labels": ",".join(product_labels),
                    "product_id": product_id,
                    "product_price": product_price,
                    "product_image": product_image,
                    "product_url": response.url,
                    "currency_iso": currency_iso,
                    "currency_symbol": currency_symbol,
                    "in_stock": in_stock,
                    "execution_date": str(date.today().strftime("%Y/%m/%d")),
                    "website_domain": "digikey",
                    "website_url": "https://www.digikey.com",
                }

        else:
            pass