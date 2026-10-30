import feedparser
import json
import re
from datetime import datetime, timedelta
import urllib.parse
import urllib.request

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

def gerar_imagem_tematica(titulo, categoria):
    titulo_lower = titulo.lower()
    
    if any(k in titulo_lower for k in ["robot", "automation", "robô", "automação"]):
        termo = "futuristic robotics technology"
    elif any(k in titulo_lower for k in ["cloud", "data center", "server", "nuvem"]):
        termo = "server data center technology"
    elif any(k in titulo_lower for k in ["security", "privacy", "segurança", "privacidade"]):
        termo = "cybersecurity digital network"
    elif any(k in titulo_lower for k in ["tv", "screen", "display", "tela"]):
        termo = "smart tv living room technology"
    elif any(k in titulo_lower for k in ["app", "phone", "mobile", "celular"]):
        termo = "modern smartphone user interface"
    elif any(k in titulo_lower for k in ["ai", "copilot", "chatgpt", "model"]):
        termo = "artificial intelligence neural network"
    else:
        termo = "modern technology business" if categoria == "Tech nos Negócios" else "digital lifestyle technology"

    return f"https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80"

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

            dt_pub = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                dt_pub = datetime(*entry.published_parsed[:6])

            if dt_pub >= limite_3_dias:
                titulo_pt = traduzir_texto(entry.title)
                resumo_limpo = limpar_html(getattr(entry, 'summary', getattr(entry, 'description', '')))
                resumo_pt = traduzir_texto(resumo_limpo[:200])

                imagem_tematica = gerar_imagem_tematica(entry.title, categoria)
                fonte = "TechCrunch (EUA)" if categoria == "Tech nos Negócios" else "The Verge (EUA)"
                
                noticias.append({
                    "id": id_counter,
                    "dataPub": dt_pub.strftime("%Y-%m-%d"),
                    "t": titulo_pt,
                    "f": fonte,
                    "cat": categoria,
                    "img": imagem_tematica,
                    "texto": f"<p>{resumo_pt}</p><p><strong>Impacto:</strong> Atualização relevante dos últimos 3 dias no cenário global de inovação e inteligência artificial.</p>"
                })
                id_counter += 1
                itens_adicionados += 1

    return noticias

def atualizar_html(noticias):
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            conteudo = f.read()

        json_noticias = json.dumps(noticias, ensure_ascii=False, indent=4)
        bloco_novo = f"// <!--INICIO_NOTICIAS-->\n        let todasNoticias = {json_noticias};\n        // <!--FIM_NOTICIAS-->"

        # Substitui exatamente a variável todasNoticias entre os marcadores do index.html
        padrao = r'// <!--INICIO_NOTICIAS-->[\s\S]*?// <!--FIM_NOTICIAS-->'
        
        if re.search(padrao, conteudo):
            novo_conteudo = re.sub(padrao, bloco_novo, conteudo)
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(novo_conteudo)
            print("Notícias injetadas com sucesso em 'todasNoticias' no index.html!")
        else:
            print("Marcadores não encontrados no index.html.")

    except Exception as e:
        print(f"Erro ao atualizar HTML: {e}")

if __name__ == "__main__":
    novas_noticias = buscar_noticias()
    if novas_noticias:
        atualizar_html(novas_noticias)
        print(f"Sucesso! {len(novas_noticias)} notícias processadas.")
