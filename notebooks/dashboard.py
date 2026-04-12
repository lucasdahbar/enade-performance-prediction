import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title="Dashboard - Insights Enade", layout="wide")
st.title("Painel de Insights Enade 2022 - UFJF")
st.markdown("Este dashboard apresenta a performance comparativa dos cursos em relacao a media da universidade.")


@st.cache_data
def load_data():
    project_root = Path(__file__).resolve().parents[1]
    raw_path = project_root / "data" / "raw" / "cursos_ufjf_enade2022.csv"
    processed_path = project_root / "data" / "processed" / "enade_ufjf_2022_model.csv"

    if raw_path.exists():
        return pd.read_csv(raw_path)

    if processed_path.exists():
        st.warning("Arquivo bruto nao encontrado. Usando base processada com menos colunas de nota.")
        return pd.read_csv(processed_path)

    st.error(f"Arquivo de dados nao encontrado em: {raw_path} nem {processed_path}")
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
        "Selecione o Curso para Analise",
        lista_cursos,
        format_func=lambda code: f"{code} - {course_lookup.get(code, 'Nome nao encontrado')}",
    )
    curso_label = f"{curso_selecionado} - {course_lookup.get(curso_selecionado, 'Nome nao encontrado')}"
else:
    curso_selecionado = st.sidebar.selectbox("Selecione o Curso para Analise", lista_cursos)
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
    st.subheader(f"Metricas: {curso_label}")
    st.write(f"Total de alunos: {len(df_course)}")
    st.dataframe(comp.style.format("{:.2f}"))

with col2:
    st.subheader("Gargalos de Desempenho (%)")
    plot_df = comp_raw.reset_index().rename(columns={"index": "IndicadorCodigo"})
    plot_df["Indicador"] = plot_df["IndicadorCodigo"].apply(lambda x: label_nota.get(x, x))
    plot_df["Status"] = plot_df["Diff_Percent"].apply(lambda x: "Abaixo da media" if x < 0 else "Acima da media")

    bars = alt.Chart(plot_df).mark_bar(cornerRadiusEnd=5).encode(
        x=alt.X("Diff_Percent:Q", title="Diferenca (%) em relacao a media UFJF"),
        y=alt.Y("IndicadorCodigo:N", sort="x", title="Codigo da variavel"),
        color=alt.Color(
            "Status:N",
            scale=alt.Scale(domain=["Abaixo da media", "Acima da media"], range=["#e74c3c", "#27ae60"]),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("IndicadorCodigo:N", title="Codigo"),
            alt.Tooltip("Indicador:N", title="Indicador"),
            alt.Tooltip("Curso:Q", format=".2f", title="Curso"),
            alt.Tooltip("Media UFJF:Q", format=".2f", title="Media UFJF"),
            alt.Tooltip("Diff_Percent:Q", format=".2f", title="Diferenca (%)"),
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
st.subheader("Conclusao do Algoritmo")
maior_gargalo = comp.index[0]
if comp.loc[maior_gargalo, "Diff_Percent"] < 0:
    st.warning(
        f"O principal ponto de atencao identificado e {maior_gargalo}, com desempenho {comp.loc[maior_gargalo, 'Diff_Percent']:.1f}% abaixo da media."
    )
else:
    st.success("O curso esta performando acima da media em todos os indicadores principais.")