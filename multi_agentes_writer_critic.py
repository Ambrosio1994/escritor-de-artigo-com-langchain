from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import END, StateGraph, START

from langchain_anthropic import ChatAnthropic

import os
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from typing import Annotated


os.getenv("ANTHROPIC_API_KEY")
os.getenv("TAVILY_API_KEY")

model = "claude-3-5-sonnet-20241022"
llm = ChatAnthropic(model=model,
                    temperature=0,
                    max_tokens=1000)

class GraphState(TypedDict):
    """
    Representa o estado do nosso gráfico.

    Atributos:
    tema : tema do artigo que sera escrito
    web_search: pesquisas sobre o tema do artigo
    artigo: geração do artigo pelo LLM
    nota: nota de 0 a 10
    """

    tema: str
    web_search: str
    # redacao: str
    artigo : str
    nota: float
    # decisao: str
    iteracoes: int

class Editor_Feedback(BaseModel):
    score: Annotated[
        float,
        Field(
            description="Pontuação de 0 a 10 para artigo escrito.",
        ),
    ]
    review: Annotated[
        str,
        Field(
            description="Destaque dos pontos positivos e os \
            detalhes devem ser melhorados pelo esctitor.",
        ),
    ]

web_search_tool = TavilySearchResults(k=5)

system_escritor = """
Você é um escritor profissional especializado em criar artigos informativos
e envolventes. Sua tarefa é criar um artigo baseado no tema {tema}
e nos materiais de apoio fornecidos.

Você poderá receber uma crítica sobre seu artigo e voce deve:

1. Observar os pontos fortes apontados pelo a avaliador
2. Observar o que ele apontar que deve ser melhorado na sua escrita
3. Implantar essas melhorias no seu proximo texto gerado

##ATENÇAÕ##

Se uma critica nao for enviada voce devera se atentar apenas aos textos
de apoio enviados.

Para criar o artigo, siga estas diretrizes:

1. TEMA PRINCIPAL: {tema}
2. MATERIAIS DE APOIO: {web_search}
3. SE HOUVER, ATENTAR PARA CRITICA DO AVALIADOR: {critica}

3. ESTRUTURA SOLICITADA:
- Título chamativo
- Introdução envolvente
- Desenvolvimento do tema em tópicos
- Conclusão

4. ELEMENTOS ADICIONAIS:
- Inclua dados estatísticos relevantes dos materiais de apoio
- Adicione exemplos práticos
- Utilize citações quando apropriado
- Mantenha um fluxo natural entre os parágrafos

5. OTIMIZAÇÃO:
- Utilize subtítulos informativos
- Mantenha parágrafos concisos
- Inclua palavras-chave naturalmente
- Evite jargões desnecessários

Por favor, crie um artigo original que atenda a estes requisitos,
mantendo um equilíbrio entre informação e engajamento do leitor.

Você poderá receber uma critica sobre seu artigo e voce deve:

1. Observar os pontos fortes apontados pelo a avaliador
2. Observar o que ele apontar que deve ser melhorado na sua escrita
3. Implantar essas melhorias no seu proximo texto gerado
"""

prompt_escritor = ChatPromptTemplate.from_messages(
    [
        ("system", system_escritor),
        (
            "human",
            "Aqui esta o tema {tema} e os textos de apoios {web_search}. \
            Aqui esta a critica do avaliador {critica}",
        ),
    ]
)
escritor = prompt_escritor | llm | StrOutputParser()

system_critico = """
Você é um especialista em análise e correção textual, com vasta experiência
em avaliação de artigos acadêmicos e textos diversos.
Sua tarefa é analisar minuciosamente os textos recebidos
considerando os seguintes aspectos:

1. Estrutura e organização:
- Coerência e coesão
- Estrutura dos parágrafos
- Progressão lógica das ideias

2. Conteúdo:
- Clareza na exposição das ideias
- Argumentação
- Profundidade da análise
- Relevância das informações

3. Linguagem:
- Adequação ao registro formal/informal
- Vocabulário
- Gramática e ortografia
- Pontuação

4. Aspectos técnicos:
- Formatação
- Citações (quando aplicável)
- Referências (quando aplicável)

Para cada texto analisado, você deve fornecer:

1. Um resumo dos pontos positivos, destacando os aspectos bem desenvolvidos do texto.

2. Uma lista de pontos que necessitam de melhorias, com sugestões específicas para aprimoramento.

3. Um breve comentário final com recomendações gerais para o autor.

Por favor, mantenha um tom construtivo e profissional em suas análises,
focando sempre em como o texto pode ser aprimorado.

5. Faca sua analise do artigo: {artigo}

"""

prompt_critico = ChatPromptTemplate.from_messages(
    [
        ("system", system_critico),
        (
            "human",
            "Aqui está a artigo: \n\n {artigo} \n De sua nota e sua avaliacao da artigo",
        ),
    ]
)

structured_llm_feedback = llm.with_structured_output(Editor_Feedback)
critico = prompt_critico | structured_llm_feedback

def web_search(state: GraphState):
    """
    Faz uma pesquisa web com base no tema e guarda os resultados no estado.

    Args:
        state (GraphState): Estado do gráfico

    Returns:
        dict: Dicionário com a chave "web_search" e o valor com os resultados da
        pesquisa.
    """
    print("-----Web Search-----\n")
    tema = state["tema"]
    searchs = web_search_tool.invoke({"query": tema})
    print("Resultados da pesquisa:", searchs)

    state["web_search"] = searchs
    return {"web_search": searchs}

def escrever_artigo(state: GraphState):
    """
    Gera um artigo a partir do tema e dos resultados da pesquisa web
    
    Args:
        state (GraphState): O estado atual do gráfico
    
    Returns:
        dict: O estado atualizado com a redação gerada
    """
    textos_apoio = "\n".join([f"{result['content']} (Source: {result['url']})" for result in state["web_search"]])
    tema = state["tema"]

    critica = state["critica"] if "critica" in state else ""

    # Gerar a redação usando o prompt
    artigo = escritor.invoke({"tema": tema, "web_search": textos_apoio, "critica":critica}).strip()

    # Atualizar o estado com a redação gerada
    state["artigo"] = artigo

    # Exibir a redação gerada
    print("-----Artigo geradO:-----")
    print(artigo)

    # Retornar o estado atualizado como um dicionário
    return {"artigo": artigo}

def avaliar_artigo(state: GraphState):
    """
    Avalia o artigo escrito e atualiza o estado com a nota e crítica.

    Args:
        state (GraphState): O estado atual do gráfico.

    Returns:
        dict: O estado atualizado com a nota e crítica do artigo.
    """
    print("-----AVALIAÇÃO-----")
    artigo = state["artigo"]

    feedback = critico.invoke({"artigo": artigo})
    print(feedback)

    state["critica"] = feedback.review
    state["nota"] = feedback.score
    state["iteracoes"] += 1


    return {"artigo": state["artigo"], "nota": state["nota"], "critica": state["critica"]}

def decide_to_generate(state: GraphState, threshold: float, max_iteracoes: int):
    """
    Decide se o artigo precisa ser refeito ou pode ser finalizado com base na nota e número de iterações.

    Args:
        state (GraphState): O estado atual do gráfico.
        threshold (float): A nota mínima para finalizar o artigo.
        max_iteracoes (int): O número máximo de iterações permitidas.

    Returns:
        str: O nome do nó a ser executado em seguida. Pode ser "refazer" ou "finalizar".
    """
    nota = state["nota"]
    iteracoes = state["iteracoes"]

    if iteracoes >= max_iteracoes:
        state["decisao"] = "finalizar"
        return "finalizar"

    if nota <= threshold:
        return "refazer"
    else:
        return "finalizar"

# @title Create the workflow
work_flow = StateGraph(GraphState)
work_flow.add_node("web_search_node", web_search)
work_flow.add_node("escritor_node", escrever_artigo)
work_flow.add_node("critico_node", avaliar_artigo)

work_flow.add_edge(START, "web_search_node")
work_flow.add_edge("web_search_node", "escritor_node")
work_flow.add_edge("escritor_node", "critico_node")


max_iteracoes = 3
threshold = 8.0
work_flow.add_conditional_edges(
    "critico_node",
    lambda state: decide_to_generate(state, threshold=threshold, max_iteracoes=max_iteracoes),
    {
        "refazer": "escritor_node",
        "finalizar": END,
    },
)

app = work_flow.compile()

from pprint import pprint

inputs = {"tema": "o que mundo no mundo após a covid", "iteracoes":0}
for output in app.stream(inputs):
    for key, value in output.items():
        pprint(f"Node '{key}':")
    pprint("\n---\n")