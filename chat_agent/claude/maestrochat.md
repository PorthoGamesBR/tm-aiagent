Aplicativo de organização de finanças usando IA como interface principal para usuários pouco técnicos. Nosso usuário final é qualquer pessoa que precise gerenciar suas finanças e queira uma experiencia mais customizada para sua própria necessidade.

---------------------------------------------------------

Bom. Proposta de valor clara: o meio-termo entre o Excel financeiro que ninguém entende e o app que só faz gráfico de pizza.
A IA como interface principal é uma escolha de produto relevante — mas também é onde a maioria dos times se perde, porque "IA como interface" pode significar muita coisa.

Quando você imagina alguém usando esse app no dia a dia, qual é a ação mais básica e frequente que ele vai fazer — e como a IA entra nessa ação especificamente?
Por exemplo: o usuário digita "gastei 50 reais no mercado" e a IA categoriza e registra automaticamente? Ou a IA proativamente avisa "você está gastando mais do que o normal essa semana"? Ou outra coisa?

---------------------------------------------------------

Cliente acessa o aplicativo, tem de cara os gráficos dos seus gastos por período e os filtros para escolher, e abaixo uma explicação por texto gerada pela IA que auxilia a entender o que aquilo significa (Vai sobrar dinheiro, vai faltar dinheiro, etc....). Depois pode perguntar para a IA sobre algo que queria comprar e se é uma decisão financeira boa no momento, declarar algum pagamento/recebimento que não foi atualizado automaticamente pelo open finance, entre outros.

---------------------------------------------------------

Ótimo. O fluxo está claro: dashboard com gráficos + narrativa gerada por IA + chat para decisões pontuais + Open Finance como fonte de dados principal, com entrada manual como fallback.
Isso é um produto concreto e executável. Agora preciso entender quem vai construir isso.

Quantas pessoas estão no time, e quais são as especialidades — front, back, IA, design?
Me dá o inventário humano, mesmo que seja informal: "somos 3, um faz front, um faz back e um faz tudo."

---------------------------------------------------------

Os integrantes são:
- João. Da area de negócio, usa muito o claude code para produzir praticamente todo o código, documentos, features, etc...
- Porto. Fullstack, da área de tecnologia e arquitetura.
- Ibere. Desenvolvedor Back-End, entende mais de servidores e testes. Ainda não fez nada pois não sabe o que tem pra fazer
- Vitor. Apenas entende de Tecnologia. É Músico. Conhece um pouco de Typescript e Python. Ainda não fez nada

---------------------------------------------------------

Interessante. Time misto — um de negócio que virou o executor principal via Claude Code, um arquiteto fullstack, um back-end ocioso e um generalista subutilizado.
Antes de eu tirar conclusões sobre gargalos, preciso entender uma coisa crítica:

O Porto, sendo o fullstack e arquiteto, está ativamente codando junto com o João — ou ele está mais no papel de revisar/orientar o que o João produz?
Em outras palavras: quem está com a mão na massa hoje, e onde o código vive atualmente?

---------------------------------------------------------

Não, está no papel de revisar e não de codar, mas não está revisando no momento. O código vive em um repositório que o Porto não tem acesso, apenas o João possui acesso.

---------------------------------------------------------

Esse é o primeiro gargalo crítico identificado. O João é um ponto único de falha — ele produz, ele revisa e ele é o único com acesso ao repositório. O Porto, que deveria ser o guardião técnico da arquitetura, está cego.
Isso precisa ser resolvido antes de qualquer outra coisa.

Existe alguma ferramenta de gestão de tarefas em uso hoje — Trello, Jira, Notion, planilha, qualquer coisa — ou as decisões e tarefas vivem só na cabeça das pessoas e em conversas de chat?

---------------------------------------------------------

Não existe ferramenta de gestão de tarefas atualmente, pois nem temos tarefas

---------------------------------------------------------

Entendido. Sem gestão, sem tarefas definidas, dois membros parados sem saber o que fazer, e o código centralizado em uma pessoa só. O diagnóstico está ficando nítido.
Última rodada de perguntas antes de eu fechar o mapeamento:

Qual é o prazo ou pressão externa que vocês têm — existe uma data, um investidor, um lançamento público, ou vocês estão construindo sem deadline definido por enquanto?

---------------------------------------------------------

O ideal é terminar antes do prazo limite do fim de setembro, mas não temos uma deadline definida

---------------------------------------------------------

Pronto. Tenho o suficiente para montar o documento. Setembro como horizonte, aproximadamente 3 meses e meio — tempo suficiente se a casa for organizada agora.
Vou gerar o Documento de Contexto Vivo.


Documento gerado. Missão do Maestro encerrada.

Resumo do diagnóstico em uma linha: O produto tem visão clara e time suficiente para executar — o problema não é capacidade, é ausência de estrutura e um gargalo crítico de centralização de código.
O que precisa acontecer amanhã, sem negociação:

João abre acesso ao repositório para o Porto.
Porto faz a auditoria do que existe.
O time escolhe uma ferramenta de gestão e registra as primeiras tarefas.

Tudo o mais — arquitetura, divisão de sprints, alocação do Ibere e do Vitor — depende dessas três ações acontecerem primeiro. Sem isso, qualquer planejamento é castelo no ar.
O documento está pronto para ser injetado no contexto do Gerente Conversacional.