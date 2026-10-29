import feedparser
import json
import re
from datetime import datetime, timedelta
import urllib.parse
import urllib.request

# CONFIGURAÇÃO DE FEEDS INTERNACIONAIS
FEEDS = {
    "Tech nos Negócios": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "Tech no Cotidiano": "https://www.theverge.com/rss/index.xml"
}

def limpar_html(texto):
    return re.sub(r'<[^>]*>', '', texto) if texto else ""

def traduzir_texto(texto):
    if not texto:
        return ""
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(texto[:250])}&langpair=en|pt-BR"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('responseData', {}).get('translatedText', texto)
    except Exception:
        return texto

def buscar_noticias():
    noticias = []
    id_counter = 1
    agora = datetime.now()
    limite_3_dias = agora - timedelta(days=3)

    for categoria, url_feed in FEEDS.items():
        parsed = feedparser.parse(url_feed)
        itens_adicionados = 0

        for entry in parsed.entries:
            if itens_adicionados >= 4:
                break

            # Data de publicação
            dt_pub = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                dt_pub = datetime(*entry.published_parsed[:6])

            if dt_pub >= limite_3_dias:
                titulo_pt = traduzir_texto(entry.title)
                resumo_limpo = limpar_html(getattr(entry, 'summary', getattr(entry, 'description', '')))
                resumo_pt = traduzir_texto(resumo_limpo[:200])

                fonte = "TechCrunch (EUA)" if categoria == "Tech nos Negócios" else "The Verge (EUA)"
                
                noticias.append({
                    "id": id_counter,
                    "dataPub": dt_pub.strftime("%Y-%m-%d"),
                    "t": titulo_pt,
                    "f": fonte,
                    "cat": categoria,
                    "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80",
                    "texto": f"<p>{resumo_pt}</p><p><strong>Impacto:</strong> Atualização relevante dos últimos 3 dias no cenário global de inovação e inteligência artificial.</p>"
                })
                id_counter += 1
                itens_adicionados += 1

    return noticias

if __name__ == "__main__":
    novas_noticias = buscar_noticias()
    if novas_noticias:
        print(f"Sucesso! {len(novas_noticias)} notícias processadas.")
