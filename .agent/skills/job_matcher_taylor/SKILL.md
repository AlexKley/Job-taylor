---
name: job-matcher-tailor
description: Busca e analisa vagas de emprego via URL ou texto, calcula a taxa de adequação (match score) contra o currículo mestre e, se o fit for superior a 60%, adapta o currículo destacando experiências relevantes e redige uma carta de apresentação personalizada.
---

# Job Matcher & Resume Tailor

## 1. Visão Geral e Arquitetura de Arquivos

Esta skill automatiza a triagem técnica de oportunidades, o cálculo objetivo de compatibilidade profissional e a geração de materiais de candidatura direcionados.

A skill opera utilizando a seguinte estrutura de arquivos locais:

- `data/base_resume.md`: Fonte única da verdade sobre o histórico do candidato.
- `data/cover_template.md`: Template padrão com estrutura e tom da carta de apresentação.
- `scripts/fetch_job.py`: Script de extração de conteúdo textual de páginas web.
- `output/<empresa>-<cargo>/`: Diretório onde os materiais gerados serão persistidos.

---

## 2. Pré-requisitos de Ambiente

Antes de executar scripts Python auxiliares, certifique-se de que temos um vitual environment instalado e ativo. Se não tiver, crie um:

```bash
python3 -m venv .venv
```

E ative-o:

```bash
source .venv/bin/activate
```

Depois instale as dependências executando:

```bash
pip install -r requirements.txt
```

---

## 3. Rubrica de Avaliação e Pontuação (Match Score)

Calcule a pontuação final (0 a 100%) confrontando os requisitos extraídos da vaga contra o arquivo `data/base_resume.md`, utilizando a matriz de pesos abaixo:

| Pilar de Avaliação | Peso | Critério de Pontuação |
|---|---:|---|
| Requisitos Obrigatórios / Hard Skills | 40% | Proporção de linguagens, frameworks, bancos e ferramentas indispensáveis dominados pelo candidato. |
| Tempo e Nível de Experiência | 25% | Compatibilidade de senioridade (Júnior, Pleno, Sênior, Especialista, Lead) e anos de atuação prática comprovada. |
| Requisitos Desejáveis / Diferenciais | 20% | Tecnologias secundárias, certificações, arquiteturas específicas ou conhecimentos complementares. |
| Alinhamento do Papel e Escopo | 15% | Correspondência entre as responsabilidades diárias da vaga e as entregas descritas no histórico do candidato. |

**Fórmula de Cálculo:**

$$
\text{Score Total} = (S_{\text{obrig}} \times 0.40) + (S_{\text{exp}} \times 0.25) + (S_{\text{desej}} \times 0.20) + (S_{\text{escopo}} \times 0.15)
$$

---

## 4. Fluxo de Execução Passo a Passo

### Passo 1: Extração dos Dados da Vaga

Quando o usuário fornecer uma URL, execute:

```bash
python scripts/fetch_job.py --url "<URL_DA_VAGA>" --output "output/temp_job.md"
```

Caso o usuário forneça o texto diretamente no prompt, utilize o texto bruto fornecido.

Extraia e catalogue internamente:

- Empresa contratante e título do cargo.
- Lista de requisitos obrigatórios versus desejáveis.
- Principais desafios técnicos e dores operacionais mencionadas.

### Passo 2: Cálculo de Compatibilidade e Relatório de Match

1. Leia `data/base_resume.md`.
2. Confronte cada requisito da vaga com as evidências do currículo.
3. Apresente ao usuário uma tabela comparativa no formato:

| Categoria | Requisito da Vaga | Evidência no Currículo Base | Status |
|---|---|---|---|
| Hard Skill | Ex: Fastify / Node.js | Microserviços em produção na Empresa X | ✅ Atende |
| Experiência | Ex: Gestão de Incidentes Tier-3 | Incident Commander no histórico | ✅ Atende |
| Diferencial | Ex: Rust | Projeto open-source documentado | ✅ Atende |
| Hard Skill | Ex: Kubernetes | Não localizado no currículo mestre | ❌ Lacuna |

4. Apresente o Score Final Calculado.

### Passo 3: Decisão por Threshold (Limite de 60%)

**Se Score < 60%:**

- Encerre o fluxo operacional.
- Explique os motivos da reprovação técnica, apontando as lacunas críticas que inviabilizam a candidatura competitiva.
- Não crie arquivos na pasta de saída.

**Se Score >= 60%:**

- Notifique o usuário sobre a aprovação de compatibilidade e prossiga imediatamente para as etapas de customização.

### Passo 4: Customização do Currículo (`curriculo_adaptado.md`)

1. Crie a pasta de destino: `output/<empresa>-<cargo>/`.
2. Gere o arquivo `output/<empresa>-<cargo>/curriculo_adaptado.md` respeitando as seguintes regras restritivas:

- **Inviolabilidade Factual:** É terminantemente proibido inventar empresas, cargos, métricas, datas ou ferramentas não presentes em `data/base_resume.md`.
- **Reordenação Estratégica:** Mova para o topo dos bullet points as realizações e stacks que respondem diretamente às exigências da vaga.
- **Alinhamento de Vocabulário (ATS):** Ajuste a terminologia técnica para espelhar os termos exatos do anúncio da vaga (ex: se o currículo diz "APIs RESTful" e a vaga exige "REST APIs", padronize).
- **Filtragem de Ruído:** Omita ou reduza tópicos secundários que não agreguem valor para esta vaga específica.

### Passo 5: Geração da Carta de Apresentação (`carta_apresentacao.md`)

1. Leia o arquivo `data/cover_template.md`.
2. Substitua os placeholders pelas variáveis mapeadas conforme a tabela abaixo:

| Variável | Origem dos Dados | Critério de Preenchimento |
|---|---|---|
| `{{CANDIDATE_NAME}}` | `data/base_resume.md` | Nome completo do candidato. |
| `{{CANDIDATE_LOCATION}}` | `data/base_resume.md` | Cidade, estado e país de residência. |
| `{{CANDIDATE_EMAIL}}` | `data/base_resume.md` | E-mail principal de contato. |
| `{{CANDIDATE_PORTFOLIO_OR_LINKEDIN}}` | `data/base_resume.md` | Link para portfólio, GitHub ou LinkedIn. |
| `{{CURRENT_DATE}}` | Sistema | Data atual por extenso (ex: 23 de Outubro de 2026). |
| `{{COMPANY_NAME}}` | Anúncio da vaga | Nome da empresa contratante. |
| `{{JOB_TITLE}}` | Anúncio da vaga | Título oficial da vaga anunciada. |
| `{{JOB_REFERENCE_OR_SOURCE}}` | Anúncio ou URL | Link ou código identificador da vaga. |
| `{{YEARS_OF_EXPERIENCE}}` | `data/base_resume.md` | Total consolidado de anos de experiência relevante. |
| `{{CORE_DOMAIN_AREA}}` | Vaga / Currículo | Área técnica central compartilhada (ex: engenharia de software full stack). |
| `{{PRIMARY_JOB_CHALLENGE_OR_PAIN_POINT}}` | Anúncio da vaga | O desafio crítico que a contratação visa solucionar. |
| `{{SPECIFIC_ACCOMPLISHMENT_WITH_METRICS}}` | `data/base_resume.md` | Conquista real com métricas comprovadas que endereça a dor acima. |
| `{{RELEVANT_TECH_STACK_1}}` | Interseção | Primeira tecnologia-chave comum à vaga e ao currículo base. |
| `{{RELEVANT_TECH_STACK_2}}` | Interseção | Segunda tecnologia-chave comum à vaga e ao currículo base. |
| `{{SECONDARY_DIFFERENTIATOR_OR_METHODOLOGY}}` | `data/base_resume.md` | Diferencial técnico comprovado (ex: observabilidade, CI/CD, microsserviços). |
| `{{CANDIDATE_PHONE_OR_CONTACT}}` | `data/base_resume.md` | Telefone ou meio de contato direto. |
| `{{CANDIDATE_GITHUB_OR_LINKEDIN}}` | `data/base_resume.md` | Perfil técnico complementar para assinatura. |

3. Salve o resultado final em `output/<empresa>-<cargo>/carta_apresentacao.md`.

### Passo 6: Exportação dos Documentos em PDF

Após persistir `curriculo_adaptado.md` e `carta_apresentacao.md`, execute no terminal:
```bash
python scripts/export_pdf.py "output/<empresa>-<cargo>/"
```

Apresente ao usuário um resumo executivo da operação contendo:
- Caminho completo dos arquivos gerados no disco.
- Principais pontos de destaque inseridos no currículo adaptado.
- Resumo da narrativa adotada na carta de apresentação.