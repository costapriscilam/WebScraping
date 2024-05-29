"""
OBJETIVO: 
    - Extrair informações de receitas do site
    - Performar web scraping vertical através de regras
    
Criado por: Priscila Costa
Última edição: 29 de Maio de 2024
"""
import logging
import pdb
from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader


class Receita(Item):
    nome = Field()
    tempo_preparo = Field()
    porcoes = Field()
    ingredientes = Field()
    preparo = Field()
    link = Field()

# CLASSE CORE - Para fazer extração de múltiplas páginas, chamamos CrawlSpider
class Receiteria(CrawlSpider):
    name = 'Receiteria_Crawler'

#Por motivos de segurança, retirei o meu User-agent do código abaixo, mas para o código funcionar, basta você inserir o seu.
# Usamos User-Agent para não sermos identificados como BOT pelo servidor. Assim evitamos bloqueio de IP  
    custom_settings = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36"
    }

    # Reduza o espectro de busca de URLs. Não podemos sair dos domínios desta lista.
    allowed_domains = ['receiteria.com.br']

    # URL inicial à qual será feita a primeira requisição
    start_urls = ['https://www.receiteria.com.br/']
 
   # Tempo de espera entre cada requisição. Isso nos ajuda a proteger nosso IP.
    download_delay = 2

    # Tupla de regras para direcionar o movimento do nosso Crawler através das páginas
    rules = (
        Rule( # Regra de movimento vertical
            LinkExtractor(
                allow=r'/receita/' # Se a URL conter este padrão, faça uma requisição a essa URL
            ), follow=True, callback="parse_receitas"), # O callback é o nome da função que será chamada com a resposta à requisição para essas URLs
    )

    # Callback da regra
    def parse_receitas(self, response):
        
        sel = Selector(response)
        item = ItemLoader(Receita(), sel)

        item.add_xpath('nome', "//div[@class='title']/h1/text()")

        # Como o local da informação não é padrão em todas as páginas, verificamos se há uma span com a classe 'info-author'
        porcoes = response.xpath("//div[contains(@class, 'info-recipe') and contains(@class, 'mb-3')]/span[1]/text()").get()
        tempo_preparo = response.xpath("//div[contains(@class, 'info-recipe') and contains(@class, 'mb-3')]/span[2]/text()").get()

        # Se existe, captura as porções do próximo span
        if response.xpath("//div[contains(@class, 'info-recipe') and contains(@class, 'mb-3')]/span[@class='info-author']"):
            
            porcoes = response.xpath("//div[contains(@class, 'info-recipe') and contains(@class, 'mb-3')]/span[@class='info-author']/following-sibling::span[1]/text()").get()
            tempo_preparo = response.xpath("//div[contains(@class, 'info-recipe') and contains(@class, 'mb-3')]/span[@class='info-author']/following-sibling::span[2]/text()").get()

        item.add_value('porcoes', porcoes)
        item.add_value('tempo_preparo', tempo_preparo)
    
        item.add_xpath('ingredientes', "//label[contains(@for, 'ingrediente')]/text()")
        item.add_xpath('preparo', "//li[contains(@id, 'passo')]/span/text()" )
        item.add_value('link', response.url)

        yield item.load_item()

# Para executar o código, insira no terminal:
# scrapy runspider receiteria.py -o receitas.csv

