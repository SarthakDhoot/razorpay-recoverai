# 💳 RecoverAI

### AI-Powered Payment Revenue Recovery Platform

RecoverAI is an AI-powered payment recovery platform designed to help businesses identify failed payments, estimate recovery opportunities, prioritize customers, and execute recovery workflows.

The platform combines payment analytics, recovery scoring, AI-generated recovery strategies, an AI decision engine, and Supabase-powered recovery tracking into a single Streamlit dashboard.

---

## 🚀 Features

### 📊 Recovery Dashboard
- Revenue at risk
- Potential recovery
- Recovered revenue
- Recovery rate
- Failed payment statistics
- Recovery priority distribution
- Top recovery opportunities

### 💳 Payment Management
- View payment transactions
- Identify failed payments
- Analyze payment failure reasons
- View payment methods and recovery status

### 🤖 AI Recovery Center
- Recovery probability calculation
- Payment priority classification
- Recommended recovery actions
- AI-generated customer recovery messages
- AI-generated recovery strategies
- AI decision engine

### 🧠 AI Decision Engine

RecoverAI evaluates:

- Payment amount
- Failure reason
- Payment method
- Recovery probability
- Potential recovery
- Priority score

It then recommends the most suitable business action and timing.

### 🗄️ Supabase Integration

Recovery actions are stored in Supabase, allowing the application to track:

- Recovery attempts
- Recovered payments
- Recovery activity
- Payment recovery history

### 📈 Analytics

The analytics dashboard provides:

- Failure reason analysis
- Payment status distribution
- Recovery status distribution
- Priority distribution
- Recovery opportunity analysis
- Database recovery activity

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Streamlit | Web dashboard |
| Pandas | Data processing |
| Supabase | Database |
| PostgreSQL | Persistent data storage |
| OpenAI API | AI strategy and decision generation |
| Git & GitHub | Version control |

---

## 📁 Project Structure

```text
razorpay-recoverai/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── app/
│   └── data/
│       └── payments.csv
│
└── services/
    ├── database.py
    ├── llm_agent.py
    ├── opportunity.py
    ├── priority.py
    ├── recovery_ai.py
    └── recovery_workflow.py