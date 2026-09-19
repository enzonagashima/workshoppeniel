# Workshop --- Mesa de Som Virtual

## Especificação técnica e pedagógica para desenvolvimento assistido por IA

**Versão:** 1.0\
**Objetivo:** construir um projeto web didático, funcional em rede
local, para ensinar adolescentes a programar do zero por meio de um
problema real de uma igreja.

------------------------------------------------------------------------

# 1. Visão geral

O projeto consiste em uma aplicação web que **simula uma mesa de som**.

O software **não controla o áudio da mesa física**. Ele funciona
exclusivamente como um sistema de comunicação entre músicos e operador
de som.

## Problema

Durante os cultos, músicos precisam solicitar alterações de volume de
seus instrumentos ao operador da mesa. Nem sempre existe um microfone
disponível para cada músico, o que dificulta a comunicação.

## Solução

Cada músico acessa uma tela web correspondente ao seu instrumento.

Na tela, ele pode solicitar aumento ou redução de volume.

A solicitação é enviada ao servidor Python e armazenada no SQLite.

A tela do operador consulta periodicamente o servidor usando
**AJAX/Fetch (polling)**. Quando existe uma nova solicitação, ela
aparece na tela do operador.

O operador então altera o volume na **mesa física de verdade** e
registra no sistema se a solicitação foi atendida ou recusada.

------------------------------------------------------------------------

# 2. Objetivo pedagógico

O objetivo principal não é criar uma mesa de som completa.

O objetivo é ensinar a lógica de funcionamento de um sistema de
software:

``` text
INTERFACE
    ↓
AÇÃO DO USUÁRIO
    ↓
JAVASCRIPT
    ↓
HTTP
    ↓
PYTHON
    ↓
REGRA DE NEGÓCIO
    ↓
SQLITE
    ↓
PYTHON
    ↓
HTTP
    ↓
OUTRA INTERFACE
```

Os alunos devem conseguir compreender:

-   interface;
-   eventos;
-   variáveis;
-   funções;
-   condições;
-   requisições HTTP;
-   cliente e servidor;
-   API;
-   JSON;
-   banco de dados;
-   SQL;
-   persistência;
-   comunicação entre computadores;
-   polling/AJAX;
-   estados de uma solicitação.

A IA deve priorizar **clareza pedagógica** em vez de complexidade
arquitetural.

------------------------------------------------------------------------

# 3. Escopo tecnológico

## Frontend

Obrigatório:

-   HTML5;
-   CSS3;
-   JavaScript puro.

Não utilizar:

-   React;
-   Vue;
-   Angular;
-   TypeScript;
-   Bootstrap;
-   Tailwind;
-   jQuery;
-   bibliotecas externas de frontend.

### Observação

O requisito de "HTML e CSS na interface" deve ser interpretado como
ausência de frameworks de frontend.

JavaScript puro é permitido e necessário para:

-   controlar os botões;
-   enviar solicitações;
-   consultar o servidor;
-   atualizar a tela do operador sem recarregar a página.

------------------------------------------------------------------------

# 4. Backend

Utilizar:

-   Python;
-   biblioteca padrão do Python;
-   servidor HTTP nativo, preferencialmente `http.server`;
-   módulo `sqlite3`.

**Não utilizar Flask ou outro framework web no MVP.**

Motivo: o projeto é educacional e deve expor aos alunos os conceitos
básicos de HTTP, servidor, requisição, resposta e banco de dados.

------------------------------------------------------------------------

# 5. Banco de dados

Utilizar exclusivamente:

**SQLite**

Não utilizar:

-   MySQL;
-   PostgreSQL;
-   MongoDB;
-   Redis;
-   ORM.

A comunicação com o banco deve ser feita pelo módulo nativo:

``` python
sqlite3
```

------------------------------------------------------------------------

# 6. Comunicação entre telas

## Estratégia escolhida

Utilizar:

**AJAX/Fetch + polling**

A tela do operador fará uma consulta periódica ao servidor Python.

Exemplo conceitual:

``` text
Operador
   ↓
GET /api/solicitacoes
   ↓
Python
   ↓
SQLite
   ↓
JSON
   ↓
JavaScript
   ↓
Atualiza tela
```

A consulta deve ocorrer aproximadamente a cada **2 segundos**.

## Não utilizar webhook

Webhook não será utilizado no MVP.

Motivos:

-   adiciona complexidade de rede;
-   exige explicar recebimento de requisições entre
    servidores/dispositivos;
-   pode envolver firewall, portas e endereçamento;
-   não é necessário para atingir o objetivo pedagógico;
-   o polling é mais simples para adolescentes iniciantes.

## Não utilizar WebSocket

WebSocket pode ser apresentado apenas como conteúdo futuro.

A IA não deve implementar WebSocket no MVP.

------------------------------------------------------------------------

# 7. Arquitetura

A aplicação deve funcionar em uma rede local.

``` text
                         REDE LOCAL
                              │
             ┌────────────────┴────────────────┐
             │                                 │
      ┌──────▼──────┐                    ┌─────▼─────┐
      │   MÚSICOS   │                    │ OPERADOR  │
      │ HTML/CSS/JS │                    │ HTML/CSS/JS│
      └──────┬──────┘                    └─────┬─────┘
             │                                 │
             └──────────────┬──────────────────┘
                            │
                           HTTP
                            │
                     ┌──────▼──────┐
                     │   PYTHON    │
                     │ HTTP SERVER  │
                     └──────┬──────┘
                            │
                         sqlite3
                            │
                     ┌──────▼──────┐
                     │   SQLITE    │
                     └─────────────┘
```

Um computador deverá executar o servidor Python.

Os demais computadores acessam o servidor pelo IP da máquina servidora.

Exemplo:

``` text
http://192.168.0.10:8000
```

------------------------------------------------------------------------

# 8. Distribuição dos computadores

Há cinco computadores disponíveis:

-   2 desktops;
-   3 notebooks.

Sugestão:

## Desktop 1

Servidor Python.

``` text
192.168.X.X:8000
```

## Desktop 2

Tela do operador.

``` text
http://IP_DO_SERVIDOR:8000/operador
```

## Notebook 1

Músico --- Vocal.

## Notebook 2

Músico --- Guitarra.

## Notebook 3

Músico --- Baixo.

O projeto deve permitir que todos os dispositivos acessem
simultaneamente o mesmo servidor e banco.

------------------------------------------------------------------------

# 9. Modelo funcional

O MVP deve possuir dois perfis principais:

## Músico

Pode:

-   visualizar seu instrumento;
-   visualizar volume atual;
-   solicitar aumento;
-   solicitar redução;
-   visualizar estado da própria solicitação.

## Operador

Pode:

-   visualizar os instrumentos;
-   visualizar volumes cadastrados;
-   visualizar solicitações pendentes;
-   aceitar uma solicitação;
-   recusar uma solicitação;
-   visualizar solicitações processadas.

------------------------------------------------------------------------

# 10. Conceito importante: o sistema não controla o áudio

Essa regra é obrigatória.

Quando o músico solicita:

``` text
Guitarra: 60% → 70%
```

o sistema **não deve alterar um equipamento físico**.

O sistema apenas registra:

``` text
"o músico deseja que o operador altere o volume para 70%"
```

O operador deve realizar a alteração fisicamente na mesa de som.

O software apenas comunica e registra a solicitação.

------------------------------------------------------------------------

# 11. Instrumentos iniciais

O banco deve possuir inicialmente alguns instrumentos para demonstração:

-   Vocal;
-   Guitarra;
-   Baixo;
-   Teclado;
-   Bateria.

O projeto deve ser estruturado para permitir posteriormente mais
instrumentos/canais.

Não limitar a lógica a exatamente cinco instrumentos.

------------------------------------------------------------------------

# 12. Modelo de dados

Utilizar inicialmente duas tabelas principais.

## Tabela `instrumentos`

Campos:

``` text
id
nome
volume_atual
musico
```

Exemplo:

``` text
1 | Vocal      | 60 | João
2 | Guitarra   | 70 | Pedro
3 | Baixo      | 65 | Lucas
4 | Teclado    | 50 | Ana
5 | Bateria    | 75 | Carlos
```

## Tabela `solicitacoes`

Campos:

``` text
id
instrumento_id
volume_atual
volume_solicitado
status
data_hora
```

Status permitidos inicialmente:

``` text
pendente
atendida
recusada
```

------------------------------------------------------------------------

# 13. Regra importante de modelagem

O volume atual do instrumento e uma solicitação são informações
diferentes.

Exemplo:

``` text
Volume atual: 60%

Solicitação:
60% → 70%

Status:
PENDENTE
```

O sistema não deve alterar `volume_atual` apenas porque o músico clicou
no botão.

O `volume_atual` representa o volume conhecido/configurado pelo sistema.

A solicitação representa o que o músico está pedindo ao operador.

Quando o operador aceitar uma solicitação, a aplicação pode atualizar o
volume registrado e mudar o status para `atendida`.

------------------------------------------------------------------------

# 14. Fluxo do músico

Exemplo:

``` text
Músico abre sua tela
        ↓
Visualiza instrumento
        ↓
Visualiza volume atual
        ↓
Clica em +
        ↓
Calcula novo volume
        ↓
Cria solicitação
        ↓
Python recebe POST
        ↓
Python valida dados
        ↓
SQLite salva solicitação
        ↓
Músico recebe confirmação
```

Exemplo:

``` text
GUITARRA

Volume atual

60%

[-]     [+]
```

Ao clicar em `+`:

``` text
Solicitação enviada:

60% → 65%
```

------------------------------------------------------------------------

# 15. Fluxo do operador

``` text
Operador abre tela
        ↓
JavaScript inicia polling
        ↓
GET /api/solicitacoes
        ↓
Python consulta SQLite
        ↓
Retorna JSON
        ↓
JavaScript verifica solicitações
        ↓
Nova solicitação aparece
```

Exemplo:

``` text
🔴 NOVA SOLICITAÇÃO

🎸 Guitarra

Volume atual: 60%
Solicitado: 70%

[ ACEITAR ] [ RECUSAR ]
```

------------------------------------------------------------------------

# 16. Aceitar solicitação

Quando o operador clicar em aceitar:

``` text
JavaScript
    ↓
POST /api/solicitacoes/{id}/aceitar
    ↓
Python
    ↓
SQLite
```

O sistema deve:

1.  localizar a solicitação;
2.  verificar se ela ainda está pendente;
3.  atualizar o volume do instrumento;
4.  alterar o status para `atendida`.

Exemplo:

``` text
Antes:

Guitarra
volume_atual = 60

Solicitação
60 → 70
status = pendente
```

Depois:

``` text
Guitarra
volume_atual = 70

Solicitação
60 → 70
status = atendida
```

------------------------------------------------------------------------

# 17. Recusar solicitação

Quando o operador clicar em recusar:

``` text
POST /api/solicitacoes/{id}/recusar
```

O sistema deve:

1.  localizar a solicitação;
2.  verificar se está pendente;
3.  alterar o status para `recusada`;
4.  não alterar o volume do instrumento.

------------------------------------------------------------------------

# 18. Regras de volume

O volume deve permanecer entre:

``` text
0 e 100
```

Nunca permitir:

``` text
-1
101
```

Ao aumentar:

``` text
volume + 5
```

Ao reduzir:

``` text
volume - 5
```

Se estiver em 100 e o usuário clicar em aumentar:

``` text
100 → 100
```

Se estiver em 0 e clicar em reduzir:

``` text
0 → 0
```

Essa regra é importante pedagogicamente para ensinar validação e
limites.

------------------------------------------------------------------------

# 19. Regras de solicitações

Uma solicitação deve possuir:

-   instrumento;
-   volume atual;
-   volume solicitado;
-   status;
-   data/hora.

O sistema deve evitar aceitar duas vezes a mesma solicitação.

Se uma solicitação já estiver:

``` text
atendida
```

ou:

``` text
recusada
```

ela não pode ser processada novamente.

------------------------------------------------------------------------

# 20. API mínima

A aplicação deve possuir uma API pequena e fácil de compreender.

Sugestão:

``` text
GET  /api/instrumentos
GET  /api/solicitacoes
POST /api/solicitacoes
POST /api/solicitacoes/{id}/aceitar
POST /api/solicitacoes/{id}/recusar
```

Não criar endpoints desnecessários.

------------------------------------------------------------------------

# 21. Comunicação JSON

A API deve utilizar JSON.

Exemplo de solicitação:

``` json
{
  "instrumento_id": 2,
  "volume_solicitado": 70
}
```

Exemplo de resposta:

``` json
{
  "sucesso": true,
  "mensagem": "Solicitação criada"
}
```

Exemplo de consulta:

``` json
[
  {
    "id": 15,
    "instrumento": "Guitarra",
    "volume_atual": 60,
    "volume_solicitado": 70,
    "status": "pendente"
  }
]
```

------------------------------------------------------------------------

# 22. Estrutura de arquivos

Utilizar uma estrutura simples.

``` text
mesa-de-som/
│
├── servidor.py
├── banco.py
├── mesa.db
│
├── index.html
├── operador.html
│
├── style.css
└── app.js
```

Se a implementação exigir uma organização adicional, a IA pode criar
subpastas, mas deve evitar complexidade desnecessária.

O princípio é:

> Poucos arquivos, responsabilidades claras e fácil compreensão pelos
> alunos.

------------------------------------------------------------------------

# 23. Responsabilidade dos arquivos

## `servidor.py`

Responsável por:

-   iniciar servidor HTTP;
-   receber requisições;
-   interpretar rotas;
-   receber dados;
-   chamar funções de banco;
-   devolver HTML, JSON e respostas HTTP.

## `banco.py`

Responsável por:

-   criar banco;
-   criar tabelas;
-   inserir dados iniciais;
-   consultar instrumentos;
-   criar solicitações;
-   consultar solicitações;
-   aceitar solicitações;
-   recusar solicitações.

## HTML

Responsável pela estrutura das telas.

## CSS

Responsável exclusivamente pela apresentação visual.

## JavaScript

Responsável por:

-   eventos;
-   botões;
-   chamadas `fetch`;
-   polling;
-   atualização da interface;
-   tratamento básico das respostas.

------------------------------------------------------------------------

# 24. Interface do músico

A interface deve ser simples e visual.

Exemplo:

``` text
┌──────────────────────────────┐
│          Guitarra            │
│                              │
│       VOLUME ATUAL           │
│                              │
│            60%               │
│                              │
│       [ - ]     [ + ]        │
│                              │
│  Última solicitação:         │
│  60% → 65%                   │
│  Aguardando operador...      │
└──────────────────────────────┘
```

A interface deve ter boa visualização em notebooks.

------------------------------------------------------------------------

# 25. Interface do operador

A interface deve apresentar a ideia de uma mesa de som.

Exemplo:

``` text
╔══════════════════════════════════════╗
║            MESA DE SOM               ║
╠══════════════════════════════════════╣
║                                      ║
║ 🎤 Vocal       60%                   ║
║ 🎸 Guitarra    70%                   ║
║ 🎸 Baixo       65%                   ║
║ 🎹 Teclado     50%                   ║
║ 🥁 Bateria     75%                   ║
║                                      ║
╠══════════════════════════════════════╣
║          SOLICITAÇÕES                ║
║                                      ║
║ 🔴 Guitarra                          ║
║ 60% → 70%                            ║
║                                      ║
║ [ ACEITAR ] [ RECUSAR ]              ║
╚══════════════════════════════════════╝
```

O visual pode ser inspirado em uma mesa de som real, mas não deve exigir
implementação de recursos de áudio.

------------------------------------------------------------------------

# 26. Polling

A tela do operador deve executar uma consulta periódica.

Conceito:

``` javascript
setInterval(verificarSolicitacoes, 2000);
```

A função:

``` text
verificarSolicitacoes()
        ↓
fetch("/api/solicitacoes")
        ↓
recebe JSON
        ↓
filtra/identifica pendentes
        ↓
atualiza HTML
```

O intervalo de aproximadamente 2 segundos pode ser configurável em uma
constante.

Não utilizar consulta diretamente ao arquivo SQLite pelo navegador.

Sempre:

``` text
Browser → Python → SQLite
```

------------------------------------------------------------------------

# 27. Tratamento de erros

O sistema deve lidar de forma simples com:

-   servidor indisponível;
-   erro de conexão;
-   solicitação inexistente;
-   instrumento inexistente;
-   volume inválido;
-   solicitação já processada.

A interface deve apresentar mensagens compreensíveis.

Não mostrar stack traces ao usuário.

Durante o workshop, erros técnicos podem ser mostrados pelo professor no
terminal para fins didáticos.

------------------------------------------------------------------------

# 28. Segurança

Como o objetivo é um workshop em rede local, segurança avançada está
fora do MVP.

Não implementar:

-   JWT;
-   OAuth;
-   login complexo;
-   HTTPS;
-   criptografia avançada;
-   autenticação externa.

Entretanto, a IA deve:

-   validar dados recebidos pelo servidor;
-   não confiar apenas na validação do JavaScript;
-   utilizar queries parametrizadas no SQLite;
-   impedir valores inválidos;
-   evitar SQL injection.

------------------------------------------------------------------------

# 29. Servidor acessível pela rede

O servidor Python deve escutar de forma que outros computadores da rede
local consigam acessá-lo.

Não limitar o servidor exclusivamente a:

``` text
127.0.0.1
```

Quando necessário, utilizar:

``` text
0.0.0.0
```

e uma porta simples, por exemplo:

``` text
8000
```

A aplicação deve documentar como descobrir o IP local da máquina
servidora.

Exemplo:

``` text
http://192.168.1.10:8000
```

O endereço exato deve ser descoberto durante a instalação/configuração
da rede, não codificado permanentemente.

------------------------------------------------------------------------

# 30. Escopo do MVP

O MVP está concluído quando for possível:

1.  iniciar o servidor Python;
2.  abrir a tela do músico em outro computador;
3.  abrir a tela do operador em outro computador;
4.  visualizar instrumentos;
5.  visualizar volume;
6.  clicar em aumentar/reduzir;
7.  criar uma solicitação;
8.  salvar a solicitação no SQLite;
9.  operador receber a solicitação via polling;
10. operador aceitar ou recusar;
11. atualizar o status;
12. atualizar o volume quando aceita;
13. utilizar os cinco computadores simultaneamente.

------------------------------------------------------------------------

# 31. O que NÃO deve ser implementado no MVP

Não implementar:

-   controle real da mesa de som;
-   reprodução de áudio;
-   integração com hardware;
-   WebSocket;
-   webhook;
-   Flask;
-   React;
-   banco externo;
-   autenticação complexa;
-   sistema de usuários completo;
-   aplicativo Android;
-   aplicativo iOS;
-   deploy em nuvem;
-   Docker;
-   microserviços.

Esses itens podem ser utilizados em versões futuras, mas desviam do
objetivo do workshop.

------------------------------------------------------------------------

# 32. Cronograma pedagógico --- 4 horas

## 00:00--00:20 --- Problema e arquitetura

Apresentar o problema.

Perguntas aos alunos:

-   Como o músico avisa o operador?
-   Como outro computador saberia que houve uma solicitação?
-   Onde guardaríamos essa informação?
-   Quem conversa com o banco?

Desenhar:

``` text
Músico
  ↓
Solicitação
  ↓
Servidor
  ↓
Banco
  ↓
Operador
```

------------------------------------------------------------------------

## 00:20--01:10 --- HTML + CSS

Criar a interface do músico.

Ensinar:

-   elementos HTML;
-   div;
-   títulos;
-   botões;
-   classes;
-   CSS;
-   tamanho;
-   espaçamento;
-   alinhamento.

Objetivo:

A mesa visual deve existir antes de qualquer backend.

------------------------------------------------------------------------

## 01:10--01:50 --- JavaScript e lógica

Ensinar:

-   variável;
-   função;
-   evento;
-   `if`;
-   alteração de valores;
-   alteração do HTML.

Implementar:

``` text
+5
-5
```

com limites:

``` text
0–100
```

Objetivo:

O aluno entende que o botão dispara uma ação.

------------------------------------------------------------------------

## 01:50--02:10 --- Intervalo

------------------------------------------------------------------------

## 02:10--02:40 --- Python + SQLite

Ensinar:

-   servidor;
-   banco;
-   tabela;
-   registro;
-   campo;
-   `INSERT`;
-   `SELECT`;
-   `UPDATE`.

Criar os instrumentos iniciais.

------------------------------------------------------------------------

## 02:40--03:20 --- API e solicitações

Implementar:

``` text
POST /api/solicitacoes
```

Fluxo:

``` text
Botão
 ↓
JavaScript
 ↓
HTTP
 ↓
Python
 ↓
SQLite
```

Depois implementar:

``` text
GET /api/solicitacoes
```

------------------------------------------------------------------------

## 03:20--03:45 --- AJAX/Polling

Explicar:

> "O operador pergunta ao servidor a cada dois segundos se existe uma
> solicitação nova."

Implementar:

``` javascript
setInterval(...)
```

Agora os computadores passam a se comunicar.

------------------------------------------------------------------------

## 03:45--04:00 --- Desafio final

Distribuir instrumentos.

Exemplo:

``` text
Notebook 1 → Vocal
Notebook 2 → Guitarra
Notebook 3 → Baixo
Desktop 2 → Operador
Desktop 1 → Servidor
```

Desafios:

-   aumentar guitarra;
-   diminuir vocal;
-   criar duas solicitações;
-   aceitar uma;
-   recusar outra;
-   observar a atualização em outro computador.

------------------------------------------------------------------------

# 33. Estratégia pedagógica para a IA

A IA que desenvolver este projeto deve seguir estas regras:

## Regra 1 --- ensinar antes de abstrair

Evitar esconder conceitos importantes atrás de frameworks ou
bibliotecas.

## Regra 2 --- código simples

Priorizar código que um adolescente iniciante consiga ler.

## Regra 3 --- explicar causa e efeito

Para cada funcionalidade, explicar:

``` text
usuário faz X
↓
JavaScript faz Y
↓
HTTP envia Z
↓
Python executa W
↓
SQLite guarda/consulta
↓
resposta retorna
↓
interface muda
```

## Regra 4 --- não entregar complexidade desnecessária

Não criar arquitetura empresarial.

## Regra 5 --- validar no backend

Mesmo que o frontend valide, Python deve validar novamente.

## Regra 6 --- código didático

Comentários devem explicar conceitos quando isso ajudar o aprendizado.

Evitar comentários óbvios em excesso.

------------------------------------------------------------------------

# 34. Evolução futura

Depois do workshop, o projeto pode evoluir.

Possíveis próximas etapas:

### Fase 2

-   login simples;
-   mais canais;
-   histórico;
-   múltiplos músicos;
-   painel administrativo.

### Fase 3

-   16 canais;
-   mute;
-   ganho;
-   equalização visual;
-   grupos de instrumentos.

### Fase 4

-   WebSocket;
-   atualização em tempo real;
-   comparação entre polling e WebSocket.

### Fase 5

-   integração com hardware;
-   API real;
-   autenticação;
-   deploy;
-   Docker.

A implementação atual não deve antecipar essas complexidades.

------------------------------------------------------------------------

# 35. Conceitos que o professor deve reforçar

Ao longo do workshop, enfatizar:

### Frontend

"É o que o usuário vê e utiliza."

### Backend

"É o programa que recebe pedidos e executa regras."

### Banco

"É onde o sistema guarda informações."

### HTTP

"É uma forma de computadores conversarem."

### API

"É uma porta organizada para outros programas conversarem com o nosso
sistema."

### JSON

"É uma forma estruturada de transportar dados."

### AJAX/Fetch

"Permite que o navegador converse com o servidor sem precisar recarregar
a página inteira."

### Polling

"O cliente pergunta periodicamente se há novidades."

------------------------------------------------------------------------

# 36. Critério de sucesso pedagógico

O workshop será considerado bem-sucedido se, ao final, um aluno
conseguir explicar com suas próprias palavras algo semelhante a:

> "Quando eu clico no botão, o JavaScript envia uma requisição para o
> Python. O Python salva a solicitação no SQLite. O computador do
> operador fica consultando o Python de tempos em tempos usando AJAX.
> Quando encontra uma solicitação pendente, mostra na tela."

Esse entendimento é mais importante do que quantidade de
funcionalidades.

------------------------------------------------------------------------

# 37. Instrução final para a IA desenvolvedora

Ao receber este documento como especificação do projeto, a IA deve:

1.  respeitar integralmente a stack definida;
2.  não introduzir Flask ou outro framework sem solicitação explícita;
3.  utilizar Python padrão e `sqlite3`;
4.  utilizar HTML, CSS e JavaScript puro;
5.  utilizar AJAX/Fetch com polling para atualização da tela do
    operador;
6.  manter SQLite como banco;
7.  manter funcionamento em rede local;
8.  preservar a separação entre músico e operador;
9.  lembrar que o software não controla a mesa física;
10. priorizar simplicidade e finalidade educacional;
11. evitar dependências externas sempre que possível;
12. fornecer instruções de execução claras;
13. explicar cada componente de maneira acessível a iniciantes;
14. validar entradas no servidor;
15. utilizar SQL parametrizado;
16. testar o fluxo completo entre computadores;
17. não implementar funcionalidades fora do MVP sem autorização;
18. manter o código organizado, legível e pequeno;
19. quando houver uma decisão técnica, escolher a alternativa mais
    simples que preserve o aprendizado;
20. considerar este documento como a fonte principal de requisitos do
    projeto.

------------------------------------------------------------------------

# 38. Resumo da stack final

``` text
FRONTEND
HTML
CSS
JavaScript puro

BACKEND
Python
http.server

BANCO
SQLite
sqlite3

COMUNICAÇÃO
HTTP
Fetch/AJAX
Polling ~2 segundos

REDE
LAN/Wi-Fi

FRAMEWORKS
Nenhum
```

## Fluxo final

``` text
                  ┌─────────────────┐
                  │     MÚSICO      │
                  │   HTML/CSS/JS   │
                  └────────┬────────┘
                           │
                     POST /api
                           │
                           ▼
                  ┌─────────────────┐
                  │     PYTHON      │
                  │   HTTP SERVER   │
                  └────────┬────────┘
                           │
                         INSERT
                           │
                           ▼
                  ┌─────────────────┐
                  │     SQLITE      │
                  └────────┬────────┘
                           │
                         SELECT
                           │
                           ▼
                  ┌─────────────────┐
                  │     PYTHON      │
                  └────────┬────────┘
                           │
                        JSON/HTTP
                           │
                           ▼
                  ┌─────────────────┐
                  │    OPERADOR     │
                  │   HTML/CSS/JS   │
                  └─────────────────┘
                           ▲
                           │
                    AJAX a cada 2s
```

**Fim da especificação.**
