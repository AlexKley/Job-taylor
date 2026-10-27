#!/usr/bin/env python3
"""
fetch_job.py
Script auxiliar para Agent Skills do Google Antigravity.
Extrai e limpa a descrição de vagas de emprego a partir de uma URL ou arquivo HTML local.
"""

import sys
import json
import argparse
from typing import Optional, Dict, Any
from pathlib import Path
import httpx
import trafilatura
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


def fetch_html_from_url(url: str, timeout: float = 15.0) -> str:
    """Realiza a requisição HTTP contornando redirecionamentos e timeouts comuns."""
    try:
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=timeout) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        sys.stderr.write(f"[ERRO HTTP] Status {e.response.status_code} ao acessar {url}\n")
        sys.exit(1)
    except httpx.RequestError as e:
        sys.stderr.write(f"[ERRO DE CONEXÃO] Falha na requisição para {url}: {e}\n")
        sys.exit(1)


def parse_job_content(html: str, url: Optional[str] = None) -> Dict[str, Any]:
    """Extrai o texto principal, título e metadados estruturados da página."""
    # 1. Tentativa primária usando Trafilatura (otimizado para artigos e descrições de texto)
    extracted_text = trafilatura.extract(
        html,
        url=url,
        output_format="markdown",
        include_links=False,
        include_images=False,
        include_tables=True,
        no_fallback=False
    )
    
    metadata = trafilatura.extract_metadata(html)
    page_title = metadata.title if metadata and metadata.title else None

    # 2. Fallback caso o Trafilatura retorne vazio (páginas com estruturas DOM peculiares)
    if not extracted_text or len(extracted_text.strip()) < 150:
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove tags indesejadas
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
            tag.decompose()
            
        if not page_title and soup.title:
            page_title = soup.title.string.strip()
            
        extracted_text = soup.get_text(separator="\n", strip=True)

    return {
        "url": url,
        "title": page_title or "Título não identificado",
        "content_markdown": extracted_text.strip() if extracted_text else ""
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extrai o conteúdo textual limpo de anúncios de vagas para análise do Antigravity."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", "-u", type=str, help="URL pública da página da vaga.")
    group.add_argument("--file", "-f", type=Path, help="Caminho para arquivo HTML baixado localmente.")
    
    parser.add_argument(
        "--output", "-o", type=Path, default=None,
        help="Caminho do arquivo para salvar a saída (Markdown ou JSON). Se omitido, imprime no stdout."
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Exporta o resultado em formato JSON contendo título, url e conteúdo."
    )

    args = parser.parse_args()

    # Leitura da fonte de dados
    if args.url:
        html_raw = fetch_html_from_url(args.url)
        origin_url = args.url
    else:
        if not args.file.exists():
            sys.stderr.write(f"[ERRO] Arquivo não encontrado: {args.file}\n")
            sys.exit(1)
        html_raw = args.file.read_text(encoding="utf-8", errors="replace")
        origin_url = str(args.file.resolve())

    # Processamento
    job_data = parse_job_content(html_raw, url=origin_url)

    if not job_data["content_markdown"]:
        sys.stderr.write("[AVISO] Nenhum texto relevante foi extraído da página.\n")
        sys.exit(2)

    # Formatação do payload de saída
    if args.json:
        output_payload = json.dumps(job_data, ensure_ascii=False, indent=2)
    else:
        output_payload = (
            f"# {job_data['title']}\n"
            f"**Origem:** {job_data['url']}\n\n"
            f"---\n\n"
            f"{job_data['content_markdown']}\n"
        )

    # Destino da saída
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_payload, encoding="utf-8")
        sys.stderr.write(f"[SUCESSO] Conteúdo salvo em {args.output}\n")
    else:
        print(output_payload)


if __name__ == "__main__":
    main()