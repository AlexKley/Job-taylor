---
name: job-matcher-tailor
description: Analisa vagas de emprego nacionais e internacionais via URL ou texto, aplica hard gates de visto, fuso horário e idioma, calcula o match score técnico contra o currículo mestre e, se o fit for >= 60%, adapta o currículo e redige carta de apresentação no idioma de origem da vaga (Português ou Inglês), exportando os materiais em Markdown e PDF.
---

# Job Matcher & Resume Tailor

## 1. Estrutura do Workspace e Fontes de Dados
Esta skill automatiza a triagem técnica de vagas (nacionais e remotas internacionais), a checagem regulatória/geográfica, a auditoria de aderência e a compilação bilíngue de currículos e cartas direcionadas.

Hierarquia de arquivos esperada:
- `data/base_resume.md`: Fonte única de fatos, métricas, competências e parâmetros de elegibilidade do candidato.
- `data/cover_template.md`: Template estruturado para cartas em português.
- `data/cover_template_en.md`: Template estruturado para cartas em inglês (*Cover Letter*).
- `scripts/fetch_job.py`: Extrator de conteúdo textual de páginas web de vagas.
- `scripts/export_pdf.py`: Compilador de Markdown para PDF via WeasyPrint.
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

## 3. Hard Gates de Elegibilidade Internacional (Etapa Eliminatória)

Antes de avaliar stacks ou calcular pontuações técnicas, verifique se a oportunidade possui bloqueios regulatórios, geográficos ou contratuais intransponíveis com base na seção de parâmetros de data/base_resume.md:

1. **Localização e Trabalho Remoto:**
    Elegível: Remote - Worldwide, Remote - LATAM, Anywhere, ou presencial com Relocation / Visa Sponsorship.
    Bloqueio: US Only, EU/UK Only, residência obrigatória em país específico sem suporte a visto.

2. **Autorização de Trabalho e Visto:**
    Bloqueio: Menções mandatórias a "US Citizen / Green Card only", "Must be authorized to work in [País] without employer sponsorship", "No C2C", "W2 only".
    Elegível para atuação internacional: Empresas que contratam via modelo B2B / Independent Contractor ou plataformas de Employer of Record (Deel, Remote, Gusto, Oyster, etc.).

3. **Compatibilidade de Fuso Horário:**
    O fuso base do candidato é UTC-3 (BRT).
    Vagas com exigência de sobreposição (overlap) de até 4 a 6 horas com horários comerciais dos EUA (EST/PST) ou Europa (WET/CET) são plenamente elegíveis.

4. **Idioma de Trabalho:**
    Exigência de fluência em inglês para escrita técnica, documentação e reuniões síncronas/assíncronas é compatível com o perfil.

**Regra de Aborto Imediato:** Se a vaga violar qualquer um dos itens acima (ex: vaga nos EUA exclusiva para residentes locais sem visto), encerre a execução imediatamente com Match Score: 0%, explicitando ao usuário o motivo regulatório ou territorial do impedimento, sem gerar arquivos de candidatura.

---

## 4. Rubricas de Avaliação de Compatibilidade (Match Score)
Caso a oportunidade seja aprovada nos Hard Gates, utilize a rubrica correspondente ao tipo de vaga:

### A. Vagas Nacionais (Brasil / CLT ou PJ)

| Pilar de Avaliação | Peso | Critério de Pontuação |
|---|---|---|
| Requisitos Obrigatórios / Hard Skills | 40% | Domínio de linguagens, frameworks, bancos de dados e ferramentas essenciais. |
| Tempo e Nível de Experiência | 25% | Compatibilidade de senioridade e tempo de atuação comprovada no mercado. |
| Requisitos Desejáveis / Diferenciais | 20% | Tecnologias secundárias, certificações e arquiteturas listadas como bônus. |
| Alinhamento do Papel e Escopo | 15% | Sinergia entre as responsabilidades diárias e as realizações comprovadas. |

### B. Vagas Internacionais (Remoto Global / B2B / Contractor)

| Pilar de Avaliação | Peso | Critério de Pontuação |
| ---|---|--- |
| Hard Skills & Arquitetura | 35% | Tecnologias centrais, design de sistemas distribuídos e qualidade de código. |
| Senioridade, Autonomia & Ownership | 25% | Capacidade de entrega autônoma, iniciativa e histórico de resolução de problemas complexos. |
| Comunicação, Idioma e Fuso Horário | 15% | Alinhamento com horário UTC-3, inglês técnico e maturidade em comunicação assíncrona. |
| Requisitos Desejáveis / Diferenciais | 15% | Diferenciais práticos (open source, linguagens de alta performance, automações). |
| Compatibilidade de Contratação | 10% | Aderência ao formato de contratação internacional (Contractor / B2B). |

Calcule a pontuação final (0 a 100%) confrontando os requisitos extraídos da vaga contra o arquivo `data/base_resume.md`, utilizando a matriz de pesos abaixo:

| Pilar de Avaliação | Peso | Critério de Avaliação Internacional |
| ---|---|--- |
| Hard Skills & Arquitetura | 35% | Tecnologias, frameworks e padrões exigidos pela vaga internacional. |
| Senioridade e Autonomia | 25% | Histórico de entregas autônomas, resolução de problemas complexos e liderança. |
| Comunicação, Idioma e Fuso | 15% | Alinhamento com fuso (UTC-3), fluência em inglês técnico e maturidade para trabalho assíncrono. |
| Requisitos Desejáveis / Bônus | 15% | Diferenciais técnicos (ex: Rust, automações avançadas, contribuições open-source). |
| Fit de Modelo de Contratação | 10% | Compatibilidade com o formato de contratação (ex: B2B/Contractor vs contratação direta). |

---

## 5. Diretriz de Idioma dos Entregáveis

O idioma do anúncio e a nacionalidade da empresa determinam o idioma dos arquivos finais:
- **Anúncio em Inglês ou Vaga Internacional:**
    - Currículo: output/<empresa>-<cargo>/resume_tailored.md (Totalmente em Inglês).
    - Carta: output/<empresa>-<cargo>/cover_letter.md (Totalmente em Inglês, baseado em `data/cover_template_en.md`).
    - Terminologia: Use padrões internacionais (Software Engineer, Contractor, Distributed Systems, High Availability).
- **Anúncio em Português ou Vaga Nacional:**
    - Currículo: output/<empresa>-<cargo>/curriculo_adaptado.md (Em Português).
    - Carta: output/<empresa>-<cargo>/carta_apresentacao.md (Em Português, baseado em `data/cover_template.md`).

---

## 6. Fluxo Operacional Passo a Passo

### Etapa 1: Captura dos Requisitos

1. Para URLs, execute o coletor:

```bash
python scripts/fetch_job.py --url "<URL_DA_VAGA>" --output "output/temp_job.md"
```

2. Para textos colados diretamente, processe o texto fornecido.

3. Identifique país da vaga, modalidade (remoto global vs local), restrições de visto e idioma exigido.

### Etapa 2: Auditoria de Hard Gates
- Valide os 4 filtros eliminatórios internacionais (Seção 3).
- Se houver impedimento legal/geográfico, emita o relatório de bloqueio e aborte.

### Etapa 3: Cálculo do Match Score
- Confronte os requisitos da vaga com data/base_resume.md.
- Apresente ao usuário uma tabela estruturada:

| Categoria | Requisito da Vaga | Evidência em base_resume.md | Status |
|---|---|---|---|
| Hard Skill | Ex: TypeScript / Node.js | Microsserviços de alta escala documentados | ✅ Atende |
| Experiência | Ex: Autonomous Delivery | Histórico de entregas ponta a ponta | ✅ Atende |
| Fuso / Idioma | Ex: 4h overlap EST / English | UTC-3 (overlap total) / Inglês fluente | ✅ Atende |
| Hard Skill | Ex: Kubernetes Cluster Admin | Não localizado no currículo mestre | ❌ Lacuna |

- Calcule e exiba a pontuação final percentual (Score Final).

### Etapa 4: Decisão por Threshold (Limite: 60%)
- Score < 60%: Encerre o fluxo sem criar pastas ou arquivos. Destaque os gaps técnicos a serem desenvolvidos.
- Score >= 60%: Notifique a aprovação e prossiga para a geração dos documentos.

### Etapa 5: Customização do Currículo
1. Crie o diretório output/<empresa>-<cargo>/.

2. Gere o arquivo Markdown (resume_tailored.md ou curriculo_adaptado.md):
    - Inviolabilidade Factual: Mantenha fidelidade estrita às experiências e números do currículo base.
    - Priorização Estratégica: Traga para o topo os projetos e tecnologias diretamente demandados pela vaga.
    - Otimização de Vocabulário (ATS): Utilize a terminologia exata da vaga.
    - Omitir informações sensíveis ou desnecessárias para a vaga, como endereço completo (pode-se usar apenas cidade/estado/país), número de documentos (RG, CPF) e estado civil.

### Etapa 6: Geração da Carta de Apresentação
1. Utilize o template do idioma correspondente (data/cover_template_en.md ou data/cover_template.md).

2. Preencha as variáveis mapeadas:

| Variável | Fonte do Dado | Critério de Preenchimento |
|----------|---------------|---------------------------|
| {{CANDIDATE_NAME}} | data/base_resume.md | Nome completo do candidato. |
| {{CANDIDATE_LOCATION}} | data/base_resume.md | Localidade e fuso horário (ex: Brazil - UTC-3). |
| {{CANDIDATE_EMAIL}} | data/base_resume.md | E-mail de contato. |
| {{CANDIDATE_PORTFOLIO_OR_LINKEDIN}} | data/base_resume.md | Links de perfil profissional. |
| {{CURRENT_DATE}} | Sistema | Data atual por extenso no idioma da vaga. |
| {{COMPANY_NAME}} | Vaga | Nome da empresa contratante. |
| {{JOB_TITLE}} | Vaga | Título oficial do cargo. |
| {{JOB_REFERENCE_OR_SOURCE}} | Entrada | Link ou código da vaga. |
| {{YEARS_OF_EXPERIENCE}} | data/base_resume.md | Total de anos de experiência relevante. |
| {{CORE_DOMAIN_AREA}} | Vaga / Currículo | Domínio técnico central compatível. |
| {{PRIMARY_JOB_CHALLENGE_OR_PAIN_POINT}} | Vaga | Principal dor ou meta técnica descrita na vaga. |
| {{SPECIFIC_ACCOMPLISHMENT_WITH_METRICS}} | data/base_resume.md | Realização comprovada com métricas alinhada ao desafio. |
| {{RELEVANT_TECH_STACK_1}} | Interseção | Primeira tecnologia-chave compartilhada. |
| {{RELEVANT_TECH_STACK_2}} | Interseção | Segunda tecnologia-chave compartilhada. |
| {{SECONDARY_DIFFERENTIATOR_OR_METHODOLOGY}} | data/base_resume.md | Diferencial prático (ex: system observability, CI/CD, Tier-3 incident response). |
| {{CONTRACT_PREFERENCE}} | data/base_resume.md | Ex: B2B/Contractor via Deel/Remote (se vaga internacional). |

3. Salve em output/<empresa>-<cargo>/cover_letter.md (ou carta_apresentacao.md).

### Etapa 7: Compilação em PDF e Entrega

1. Execute no terminal:
```bash
python scripts/export_pdf.py "output/<empresa>-<cargo>/"
```
2. Apresente ao usuário o relatório final:
    - Caminhos dos arquivos gerados (.md e .pdf).
    - Resumo da pontuação nos pilares de avaliação.
    - Justificativa do direcionamento adotado no currículo e na carta.