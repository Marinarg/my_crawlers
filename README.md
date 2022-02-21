# My Crawlers

Dedicated repository for storing crawler scripts using Scrapy tool. So far there are 7 crawlers:

- **[baudaeletronica]**
- **[baudaeletronica_shipping]**
- **[digikey]**
- **[filipeflop]**
- **[filipeflop_shipping]**
- **[filipeflop]**
- **[filipeflop]**

## Crawlers

### baudaeletronica

This is a general purpose crawler based on the [Baú da Eletrônica website](https://www.baudaeletronica.com.br/?gclid=CjwKCAiA6seQBhAfEiwAvPqu11zqrLLNP4G074_0oRTV6MLQCXVkVB-eVhounV9Pq0njX0xMLYdHvBoC-ncQAvD_BwE) (electronic components online store). Its objective is to get information about all the products on the site. [Here](websites_crawlers/spiders/baudaeletronica.py) is the link to the spider.

### baudaeletronica_shipping

This is also a crawler based on the website mentioned above ([Baú da Eletrônica](https://www.baudaeletronica.com.br/?gclid=CjwKCAiA6seQBhAfEiwAvPqu11zqrLLNP4G074_0oRTV6MLQCXVkVB-eVhounV9Pq0njX0xMLYdHvBoC-ncQAvD_BwE)), however it is intended to get product delivery price data. [Here](websites_crawlers/spiders/baudaeletronica_shipping.py) is the link to the spider.

### digikey

This is a general purpose crawler based on the [Digi-Key website](https://www.digikey.com.br/) (electronic components online store). Its objective is to get information about all the products on the site. [Here](websites_crawlers/spiders/digikey.py) is the link to the spider.

### filipeflop

This is a general purpose crawler based on the [Filipeflop website](https://www.filipeflop.com/) (electronic components online store). Its objective is to get information about all the products on the site. [Here](websites_crawlers/spiders/filipeflop.py) is the link to the spider.

### filipeflop_shipping

This is also a crawler based on the website mentioned above ([Filipeflop](https://www.filipeflop.com/)), however it is intended to get product delivery price data. [Here](websites_crawlers/spiders/filipeflop_shipping.py) is the link to the spider.

### soldafria

This is a general purpose crawler based on the [SoldaFria website](https://www.soldafria.com.br/) (electronic components online store). Its objective is to get information about all the products on the site. [Here](websites_crawlers/spiders/soldafria.py) is the link to the spider.


### tiggercomp

This is a general purpose crawler based on the [TiggerCOMP website](https://tiggercomp.com.br/novaloja2/) (electronic components online store). Its objective is to get information about all the products on the site. [Here](websites_crawlers/spiders/tiggercomp.py) is the link to the spider.

## Installation Instructions

This project currently uses:
- Python 3.6.12
- Scrapy 2.5.0

1. Install Miniconda:
- `wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh`
- `chmod +x Miniconda3-latest-Linux-x86_64.sh`
- `./Miniconda3-latest-Linux-x86_64.sh`
- `export PATH="/home/<YOUR-USER>/miniconda3/bin:$PATH" source ~/.bashrc`

2. Create a Python environment, activate and install requirements:
- `conda create -n my_crawlers python=3.6`
- `conda activate my_crawlers`
- `pip install -r requirements.txt`

## Running a Spider

To run a spider you can type `scrapy crawl <spider_name>` in the terminal, replacing `<spider_name>` with the spider name you want to run. If you want to export results to a JL file, you can run `scrapy crawl <spider_name> -o <filename>.jl` or, if you want to export a CSV, you can run `scrapy crawl <spider_name> -o <filename>.csv -t csv`.