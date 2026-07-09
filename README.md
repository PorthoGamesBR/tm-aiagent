# Maestro

> Um gerente de projeto assistido por IA que mantém o estado do projeto, propõe tarefas e ajuda equipes pequenas a transformar objetivos em entregas.

## O problema

Equipes pequenas costumam ter uma característica curiosa:

Todo mundo sabe construir.

Poucos sabem organizar.

No nosso caso somos quatro desenvolvedores construindo uma startup.

O conhecimento fica concentrado em uma pessoa.

As decisões acontecem em conversas.

As tarefas não são explícitas.

O roadmap muda constantemente.

Como consequência:

- ninguém sabe exatamente o que fazer hoje;
- novas funcionalidades aparecem antes das antigas terminarem;
- o projeto evolui sem uma direção clara;
- decisões importantes se perdem em conversas;
- documentação fica desatualizada;
- pessoas deixam de contribuir simplesmente porque não sabem onde ajudar.

Esse problema não é exclusivo da nossa equipe.

Ferramentas como Jira, Trello e Notion armazenam informação, mas dependem que alguém organize tudo manualmente.

O Maestro nasce para diminuir esse trabalho.

---

# Objetivo

O objetivo do Maestro não é substituir um gerente.

Seu objetivo é responder continuamente perguntas como:

- Qual minha tarefa hoje?
- O que falta para entregar o MVP?
- Quem está responsável por isso?
- Existe algum bloqueio?
- Essa decisão já foi tomada?
- O que mudou desde ontem?
- Essa funcionalidade já existe?

---

# MVP

O primeiro MVP terá apenas um fluxo principal.

```
Funcionário

↓

"Qual minha tarefa hoje?"

↓

Maestro

↓

Analisa

- Estado do projeto
- Objetivo atual
- Perfil do colaborador
- Dependências
- Prioridades

↓

Propõe uma tarefa

↓

Funcionário aceita

↓

Cria automaticamente um card no Trello

↓

Ao finalizar

↓

Atualiza o estado do projeto
```

Esse fluxo já resolve um problema real da equipe.

---

# Como o Maestro funciona

O Maestro trabalha sobre um **Estado do Projeto**.

Esse estado representa a verdade atual do projeto.

Exemplo:

```
Projeto

Objetivo Atual

Equipe

Tarefas

Decisões

Roadmap

Riscos

Arquitetura

Documentação
```

Esse estado possui versionamento.

Toda alteração gera uma nova versão.

O histórico nunca é perdido.

---

# Fontes de conhecimento

O estado inicial é construído a partir de diferentes fontes.

## Código

O código fonte é analisado por um LLM.

O objetivo não é responder perguntas sobre código.

O objetivo é extrair conhecimento como:

- arquitetura
- funcionalidades existentes
- módulos
- tecnologias utilizadas
- responsabilidades

---

## Documentação

README

Documentos técnicos

Documentação de negócio

---

## Contexto de negócio

- Mercado financeiro
- BACEN
- Ouvidorias
- Clientes
- Concorrentes
- Estratégia

---

## Equipe

Cada colaborador possui um perfil.

Exemplo:

- tecnologias dominadas
- disponibilidade
- responsabilidades
- interesses

---

## Conversas

As conversas não representam a verdade.

Elas geram propostas de alteração no estado.

---

# Estado do Projeto

O Estado do Projeto é o núcleo do Maestro.

Ele contém informações estruturadas.

Exemplo:

```
Objetivos

Tarefas

Riscos

Decisões

Roadmap

Equipe

Dependências

Arquitetura

Documentação
```

Toda alteração gera uma nova versão.

Nenhuma informação é sobrescrita.

---

# Papel do RAG

O RAG NÃO guarda o estado do projeto.

Ele serve para responder perguntas usando:

- código
- documentação
- mercado
- negócio

Exemplos:

"Como funciona essa feature?"

"Qual documento fala sobre isso?"

"Onde essa decisão foi tomada?"

---

# Papel do Agente

O agente trabalha sobre o Estado do Projeto.

Seu trabalho é:

- responder perguntas
- propor tarefas
- detectar bloqueios
- atualizar o estado
- registrar decisões
- criar cartões no Trello
- identificar desalinhamentos

O agente nunca modifica o estado diretamente.

Ele propõe alterações.

Após confirmação, uma nova versão do estado é criada.

---

# Fluxos do MVP

## Fluxo 1

Pergunta

> Qual minha tarefa hoje?

Resposta

- analisa objetivo atual
- analisa backlog
- analisa perfil do colaborador
- propõe uma tarefa

Após confirmação

- cria card no Trello
- registra responsável

---

## Fluxo 2

Pergunta

> Terminei.

Resposta

- move cartão
- pergunta o que mudou
- atualiza estado
- identifica tarefas desbloqueadas

---

## Fluxo 3

Pergunta

> Estou bloqueado.

Resposta

- registra bloqueio
- identifica responsável
- cria ação para resolver

---

# Arquitetura

```
                  Código

              Documentação

               Negócio

                Equipe

                    │

             Processamento

                    │

                 RAG Index

                    │

            Estado do Projeto
              (Versionado)

                    │

          Agente Conversacional

                    │

        Trello / Usuários / Chat
```

---

# Stack

## Backend

FastAPI

Pydantic Settings

JWT

Firebase (temporário)

---

## IA

LangGraph

LangChain (apenas onde fizer sentido)

Groq

---

## Frontend

HTML

CSS

JavaScript

---

# Roadmap

## Fase 1

Estado do Projeto

- modelo
- versionamento
- persistência

---

## Fase 2

Indexador

- código
- documentação
- negócio
- equipe

---

## Fase 3

RAG

Consulta das fontes de conhecimento.

---

## Fase 4

Agente

Responder:

"Qual minha tarefa hoje?"

---

## Fase 5

Integração Trello

Criação automática de cartões.

---

## Fase 6

Atualização automática do Estado do Projeto

Após conclusão das tarefas.

---

# Objetivos futuros

- Detecção automática de riscos
- Sugestão de roadmap
- Identificação de gargalos
- Atualização automática da documentação
- Planejamento de entregas
- Métricas de produtividade
- Auditoria contínua do projeto