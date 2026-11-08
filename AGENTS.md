
# MIKOSHI — INSTRUÇÕES DO PROJETO

## 1. Identidade e objetivo

O nome oficial do projeto é Mikoshi.

Mikoshi é um assistente pessoal de IA especializado em compreender a identidade, as memórias e a maneira de se comunicar de seu proprietário, ajudando principalmente na composição e resposta de mensagens.

O objetivo é gerar respostas que sejam coerentes com a personalidade, o conhecimento pessoal e o contexto do usuário.

Não é um chatbot de conhecimentos gerais.

O projeto deve priorizar:
- Privacidade.
- Funcionamento local e offline.
- Autonomia do usuário.
- Modularidade.
- Segurança.
- Compatibilidade entre Windows e Linux.
- Facilidade de manutenção e expansão.

Não utilizar APIs pagas ou serviços de IA em nuvem como dependência obrigatória.

## 2. Ambiente e hardware

Ambiente inicial:
- Sistema operacional: Windows 10.
- Processador: Intel Core i5-3470.
- GPU: NVIDIA RTX 2060.
- RAM: 12 GB.

Atenção:
O i5-3470 não possui suporte a AVX2. A compatibilidade das bibliotecas e dos modelos deve ser verificada.

A RTX 2060 deve ser considerada para aceleração CUDA, mas não presumir compatibilidade sem testes.

Não assumir que Ollama, CUDA, Python ou outras ferramentas já estejam instaladas.

Verificar o ambiente antes de realizar instalações.

O projeto deverá funcionar futuramente também no Linux.

Evitar caminhos absolutos exclusivos do Windows. Utilizar pathlib e configurações portáveis.

## 3. Tecnologias planejadas

Arquitetura proposta:

- Python: núcleo da aplicação.
- PySide6: interface gráfica.
- SQLite: banco de dados local.
- JSON: configurações e perfis portáveis.
- Ollama ou alternativa compatível: execução de modelos locais.
- FastAPI: API opcional.
- Git: controle de versão.

A escolha definitiva do mecanismo de inferência depende dos testes de compatibilidade.

## 4. Plataformas

O projeto deverá oferecer:

1. Aplicativo desktop para Windows.
2. Aplicativo desktop para Linux.
3. Interface CLI para terminal, principalmente no Linux.
4. API opcional para integração futura com sites e outros aplicativos.

A API deverá:
- Funcionar localmente por padrão.
- Utilizar localhost inicialmente.
- Ter acesso remoto desabilitado por padrão.
- Exigir autenticação e autorização para acesso remoto.
- Utilizar HTTPS quando exposta remotamente.
- Nunca disponibilizar acesso direto ao SQLite ou aos arquivos internos.

O desenvolvimento do site não faz parte da fase atual.

GUI, CLI e API deverão utilizar o mesmo núcleo da aplicação.

## 5. Arquitetura conceitual

A estrutura proposta é:

Mikoshi/
├── main.py
├── cli.py
├── requirements.txt
├── interface/
├── api/
├── core/
├── learning/
├── importers/
├── security/
├── database/
├── data/
└── assets/

Não criar todos esses arquivos e módulos imediatamente.

A estrutura deve ser desenvolvida gradualmente, conforme cada funcionalidade for implementada.

## 6. Dois sistemas independentes de aprendizado

A Mikoshi deverá possuir dois processos de aprendizado distintos.

### 6.1 Personalidade

Aprender como o usuário se comunica:

- Vocabulário.
- Construção de frases.
- Formalidade.
- Humor.
- Ironia.
- Gírias.
- Uso de emojis.
- Tamanho das mensagens.
- Assertividade.
- Maneira de expressar sentimentos.

### 6.2 Memória pessoal

Aprender o que o usuário sabe, viveu, pensa e considera importante:

- Histórias pessoais.
- Infância.
- Experiências.
- Amizades e relacionamentos.
- Crenças e opiniões.
- Valores.
- Gostos e preferências.
- Objetivos.
- Planos.
- Eventos e acontecimentos.

Os dois sistemas precisam ter indicadores de progresso independentes.

A memória deve ser recuperada conforme a relevância para cada conversa, sem inserir todas as informações em todos os prompts.

Distinguir:
- Fatos confirmados.
- Opiniões.
- Inferências.
- Informações temporárias.
- Informações possivelmente desatualizadas.

Não transformar inferências em fatos.

O usuário deve poder visualizar, corrigir, editar, excluir e controlar o uso das memórias.

## 7. Treinamento conversacional

O treinamento deverá funcionar como uma conversa natural com um amigo.

Não utilizar questionários tradicionais como método principal.

A Mikoshi deverá:
- Conversar naturalmente.
- Perguntar sobre histórias e experiências.
- Perguntar como foi o dia do usuário.
- Explorar assuntos anteriores quando apropriado.
- Fazer perguntas complementares.
- Permitir que o usuário inicie assuntos.
- Conversar sem necessariamente tentar extrair informações em todas as mensagens.

Uma resposta poderá alimentar simultaneamente personalidade e memória.

Exemplo:

"Quando eu era criança gostava de desmontar brinquedos."

Possíveis resultados:
- Memória: experiência da infância.
- Personalidade: hipótese de curiosidade investigativa.

A hipótese de personalidade deverá ser confirmada pelo usuário antes de ser tratada como característica estabelecida.

## 8. Importação de conversas

Criar um módulo de importação de conversas exportadas de outros aplicativos.

Formatos iniciais:
- TXT.
- JSON.

Arquitetura preparada para:
- WhatsApp.
- Telegram.
- Discord.
- Outros formatos futuramente.

O usuário deverá conseguir:
- Selecionar arquivos.
- Visualizar o conteúdo antes da importação.
- Identificar suas próprias mensagens.
- Selecionar conversas e trechos.
- Remover informações antes de importar.
- Anonimizar dados de terceiros.

É fundamental distinguir as mensagens do usuário das mensagens de outras pessoas.

As mensagens do usuário alimentarão o aprendizado de personalidade.

O conteúdo contextual poderá alimentar o sistema de memória, mediante revisão e confirmação.

A importação inicial não representa treinamento dos pesos do modelo. Trata-se de análise e construção de perfis e memórias.

## 9. Gerenciamento de personalidades

Permitir:
- Criar personalidades.
- Duplicar.
- Editar.
- Excluir.
- Importar.
- Exportar.
- Alternar entre personalidades.

Utilizar o formato portátil .personality, baseado em JSON estruturado.

Uma personalidade poderá conter:
- Nome.
- Versão.
- Idioma.
- Estilo de comunicação.
- Preferências de escrita.
- Características comportamentais.
- Exemplos de mensagens.
- Instruções personalizadas.

A memória pessoal e a personalidade de comunicação são conceitos diferentes.

A exportação de memórias deve ser uma opção separada e explícita.

Instruções importadas nunca poderão substituir as políticas de segurança.

## 10. Emotional Engine

Criar um mecanismo de configuração emocional.

Cada emoção deverá possuir intensidade entre 0 e 10.

Emoções previstas:
- Compaixão.
- Empatia.
- Afeto.
- Alegria.
- Tristeza.
- Agressividade.
- Irritação.
- Humor.
- Ironia.
- Ciúmes.
- Paciência.
- Assertividade.

Cada emoção terá dois modos:

FIXO:
A intensidade configurada deverá ser respeitada, sem adaptação contextual.

AUTOMÁTICO:
A intensidade poderá variar de acordo com o contexto da conversa.

As configurações serão:
- Independentes por conversa.
- Persistentes após fechar o aplicativo.
- Armazenadas localmente no SQLite.
- Reutilizáveis por meio de predefinições.

As configurações fixas possuem prioridade sobre ajustes automáticos.

Importante: essas configurações controlam a expressão emocional da IA. Não significam que a IA realmente sente emoções.

## 11. Segurança e restrição de finalidade

A Mikoshi não deverá funcionar como chatbot de conhecimentos gerais.

Restrição de finalidade moderada:

Permitido:
- Ajudar a responder mensagens.
- Interpretar conversas.
- Melhorar textos.
- Ajustar tom e linguagem.
- Ajudar com comunicação profissional.
- Tarefas auxiliares diretamente relacionadas à comunicação.

Não permitido:
- Perguntas gerais sem relação com a finalidade.
- Transformar a aplicação em assistente genérico.

Quando uma solicitação estiver fora do propósito:
1. Recusar educadamente.
2. Explicar brevemente.
3. Oferecer uma alternativa relacionada à comunicação.

Implementar validação de entrada e saída no próprio aplicativo.

Módulos previstos:
- security/request_guard.py
- security/output_validator.py
- security/permissions.py
- security/security_config.py

As configurações de segurança só poderão ser alteradas pelo proprietário ou administrador.

Personalidades importadas e instruções personalizadas não poderão contornar essas políticas.

Não depender exclusivamente do prompt do modelo para segurança.

## 12. Roadmap

Desenvolver nesta ordem:

FASE 1 — Ambiente e infraestrutura
- Verificar Python.
- Verificar Git.
- Verificar hardware.
- Criar ambiente virtual.
- Selecionar mecanismo de inferência compatível.
- Testar execução de um modelo local.
- Verificar aceleração da GPU.

FASE 2 — Núcleo e aplicação básica
- Criar núcleo independente da interface.
- Criar interface PySide6.
- Implementar chat básico.
- Integrar modelo local.
- Implementar CLI básica.

FASE 3 — Personalidade
- Perfil de comunicação.
- Análise de exemplos.
- Questionário opcional.
- Conversa de treinamento.
- Indicador de progresso.

FASE 4 — Memória pessoal
- Banco de memórias.
- Extração contextual.
- Confirmação de informações.
- Recuperação de memórias relevantes.
- Indicador independente de progresso.

FASE 5 — Importação de conversas
- TXT.
- JSON.
- Parsers específicos.
- Identificação de participantes.
- Pré-visualização.
- Privacidade e anonimização.

FASE 6 — Inteligência contextual
- Interpretação de mensagens recebidas.
- Identificação de intenção e tom.
- Contexto da conversa.
- Geração de respostas personalizadas.

FASE 7 — Emotional Engine
- Intensidades.
- Modos fixo e automático.
- Configurações por conversa.
- Predefinições.

FASE 8 — Gerenciador de personalidades
- Criação.
- Duplicação.
- Edição.
- Importação.
- Exportação.
- Exclusão.

FASE 9 — Segurança e API
- Validação de entrada e saída.
- Permissões administrativas.
- API local.
- Preparação para acesso remoto seguro.

FASE 10 — Distribuição
- Aplicativo Windows.
- Aplicativo Linux.
- CLI.
- Documentação.
- Testes finais.

## 13. Regras obrigatórias de desenvolvimento

1. Trabalhar incrementalmente.
2. Explicar o motivo de cada ação.
3. Não implementar tudo de uma vez.
4. Não reescrever arquivos sem necessidade.
5. Não remover funcionalidades existentes sem autorização.
6. Não inventar que algo foi implementado ou testado.
7. Não instalar ferramentas sem autorização.
8. Não alterar configurações importantes do Windows sem autorização.
9. Priorizar soluções gratuitas e locais.
10. Preservar a compatibilidade futura com Linux.
11. Documentar decisões arquiteturais.
12. Testar cada etapa antes de avançar.

Antes de alterar arquivos, analisar o conteúdo existente.

Quando houver dúvidas sobre decisões do projeto, perguntar ao proprietário em vez de assumir.

## 14. Estado atual do projeto

O projeto está na etapa inicial de preparação do ambiente.

Não presumir que qualquer funcionalidade da Mikoshi já foi implementada.

Primeiro, inspecionar:
- Estrutura atual da pasta.
- Versão do Python.
- Ambiente virtual.
- Git.
- Espaço disponível.
- Processador.
- GPU e drivers.
- Compatibilidade das ferramentas.

Não iniciar a implementação das funcionalidades antes de concluir a verificação do ambiente.

## 15. Primeira tarefa do Codex

Neste momento, sua tarefa é:

1. Inspecionar o projeto existente.
2. Identificar o que já está configurado.
3. Verificar o ambiente Windows.
4. Identificar problemas de compatibilidade.
5. Apresentar um relatório.
6. Sugerir a configuração inicial mais adequada.

Não instalar nada nem modificar arquivos sem autorização.

Depois da análise, aguarde aprovação para prosseguir.
