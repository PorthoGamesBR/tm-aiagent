# Documento de Contexto Vivo — Projeto: App de Finanças com IA
**Versão:** 1.0  
**Gerado por:** O Maestro v5.0  
**Data de geração:** Junho 2026  
**Destinatário:** Agente Gerente Conversacional  

---

## 1. Mapeamento do Produto e MVP

### Visão de Negócio
Aplicativo mobile/web de organização financeira pessoal que usa **IA como interface principal**, posicionado como alternativa ao meio-termo entre apps hipercomplexos (inacessíveis para usuários leigos) e apps simples demais (sem valor real de insight).

**Público-alvo:** Usuários com baixa familiaridade técnica que querem entender sua situação financeira sem precisar aprender um software.

### Proposta de Valor
O diferencial não é o gráfico — é a **narrativa**. A IA transforma dados financeiros brutos em linguagem acessível e orientada a decisão: "Vai sobrar dinheiro esse mês", "Essa compra agora é arriscada", etc.

### Funcionalidades Mapeadas do MVP

| Funcionalidade | Descrição | Fonte de Dado |
|---|---|---|
| Dashboard financeiro | Gráficos de gastos por período com filtros | Open Finance (automático) |
| Narrativa por IA | Texto gerado abaixo do dashboard explicando o que os números significam | LLM sobre dados financeiros |
| Chat de decisão | Usuário pergunta se uma compra é boa decisão no momento | LLM contextualizado |
| Registro manual | Declarar pagamento/recebimento não capturado pelo Open Finance | Entrada manual do usuário |

### Linha de Chegada do MVP
Produto funcional com as 4 funcionalidades acima, integrado ao Open Finance, com entrada manual como fallback, e interface conversacional operacional — **entregue antes do fim de setembro de 2026**.

### Riscos de Produto a Observar
- A integração com Open Finance é regulatória e técnica — tem burocracia e prazo próprio. Precisa ser priorizada cedo.
- "IA como interface principal" aumenta a complexidade de UX — o Gerente deve monitorar se o time está over-engineerando a IA antes de ter o básico funcionando.

---

## 2. Diagnóstico Operacional e Gargalos

### Estado Atual das Ferramentas
- **Ferramenta de gestão de tarefas:** Inexistente.
- **Repositório de código:** Existe, mas com acesso exclusivo do João. Nenhum outro membro tem visibilidade do código.
- **Processo de revisão:** Não está acontecendo. Porto é o designado para revisar, mas está sem acesso e inativo nessa função.
- **Tarefas definidas:** Não existem formalmente. Dois membros (Ibere e Vitor) estão ociosos por ausência total de escopo.

### Gargalos Identificados (por criticidade)

#### 🔴 CRÍTICO — Centralização de Código no João
João é o único com acesso ao repositório e o único produzindo código ativamente. Isso cria:
- **Risco de qualidade:** Código gerado por IA sem revisão técnica humana especializada.
- **Risco de continuidade:** Se João parar, o projeto para.
- **Risco de arquitetura:** Porto não pode garantir decisões técnicas saudáveis sem ver o que foi construído.

**Ação imediata necessária:** Porto precisa ter acesso ao repositório hoje.

#### 🔴 CRÍTICO — Ausência de Gestão de Tarefas
Sem tarefas definidas, dois membros estão parados sem culpa. O projeto não avança por falta de estrutura, não por falta de pessoas.

**Ação imediata necessária:** Criar estrutura mínima de gestão (ver Fase 0 abaixo).

#### 🟡 MODERADO — Porto sem papel ativo
Porto tem o perfil técnico mais robusto do time mas está em modo passivo. Sem acesso ao código e sem demanda de revisão ativa, seu valor está desperdiçado.

#### 🟡 MODERADO — Ibere e Vitor ociosos
Não é problema de motivação — é problema de ausência de escopo. Assim que tarefas forem definidas e o repositório for aberto, ambos podem ser ativados.

---

## 3. Matriz de Atuação Humana

### João
- **Papel real:** Executor principal. Produz código, documentos e features usando Claude Code como ferramenta primária.
- **Papel formal:** Área de negócio / Product Owner informal.
- **Riscos operacionais:**
  - Ponto único de falha no código.
  - Pode gerar dívida técnica acelerada por usar IA sem revisão.
  - Pode ter viés de produto (área de negócio) sobrepondo decisões técnicas.
- **Como o Gerente deve interagir:**
  - Cobrar abertura de acesso ao repositório para Porto como primeira ação.
  - Perguntar regularmente: *"O que você produziu essa semana e o Porto já revisou?"*
  - Não deixar João acumular entregas sem revisão por mais de 3 dias.
  - Validar com João o escopo do MVP — ele tem visão de produto e precisa ser o guardião da priorização.

### Porto
- **Papel real:** Arquiteto e revisor técnico — atualmente inativo.
- **Papel formal:** Fullstack / Referência técnica do time.
- **Riscos operacionais:**
  - Passividade crescente sem demanda explícita.
  - Pode se tornar um bottleneck de revisão se não for ativado logo.
- **Como o Gerente deve interagir:**
  - Primeira cobrança: acesso ao repositório.
  - Segunda cobrança: auditoria técnica do que já foi produzido pelo João.
  - Perguntar regularmente: *"Você revisou o último PR do João? Teve algum problema de arquitetura?"*
  - Envolver Porto em decisões de stack e integração com Open Finance — é onde seu perfil agrega mais.

### Ibere
- **Papel real:** Back-end / Testes — atualmente ocioso por falta de escopo.
- **Papel formal:** Desenvolvedor Back-End.
- **Riscos operacionais:**
  - Desmotivação por ociosidade prolongada.
  - Pode se desconectar do projeto se não for ativado em breve.
- **Como o Gerente deve interagir:**
  - Assim que o repositório for aberto e o Porto fizer a auditoria, Ibere deve receber as primeiras tarefas de back-end (infraestrutura de servidor, estrutura de testes).
  - Perguntar: *"Você já tem clareza do que precisa fazer essa semana?"*
  - Nunca deixar Ibere sem tarefa por mais de uma semana após a Fase 0 estar completa.

### Vitor
- **Papel real:** Generalista técnico — atualmente ocioso.
- **Papel formal:** Desenvolvedor com conhecimento em TypeScript e Python.
- **Riscos operacionais:**
  - Perfil mais júnior tecnicamente — precisa de tarefas bem definidas e escopo pequeno.
  - Risco de ser mal alocado em tarefas acima da sua senioridade atual.
- **Como o Gerente deve interagir:**
  - Alocar em tarefas de suporte, scripts auxiliares, automações simples em Python ou TypeScript.
  - Perguntar: *"Você entendeu o que precisa entregar e tem o que precisa para começar?"*
  - Checar se está travado — Vitor pode não pedir ajuda ativamente.
  - Não alocar em decisões de arquitetura ou integração crítica (Open Finance, LLM core).

---

## 4. O Plano de Voo Imediato

### Fase 0 — Estabilização da Infraestrutura de Gestão
**Duração estimada:** 1 semana  
**Objetivo:** Criar as condições mínimas para o time operar de forma coordenada.

#### Ações da Fase 0 (em ordem de prioridade):

1. **Abrir acesso ao repositório para Porto** — João adiciona Porto como colaborador. Não negociável.
2. **Auditoria técnica do Porto** — Porto lê o código existente, mapeia o que foi feito, identifica dívidas técnicas e valida a arquitetura atual.
3. **Criar ferramenta mínima de gestão de tarefas** — Recomendado: Notion ou Linear. Criar quadro com colunas: `Backlog → Em andamento → Em revisão → Feito`.
4. **Definir e registrar o backlog inicial do MVP** — João (visão de produto) + Porto (viabilidade técnica) definem as primeiras tarefas concretas e as registram na ferramenta.
5. **Ativar Ibere e Vitor com tarefas da Fase 1** — Assim que o backlog existir, ninguém fica sem escopo.

---

### Fase 1 — Construção do Core do MVP
**Duração estimada:** Junho–Agosto 2026  
**Objetivo:** Entregar as 4 funcionalidades do MVP funcionando em ambiente de desenvolvimento.

#### Frentes paralelas sugeridas:

| Frente | Responsável sugerido | Entregável |
|---|---|---|
| Integração Open Finance | Porto + Ibere | Conexão autenticada com pelo menos 1 banco, dados fluindo |
| Dashboard + Gráficos | João (Claude Code) + Vitor (suporte) | Tela de gráficos com filtros funcionando |
| Camada de IA (narrativa + chat) | João (Claude Code) + Porto (revisão de arquitetura) | LLM integrado gerando narrativas e respondendo perguntas |
| Registro manual | Ibere | Formulário de entrada manual persistindo no banco |
| Testes e infraestrutura | Ibere | Suite de testes básica, ambiente de staging |

---

### Fase 2 — Estabilização e Lançamento
**Duração estimada:** Setembro 2026  
**Objetivo:** Polimento, testes com usuários reais e preparação para lançamento antes do fim de setembro.

- Testes de usabilidade com usuários do público-alvo (leigos financeiros).
- Ajustes de UX na interface de IA baseados em feedback.
- Deploy em produção.
- Definição de métricas de sucesso pós-lançamento.

---

## 5. Instruções de Operação para o Gerente Conversacional

### Cadência de Acompanhamento Sugerida
- **Diário (assíncrono):** Checar se alguém está travado ou sem tarefa.
- **Semanal:** Perguntar a cada membro o que foi entregue e o que está em andamento.
- **Por sprint (quinzenal):** Revisar se o backlog está atualizado e se o MVP ainda está no escopo correto.

### Sinais de Alerta para Agir Imediatamente
- João produzindo código por mais de 3 dias sem revisão do Porto.
- Ibere ou Vitor sem tarefa atribuída.
- Porto sem acesso ao repositório após a Fase 0.
- Qualquer decisão de adicionar nova feature antes do core do MVP estar funcional.
- Menção de integração com Open Finance sendo postergada (é o item de maior risco regulatório).

### Tom de Comunicação com o Time
- Direto, sem jargão.
- Cobranças feitas como perguntas, não como ordens: *"Isso já foi feito?"* em vez de *"Faça isso."*
- Quando identificar ociosidade, perguntar primeiro antes de assumir desinteresse.

---

*Este documento é vivo. Deve ser atualizado pelo Gerente Conversacional sempre que houver mudança relevante de escopo, equipe, ferramentas ou prioridades.*