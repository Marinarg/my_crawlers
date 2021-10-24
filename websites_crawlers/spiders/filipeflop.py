# -*- coding: utf-8 -*-
import re
from datetime import date

import scrapy


class FilipeflopSpider(scrapy.Spider):
    name = "filipeflop"
    allowed_domains = ["filipeflop.com"]
    start_urls = ["https://www.filipeflop.com"]

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
            "authority": "www.filipeflop.com",
            "method": "GET",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "referer": "https://www.filipeflop.com/",
            "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
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
                '(?<=href=")((https:\/\/www\.filipeflop\.com\/categoria\/[a-z]+-*[a-z]*\d*-*[a-z]*\d*-*[a-z]*\d*\/*)(?=">Ver\stodos))',
                response.xpath(
                    "//div[@class='departments-menu-v2']/div[@class='dropdown show-dropdown']"
                ).getall()[0],
            )
        ]

        for i, url in enumerate(categories_urls):
            yield scrapy.Request(
                url,
                method="GET",
                headers=headers,
                meta={"cookiejar": i},
                callback=self.parse_products,
                dont_filter=True,
                cb_kwargs={"category": url.split("/")[-2]},
            )

    def parse_products(self, response, **kwargs):
        """Function to get all products from a specific category."""

        headers = {
            "authority": "www.filipeflop.com",
            "method": "GET",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "referer": "https://www.filipeflop.com/",
            "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
        }

        products_urls = [
            prod[0]
            for prod in re.findall(
                '(?<=href=")((https:\/\/www\.filipeflop\.com\/produto\/(.*?))(?=\/))',
                response.xpath("//main[@id='main']/ul").getall()[0],
            )
        ]

        for url in products_urls:
            yield scrapy.Request(
                url,
                method="GET",
                headers=headers,
                meta=response.meta,
                callback=self.parse_each_product,
                dont_filter=True,
                cb_kwargs=kwargs,
            )

        if (
            response.xpath("//ul[@class='page-numbers']")
            and len(response.url.split("/")) == 6
        ):
            # Check if there are more pages and we are on the first one.

            pages = set(
                [
                    x[0]
                    for x in re.findall(
                        f'(?<=href=")(({response.url}page/(\d)+\/)(?=">))',
                        response.xpath("//ul[@class='page-numbers']").get(),
                    )
                ]
            )

            for i, url in enumerate(pages):
                yield scrapy.Request(
                    url,
                    method="GET",
                    headers=headers,
                    meta={"cookiejar": i},
                    callback=self.parse_products,
                    dont_filter=True,
                    cb_kwargs=kwargs,
                )

    def parse_each_product(self, response, **kwargs):
        """Function to parse each product."""

        # Product name
        product_name = response.xpath(
            "//div[@class='summary entry-summary']/h1[@class='product_title entry-title']/text()"
        ).get()

        # Product description
        product_description = "".join(
            response.xpath(
                "//div[@class='woocommerce-product-details__short-description']/p"
            ).getall()
        )

        # Product id
        try:
            product_id = re.findall(
                '(?<=product_id=")((\d)+(?="\s))',
                response.xpath(
                    "//div[@class='product-outer product-item__outer']/span"
                ).get(),
            )[0][0]

        except:
            product_id = re.findall(
                '(?<=product_id":)((\d)+(?=,))',
                response.xpath("//div[@class='product-actions']/div/div").get(),
            )[0][0]

        # Product image
        product_image = re.findall(
            '(?<=large_image=")((https:\/\/(.*?))(?="\s))',
            response.xpath("//div[@class='product-images-wrapper']/div").get(),
        )[0][0]

        # Product currency
        currency_iso = (
            response.xpath(
                "//p[@class='price']/span[@class='electro-price']/span[@class='woocommerce-Price-amount amount']/span[@class='woocommerce-Price-currencySymbol']/text()"
            ).get()
            if response.xpath(
                "//p[@class='price']/span[@class='electro-price']/span[@class='woocommerce-Price-amount amount']/span[@class='woocommerce-Price-currencySymbol']/text()"
            )
            else re.findall(
                '(?<=priceCurrency":")(([a-z]*[A-Z]*)+(?="))',
                response.xpath("//script[@type='application/ld+json']").getall()[1],
            )[0][0]
        )

        if currency_iso == "BRL":
            currency_symbol = "R$"
        elif currency_iso == "USD":
            currency_symbol = "$"

        # Product in stock and product price
        if response.xpath("//p[@class='stock in-stock']/text()"):
            in_stock = True

            if response.xpath(
                "//p[@class='price']/span[@class='electro-price']/span[@class='woocommerce-Price-amount amount']/text()"
            ):
                product_price = response.xpath(
                    "//span[@class='electro-price']/ins/span[@class='woocommerce-Price-amount amount']/text()"
                ).get()
            elif (
                re.findall(
                    '(?<=display_price":)((\d+\.*\d+)(?=,))',
                    response.xpath("//div[@class='product-actions']").get()
                    )
            ):
                product_price = re.findall(
                    '(?<=display_price":)((\d+\.*\d+)(?=,))',
                    response.xpath("//div[@class='product-actions']").get(),
                )[0][0]
            else:
                product_price = response.xpath("//p[@class='price']/span[@class='electro-price']/span[@class='woocommerce-Price-amount amount']/bdi/text()").get()

        elif response.xpath("//p[@class='stock out-of-stock']/text()"):
            in_stock = False
            product_price = None

        else:
            in_stock = False
            product_price = None

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
                "execution_date": str(date.today().strftime("%Y/%m/%d")),
                "website_domain": "filipeflop",
                "website_url": "https://www.filipeflop.com/",
            }
