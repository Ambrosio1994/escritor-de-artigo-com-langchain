![Fluxo LangChain](writer_crtic.png)

 # 🖋️ Workflow Automatizado de Escrita e Avaliação de Artigos com LLMs

Este projeto implementa um **fluxo de trabalho automatizado** para geração, avaliação e melhoria iterativa de artigos. Ele combina ferramentas como **LangChain**, **Tavily Search**, e **Anthropic LLMs** para criar artigos otimizados baseados em pesquisa web e críticas automáticas.

---

## 📜 Descrição

O sistema é projetado para:

1. **Pesquisar conteúdo** relevante baseado em um tema específico.
2. **Gerar artigos** usando um modelo de linguagem (LLM) treinado.
3. **Avaliar os artigos** gerados com base em critérios técnicos e de qualidade textual.
4. **Iterar o processo**, incorporando feedback para melhorar os resultados até atingir um padrão definido.

O fluxo é organizado em nós e condições, permitindo a iteração automática até que o artigo atenda aos requisitos de qualidade estabelecidos.

---

## ✨ Funcionalidades

- **Pesquisa na Web Automatizada**: Utiliza a API do **Tavily Search** para encontrar conteúdo relevante baseado no tema especificado.
- **Geração de Artigos**: Usa o modelo **Anthropic Claude** para criar textos detalhados e bem estruturados.
- **Avaliação de Artigos**: Um crítico automatizado fornece feedback detalhado, incluindo notas e sugestões de melhorias.
- **Fluxo Iterativo**: O processo de geração e avaliação continua até que a qualidade do artigo atenda a um limite predefinido.
- **Configuração Personalizável**: Permite ajustar o limite de qualidade (`threshold`) e o número máximo de iterações.

---

## 📋 Requisitos

Certifique-se de ter o seguinte ambiente configurado:

- **Python 3.8** ou superior.
- **Chaves de API**:
  - `ANTHROPIC_API_KEY` para acessar o modelo de linguagem.
  - `TAVILY_API_KEY` para realizar pesquisas na web.

Dependências Python:
- `langchain-core`
- `langchain-community`
- `langgraph`
- `pydantic`
- `typing-extensions`

---
