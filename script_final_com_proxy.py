import requests
import re
import urllib.parse
import time

# Configuração do proxy para capturar requisições no Burp Suite
proxy = "http://127.0.0.1:8080"
proxies = {
    "http": proxy,
    "https": proxy  # Burp Suite precisa interceptar HTTPS, por isso redirecionamos
}

# Desativando a verificação de SSL para evitar erros com o proxy
session = requests.Session()
session.proxies.update(proxies)
session.verify = False  # Desativa a verificação SSL
session.trust_env = False  # Evita que o sistema use configurações globais de proxy

# Adaptador para garantir o uso do proxy em todas as requisições
adapter = requests.adapters.HTTPAdapter()
session.mount("http://", adapter)
session.mount("https://", adapter)

# URL base da primeira requisição
url1 = "https://bancocarrefourcx.qualtrics.com/jfe/form/SV_086DabUpWp3iY8m"

# Cabeçalhos fixos
headers1 = {
    "Sec-Ch-Ua": '"Chromium";v="133", "Not(A:Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=0, i"
}

while True:
    try:
        # Fazendo a primeira requisição e capturando os cookies
        response1 = session.get(url1, headers=headers1, allow_redirects=True)

        # Capturando o cookie ak_bmsc
        akcookie = session.cookies.get("ak_bmsc")

        # Capturando tokens da resposta JSON
        session_match = re.search(r'session%22%3A%7B%22id%22%3A%22(.*?)%22', response1.text)
        client_id_match = re.search(r'clientId%22%3A%22(.*?)%22', response1.text)
        cached_runtime_match = re.search(r'cachedRuntime%22%3A%22(.*?)%22', response1.text)

        # Armazenando valores capturados
        session_id = session_match.group(1) if session_match else None
        client_id = client_id_match.group(1) if client_id_match else None
        cached = cached_runtime_match.group(1) if cached_runtime_match else None
        cached_encoded = urllib.parse.unquote(cached) if cached else None

        # Enviando segunda requisição via proxy
        url2 = f"https://bancocarrefourcx.qualtrics.com/jfe3/form/SV_086DabUpWp3iY8m/session/{session_id}/next?clientId={client_id}"
        headers2 = {
            "Host": "bancocarrefourcx.qualtrics.com",
            "Cookie": f"ak_bmsc={akcookie}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Origin": "https://bancocarrefourcx.qualtrics.com",
            "Referer": "https://bancocarrefourcx.qualtrics.com/jfe/form/SV_086DabUpWp3iY8m",
            "Accept-Encoding": "gzip, deflate, br"
        }
        payload2 = {
            "transactionId": 1,
            "cachedRuntime": cached_encoded,
            "type": "questions",
            "analytics": {"questions": {}, "page": {"elapsedSeconds": 91.269}},
            "meta": {"resolution": "1920x1080"}
        }

        response2 = session.post(url2, headers=headers2, json=payload2, allow_redirects=True)

        # Capturando o novo cookie
        cookie_jfe3 = session.cookies.get("9Wr0SLdEGMbV5zHWGkVu5AslQexqxRQlvDk31%2FcRqhc%3D")

        # Lista de requisições a serem enviadas
        requests_list = [
            {"transactionId": 3, "type": "questions", "analytics": {"questions": {}, "page": {"elapsedSeconds": 149.409}}},
            {"transactionId": 5, "type": "questions", "hiddenQuestions": ["QID4"], "analytics": {"questions": {}, "page": {"elapsedSeconds": 14.329}}},
            {"transactionId": 7, "type": "questions", "analytics": {"questions": {}, "page": {"elapsedSeconds": 15.395}}},
            {"transactionId": 9, "type": "questions", "analytics": {"questions": {}, "page": {"elapsedSeconds": 14.939}}},
            {"transactionId": 11, "type": "questions", "responses": {"QID7": "Automacao"}, "analytics": {"questions": {"QID7": {"keystrokeCount": 13, "pasteCount": 0, "elapsedSeconds": 10.755}}, "page": {"elapsedSeconds": 23.118}}}
        ]

        # Enviando as requisições via proxy
        for req in requests_list:
            response = session.post(
                f"https://bancocarrefourcx.qualtrics.com/jfe3/form/SV_086DabUpWp3iY8m/session/{session_id}/next?clientId={client_id}",
                headers={
                    "Host": "bancocarrefourcx.qualtrics.com",
                    "Cookie": f"ak_bmsc={akcookie}; 9Wr0SLdEGMbV5zHWGkVu5AslQexqxRQlvDk31%2FcRqhc%3D={cookie_jfe3}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                    "Origin": "https://bancocarrefourcx.qualtrics.com",
                    "Referer": "https://bancocarrefourcx.qualtrics.com/jfe/form/SV_086DabUpWp3iY8m",
                    "Accept-Encoding": "gzip, deflate, br"
                },
                json=req,
                allow_redirects=True
            )

            # Se for a última requisição, verificar a resposta
            if req["transactionId"] == 11:
                if "Agradecemos o tempo que você dedicou respondendo a esta pesquisa. <br> Sua resposta foi registrada." in response.text:
                    print("Formulário aceito pela aplicação")

            # Delay de 0.5s entre requisições
            time.sleep(0.5)

        # Exibindo valores capturados
        print(f"\nCiclo concluído, reiniciando.")
#        print(f"akcookie: {akcookie}")
#        print(f"session_id: {session_id}")
#        print(f"client_id: {client_id}")
#        print(f"cached: {cached}")
#        print(f"cached_encoded: {cached_encoded}")
#        print(f"cookie_jfe3: {cookie_jfe3}")

        # Delay de 0.5 segundos antes do próximo ciclo
        time.sleep(0.5)

    except Exception as e:
        print(f"Erro: {e}")
