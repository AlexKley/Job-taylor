# Busca Trabalho — Job Matcher & Resume Tailor

Repositório de automação e inteligência para busca, triagem técnica e preparação personalizada de candidaturas a vagas de tecnologia.

Este projeto utiliza o **Google Antigravity** em conjunto com a skill customizada [`job-matcher-tailor`](file:///.agent/skills/job_matcher_taylor/README.md).

---

## 🎯 Objetivo

1. **Extração de Vagas:** Obtenção e parsing automático de anúncios de empregos a partir de URLs públicas (LinkedIn, Gupy, portais corporativos) ou texto direto.
2. **Avaliação Técnica Objetiva:** Cálculo do índice de aderência (*Match Score*) através de rubrica ponderada confrontando os requisitos com o currículo mestre (`data/base_resume.md`).
3. **Customização Guiada (Score ≥ 60%):** Adaptação estratégica do currículo mantendo inviolabilidade factual e redação de carta de apresentação sob medida.
4. **Exportação Automática:** Geração de PDFs em alta resolução (padrão A4, compatíveis com leitores ATS) via WeasyPrint.

---

## 🚀 Como Começar

### 1. Configurar o Ambiente Virtual

```bash
# Criar o ambiente virtual
python3 -m venv .venv

# Ativar o ambiente virtual
source .venv/bin/activate

# Instalar as dependências
pip install -r .agent/skills/job_matcher_taylor/requirements.txt
```

### 2. Documentação da Skill

Consulte a documentação completa da arquitetura, scripts e regras em:
👉 [**Documentação da Skill Job Matcher & Resume Tailor**](file:///.agent/skills/job_matcher_taylor/README.md)

---

## 📂 Diretórios

* `.agent/skills/job_matcher_taylor/`: Código da skill, templates, currículo mestre e scripts.
* `output/`: Diretório de saída com materiais gerados por vaga (`output/<empresa>-<cargo>/`).
