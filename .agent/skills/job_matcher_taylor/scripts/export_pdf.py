#!/usr/bin/env python3
"""
export_pdf.py
Converte arquivos Markdown (currículos e cartas de apresentação) em PDFs estilizados
utilizando WeasyPrint e regras de CSS Paged Media.
"""

import sys
import argparse
from pathlib import Path
import markdown
# pyrefly: ignore[missing-import]
from weasyprint import HTML, CSS

# CSS otimizado para leitura em tela, impressão A4 e parsers ATS
DEFAULT_CSS = """
@page {
    size: A4;
    margin: 18mm 18mm 18mm 18mm;
    @bottom-right {
        content: counter(page);
        font-size: 8pt;
        color: #718096;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.45;
    color: #1a202c;
    background: #ffffff;
    margin: 0;
    padding: 0;
}

/* Cabeçalho do Candidato */
h1 {
    font-size: 18pt;
    font-weight: 700;
    color: #0f172a;
    margin-top: 0;
    margin-bottom: 4px;
    letter-spacing: -0.02em;
}

/* Seções Principais */
h2 {
    font-size: 12pt;
    font-weight: 600;
    color: #0f172a;
    border-bottom: 1.5px solid #cbd5e1;
    padding-bottom: 3px;
    margin-top: 14px;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    page-break-after: avoid;
    break-after: avoid;
}

/* Subcabeçalhos de Cargos e Projetos */
h3 {
    font-size: 10.5pt;
    font-weight: 600;
    color: #1e293b;
    margin-top: 10px;
    margin-bottom: 2px;
    page-break-after: avoid;
    break-after: avoid;
}

p {
    margin-top: 0;
    margin-bottom: 6px;
}

/* Linhas divisórias */
hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 10px 0;
}

/* Listas de realizações e stacks */
ul {
    margin-top: 2px;
    margin-bottom: 8px;
    padding-left: 18px;
}

li {
    margin-bottom: 3px;
}

/* Badges e termos inline de tecnologia */
code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 8.5pt;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 1px 4px;
    border-radius: 3px;
    border: 1px solid #e2e8f0;
}

/* Tabelas (quando presentes) */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 9pt;
}

th, td {
    border: 1px solid #cbd5e1;
    padding: 6px 8px;
    text-align: left;
}

th {
    background-color: #f8fafc;
    font-weight: 600;
}

/* Prevenção de quebras desagradáveis em blocos de cargo */
.job-block {
    page-break-inside: avoid;
    break-inside: avoid;
}
"""


def convert_markdown_to_pdf(input_file: Path, output_file: Path, custom_css: Path = None):
    """Converte um arquivo Markdown individual para PDF aplicando o CSS especificado."""
    if not input_file.exists():
        sys.stderr.write(f"[ERRO] Arquivo de entrada não encontrado: {input_file}\n")
        return False

    # Leitura do markdown
    md_text = input_file.read_text(encoding="utf-8")

    # Conversão para HTML com extensões para tabelas e metadados
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists"]
    )

    full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>{input_file.stem}</title>
</head>
<body>
{html_body}
</body>
</html>
"""

    # Carrega CSS customizado se fornecido, senão usa o padrão embutido
    css_rules = custom_css.read_text(encoding="utf-8") if custom_css and custom_css.exists() else DEFAULT_CSS

    # Renderização via WeasyPrint
    output_file.parent.mkdir(parents=True, exist_ok=True)
    html_doc = HTML(string=full_html, base_url=str(input_file.parent))
    css_doc = CSS(string=css_rules)

    html_doc.write_pdf(output_file, stylesheets=[css_doc])
    print(f"[SUCESSO] PDF gerado: {output_file}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Gera PDFs estilizados a partir de Markdowns para o Antigravity."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Caminho do arquivo Markdown ou diretório contendo os arquivos."
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Caminho do PDF de saída. Se omitido, substitui .md por .pdf."
    )
    parser.add_argument(
        "--css",
        type=Path,
        default=None,
        help="Caminho para arquivo CSS externo customizado (opcional)."
    )

    args = parser.parse_args()

    # Caso 1: Processamento de pasta inteira
    if args.input.is_dir():
        md_files = list(args.input.glob("*.md"))
        if not md_files:
            print(f"[AVISO] Nenhum arquivo .md encontrado em {args.input}")
            sys.exit(0)

        for md in md_files:
            out_pdf = md.with_suffix(".pdf")
            convert_markdown_to_pdf(md, out_pdf, args.css)

    # Caso 2: Processamento de arquivo único
    elif args.input.is_file():
        out_pdf = args.output if args.output else args.input.with_suffix(".pdf")
        success = convert_markdown_to_pdf(args.input, out_pdf, args.css)
        if not success:
            sys.exit(1)
    else:
        sys.stderr.write(f"[ERRO] Caminho inválido: {args.input}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()