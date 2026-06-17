# Documento de Contexto Vivo — Projeto de Assistente Financeiro com IA

Versão 1.0

## 1. Mapeamento do Produto e MVP

### Visão do Produto

Aplicativo de organização financeira pessoal que utiliza IA como interface principal de interação.

O produto busca ocupar o espaço entre:

* Aplicativos financeiros extremamente completos, porém complexos para usuários comuns.
* Aplicativos simples que apresentam pouca capacidade de análise e orientação.

A proposta de valor não é apenas exibir dados financeiros, mas interpretar esses dados para o usuário.

### Público-Alvo

Usuários pouco técnicos que:

* Possuem dificuldade em interpretar gráficos e relatórios financeiros.
* Querem respostas diretas sobre sua situação financeira.
* Desejam orientação financeira contextual sem precisar aprender conceitos avançados.

### Problemas Resolvidos

* Falta de clareza sobre para onde o dinheiro está indo.
* Dificuldade em prever sobra ou falta de dinheiro.
* Dificuldade em tomar decisões de compra.
* Complexidade excessiva dos aplicativos financeiros tradicionais.

### Fluxo Principal do Usuário

1. Usuário acessa o aplicativo.
2. Visualiza gráficos de gastos e movimentações.
3. Recebe uma interpretação textual gerada por IA.
4. Interage com o assistente financeiro por linguagem natural.
5. Faz perguntas como:

   * Posso comprar determinado item?
   * Vou fechar o mês no positivo?
   * Onde estou gastando mais?
6. Corrige ou adiciona movimentações manualmente quando necessário.

### Estado Atual do Produto

Existe um protótipo funcional contendo:

* APK gerado.
* Código hospedado no GitHub.
* Dashboard financeiro.
* Gráficos financeiros.
* Chat baseado em IA.
* Visualização de entradas e saídas.
* Filtros financeiros.
* Configuração de Open Finance utilizando dados mockados.

### Dependências Externas Críticas

* Obtenção de CNPJ.
* Integração real com Open Finance.
* Publicação em lojas.
* Estrutura jurídica mínima para operação.

### Definição Atual de MVP

O MVP será considerado entregue quando:

* O usuário puder conectar suas finanças via Open Finance.
* O sistema exibir automaticamente movimentações.
* O dashboard gerar análises compreensíveis.
* O usuário puder conversar com a IA sobre sua situação financeira.
* O aplicativo estiver disponível para usuários externos.
* Houver validação com usuários reais.

---

# 2. Diagnóstico Operacional e Gargalos

## Nível de Maturidade Organizacional

Classificação atual:

Estágio Inicial de Operação Informal.

Características observadas:

* Reuniões ocasionais.
* Conversas presenciais na faculdade.
* Comunicação dispersa via WhatsApp.
* Ausência de backlog.
* Ausência de gestão formal de tarefas.
* Ausência de definição operacional de prioridades.

## Gargalos Principais

### Gargalo 1 — Ausência de Fonte Única da Verdade

Hoje não existe:

* Jira
* Trello
* GitHub Projects
* Notion operacional
* Documento central de acompanhamento

Consequências:

* Baixa visibilidade.
* Retrabalho.
* Decisões perdidas em conversas.

---

### Gargalo 2 — Prioridades Não Compartilhadas

Parte da equipe não consegue responder:

"Qual é a tarefa mais importante desta semana?"

Consequências:

* Esforço disperso.
* Dificuldade de coordenação.
* Paralisação por falta de direção.

---

### Gargalo 3 — Conhecimento Não Estruturado

Existe forte indício de que:

* Parte relevante das decisões foi tomada durante sessões de Claude Code.
* O contexto arquitetural não está consolidado em documentos compartilhados.

Consequências:

* Dependência indireta de contexto de IA.
* Dificuldade de onboarding.
* Dificuldade de manutenção futura.

---

### Gargalo 4 — Dependência de Pessoas-Chave

Existem atividades críticas cujo funcionamento é conhecido por poucos membros.

Exemplo conhecido:

* Processo de geração do APK.

Consequências:

* Ponto único de falha.
* Baixa resiliência operacional.

---

# 3. Matriz de Atuação Humana

## João

### Papel Atual

* Negócio.
* Produto.
* Desenvolvimento apoiado por Claude Code.

### Valor Gerado

* Mantém a visão do produto.
* Impulsiona evolução funcional.

### Riscos Operacionais

* Acúmulo de responsabilidades.
* Conhecimento disperso em conversas com IA.
* Possível dependência excessiva para decisões de produto.

### Como o próximo agente deve interagir

Perguntas recorrentes:

* Qual problema de usuário esta funcionalidade resolve?
* Isso aproxima o MVP da validação real?
* Existe documentação da decisão tomada?

Cobranças:

* Registrar decisões de produto.
* Tornar explícitas as prioridades.

---

## Porto

### Papel Atual

* Fullstack.

### Valor Gerado

* Capacidade de implementação transversal.

### Riscos Operacionais

* Tornar-se gargalo técnico.
* Receber demandas pouco definidas.

### Como o próximo agente deve interagir

Perguntas recorrentes:

* O que está bloqueando sua execução?
* Qual atividade gera mais impacto no MVP?

Cobranças:

* Documentar arquitetura emergente.
* Identificar dependências técnicas críticas.

---

## Ibere

### Papel Atual

* Backend.
* Infraestrutura.
* Servidores.

### Valor Gerado

* Sustentação técnica do produto.

### Riscos Operacionais

* Disponibilidade indefinida.
* Possíveis entregas sem previsibilidade.

### Como o próximo agente deve interagir

Perguntas recorrentes:

* Existe algum risco de infraestrutura?
* Existe alguma dependência crítica sem responsável?

Cobranças:

* Tornar responsabilidades explícitas.
* Registrar processos operacionais.

---

## Vitor

### Papel Atual

* Apoio técnico.
* Conhecimento inicial em Python e TypeScript.

### Valor Potencial

* QA.
* Testes.
* Documentação.
* Pesquisa.
* Organização operacional.

### Riscos Operacionais

* Ociosidade por falta de escopo.
* Participação reativa.

### Como o próximo agente deve interagir

Perguntas recorrentes:

* O que você consegue validar esta semana?
* Que documentação está faltando?

Cobranças:

* Produzir artefatos organizacionais.
* Apoiar validação funcional.

---

# 4. Plano de Voo Imediato

## Fase 0 — Estabilização Operacional

Objetivo:

Criar a infraestrutura mínima de gestão.

Entregas:

* Fonte única da verdade.
* Backlog centralizado.
* Lista oficial de responsáveis.
* Lista oficial do que existe.
* Lista oficial do que falta.

Nenhuma nova funcionalidade deve ter prioridade acima desta fase.

---

## Fase 1 — Auditoria do Produto Existente

Objetivo:

Descobrir exatamente o que já funciona.

Entregas:

* Inventário de funcionalidades.
* Inventário técnico.
* Inventário de integrações.
* Processo de build documentado.
* Processo de deploy documentado.

---

## Fase 2 — Definição Formal do MVP

Objetivo:

Transformar visão em escopo fechado.

Responder:

* O que entra no MVP?
* O que fica para depois?
* O que é obrigatório para lançamento?

---

## Fase 3 — Preparação para Operação Real

Objetivo:

Remover bloqueadores externos.

Frentes:

* CNPJ.
* Open Finance real.
* Aspectos regulatórios.
* Publicação nas lojas.

---

## Fase 4 — Validação de Mercado

Objetivo:

Colocar usuários reais dentro do sistema.

Métricas iniciais:

* Usuários ativos.
* Retenção.
* Frequência de uso do chat.
* Perguntas mais comuns.
* Feedback qualitativo.

---

## Meta Estratégica do Projeto

Transformar o protótipo acadêmico atual em uma startup operacional capaz de:

* Operar legalmente.
* Estar publicada nas lojas.
* Possuir usuários reais.
* Validar mercado.
* Obter os primeiros clientes pagantes.
