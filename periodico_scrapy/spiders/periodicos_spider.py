from typing import Any
import scrapy
import json

class PeriodicosSpider(scrapy.Spider):
    name = "periodico"

    total_papers = 0

    def __init__(self, name: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.file = open("export.ris", "a")

    def start_requests(self):
        urls = [
            "https://www-periodicos-capes-gov-br.ez45.periodicos.capes.gov.br/index.php/acervo/buscador.html?q=all%3Acontains%28%28%26quot%3Bself-esteem%26quot%3B+OR+%26quot%3Bself-image%26quot%3B+OR+%26quot%3Bself-concept%26quot%3B%29+AND+all%3Acontains%28%28%26quot%3Bschema+therapy%26quot%3B+OR+%26quot%3Bmaladaptive+schemas%26quot%3B%29&source=all&publishyear_min%5B%5D=2000&publishyear_max%5B%5D=2025&mode=advanced&source=all&page=1"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        details_links = response.css("a::attr(href)").re("/index.php/acervo/buscador.html\\?task=detalhes&source=&id.*")
        yield from response.follow_all(details_links, self.parse_detail)

        if details_links:
            page_number = int(response.url[-1])
            yield scrapy.Request(response.url[:-1] + str(page_number+1), callback=self.parse)
    
    def parse_detail(self, response):
        for script in response.xpath("//script/text()"):
            if ris := script.re("TY.*ER  -"):
                self.total_papers += 1
                print(self.total_papers)
                self.file.write(ris[0][::-1].replace("            ", "\n")[::-1])
