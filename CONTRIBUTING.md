# Contribuindo para FastRAG

Obrigado por seu interesse em contribuir com o FastRAG! Este documento fornece diretrizes para contribuir com o projeto.

## Como Contribuir

### Reportando Bugs

Se você encontrar um bug, por favor abra uma [issue](https://github.com/strondata/fastrag/issues) com:

- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. comportamento atual
- Versão do Python e do FastRAG
- Qualquer informação adicional relevante

### Sugerindo Melhorias

Para sugerir melhorias ou novas funcionalidades:

1. Verifique se já não existe uma issue similar
2. Abra uma nova issue descrevendo:
   - A funcionalidade desejada
   - Por que seria útil
   - Exemplos de uso

### Pull Requests

1. **Fork o repositório** e crie uma branch a partir de `main`:
   ```bash
   git checkout -b feature/minha-feature
   ```

2. **Faça suas alterações** seguindo as diretrizes de código:
   - Siga o estilo de código existente
   - Adicione testes para novas funcionalidades
   - Atualize a documentação quando necessário

3. **Execute os testes**:
   ```bash
   pytest
   ```

4. **Formate o código**:
   ```bash
   black src/ tests/
   isort src/ tests/
   ```

5. **Verifique o linting**:
   ```bash
   flake8 src/ tests/
   mypy src/
   ```

6. **Commit suas mudanças**:
   ```bash
   git commit -m "Descrição clara da mudança"
   ```

7. **Push para sua branch**:
   ```bash
   git push origin feature/minha-feature
   ```

8. **Abra um Pull Request** com:
   - Título descritivo
   - Descrição do que foi alterado e por quê
   - Referência a issues relacionadas

## Diretrizes de Código

### Estilo

- Seguimos [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Usamos [Black](https://black.readthedocs.io/) para formatação automática
- Limite de linha: 100 caracteres
- Use type hints quando possível

### Testes

- Todos os novos recursos devem ter testes
- Mantenha a cobertura de testes alta
- Use pytest para escrever testes
- Nomeie os testes de forma descritiva

### Documentação

- Docstrings para todas as funções, classes e módulos públicos
- Formato de docstring: Google style
- Atualize README.md e docs/ quando relevante

### Commits

- Mensagens de commit em português ou inglês
- Use presente do indicativo ("Adiciona feature" não "Adicionada feature")
- Primeira linha: resumo breve (máx. 72 caracteres)
- Linhas adicionais: descrição detalhada se necessário

## Configuração do Ambiente de Desenvolvimento

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/strondata/fastrag.git
   cd fastrag
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Execute os testes**:
   ```bash
   pytest
   ```

## Processo de Review

- Todos os PRs serão revisados por um mantenedor
- Feedback será fornecido construtivamente
- Mudanças podem ser solicitadas antes da aprovação
- Após aprovação, o PR será merged

## Código de Conduta

- Seja respeitoso e profissional
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros da comunidade

## Dúvidas?

Se tiver dúvidas sobre como contribuir, sinta-se à vontade para:

- Abrir uma issue
- Entrar em contato com os mantenedores
- Consultar a documentação

Obrigado por contribuir! 🎉
