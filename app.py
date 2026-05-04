"""
Sovos Invoice Validator
Entry point for the Streamlit app.
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import tempfile
import os
from validator import validate_csv
from dashboard import chart_valid_vs_invalid, chart_error_frequency, chart_invoices_by_date
from ai_assistant import ask_assistant, init_chat_history

st.set_page_config(
    page_title="Sovos Invoice Validator",
    page_icon="🧾",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────

st.title("🧾 Sovos Invoice Validator")
st.caption("Upload a CSV file to validate your invoices against compliance rules.")
st.divider()

# ── File uploader ─────────────────────────────────────────────────────────────

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    help="Upload an invoice file exported from your ERP system."
)

if not uploaded_file:
    st.info("👆 Upload a CSV file to get started.")
    st.stop()

# ── Run validation ────────────────────────────────────────────────────────────

with st.spinner("Validating invoices..."):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    report = validate_csv(tmp_path)
    os.unlink(tmp_path)

if "error" in report:
    st.error(f"Error reading file: {report['error']}")
    st.stop()

# ── Build rows_display (shared between tabs) ──────────────────────────────────

seen_ids = set()
rows_display = []
for row_num, row in report["rows"]:
    inv_id = str(row.get("invoice_id", "")).strip() or f"row_{row_num}"
    display_id = inv_id if inv_id not in seen_ids else f"{inv_id} (row {row_num})"
    seen_ids.add(inv_id)

    has_errors = inv_id in report["errors"]
    errors = report["errors"].get(inv_id, [])
    error_summary = "; ".join(
        err.split("|")[0].strip() for err in errors
    ) if errors else ""

    rows_display.append({
        "Status":     "❌ Invalid" if has_errors else "✅ Valid",
        "Invoice ID": display_id,
        "Vendor":     row.get("vendor_name", ""),
        "Customer":   row.get("customer_name", ""),
        "Date":       row.get("issue_date", ""),
        "Total":      row.get("total", ""),
        "Currency":   row.get("currency", ""),
        "Errors":     error_summary,
    })

# ── Metrics ───────────────────────────────────────────────────────────────────

st.subheader("Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Invoices", report["total"])
col2.metric("Valid",          report["valid"])
col3.metric("Invalid",        report["invalid"],
            delta=f"-{report['invalid']}" if report["invalid"] > 0 else None,
            delta_color="inverse")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["📋 Results", "📊 Dashboard", "🤖 AI Assistant"])

# ── Tab 1: Results ────────────────────────────────────────────────────────────

with tab1:
    st.subheader("Invoice Results")

    df = pd.DataFrame(rows_display)

    status_filter = st.selectbox(
        "Filter by status",
        ["All", "Valid", "Invalid"]
    )

    df_filtered = df.copy()
    if status_filter == "Valid":
        df_filtered = df[df["Status"].str.contains("Valid")]
    elif status_filter == "Invalid":
        df_filtered = df[df["Status"].str.contains("Invalid")]

    def highlight_invalid(row):
        if "Invalid" in str(row["Status"]):
            return ["background-color: #2d1b1b"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_filtered.style.apply(highlight_invalid, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    if report["errors"]:
        st.subheader("Error Detail")
        for inv_id, errors in report["errors"].items():
            with st.expander(f"❌ {inv_id} — {len(errors)} error(s)"):
                for err in errors:
                    parts = err.split("|")
                    error_type = parts[0].strip()
                    detail     = parts[1].strip() if len(parts) > 1 else ""
                    st.markdown(f"**{error_type}** — `{detail}`")

        st.divider()

    st.subheader("Export Report")
    csv_export = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download report as CSV",
        data=csv_export,
        file_name=f"validation_report_{uploaded_file.name}",
        mime="text/csv",
    )

# ── Tab 2: Dashboard ──────────────────────────────────────────────────────────

with tab2:
    st.subheader("Validation Dashboard")

    if report["total"] == 0:
        st.warning("No data to display.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            fig_donut = chart_valid_vs_invalid(report)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col2:
            fig_bars = chart_error_frequency(report)
            if fig_bars:
                st.plotly_chart(fig_bars, use_container_width=True)
            else:
                st.success("No errors found in this file.")

        fig_timeline = chart_invoices_by_date(rows_display)
        if fig_timeline:
            st.plotly_chart(fig_timeline, use_container_width=True)

# ── Tab 3: AI Assistant ───────────────────────────────────────────────────────

with tab3:
    st.subheader("🤖 AI Implementation Assistant")
    st.caption("Ask me anything about your validation results, error fixes, or compliance rules.")

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = init_chat_history()

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("Ask about your invoices or compliance rules...")

    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Build messages list without the initial assistant message
                    messages = [
                        m for m in st.session_state.chat_history
                        if not (m["role"] == "assistant" and "Hi! I'm your Sovos" in m["content"])
                    ]

                    response = ask_assistant(messages, report=report)
                    st.markdown(response)

                    # Add response to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    error_msg = f"⚠️ Error connecting to AI: {str(e)}"
                    st.error(error_msg)

    # Clear chat button
    if st.button("🗑️ Clear chat"):
        st.session_state.chat_history = init_chat_history()
        st.rerun()