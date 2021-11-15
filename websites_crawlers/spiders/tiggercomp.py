# -*- coding: utf-8 -*-
import re
from datetime import date

import scrapy

from websites_crawlers.utils import get_info


class TiggerCompSpider(scrapy.Spider):
    name = "tiggercomp"
    allowed_domains = ["www.tiggercomp.com.br"]
    start_urls = ["http://www.tiggercomp.com.br/novaloja2/"]

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
            "Host": "www.tiggercomp.com.br",
            "Referer": "http://www.tiggercomp.com.br/novaloja/product_info.php?products_id=6823",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
        }

        categories_urls = [
            cat for cat in response.xpath("//table[@class='infoBoxContents']/tr/td/a/@href").getall()
        ]

        for i, url in enumerate(categories_urls):

            if "cPath" in url:
                yield scrapy.Request(
                    url,
                    method="GET",
                    headers=headers,
                    meta={"cookiejar": i},
                    callback=self.parse_products,
                    dont_filter=True,
                )
            elif "products_id" in url:
                yield scrapy.Request(
                    url,
                    method="GET",
                    headers=headers,
                    meta={"cookiejar": i},
                    callback=self.parse_each_product,
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

        products_urls = [
            prod for prod in response.xpath("//td[@class='productListing-data']/a/@href").getall()
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
            response.xpath("//td[@class='smallText']/a/u").getall() and
            "PRÓXIMO" in response.xpath("//td[@class='smallText']/a/u").getall()[-1]
        ):
            # Checks if there are more pages to get products.

            url = response.xpath("//td[@class='smallText']/a/@href").getall()[-1]

            yield scrapy.Request(
                url,
                method="GET",
                headers=headers,
                meta={"cookiejar": 0},
                callback=self.parse_products,
                dont_filter=True,
                cb_kwargs=kwargs,
            )

    def parse_each_product(self, response, **kwargs):
        """Function to parse each product."""

        if response.xpath("//td[@class='productListing-data']/a/@href").getall():
            # Checks that we are on the product listing page (and not on a product page). If true, go to the product page.

            product_id = response.xpath("//td[@class='productListing-data']/a/@href").getall()[0].split("=")[-1]

            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "Host": "www.tiggercomp.com.br",
                "Referer": f"http://www.tiggercomp.com.br/novaloja/product_info.php?products_id={product_id}",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
            }

            url = response.xpath("//td[@class='productListing-data']/a/@href").getall()[0]

            yield scrapy.Request(
                    url,
                    method="GET",
                    headers=headers,
                    meta=response.meta,
                    callback=self.parse_each_product,
                    dont_filter=True,
                )

        else:
            # Product name
            product_name = get_info(response, "property", "og:title")

            # Product description
            product_description = get_info(response, "property", "og:description")

            # Product id
            product_id = response.url.split("=")[-1]

            # Product image
            product_image = get_info(response, "property", "og:image")

            # Product currency
            if [s for s in response.xpath("//table[@class='infobox']/tr/td[@align='center']/text()").getall() if "R$" in s]:
                currency_symbol = re.findall("R*\$*", [s for s in response.xpath("//table[@class='infobox']/tr/td[@align='center']/text()").getall() if "R$" in s][0])[0]
            elif response.xpath("//span[@class='productSpecialPrice']/text()").get():
                currency_symbol = re.findall("R*\$*", response.xpath("//span[@class='productSpecialPrice']/text()").get())[0]
            else:
                currency_symbol = re.findall("R*\$*", [s for s in response.xpath("//td[@class='pageHeading']/text()").getall() if "R$" in s][0])[1]
            
            if currency_symbol == "R$":
                currency_iso = "BRL"
            elif currency_symbol == "$":
                currency_iso = "USD"

            # Product in stock
            if response.xpath("//img[@title=' Esgotado, avise-me ']"):
                in_stock= False
            else:
                in_stock = True

            # Product price
            if response.xpath("//table[@class='infobox']/tr/td[@align='center']/text()").getall():
                product_price = re.findall("\d+,\d+", [s for s in response.xpath("//table[@class='infobox']/tr/td[@align='center']/text()").getall() if "R$" in s][0])
            elif response.xpath("//span[@class='productSpecialPrice']/text()").get():
                product_price = re.findall("\d+,\d+", response.xpath("//span[@class='productSpecialPrice']/text()").get())[0]
            else:
                product_price = re.findall("\d+,\d+", [s for s in response.xpath("//td[@class='pageHeading']/text()").getall() if "R$" in s][0])[0]

            if product_name:
                yield {
                    "product_name": product_name.lower(),
                    "product_description": product_description,
                    "product_labels": None,
                    "product_id": product_id,
                    "product_price": product_price,
                    "product_image": product_image,
                    "product_url": response.url,
                    "currency_iso": currency_iso,
                    "currency_symbol": currency_symbol,
                    "in_stock": in_stock,
                    "execution_date": str(date.today().strftime("%Y/%m/%d")),
                    "website_domain": "tiggercomp",
                    "website_url": "http://www.tiggercomp.com.br/novaloja/",
                }