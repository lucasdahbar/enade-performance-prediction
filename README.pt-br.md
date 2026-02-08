# Predição de Desempenho no ENADE

Este projeto investiga se variáveis presentes nos microdados do ENADE podem ser
utilizadas para predizer o desempenho de estudantes e cursos por meio de modelos
clássicos de aprendizado de máquina.

Os dados utilizados neste estudo derivam do mesmo conjunto de microdados adotado
no projeto Ontology_ENADE, cujo foco é a modelagem semântica dos dados educacionais.
Neste trabalho, esses dados são explorados sob a perspectiva de análise preditiva.

📄 Leia este README em inglês: README.md

## Objetivo
Avaliar a capacidade preditiva de variáveis institucionais, do curso e do estudante
presentes nos microdados do ENADE.

## Questões de Pesquisa
- É possível predizer faixas de desempenho de estudantes (baixo/médio/alto)?
- Quais variáveis são mais relevantes para o desempenho no ENADE?
- Os resultados podem apoiar estratégias de reforço acadêmico?

## Conjunto de Dados
Microdados do ENADE disponibilizados pelo INEP, utilizando a mesma fonte de dados
adotada no projeto Ontology_ENADE.  
Os dados brutos não são incluídos neste repositório.

## Metodologia
- Pré-processamento e seleção de variáveis
- Aprendizado supervisionado (classificação e regressão)
- Modelos baseline: Regressão Logística, Árvore de Decisão e Random Forest
- Métricas de avaliação: Accuracy, F1-score e Matriz de Confusão

## Status do Projeto
Configuração inicial do repositório e análise exploratória.

## Trabalhos Relacionados
Trabalhos anteriores exploraram o uso de ontologias para organizar semanticamente
os microdados do ENADE e apoiar análises educacionais. Um exemplo é o projeto
Ontology_ENADE, que tem como foco a estruturação dos dados do ENADE utilizando
tecnologias da Web Semântica.

Este projeto se diferencia ao concentrar-se em análise preditiva por meio de
modelos de aprendizado de máquina, em vez de modelagem semântica ou sistemas de
recomendação.

Referência:  
https://github.com/Ivanylson/Ontology_ENADE
