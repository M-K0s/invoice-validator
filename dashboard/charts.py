"""
Plotly charts for the validation dashboard.
Implemented in v0.4.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def chart_valid_vs_invalid(report):
    """Donut chart: valid vs invalid invoices."""
    labels = ["Valid", "Invalid"]
    values = [report["valid"], report["invalid"]]
    colors = ["#2ecc71", "#e74c3c"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors),
        textinfo="label+percent",
        hovertemplate="%{label}: %{value} invoices<extra></extra>",
    )])

    fig.update_layout(
        title="Valid vs Invalid Invoices",
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(t=60, b=20, l=20, r=20),
    )
    return fig


def chart_error_frequency(report):
    """Bar chart: most frequent error types."""
    error_counts = {}

    for errors in report["errors"].values():
        for err in errors:
            error_type = err.split("|")[0].strip()
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

    if not error_counts:
        return None

    df = pd.DataFrame(
        sorted(error_counts.items(), key=lambda x: x[1], reverse=True),
        columns=["Error Type", "Count"]
    )

    fig = px.bar(
        df,
        x="Count",
        y="Error Type",
        orientation="h",
        color="Count",
        color_continuous_scale=["#e67e22", "#e74c3c"],
        text="Count",
    )

    fig.update_layout(
        title="Error Frequency by Type",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(t=60, b=20, l=20, r=20),
        yaxis=dict(autorange="reversed"),
    )
    fig.update_traces(textposition="outside")
    return fig


def chart_invoices_by_date(rows_display):
    """Line chart: number of invoices per issue date."""
    df = pd.DataFrame(rows_display)

    if "Date" not in df.columns or df["Date"].isnull().all():
        return None

    df = df[df["Date"].str.match(r"\d{4}-\d{2}-\d{2}", na=False)]
    df["Date"] = pd.to_datetime(df["Date"])
    daily = df.groupby("Date").size().reset_index(name="Count")

    fig = px.line(
        daily,
        x="Date",
        y="Count",
        markers=True,
        line_shape="spline",
    )

    fig.update_traces(
        line=dict(color="#3498db", width=2),
        marker=dict(size=8, color="#3498db"),
    )

    fig.update_layout(
        title="Invoices by Issue Date",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(t=60, b=20, l=20, r=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
    )
    return fig