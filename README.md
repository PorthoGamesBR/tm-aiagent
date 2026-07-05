# Agente organizador de equipe não nomeado

Ideias de nomes:
- Maestro

## O problema
Somos uma equipe formada pro 4 profissionais técnicos. Somos bons em criar coisas, mas não tanto em organizar o que precisamos criar.

Temos uma visão do que queremos criar e por que. Somos simultaneamente os stakeholders do projeto e seus desenvolvedores.

Os problemas que enfrentamos são:
- Apenas um de nós cria quase todo o código com um agente de IA. Chamaremos de "O Visionário", aquele que cria a base das ideias dos projetos.
- Muito codigo, documentos e features são criados em pouco tempo, mas não sabemos como entregar, como vender o que criamos, nem sabemos se falta algo para entregar.
- Dois acabam não fazendo nada por não saberem o que precisa ser feito. Vamos chamá-los de "Os Contratados"
- Um entende mais de tecnologia e consegue analisar arquitetura de tecnologia mais profundamente, mas não entende bem de criar tarefas e comunicação. Vamos chama-lo de "O Nerd"
- No fim não temos um roadmap, apenas estamos adicionando coisas à um projeto sem saber como transformá-lo em um produto de verdade.

A solução que quero criar deve:
- Ajudar a organizar as tarefas que cada um deve fazer, dividir objetivos de negócio em tarefas técnicas.
- Agir como um gerente que escuta as necessidades de negócio e as converte/distribui para quem irá executá-las.
- Entender o custo de cada demanda, o custo de cada decisão, baseado no contexto como um todo.
- O agente deve nos alinhar como devs as decisões de negócios que tomamos, e como stakeholders as limitações técnicas que temos.
- Deixar claro quando houver desalinhamento no projeto e na equipe.
- Garantir que cheguemos à um produto final e não fiquemos apenas adicionando coisas ad eternum.
- Garantir que todos participem e contribuam para o projeto.
- Ser adaptável e genérica o suficiente para que possa ser usada em outros contextos. O problema que trouxe é um case que esse agente deve solucionar, mas não o unico.

## Os agentes
O trabalho acabou ficando muito complexo para um agente só. Precisamos primeiro de um agente que consiga lidar com a pesquisa de elicitação de conhecimento organizacional e depois um que aja como gerente com essas informações.

O problema principal é a tech stack que estamos usando para comunicação com o LLM: _LangChain_ e _LangGraph_. _LangChain_ não é otimizada para agentes muito complexos, geralmente é mais focada para agentes simples, quase determinísticos, e estava usando como tecnologia primária para desenvolver ambos os agentes.

### Agente de Pesquisa
O agente de pesquisa é construido com _LangGraph_ por conta de sua complexidade. Para alcançar o objetivo precisamos de um agente com estado, um fluxo bem definido e uma saída bem definida.

Regra: Sempre que recebe uma resposta do usuário, valida se a resposta tem alguma coisa haver com a pergunta original. 
1. Envia uma mensagem pro usuário explicando seu propósito e pedindo mais informações sobre a empresa
2. Após receber a resposta, calcula uma unica vez quais assuntos são necessários além dos pré definidos (genéricos pra qualquer empresa).
3. Para cada assunto gera uma pergunta, espera a resposta do usuário e adiciona a resposta ao contexto
4. Quando não tiver mais nenhuma pergunta, gera o documento final.

O desenvolvimento desse agente será feito passo a passo, testando cada nó e sua resposta individualmente baseado em roteiro de case pré definido.

#### Nós
1. Introduction
2. Wait Initial Description (interrupt)
3. Generate Question
4. Ask User (interrupt)
5. Validate Answer
6. Update Context
7. Critic
8. Evaluate Coverage
9. Finalize

O unico objetivo do nó de introduction é mandar a mensagem inicial que é fixa. O teste deste é só ver se o agente compilado recebe a mensagem do usuário após isso e se classifica devidamente como tendo haver com a pergunta ou não.
### Agente Gerente

## Front end

Preciso fazer esse agente ser acessível para a equipe. Pensei no seguinte setup:

- Static (HTML + CSS + JS) por simplicidade
    - Pagina de login para evitar abuso do limite do agente
    - Pagina de chat já criada (agent-showcase-base), mas precisa ser adaptada para ser usada em servidor
- Fast-API para o backend. Precisa ser agnostico pois ainda não sabemos qual cloud vamos usar·
    - JWT para controle de acesso
    - Duas rotas de get, login e chat
    - Usando Render por enquanto pelo free tier
- Agnostico para banco de dados tambem, pelo mesmo motivo
    - Temporariamente Firebase por ser de gratis (Tanto historico de conversa quanto documento de contexto salvo)
    - Autenticação é registrada manualmente pelo admin
    - Database de usuário e chat


### Passo 1 - Fast API Rodando
Vamos fazer isso incrementalmente. Botando o servidor pra rodar, depois vamos adicionando as paginas e funcionalidades.

Rodar o servidor, configurar as rotas e os Settings vão ser todos no server.py

Vamos usar pydantic-settings para automatizar validação de existencia de variáveis necessárias e conversão de tipos.

_uvicorn_ para rodar o servidor localmente, mas deixar aberto para funcionar em container futuramente (mais facil de botar na cloud).

Para rodar o aplicativo:
```
uvicorn backend.server:app --reload
```

### Passo 2 - Páginas Estáticas
Precisamos de duas páginas estáticas:
- Login
- Chat (Já temos, só precisamos adaptar a logica)

Se os dois GETs estiverem funcionando, ta ok

_O que seria adaptar a lógica?_  
No momento a página executa lógica de backend no front. Precisamos colocar toda a lógica de chamada de agente, acesso de arquivos, etc, no backend, para que o front apenas chame os endpoints.

Se
### Passo 3 - Endpoints
- Login
- Logout
- Me
- Chat
- Conversations
- Conversations (ID)
- Context Doc

### Passo 4 - Requests
Objetos para validar formato da requisição do usuário ao servidor

### Passo 5 - Serviços
Lógica de negócio para rodar autenticação e comunicação com a LLM

Quando o primeiro agente rodar, salva o documento de contexto na database.

### Passo 6 - Separação
Endpoints vão para API, Logica de negócios para Serviços

### Passo 7 - Database agnóstica
Abstrações para acesso de databases.

Usuários, chat, documento de contexto.

Definição de forma de dados é nos modelos.

### Passo 8 - Modelos
Entidades de negócio: user, chat e message.

### Passo 9 - Main
Servidor inicializado pela main, com o agente sendo configurado antes e depois passado para o servidor.

O objetivo disso é poder separar e testar individualmente a lógica do agente e das tools, sem precisar rodar o servidor pra isso.

Em vez do backend se comunicar diretamente com o Groq, quem configura os objetos de agente para se comunicarem com o Groq é ```main.py``` e ```agent.py```, depois disponibilizando o objeto criado para o servidor. Ainda não sei como passar os objetos para a camada de negócio, é uma coisa que preciso ver ainda.
