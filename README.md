# python-agent-challange
Repositorio para o desafio tecnico para a vaga de desenvolvedor chatbot ai

## Decisões tecnicas
### Independência de funções
Optei por ter um arquivo em separado para cada tool, como por exemplo extração de contexto, palavras chaves, parse da KB, também optei por separa o llm client do llm tools, ainda que tenha definido eles como classes.

### Tratamento da mensagem
Optei por filtrar palavras chaves dentro da mensagem e a partir delas extrair contexto, para não procurar toda a mensagem dentro da KB, ainda que isso gerasse erro na resposta do LLM, para contornar passei regras bem definidas do tipo de assistente que o modelo deve ser, consegui evitar falsos positivos de contexto dessa forma.

### LLM MODEL
Utilizei um modelo gratuito dentro da openrouter, por questões de liberdade de uso em testes da aplicação.

## Evoluções possiveis
Não implementei session id, mas deixei o projeto pronto para uma eventual evolução neste sentido, também pode fazer sentido melhorar o método get_context para evitar falsos positivos ao retornar contexto.

## Como Testar
1. Para testar a aplicação necessário iniciar o container docker e acessar localhost:8000/docs 
Sendo este endereço a página de documentação da FastAPI onde ao selecionar a opção try it out é possível enviar a requisição para a api e visualizar o response.
2. Também é possível realizar testes via postman ou ainda um script python que realize a requisição.



