# -*- coding: utf-8 -*-
import re
from datetime import date

from scrapy.spiders import SitemapSpider

from websites_crawlers.utils import get_info


class SoldafriaSpider(SitemapSpider):
    name = "soldafria"
    allowed_domains = ["www.soldafria.com.br"]
    sitemap_urls = [
        "https://www.soldafria.com.br/sitemap.xml",
    ]

    custom_settings = {
        "CONCURRENT_REQUESTS": 64,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 64,
        "DOWNLOAD_DELAY": 1,
        "ROBOTSTXT_OBEY": False,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def sitemap_filter(self, entries):
        """Function to get product URLs from sitemap."""

        for entry in entries:
            if entry["priority"] == "1.0" and "blog" not in entry["loc"]:
                yield entry

    def parse(self, response):
        """Function to parse each product."""

        # Product name
        product_name = get_info(response, "property", "og:title")

        # Product description
        product_description = get_info(response, "name", "description")

        # Product keywords
        product_keywords = get_info(response, "name", "keywords")

        # Product id
        product_id = response.xpath("//input[@id='product-id']/@value").get()

        # Product price
        product_price = re.findall(
            "\d+,\d+", response.xpath("//div[@class='product-price']/text()").get()
        )[0]

        # Product image
        product_image = get_info(response, "property", "og:image")

        # Product currency
        currency_symbol = re.findall(
            "[A-Z]*\$*", response.xpath("//div[@class='product-price']/text()").get()
        )[0]

        if currency_symbol == "R$":
            currency_iso = "BRL"
        elif currency_symbol == "$":
            currency_iso = "USD"

        # Product in stock
        if response.xpath("//li[@class='product-stock in-stock']/span/text()").get():
            in_stock = True
        elif response.xpath("//li[@class='product-stock out-of-stock']").get():
            in_stock = False
        else:
            in_stock = None

        if product_name:
            yield {
                "product_name": product_name.lower().replace(",", "."),
                "product_description": product_description,
                "product_labels": product_keywords,
                "product_id": product_id,
                "product_price": product_price,
                "product_image": product_image,
                "product_url": response.url,
                "currency_iso": currency_iso,
                "currency_symbol": currency_symbol,
                "in_stock": in_stock,
                "execution_date": str(date.today().strftime("%Y/%m/%d")),
                "website_domain": "soldafria",
                "website_url": "https://www.soldafria.com.br/",
            }
