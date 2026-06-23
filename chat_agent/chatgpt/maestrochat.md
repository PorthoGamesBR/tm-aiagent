Aplicativo de organização de finanças usando IA como interface principal para usuários pouco técnicos. Ele vem para servir como uma alternativa a aplicativos hipercomplexos de gerenciamento de finanças, ou aplicativos simples mas muito basicos.

---------------------------------------------------------

Entendido.

O que captei até agora:

Produto: aplicativo de organização financeira.
Diferencial: IA como interface principal de interação.
Público-alvo: usuários pouco técnicos.
Posicionamento: ocupar o espaço entre:
apps financeiros extremamente completos, porém complexos;
apps simples, porém limitados demais.

Ainda falta a peça mais importante para definir escopo.

Qual é a linha de chegada do MVP?

Imagine que vocês precisam lançar uma primeira versão em 60 dias.

Qual é a menor sequência de ações que faria um usuário dizer:

"Ok, isso já resolveu meu problema e vale a pena usar."

Descreva o fluxo ideal do usuário desde o primeiro acesso até o momento em que ele obtém valor real do produto.

---------------------------------------------------------

Cliente acessa o aplicativo, tem de cara os gráficos dos seus gastos por período e os filtros para escolher, e abaixo uma explicação por texto gerada pela IA que auxilia a entender o que aquilo significa (Vai sobrar dinheiro, vai faltar dinheiro, etc....). Depois pode perguntar para a IA sobre algo que queria comprar e se é uma decisão financeira boa no momento, declarar algum pagamento/recebimento que não foi atualizado automaticamente pelo open finance, entre outros.

---------------------------------------------------------

Bom. Agora já consigo enxergar um MVP concreto e não apenas uma ideia.

O que identifiquei:

A IA não é um recurso secundário; ela é a interface principal do produto.
O usuário não quer "categorizar despesas". Ele quer respostas para perguntas como:
"Posso comprar isso?"
"Vou fechar o mês no vermelho?"
"Onde estou gastando demais?"
"Quanto sobra depois das contas?"
Os gráficos existem para dar transparência e confiança, mas o valor principal parece ser a interpretação automática.

Minha próxima pergunta é sobre execução, não sobre produto.

Quantas pessoas existem hoje no projeto e quem são elas?

Para cada pessoa, me diga apenas:

Nome ou apelido.
Função principal.
Se ela trabalha em tempo integral, parcial ou ocasionalmente.

Exemplo:

João — Backend — parcial.
Maria — UX/UI — integral.
Pedro — Negócios — ocasional.

Quero descobrir se o maior risco atual é técnico, organizacional ou simplesmente falta de capacidade de execução.

---------------------------------------------------------

Os integrantes são:
- João -- Negócio, Desenvolvimento do Produto com Claude Code -- parcial
- Porto -- Fullstack -- parcial
- Ibere -- Back-End, Servers -- sem tempo definido
- Vitor --Músico, Conhece um pouco de Typescript e Python -- sem tempo definido

---------------------------------------------------------

Primeiro diagnóstico preliminar:

### Estrutura atual

**João**

* Atua como produto/negócio.
* Também desenvolve usando IA.
* Risco: acumular decisões de produto e implementação ao mesmo tempo.

**Porto**

* Fullstack.
* Provavelmente um dos principais executores técnicos.
* Risco: virar gargalo se a arquitetura e as decisões ficarem centralizadas.

**Ibere**

* Backend/infraestrutura.
* Disponibilidade indefinida.
* Risco: componente crítico do sistema sem previsibilidade de entrega.

**Vitor**

* Perfil híbrido.
* Conhecimento técnico inicial.
* Potencial para QA, documentação, testes, pesquisa e tarefas de menor acoplamento.
* Risco: ficar ocioso por falta de escopo claro.

Meu radar de governança está apontando um possível problema: vocês parecem ter pessoas, mas ainda não sei se existe coordenação operacional. Muitas equipes pequenas travam não por falta de código, mas porque ninguém sabe exatamente o que está sendo feito, por quem e até quando.

Então a próxima pergunta é:

**Hoje existe algum lugar único que represente a verdade do projeto?**

Exemplos:

* Jira
* Trello
* GitHub Projects
* Notion
* Discord com mensagens soltas
* Planilhas
* Nenhum lugar central

Quero saber como vocês acompanham o que já foi feito, o que está em andamento e o que falta fazer.

---------------------------------------------------------

Não, nenhum lugar contém isso. Apenas conversamos uma vez por semana na faculdade sobre as ideias e, de vez em quando, mandamos mensagens no whatsapp

---------------------------------------------------------

Isso muda bastante o diagnóstico.

Neste momento, o principal gargalo não parece ser técnico. Parece ser operacional.

Vocês estão em um estágio que eu classificaria como:

Equipe formada + visão de produto razoavelmente clara + operação informal.

Isso funciona quando existem duas pessoas e um protótipo. Começa a quebrar quando existem quatro pessoas, código sendo produzido e decisões acontecendo em paralelo.

O risco imediato que estou vendo é:

Trabalho duplicado.
Funcionalidades começando e nunca terminando.
Pessoas sem saber no que ajudar.
Conhecimento preso em conversas presenciais.
Decisões importantes desaparecendo no WhatsApp.

Ainda não vou prescrever ferramentas. Primeiro preciso entender o estado real do produto.

Pergunta:

Hoje existe alguma coisa funcionando?

Pode ser qualquer uma destas situações:

Apenas ideia e documentação.
Wireframes/protótipos.
Front-end funcionando.
Backend funcionando.
Integração Open Finance iniciada.
Chat com IA funcionando.
Repositório criado mas vazio.
MVP parcialmente operacional.

Me diga o que já existe concretamente e onde esse código está hospedado.

---------------------------------------------------------

Existe um app, um apk, código hospedado no GitHub e o apk produzido por alguma plataforma que apenas o João sabe qual é. O apk já tem a tela de graficos de finanças, chat, visualização de entradas e saídas filtradas, configuração open banking (apenas com dados mock por enquanto por não termos CNPJ)

---------------------------------------------------------

Isso é uma informação importante.

O projeto está mais avançado do que eu imaginava.

Meu diagnóstico muda de:

"Equipe tentando sair da fase de ideia"

para

"Equipe com protótipo funcional correndo risco de desorganização."

O que já existe:

APK gerado e distribuível.
Repositório GitHub.
Interface principal construída.
Chat implementado.
Visualização financeira implementada.
Integração Open Finance desenhada.
Dados mockados funcionando.

O principal risco técnico que apareceu agora é outro:

Conhecimento concentrado.

O fato de você mencionar que "o APK é produzido por alguma plataforma que apenas o João sabe qual é" acende um alerta imediato.

Se amanhã o João ficar duas semanas sem participar, alguém consegue:

Gerar uma nova versão?
Publicar uma atualização?
Subir ambiente?
Reproduzir o build?

Se a resposta for "não", existe um ponto único de falha.

Minha próxima pergunta é justamente para medir isso.

Hoje, quem realmente entende a arquitetura do projeto de ponta a ponta?

Estou procurando algo como:

Apenas João.
João e Porto.
Cada um entende uma parte.
Ninguém entende tudo.
Existe documentação arquitetural.

Quero descobrir se o conhecimento está distribuído ou concentrado.

---------------------------------------------------------

Acho que existe documentação no código, mas duvido que o João saiba a arquitetura ponta a ponta, ele não é técnico. Provavelmente o unico que sabe o contexto inteiro é o Claude Code do João

---------------------------------------------------------

Interessante. Isso revela um cenário que estou vendo cada vez mais em equipes que usam IA para desenvolver.

O risco não é exatamente "João sabe tudo".

O risco é:

> **O conhecimento operacional do projeto pode estar dentro do histórico de conversa do Claude Code e não dentro da equipe.**

Isso cria alguns problemas:

* Decisões arquiteturais sem registro humano.
* Funcionalidades implementadas sem ninguém saber exatamente por quê.
* Dificuldade para novos membros contribuírem.
* Dependência indireta de um contexto que ninguém além do João possui.

Até agora meu diagnóstico operacional preliminar é:

| Área                          | Estado              |
| ----------------------------- | ------------------- |
| Visão de produto              | Boa                 |
| MVP                           | Relativamente claro |
| Protótipo                     | Existe              |
| Equipe                        | Existe              |
| Gestão de tarefas             | Inexistente         |
| Documentação estratégica      | Desconhecida        |
| Conhecimento distribuído      | Baixo               |
| Dependência de pessoas        | Alta                |
| Dependência de contexto de IA | Possivelmente alta  |

Agora preciso descobrir onde está o gargalo mais urgente.

**Se eu perguntasse para cada integrante hoje:**

> "Qual é a tarefa mais importante para avançar o MVP nesta semana?"

Você acha que eles responderiam a mesma coisa ou cada um daria uma resposta diferente?

E qual seria essa resposta, na sua visão?

---------------------------------------------------------

Metade não saberia. Um falaria "Organizar, validar que o projeto está fazendo o que diz estar fazendo". Outro diria "Criar o CNPJ, publicar". Ambos diriam tambem "Organizar o que precisa ser feito"

---------------------------------------------------------

Perfeito.

Essa resposta é provavelmente a mais valiosa da investigação até agora.

Ela mostra que o projeto não está travado por tecnologia, IA, Open Finance ou programação.

Ele está travado por uma ausência de alinhamento operacional.

Quando metade da equipe não sabe qual é a prioridade da semana, o problema não é execução. É direção.

O padrão que estou vendo é:

1. Existe uma visão de produto relativamente consistente.
2. Existe software funcionando.
3. Existe equipe.
4. Não existe uma fonte oficial de verdade.
5. Não existe backlog.
6. Não existe definição compartilhada do que falta para o MVP.
7. Não existe responsável explícito por cada frente.

Isso me leva a uma hipótese:

> O próximo grande ganho do projeto não virá de escrever mais código.
>
> Virá de transformar conhecimento implícito em conhecimento compartilhado.

Antes de encerrar a investigação e gerar o Documento de Contexto Vivo, falta apenas uma peça.

**Qual é o objetivo concreto do projeto nos próximos 3 a 6 meses?**

Exemplos:

* Conseguir usuários reais.
* Publicar nas lojas.
* Virar startup.
* Validar mercado.
* Entregar como projeto acadêmico.
* Conseguir investimento.
* Conseguir os primeiros clientes pagantes.

Qual é a linha de chegada que a equipe acredita estar perseguindo?

---------------------------------------------------------

Virar startup (precisa para o projeto sequer funcionar), Publicar nas Lojas, conseguir usuários reais, entregar como projeto academico, conseguir primeiros clientes pagantes

---------------------------------------------------------

A investigação atingiu um nível suficiente de confiança para produzir o primeiro Documento de Contexto Vivo.


Como Maestro, minha conclusão é simples:

O projeto não precisa de mais visão. Precisa de clareza compartilhada.

A prioridade número 1 não é desenvolver uma nova funcionalidade. É fazer com que a equipe inteira consiga responder, sem divergências:

"O que existe, o que falta e quem é responsável por cada parte."

Sem isso, cada linha de código nova aumenta a complexidade mais rápido do que o valor entregue.