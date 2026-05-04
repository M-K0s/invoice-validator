# 🧾 Invoice Validator

A web-based invoice validation tool with an AI-powered assistant, built to simulate real-world ERP compliance workflows. Developed as a portfolio project to demonstrate technical consulting, data validation, and AI integration skills.

---

## What It Does

Companies that use ERP systems (like SAP or Oracle) need to export invoice data and send it to tax compliance platforms. During that process, data often arrives with errors — missing fields, incorrect formats, or amounts that don't add up.

This tool:
- Accepts invoice files in **CSV or XML** format
- Validates them against **8 compliance rules** (structural + business logic)
- Displays results in an **interactive web dashboard**
- Provides an **AI assistant** (powered by Claude) that explains errors and suggests fixes in natural language

---

## Features

| Feature | Description |
|---|---|
| CSV & XML validation | Upload files exported from any ERP system |
| 8 validation rules | Required fields, date formats, positive amounts, duplicate IDs, math totals, date logic, currency codes, tax rates |
| Results table | Color-coded rows with error details and filter by status |
| Validation dashboard | Donut chart, error frequency bar chart, invoice timeline |
| AI Assistant | Claude-powered chatbot with context of the current validation report |
| Export report | Download full validation results as CSV |

---

## Validation Rules

### Structural Rules (v0.1)
| Rule | Description |
|---|---|
| Required Fields | All mandatory fields must be present and non-empty |
| Date Format | Dates must follow `YYYY-MM-DD` (ISO 8601) |
| Positive Amounts | Subtotal, tax amount, and total must be non-negative numbers |
| Unique IDs | Each `invoice_id` must be unique within the file |

### Business Rules (v0.2)
| Rule | Description |
|---|---|
| Total Math | `total` must equal `subtotal + tax_amount` (±$0.02 tolerance) |
| Date Logic | `due_date` must be after `issue_date` |
| Valid Currency | Currency must be `ARS`, `USD`, or `EUR` (ISO 4217) |
| Valid Tax Rate | Tax rate must be `0%`, `10.5%`, or `21%` (Argentine IVA rates) |

---

## Tech Stack

- **Python 3.8+**
- **Streamlit** — web interface
- **pandas** — CSV parsing and data manipulation
- **lxml / xmltodict** — XML parsing
- **Plotly** — interactive charts
- **Anthropic Claude API** — AI assistant
- **python-dotenv** — environment variable management

---

## Project Structure

```
invoice-validator/
├── app.py                  ← Streamlit entry point
├── requirements.txt
├── .env.example            ← API key template
├── validator/
│   ├── rules.py            ← All validation rules
│   ├── csv_validator.py    ← CSV validation logic + CLI
│   └── xml_validator.py    ← XML validation (v0.2+)
├── dashboard/
│   ├── charts.py           ← Plotly visualizations
│   └── exporter.py         ← Report export
├── ai_assistant/
│   ├── claude_client.py    ← Anthropic API client
│   └── prompts.py          ← System prompts and context builder
└── data/samples/
    ├── facturas_validas.csv
    ├── facturas_con_errores.csv
    └── factura_ejemplo.xml
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/M-K0s/invoice-validator.git
cd invoice-validator
```

### 2. Create and activate virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_key_here
```

Get your API key at [console.anthropic.com](https://console.anthropic.com)

### 5. Run the app

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

---

## CLI Usage

You can also run the validator directly from the terminal without the UI:

```bash
python -m validator.csv_validator data/samples/facturas_validas.csv
python -m validator.csv_validator data/samples/facturas_con_errores.csv
```

---

## Sample Data

The `data/samples/` folder includes three test files:

- **`facturas_validas.csv`** — 10 invoices that pass all validation rules
- **`facturas_con_errores.csv`** — 10 invoices with 8 different error types intentionally included
- **`factura_ejemplo.xml`** — A single XML invoice in AFIP-compatible format

---

## Security

- API keys are stored in `.env` and never committed to Git
- `.env` is listed in `.gitignore`
- Use `.env.example` as a template — it contains no sensitive data

---

## Roadmap

- [x] CSV validation with 8 rules
- [x] Web interface with Streamlit
- [x] Interactive dashboard with Plotly
- [x] AI assistant with Claude API
- [ ] Full XML validation
- [ ] Streamlit Cloud deployment
- [ ] Support for additional tax jurisdictions (Brazil, Mexico)
- [ ] Batch processing for multiple files

---

## Author

Built by [@M-K0s](https://github.com/M-K0s) as a portfolio project for a Technical Consultant Intern role in the Professional Services / tax compliance domain.
