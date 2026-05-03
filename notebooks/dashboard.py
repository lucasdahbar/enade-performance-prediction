import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title="Dashboard - Insights Enade", layout="wide")
st.title("Painel de Insights Enade 2022 - UFJF")
st.markdown("Este dashboard apresenta a performance comparativa dos cursos em relação à média da universidade.")


@st.cache_data
def load_data():
    project_root = Path(__file__).resolve().parents[1]
    raw_path = project_root / "data" / "raw" / "cursos_ufjf_enade2022.csv"
    processed_path = project_root / "data" / "processed" / "enade_ufjf_2022_model.csv"

    if raw_path.exists():
        return pd.read_csv(raw_path)

    if processed_path.exists():
        st.warning("Arquivo bruto não encontrado. Usando base processada com menos colunas de nota.")
        return pd.read_csv(processed_path)

    st.error(f"Arquivo de dados não encontrado em: {raw_path} nem {processed_path}")
    st.stop()


@st.cache_data
def load_course_lookup():
    project_root = Path(__file__).resolve().parents[1]
    lookup_path = project_root / "data" / "raw" / "metadata" / "cursos_ufjf2022.csv"

    if not lookup_path.exists():
        return {}

    course_df = None
    for encoding in ["utf-8", "latin1"]:
        try:
            course_df = pd.read_csv(lookup_path, encoding=encoding)
            break
        except Exception:
            continue

    if course_df is None:
        return {}

    code_col = next((col for col in ["codigo", "código", "c�digo", "CO_CURSO"] if col in course_df.columns), None)
    name_col = next((col for col in ["Curso", "NO_CURSO"] if col in course_df.columns), None)
    if code_col is None or name_col is None:
        return {}

    lookup = {}
    for _, row in course_df[[code_col, name_col]].dropna().iterrows():
        lookup[str(row[code_col]).strip()] = str(row[name_col]).strip()
    return lookup


df = load_data()
course_lookup = load_course_lookup()

st.sidebar.header("Filtros")

course_col = next((col for col in ["NO_CURSO", "CO_CURSO"] if col in df.columns), None)
if course_col is None:
    st.error("Nenhuma coluna de curso foi encontrada. Esperado: NO_CURSO ou CO_CURSO.")
    st.stop()

if course_col == "CO_CURSO" and course_lookup:
    ufjf_codes = set(course_lookup.keys())
    df = df[df[course_col].astype(str).isin(ufjf_codes)].copy()

lista_cursos = sorted(df[course_col].dropna().astype(str).unique())

if course_col == "CO_CURSO" and course_lookup:
    curso_selecionado = st.sidebar.selectbox(
        "Selecione o Curso para Análise",
        lista_cursos,
        format_func=lambda code: f"{code} - {course_lookup.get(code, 'Nome não encontrado')}",
    )
    curso_label = f"{curso_selecionado} - {course_lookup.get(curso_selecionado, 'Nome não encontrado')}"
else:
    curso_selecionado = st.sidebar.selectbox("Selecione o Curso para Análise", lista_cursos)
    curso_label = curso_selecionado

df_course = df[df[course_col].astype(str) == curso_selecionado]

notas_cols_desejadas = ["NT_FG_D1_CT", "NT_FG_D2_CT", "NT_CE_D1", "NT_CE_D2", "NT_CE_D3", "NT_GER"]
notas_cols = [col for col in notas_cols_desejadas if col in df.columns]

if not notas_cols:
    st.error("Nenhuma coluna de nota foi encontrada no dataset para comparar desempenho.")
    st.stop()

label_nota = {
    "NT_FG_D1_CT": "Discursiva geral número 1",
    "NT_FG_D2_CT": "Discursiva geral número 2",
    "NT_CE_D1": "Discursiva específica número 1",
    "NT_CE_D2": "Discursiva específica número 2",
    "NT_CE_D3": "Discursiva específica número 3",
    "NT_GER": "Nota Geral",
}

comp_raw = pd.DataFrame(
    {
        "Curso": df_course[notas_cols].mean(),
        "Media UFJF": df[notas_cols].mean(),
    }
)
comp_raw["Diff_Percent"] = ((comp_raw["Curso"] - comp_raw["Media UFJF"]) / comp_raw["Media UFJF"]) * 100
comp_raw = comp_raw.sort_values(by="Diff_Percent")

comp = comp_raw.copy()
comp.index = [label_nota.get(indicador, indicador) for indicador in comp.index]

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader(f"Métricas: {curso_label}")
    st.write(f"Total de alunos: {len(df_course)}")
    st.dataframe(comp.style.format("{:.2f}"))

with col2:
    st.subheader("Gráfico de métricas (%)")
    plot_df = comp_raw.reset_index().rename(columns={"index": "IndicadorCodigo"})
    plot_df["Indicador"] = plot_df["IndicadorCodigo"].apply(lambda x: label_nota.get(x, x))
    plot_df["Status"] = plot_df["Diff_Percent"].apply(lambda x: "Abaixo da média" if x < 0 else "Acima da média")

    bars = alt.Chart(plot_df).mark_bar(cornerRadiusEnd=5).encode(
        x=alt.X("Diff_Percent:Q", title="Diferença (%) em relação à média UFJF"),
        y=alt.Y("IndicadorCodigo:N", sort="x", title="Código da variável"),
        color=alt.Color(
            "Status:N",
            scale=alt.Scale(domain=["Abaixo da média", "Acima da média"], range=["#e74c3c", "#27ae60"]),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("IndicadorCodigo:N", title="Código"),
            alt.Tooltip("Indicador:N", title="Indicador"),
            alt.Tooltip("Curso:Q", format=".2f", title="Curso"),
            alt.Tooltip("Media UFJF:Q", format=".2f", title="Média UFJF"),
            alt.Tooltip("Diff_Percent:Q", format=".2f", title="Diferença (%)"),
        ],
    )

    labels_pos = (
        alt.Chart(plot_df)
        .transform_filter("datum.Diff_Percent >= 0")
        .mark_text(baseline="middle", color="#111", align="left", dx=6)
        .encode(
            x="Diff_Percent:Q",
            y=alt.Y("IndicadorCodigo:N", sort="x"),
            text=alt.Text("Diff_Percent:Q", format=".1f"),
        )
    )

    labels_neg = (
        alt.Chart(plot_df)
        .transform_filter("datum.Diff_Percent < 0")
        .mark_text(baseline="middle", color="#111", align="right", dx=-6)
        .encode(
            x="Diff_Percent:Q",
            y=alt.Y("IndicadorCodigo:N", sort="x"),
            text=alt.Text("Diff_Percent:Q", format=".1f"),
        )
    )

    zero_line = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="black", strokeDash=[6, 4]).encode(x="x:Q")
    st.altair_chart((bars + labels_pos + labels_neg + zero_line).properties(height=380), use_container_width=True)

st.divider()
st.subheader("Feedback para o curso")

def classificar_competencia(indicador_codigo):
    codigo = str(indicador_codigo).upper()
    if codigo.startswith("NT_FG"):
        return "FG"
    if "OBJ" in codigo or "_O" in codigo:
        return "OBJ"
    if "_D" in codigo:
        return "DIS"
    return "GERAL"


def recomendacao_por_competencia(tipo_competencia):
    if tipo_competencia == "DIS":
        return (
            "Sugestão: implementar oficinas de escrita acadêmica, treino de argumentação técnica "
            "e aplicação recorrente de provas dissertativas ao longo do semestre."
        )
    if tipo_competencia == "OBJ":
        return (
            "Sugestão: reforçar simulados no formato Enade e revisões focadas nos conceitos centrais "
            "da grade curricular."
        )
    if tipo_competencia == "FG":
        return (
            "Sugestão: promover debates sobre atualidades, atividades interdisciplinares e exercícios "
            "de interpretação de texto."
        )
    return "Sugestão: monitorar esse eixo e ajustar as estratégias didáticas conforme os resultados por disciplina."


feedback_df = comp_raw.reset_index().rename(columns={"index": "IndicadorCodigo"})
feedback_df["Indicador"] = feedback_df["IndicadorCodigo"].apply(lambda x: label_nota.get(x, x))
feedback_df["TipoCompetencia"] = feedback_df["IndicadorCodigo"].apply(classificar_competencia)

indicador_melhor_codigo = comp_raw["Diff_Percent"].idxmax()
indicador_melhor = label_nota.get(indicador_melhor_codigo, indicador_melhor_codigo)
diff_melhor = comp_raw.loc[indicador_melhor_codigo, "Diff_Percent"]

negativos = feedback_df[feedback_df["Diff_Percent"] < 0].copy()

if not negativos.empty:
    indicador_critico_idx = negativos["Diff_Percent"].idxmin()
    indicador_critico = negativos.loc[indicador_critico_idx]
    
    st.warning(
        (
            f"Ponto crítico identificado: {indicador_critico['Indicador']} apresenta desempenho "
            f"{indicador_critico['Diff_Percent']:.1f}% abaixo da média UFJF.\n\n"
            f"Sugestão: implementar oficinas de escrita acadêmica, treino de argumentação técnica "
            f"e aplicação recorrente de provas dissertativas ao longo do semestre, com foco em "
            f"fortalecer as competências relacionadas a {indicador_critico['Indicador'].lower()}."
        )
    )
else:
    st.success("Não foram detectados desvios negativos nas métricas comparadas com a média UFJF.")

st.markdown("**Pontos críticos por gravidade**")

alerta_critico = feedback_df[feedback_df["Diff_Percent"] < -10].sort_values("Diff_Percent")
ponto_atencao = feedback_df[(feedback_df["Diff_Percent"] <= -1) & (feedback_df["Diff_Percent"] >= -9.9)].sort_values(
    "Diff_Percent"
)

if not alerta_critico.empty:
    st.error("Alerta Crítico (abaixo de -10%): necessidade de intervenção imediata da coordenação.")
    st.markdown(
        "\n".join(
            [
                f"- {row.Indicador} ({row.IndicadorCodigo}): {row.Diff_Percent:.1f}% em relação à média UFJF."
                for row in alerta_critico.itertuples()
            ]
        )
    )

if not ponto_atencao.empty:
    st.info("Ponto de Atenção (entre -1% e -9.9%): área que precisa de ajustes finos nas disciplinas relacionadas.")
    st.markdown(
        "\n".join(
            [
                f"- {row.Indicador} ({row.IndicadorCodigo}): {row.Diff_Percent:.1f}% em relação à média UFJF."
                for row in ponto_atencao.itertuples()
            ]
        )
    )

if alerta_critico.empty and ponto_atencao.empty:
    st.success("Nenhum ponto entrou nas faixas de gravidade definidas para alerta no momento.")

    

st.caption(
    f"Melhor destaque atual: {indicador_melhor}, com desempenho {diff_melhor:.1f}% em relação à média UFJF."
)