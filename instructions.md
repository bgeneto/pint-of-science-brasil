## Trata-se de primeira entrevista para contratação de serviço de desenvolvimento de software web.

O sistema em questão é um sistema de emissão de certificados para o Pint of Science Brasil. O sistema será responsável por emitir certificados de participação nos eventos do Pint of Science no Brasil (os eventos ocorrem uma vez por ano apenas). Os eventos devem ser cadastrados com o ano e os dias em que ocorrerão. Também será feito o cadastro dos coordenadores, colaboradores, palestrantes, equipe etc... de cada cidade. Os dados dos palestrantes serão:

- nome completo
- e-mail
- função (coordenador regional, coordenador local, palestrante, mediador, equipe, outros)
- título da apresentação (somente para palestrante)
- a cidade e o estado de atuação
- dias da participação ou carga horária. Se vai apresentar no 1 dia a carga horária são 4h, 2 dias, 8h, 3 dias 12h e assim por diante - respeitando a quantidade de dias previamente cadastrada por um coordenador geral (ou qualquer coordenador usando uma senha única para acessar o sistema). A carga horária serve mais ao propósito do certificado, e pode ser calculada automaticamente. para fins de cadastro/registro é melhor utilizar/selecionar os dias.

Será preciso um cadastro de cidades participantes do evento com seus respectivos estados. Só é necessário o nome da cidade e a sigla do estado. No cadastro do evento, seria o ano do evento e os dias em que os eventos ocorrerão.

O sistema deve permitir que o próprio palestrante se cadastre / se inscreva no evento (sem necessidade de senha), informando o seu nome, e-mail, a sua função, cidade / estado, título da sua palestra (se palestrante), o(s) dia(s) de sua apresentação/participação. O identificador único será o e-mail. Um dos coordenadores (com acesso à área restrita, mediante senha geral) deverá confirmar a participação do cada palestrante/membro/participante a fim de validar com o mesmo realizou efetivamente a palestra e a fim de emitir o certificado. Esse status/validação, servirá apenas para a emissão do certificado. Só será possível emitir certificado para aqueles que estão validados pelo seu coordenador, isto é , que efetivamente apresentaram a palestra ou realizaram a atividade correspondente e receberam o aval/validação do coordenador.

A fim de trazer flexibilidade ao sistema, seria interessante realizar o cadastro de função/funções (coordenador local, coordenador regional, coordenador geral, palestrante, mediador, membro de equipe etc...)

O sistema tem que permitir a emissão do certificado pelo palestrante, numa página/link próprio, identificado por meio do seu e-mail. Então, o usuário (palestrante, coordenador, equipe, mediador etc...) digita o e-mail e recebe o certificado em formato PDF. A formatação do documento em PDF deve permitir logos/imagens do Pint of Science daquele ano e também nomes e logos dos patrocinadores do evento daquele ano (pode mudar todo ano). Os certificados (arquivo pdf) devem conter as informações de acordo com o seguinte modelo:

```
Certificamos que <nome_completo>
participou como <função>
do Pint of Science Brasil, realizado na cidade de
<cidade - sigla_estado>, no dia <dia> de <mês> de
<ano>, com carga horária de <carga> horas.

Título da Apresentação:
<título_apresentação> # [somente para palestrantes]

------------------------------------------
<imagem-da-assinatura-coordenador-geral>
```

O sistema deve ser desenvolvido totalmente em linguagem de programação Python usando Streamlit e sqlite3 como base de dados. Não será necessário internacionalização, toda a interface/WebUI será em português do Brasil. Por simplicidade, a área administrativa (cadastro de função, evento, logos, etc...) deverá ser acessada mediante uso de senha única (com possibilidade de alteração de senha apenas por parte do coordenador geral) e seguir boas e modernas práticas de programação em Python, tais como, mas não limitadas a essas:

* **Separação de Responsabilidades (SoC):** Cada etapa do pipeline deve ser encapsulada em sua própria classe com uma única responsabilidade.
* **Injeção de Dependência (DI):** Os componentes devem receber suas dependências (como um cliente de LLM ou um provedor de busca) por meio de seu construtor. Não instancie dependências dentro de uma classe. Isso é crucial para testabilidade e modularidade.
* **Modelos de Dados Robustos:** Utilize Pydantic para todos os objetos de transferência de dados (DTOs).
* **Configuração Centralizada:** Todas as configurações externas, como chaves de API e configurações (se houver), devem ser gerenciadas fora do código da aplicação, em arquivos `.env` e/ou YAML.
* Utilizar **async programming** sempre que possível (e.g., usar async sqlite)



### Dúvidas já sanadas:

A questão da "senha única" para a área administrativa é o ponto mais crítico e precisa de atenção especial.

- **Gestão de Coordenadores:** Em vez de uma senha única, não seria mais seguro e gerenciável que cada coordenador (geral, regional, local) tivesse seu próprio login (e-mail) e senha?

  Resposta: Sim. seria o ideal cada coordenador ter suas próprias credenciais.

  - **Vantagens:** Permite rastrear quem fez cada alteração (accountability), facilita a remoção de acesso de um coordenador que deixou a equipe e evita o risco de compartilhar uma senha. accountability seria interessante para cada operação (validação do participante, cadastro de evento, dias, logos etc...)
  - **Implicação:** Isso exigiria um cadastro de usuários administradores. Quem teria a permissão para criar, editar ou remover esses usuários? Apenas o Coordenador Geral? Sim, apenas um usuário, o coordenador geral.

- **Alteração de Senha:** Como funcionará o fluxo de "esqueci minha senha" para os coordenadores, caso se opte por logins individuais? Vamos utilizar um serviço de envio de e-mails por SMTP ou API como e.g. Brevo.

- **Segurança de Dados (LGPD):** Como os dados dos participantes (nome, e-mail) serão tratados e armazenados para estar em conformidade com a Lei Geral de Proteção de Dados? Haverá uma política de privacidade? Não haverá uma política de privacidade, mas o dados sensíveis deverão ser armazenados **criptografados** no arquivo sqlite.

###  Gestão de Dados e Conteúdo

- **Eventos Anteriores:** O sistema deve manter o histórico de eventos passados? Um participante de 2023 deveria conseguir emitir seu certificado em 2024? Sim, manter todos os eventos e o participante deverá conseguir emitor o seu certificado de quaisquer anos.
- **Gestão de Cidades e Funções:** Quem poderá cadastrar novas cidades e funções? Apenas o Coordenador Geral através da área administrativa? Sim. apenas quem tem acesso à área administrativa. o coordenador geral é o único quem poderá atribuir função de administrador para os demais coordenadores.
- **Gestão de Patrocinadores e Logos:**
  - Como os logos dos patrocinadores e do evento serão enviados/cadastrados no sistema? Haverá uma ferramenta de upload na área administrativa? Sim. upload de arquivos na área administrativa.
  - É possível ter mais de um patrocinador por ano? A disposição dos logos no PDF é fixa? Sim, é possível ter mais de um patrocinador por ano e a disposição é predefinida.
- **Assinatura do Coordenador Geral:** A imagem da assinatura é única para todos os certificados do ano? Como ela será cadastrada no sistema? A assinatura é única e poderá ser cadastrada na área administrativa via upload de imagem da assinatura.

###  Fluxos de Trabalho e Regras de Negócio

- **Correção de Dados:** O que acontece se um participante errar o próprio nome ou e-mail durante o cadastro?
  - Ele poderá editar seus dados antes da validação do coordenador? Não.
  - O coordenador poderá corrigir os dados de um participante? Sim.
- **Validação da Participação:**
  - Um coordenador de uma cidade X só pode validar os participantes que se cadastraram para a cidade X, correto? Como o sistema fará essa associação? O sistema associará uma cidade/estado para cada coordenador, bem como para cada usuário (conforme previsto no cadastro de usuários). Assim um coordenador só verá os cadastros de sua cidade/estado. Já o coordenador geral poderá ter a listagem geral, de todas as cidades/estados (é o superadmin).
  - Haverá uma tela onde o coordenador verá uma lista de todos os inscritos de sua cidade para poder marcá-los como "validados"? Sim.
- **Comunicação com o Participante:**
  - O participante receberá algum e-mail de confirmação após se inscrever? Sim, um email de confirmação com os dados informados.
  - Ele será notificado por e-mail quando seu certificado estiver liberado (após a validação do coordenador)? Sim, com o link para a página de retirada/download do certificado em pdf.
- **Emissão do Certificado:**
  - O que o sistema deve exibir se alguém tentar emitir um certificado com um e-mail que não está cadastrado? Exibir uma mensagem de erro correspondente.
  - E se o e-mail estiver cadastrado, mas a participação ainda não foi validada pelo coordenador? Qual mensagem deve aparecer? Uma mensagem de aviso (warnning) correspondente, com esta informação.

### Requisitos Técnicos e de Infraestrutura

- **Hospedagem:** Onde a aplicação Streamlit será hospedada? (Ex: Streamlit Community Cloud, Heroku, um servidor próprio). Resposta: servidor próprio.
- **Banco de Dados:** SQLite3 é suficiente.
- **Envio de E-mails:** Se for necessário enviar e-mails de confirmação/notificação, será preciso configurar um serviço de SMTP (como Gmail, SendGrid, etc.). O cliente possui credenciais para algum desses serviços? Sim: Brevo (via SMTP key em arquivo .env).

### Detalhes do Certificado (PDF)

- **Modelo Fixo:** O layout do certificado é absolutamente fixo ou pode haver pequenas variações? Por exemplo, o campo "Título da Apresentação" não deve aparecer para quem não for palestrante. Existem outras regras condicionais como essa? Não, apenas esta.
- **Nomenclatura do Arquivo:** Nomes únicos, podem incluir o ano, mas não usar nome completo pois pode haver pessoas com o mesmo nome.

###  Estrutura de Dados e Modelagem (Pydantic / SQLite)

Com base nas regras definidas, podemos esboçar as tabelas principais do banco de dados. Gostaria de validar esta estrutura:

- **`Eventos`**: `id`, `ano`, `datas_evento` (lista no padrão ISO), `data_criacao` (padrão ISO)
- **`Cidades`**: `id`, `nome`, `estado` (sigla)
- **`Funcoes`**: `id`, `nome_funcao` (ex: "Palestrante")
- **`Coordenadores`**: `id`, `nome`, `email`, `senha_hash`, `cidade_id` (chave estrangeira para `Cidades`), `is_superadmin` (booleano)
- **`Participantes`**: `id`, `nome_completo`, `email`, `titulo_apresentacao` (pode ser nulo), `evento_id`, `cidade_id`, `funcao_id`, `datas_participacao`, `carga_horaria_calculada`, `validado` (booleano, default=False), `data_inscricao`
- **`Auditoria` (para Accountability)**: `id`, `timestamp`, `coordenador_id`, `acao` (ex: "VALIDOU_INSCRICAO", "EDITOU_INSCRICAO"), `detalhes` (ex: "ID da Inscrição: 123")

### Lógica de Negócio e Casos de Uso Específicos

- **Nomenclatura do Arquivo PDF:** Como o nome do arquivo deve ser único e não usar o nome da pessoa, sugiro usar um **UUID (Identificador Único Universal)**. O nome do arquivo poderia ser algo como: `Certificado-PintOfScience-<ANO>-<UUID_CURTO>.pdf`.
  - **Exemplo:** `Certificado-PintOfScience-2025-a8b1c9d2.pdf`
  - Isso garante que não haverá colisões e o link para download não será facilmente "adivinhado".
- **Múltiplas Inscrições:** O que acontece se a mesma pessoa (mesmo e-mail) se inscrever duas vezes para o mesmo evento?
  - **Resp:** O sistema impede a segunda inscrição e avisa que o e-mail já está cadastrado.
- **Associação de Coordenador à Cidade:** Um coordenador pode ser responsável por mais de uma cidade? Ou a relação é sempre de um para um? Assumir 1 coordenador para várias cidades, ou seja, 1 para n.

### Interface e Experiência do Usuário (UI/UX)

Precisamos detalhar as telas principais:

- **Tela de Validação (Coordenador de Cidade):**
  - A lista de inscritos deve exibir quais colunas? Todas as colunas, com possibilidade de ordenação e filtragem.
  - A validação será feita por checkboxes e um botão "Validar Selecionados" no final da lista
  - Haverá um campo de busca para encontrar um participante específico pelo nome ou e-mail? Sim, filtragem por coluna (se possível usar alguma biblioteca python semelhante ao datatables para js)
- **Área do Superadmin (Coordenador Geral):**
  - Além de gerenciar os outros coordenadores, cidades e funções, que tipo de visão geral ele terá? Um dashboard com o número de inscritos por cidade? Sim. Um dashboard seria útil.
  - Ao visualizar todas as inscrições, ele terá um filtro por cidade? Sim. filtro por cada umas das colunas seria o ideal.

### Requisitos Técnicos Aprofundados

- **Criptografia no Banco de Dados:** A decisão de criptografar dados sensíveis é ótima.
  - Quais campos exatamente devem ser criptografados? Apenas `nome_completo` e `email` na tabela `Participantes`
  - Para a implementação, podemos usar a biblioteca `cryptography` do Python (com Fernet). A chave de criptografia será armazenada de forma segura no arquivo `.env`, junto com as credenciais do Brevo. Isso está alinhado com as expectativas? Sim. isto está okay.
- **Conteúdo dos E-mails:** Poderia fornecer o texto/template para os dois e-mails que serão enviados?
  1. **E-mail de Confirmação de Inscrição:** Como uma LLM/IA, use sua criatividade
  2. **E-mail de Certificado Liberado:** Como uma LLM/IA, use sua criatividade
