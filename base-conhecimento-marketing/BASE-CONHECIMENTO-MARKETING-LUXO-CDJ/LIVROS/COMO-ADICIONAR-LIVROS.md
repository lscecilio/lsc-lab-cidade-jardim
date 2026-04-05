# COMO ADICIONAR LIVROS À BASE DE CONHECIMENTO — ESPECIALISTA EM MARKETING DE LUXO

## PASSO A PASSO

### 1. Coloque os PDFs na pasta correta
Vá até a pasta `LIVROS/` e coloque cada PDF na subpasta correspondente ao tema:

- `01-FUNDAMENTOS-DO-LUXO/` → Kapferer, Bastien, Okonkwo, Chevalier, Mazzalovo, Veblen
- `02-NEUROMARKETING-E-PSICOLOGIA/` → Lindstrom, Zaltman, Dooley, Ariely, Barden
- `03-EXPERIENCIA-E-HOSPITALIDADE-LUXO/` → Pine & Gilmore, Schulze, Meyer, Sharp, Inghilleri
- `04-BRANDING-ESTRATEGICO/` → Aaker, Ries & Trout, Sinek, Kapferer branding
- `05-IMOBILIARIO-ALTO-PADRAO/` → Luxury real estate, loteamentos, branded residences, HNWI
- `06-PSICOLOGIA-DO-CONSUMIDOR-PREMIUM/` → Cialdini, comportamento comprador de luxo, UHNWI
- `07-COMUNICACAO-E-PERSUASAO/` → Copywriting premium, storytelling de luxo, tom de voz
- `08-CASES-E-REFERENCIAS-LUXO/` → Aman, Four Seasons, Ritz-Carlton, Fendi Casa, branded residences

### 2. Avise o Claude quais livros foram adicionados
Exemplo: "Adicionei Kapferer e Lindstrom na pasta 01-FUNDAMENTOS-DO-LUXO"

### 3. O Claude converte automaticamente
- Usa `pdftotext` (leve, sem estourar memória)
- Gera arquivo `.md` com nome MAIÚSCULO padronizado
- Salva o PDF original em `_ORIGINAIS_PDF/`
- Atualiza o índice de conhecimento

---

## FORMATO DOS ARQUIVOS CONVERTIDOS

Cada livro vira um arquivo .md com esta estrutura:
```
AUTOR-SOBRENOME_TITULO-RESUMIDO.md
```

Exemplos:
- `KAPFERER_LUXURY-STRATEGY.md`
- `LINDSTROM_BUYOLOGY.md`
- `PINE-GILMORE_EXPERIENCE-ECONOMY.md`
- `SCHULZE_EXCELLENCE-WINS.md`
- `CIALDINI_INFLUENCE.md`

---

## CONSULTE OS GUIAS
- `GUIA-LIVROS-POR-CATEGORIA.md` → lista completa por tema com prioridade
- `AUDITORIA-LIVROS-FALTANTES.md` → o que ainda precisa ser adicionado
