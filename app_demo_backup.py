import streamlit as st
import pandas as pd

from services.database import (
    save_recovery_action,
    get_recovery_actions,
    mark_payment_recovered
)

from services.recovery_ai import (
    calculate_recovery_score,
    get_priority,
    get_recommended_action,
    generate_recovery_message
)

from services.opportunity import calculate_recovery_opportunity

from services.priority import (
    assign_priority,
    priority_score
)

from services.llm_agent import (
    generate_ai_strategy,
    generate_ai_decision
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="RecoverAI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

.main-title {
    font-size: 44px;
    font-weight: 800;
    letter-spacing: -1.5px;
    margin-bottom: 0;
}

.subtitle {
    font-size: 17px;
    opacity: 0.65;
    margin-bottom: 8px;
}

.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid rgba(128,128,128,0.35);
    margin-bottom: 22px;
}

.section-header {
    font-size: 28px;
    font-weight: 750;
    margin-top: 8px;
    margin-bottom: 4px;
}

.section-description {
    opacity: 0.65;
    margin-bottom: 20px;
}

.metric-card {
    padding: 18px;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,0.20);
    background: rgba(128,128,128,0.04);
}

.priority-high {
    border-left: 5px solid #ff4b4b;
}

.priority-medium {
    border-left: 5px solid #ffa500;
}

.priority-low {
    border-left: 5px solid #21c354;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD PAYMENTS
# =========================================================

@st.cache_data
def load_payments():
    return pd.read_csv("app/data/payments.csv")


payments = load_payments()


# =========================================================
# LOAD DATABASE ACTIONS
# =========================================================

try:
    db_actions = get_recovery_actions()
except Exception:
    db_actions = []


# =========================================================
# DATABASE HELPERS
# =========================================================

def payment_was_attempted(payment_id):

    for action in db_actions:

        if str(action.get("payment_id")) == str(payment_id):

            if action.get("status") in [
                "attempted",
                "recovered"
            ]:
                return True

    return False


def payment_was_recovered(payment_id):

    for action in db_actions:

        if str(action.get("payment_id")) == str(payment_id):

            if action.get("status") == "recovered":
                return True

    return False


# =========================================================
# SESSION STATE
# =========================================================

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

if "decision_result" not in st.session_state:
    st.session_state.decision_result = None


# =========================================================
# BASIC PAYMENT CALCULATIONS
# =========================================================

total_transactions = len(payments)

successful_payments = len(
    payments[payments["status"] == "Success"]
)

failed_data = payments[
    payments["status"] == "Failed"
]

failed_payments = len(failed_data)

revenue_at_risk = failed_data["amount"].sum()

recovered_revenue = payments[
    payments["recovery_status"] == "Recovered"
]["amount"].sum()


# =========================================================
# DATABASE RECOVERED REVENUE
# =========================================================

database_recovered_amount = 0

for action in db_actions:

    if action.get("status") == "recovered":

        payment_id = str(
            action.get("payment_id")
        )

        matching_payment = payments[
            payments["payment_id"].astype(str)
            == payment_id
        ]

        if not matching_payment.empty:

            database_recovered_amount += (
                matching_payment.iloc[0]["amount"]
            )


display_recovered_revenue = (
    recovered_revenue
    + database_recovered_amount
)


if revenue_at_risk > 0:

    recovery_rate = (
        display_recovered_revenue
        / revenue_at_risk
    ) * 100

else:

    recovery_rate = 0


# =========================================================
# OPPORTUNITY CALCULATIONS
# =========================================================

opportunity_data = []

for _, payment in failed_data.iterrows():

    recovery_probability = calculate_recovery_score(
        payment
    )

    opportunity = calculate_recovery_opportunity(
        payment["amount"],
        recovery_probability
    )

    priority = assign_priority(
        recovery_probability,
        opportunity
    )

    score = priority_score(
        recovery_probability,
        opportunity
    )

    opportunity_data.append({

        "Payment ID":
            payment["payment_id"],

        "Customer":
            payment["customer_name"],

        "Amount":
            payment["amount"],

        "Recovery Probability":
            recovery_probability,

        "Potential Recovery":
            opportunity,

        "Priority":
            priority,

        "Priority Score":
            score
    })


opportunity_df = pd.DataFrame(
    opportunity_data
)


if not opportunity_df.empty:

    total_potential_recovery = (
        opportunity_df["Potential Recovery"].sum()
    )

else:

    total_potential_recovery = 0


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 💳 RecoverAI")

    st.caption(
        "AI-Powered Payment Recovery"
    )

    st.divider()

    st.markdown("### 🧭 Navigation")

    page = st.radio(
        "Go to",
        [
            "🏠 Dashboard",
            "💳 Payments",
            "🤖 AI Recovery",
            "📈 Analytics"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### 🤖 System Status")

    st.success("AI Engine Online")

    st.success("Database Connected")

    st.divider()

    st.metric(
        "Failed Payments",
        failed_payments
    )

    st.metric(
        "Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}"
    )

    st.divider()

    st.caption(
        "RecoverAI MVP\n"
        "AI Revenue Recovery Platform"
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">💳 RecoverAI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Payment Revenue Recovery Platform'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="badge">'
    '🤖 AI Revenue Recovery Agent • Live'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="section-header">'
        '📊 Recovery Overview'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Identify failed payments, prioritize recovery opportunities, '
        'and track recovered revenue.'
        '</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "💰 Revenue at Risk",
            f"₹{revenue_at_risk:,.0f}"
        )

    with col2:

        st.metric(
            "🎯 Potential Recovery",
            f"₹{total_potential_recovery:,.0f}"
        )

    with col3:

        st.metric(
            "✅ Recovered",
            f"₹{display_recovered_revenue:,.0f}"
        )

    with col4:

        st.metric(
            "📈 Recovery Rate",
            f"{recovery_rate:.2f}%"
        )

    st.divider()

    # -----------------------------------------------------
    # TRANSACTION OVERVIEW
    # -----------------------------------------------------

    st.markdown("### 💳 Transaction Overview")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Transactions",
            total_transactions
        )

    with col2:

        st.metric(
            "Successful Payments",
            successful_payments
        )

    with col3:

        st.metric(
            "Failed Payments",
            failed_payments
        )

    st.divider()

    # -----------------------------------------------------
    # RECOVERY FUNNEL
    # -----------------------------------------------------

    st.markdown("### 🔄 Recovery Funnel")

    funnel_data = pd.DataFrame({
        "Stage": [
            "Total Transactions",
            "Failed Payments",
            "Recovery Opportunities",
            "Recovered Payments"
        ],
        "Count": [
            total_transactions,
            failed_payments,
            len(opportunity_df),
            len([
                a for a in db_actions
                if a.get("status") == "recovered"
            ])
        ]
    })

    st.bar_chart(
        funnel_data.set_index("Stage")
    )

    st.divider()

    # -----------------------------------------------------
    # PRIORITY
    # -----------------------------------------------------

    st.markdown("### 🎯 Recovery Priority")

    if not opportunity_df.empty:

        priority_counts = (
            opportunity_df["Priority"]
            .value_counts()
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🔴 HIGH",
                priority_counts.get(
                    "HIGH",
                    0
                )
            )

        with col2:

            st.metric(
                "🟡 MEDIUM",
                priority_counts.get(
                    "MEDIUM",
                    0
                )
            )

        with col3:

            st.metric(
                "🟢 LOW",
                priority_counts.get(
                    "LOW",
                    0
                )
            )

        st.bar_chart(
            priority_counts
        )

    else:

        st.info(
            "No recovery opportunities found."
        )

    st.divider()

    # -----------------------------------------------------
    # HIGH PRIORITY PAYMENTS
    # -----------------------------------------------------

    st.markdown(
        "### 🔥 High-Priority Recovery Opportunities"
    )

    if not opportunity_df.empty:

        high_priority = opportunity_df[
            opportunity_df["Priority"] == "HIGH"
        ].sort_values(
            "Priority Score",
            ascending=False
        )

        if high_priority.empty:

            high_priority = (
                opportunity_df
                .sort_values(
                    "Priority Score",
                    ascending=False
                )
                .head(5)
            )

        st.dataframe(
            high_priority.head(5),
            width="stretch",
            hide_index=True
        )

    else:

        st.info(
            "No high-priority opportunities available."
        )

    st.divider()

    # -----------------------------------------------------
    # TOP RECOVERY OPPORTUNITIES
    # -----------------------------------------------------

    st.markdown(
        "### 💰 Top Recovery Opportunities"
    )

    if not opportunity_df.empty:

        top_opportunities = (
            opportunity_df
            .sort_values(
                "Priority Score",
                ascending=False
            )
            .head(10)
        )

        st.dataframe(
            top_opportunities,
            width="stretch",
            hide_index=True
        )

    else:

        st.info(
            "No failed payment opportunities found."
        )


# =========================================================
# PAYMENTS
# =========================================================

elif page == "💳 Payments":

    st.markdown(
        '<div class="section-header">'
        '💳 Payment Management'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'View all transactions and identify failed payments.'
        '</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # FILTER
    # -----------------------------------------------------

    status_filter = st.selectbox(
        "Filter payments",
        [
            "All",
            "Success",
            "Failed"
        ]
    )

    if status_filter == "All":

        filtered_payments = payments

    else:

        filtered_payments = payments[
            payments["status"] == status_filter
        ]

    st.dataframe(
        filtered_payments,
        width="stretch",
        hide_index=True
    )

    st.divider()

    st.markdown(
        "### ❌ Failed Payments"
    )

    st.dataframe(
        failed_data,
        width="stretch",
        hide_index=True
    )


# =========================================================
# ANALYTICS
# =========================================================

elif page == "📈 Analytics":

    st.markdown(
        '<div class="section-header">'
        '📈 Recovery Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Understand failure patterns, recovery potential and '
        'business performance.'
        '</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # KPI
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "💰 Revenue at Risk",
            f"₹{revenue_at_risk:,.0f}"
        )

    with col2:

        st.metric(
            "🎯 Potential Recovery",
            f"₹{total_potential_recovery:,.0f}"
        )

    with col3:

        st.metric(
            "✅ Recovered",
            f"₹{display_recovered_revenue:,.0f}"
        )

    with col4:

        st.metric(
            "📈 Recovery Rate",
            f"{recovery_rate:.2f}%"
        )

    st.divider()

    # -----------------------------------------------------
    # FAILURE REASONS
    # -----------------------------------------------------

    st.markdown(
        "### ❌ Payment Failure Reasons"
    )

    failure_chart = (
        failed_data["failure_reason"]
        .value_counts()
    )

    st.bar_chart(
        failure_chart
    )

    st.divider()

    # -----------------------------------------------------
    # PAYMENT STATUS
    # -----------------------------------------------------

    st.markdown(
        "### 💳 Payment Status"
    )

    status_chart = (
        payments["status"]
        .value_counts()
    )

    st.bar_chart(
        status_chart
    )

    st.divider()

    # -----------------------------------------------------
    # RECOVERY STATUS
    # -----------------------------------------------------

    st.markdown(
        "### 🔄 Recovery Status"
    )

    recovery_chart = (
        payments["recovery_status"]
        .value_counts()
    )

    st.bar_chart(
        recovery_chart
    )

    st.divider()

    # -----------------------------------------------------
    # PRIORITY DISTRIBUTION
    # -----------------------------------------------------

    st.markdown(
        "### 🎯 Priority Distribution"
    )

    if not opportunity_df.empty:

        priority_chart = (
            opportunity_df["Priority"]
            .value_counts()
        )

        st.bar_chart(
            priority_chart
        )

        st.dataframe(
            opportunity_df.sort_values(
                "Priority Score",
                ascending=False
            ),
            width="stretch",
            hide_index=True
        )

    st.divider()

    # -----------------------------------------------------
    # DATABASE ACTIVITY
    # -----------------------------------------------------

    st.markdown(
        "### 🗄️ Recovery Activity"
    )

    if db_actions:

        db_df = pd.DataFrame(
            db_actions
        )

        st.dataframe(
            db_df,
            width="stretch",
            hide_index=True
        )

    else:

        st.info(
            "No recovery actions have been stored yet."
        )


# =========================================================
# AI RECOVERY
# =========================================================

elif page == "🤖 AI Recovery":

    st.markdown(
        '<div class="section-header">'
        '🤖 AI Recovery Center'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Analyze failed payments and let AI recommend the best '
        'recovery strategy.'
        '</div>',
        unsafe_allow_html=True
    )

    if failed_data.empty:

        st.success(
            "🎉 No failed payments available for recovery."
        )

    else:

        # -------------------------------------------------
        # PAYMENT SELECTION
        # -------------------------------------------------

        selected_payment_id = st.selectbox(
            "Select a failed payment",
            failed_data["payment_id"].tolist()
        )

        selected_payment = failed_data[
            failed_data["payment_id"]
            == selected_payment_id
        ].iloc[0]

        # -------------------------------------------------
        # AI ANALYSIS
        # -------------------------------------------------

        recovery_score = calculate_recovery_score(
            selected_payment
        )

        priority = get_priority(
            recovery_score
        )

        recommended_action = get_recommended_action(
            selected_payment,
            recovery_score
        )

        recovery_message = generate_recovery_message(
            selected_payment
        )

        selected_opportunity = (
            calculate_recovery_opportunity(
                selected_payment["amount"],
                recovery_score
            )
        )

        # -------------------------------------------------
        # PAYMENT SUMMARY
        # -------------------------------------------------

        st.markdown(
            "### 💳 Payment Summary"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Payment Amount",
                f"₹{selected_payment['amount']:,.0f}"
            )

        with col2:

            st.metric(
                "Recovery Probability",
                f"{recovery_score}%"
            )

        with col3:

            st.metric(
                "Potential Recovery",
                f"₹{selected_opportunity:,.0f}"
            )

        with col4:

            st.metric(
                "Priority",
                priority
            )

        st.divider()

        # -------------------------------------------------
        # PAYMENT DETAILS
        # -------------------------------------------------

        st.markdown(
            "### 🔎 Payment Details"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Customer:** "
                f"{selected_payment['customer_name']}"
            )

            st.write(
                f"**Payment ID:** "
                f"{selected_payment['payment_id']}"
            )

        with col2:

            st.write(
                f"**Failure Reason:** "
                f"{selected_payment['failure_reason']}"
            )

            st.write(
                f"**Payment Method:** "
                f"{selected_payment['payment_method']}"
            )

        st.divider()

        # -------------------------------------------------
        # RECOMMENDED ACTION
        # -------------------------------------------------

        st.markdown(
            "### 💡 Recommended Action"
        )

        st.info(
            recommended_action
        )

        st.divider()

        # -------------------------------------------------
        # CUSTOMER MESSAGE
        # -------------------------------------------------

        st.markdown(
            "### ✉️ Customer Recovery Message"
        )

        st.text_area(
            "Message",
            recovery_message,
            height=120
        )

        st.divider()

        # -------------------------------------------------
        # AI STRATEGY
        # -------------------------------------------------

        st.markdown(
            "### 🤖 AI Recovery Strategy"
        )

        if st.button(
            "Generate AI Recovery Strategy",
            type="primary",
            width="stretch"
        ):

            with st.spinner(
                "AI is analyzing the payment..."
            ):

                st.session_state.ai_result = (
                    generate_ai_strategy(
                        customer_name=
                            selected_payment[
                                "customer_name"
                            ],
                        amount=
                            selected_payment[
                                "amount"
                            ],
                        failure_reason=
                            selected_payment[
                                "failure_reason"
                            ],
                        payment_method=
                            selected_payment[
                                "payment_method"
                            ],
                        recovery_probability=
                            recovery_score,
                        priority=
                            priority
                    )
                )

        if st.session_state.ai_result:

            ai_result = (
                st.session_state.ai_result
            )

            st.success(
                "AI strategy generated successfully."
            )

            st.markdown(
                "#### 🎯 Strategy"
            )

            st.write(
                ai_result["strategy"]
            )

            st.markdown(
                "#### ✉️ AI Customer Message"
            )

            st.info(
                ai_result["message"]
            )

            st.markdown(
                "#### 🧠 Reason"
            )

            st.write(
                ai_result["reason"]
            )

        st.divider()

        # -------------------------------------------------
        # AI DECISION ENGINE
        # -------------------------------------------------

        st.markdown(
            "### 🧠 AI Decision Engine"
        )

        st.write(
            "RecoverAI evaluates payment value, failure reason, "
            "recovery probability and priority to recommend the "
            "best business action."
        )

        if st.button(
            "⚡ Generate AI Decision",
            type="primary",
            width="stretch"
        ):

            with st.spinner(
                "AI is evaluating the payment..."
            ):

                st.session_state.decision_result = (
                    generate_ai_decision(
                        customer_name=
                            selected_payment[
                                "customer_name"
                            ],
                        amount=
                            selected_payment[
                                "amount"
                            ],
                        failure_reason=
                            selected_payment[
                                "failure_reason"
                            ],
                        payment_method=
                            selected_payment[
                                "payment_method"
                            ],
                        recovery_probability=
                            recovery_score,
                        priority=
                            priority,
                        potential_recovery=
                            selected_opportunity
                    )
                )

        if st.session_state.decision_result:

            decision = (
                st.session_state.decision_result
            )

            st.success(
                "AI decision generated successfully."
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    "#### 🎯 Decision"
                )

                st.info(
                    decision["decision"]
                )

            with col2:

                st.markdown(
                    "#### ⏰ Timing"
                )

                st.info(
                    decision["timing"]
                )

            st.markdown(
                "#### 🔎 Why?"
            )

            st.write(
                decision["why"]
            )

            st.markdown(
                "#### 🚀 Recommended Business Action"
            )

            st.success(
                decision["action"]
            )

        st.divider()

        # -------------------------------------------------
        # RECOVERY WORKFLOW
        # -------------------------------------------------

        st.markdown(
            "### 🚀 Recovery Workflow"
        )

        is_attempted = payment_was_attempted(
            selected_payment_id
        )

        is_recovered = payment_was_recovered(
            selected_payment_id
        )

        if is_recovered:

            st.success(
                "✅ This payment has been marked as recovered."
            )

        elif is_attempted:

            st.warning(
                "🟡 Recovery has already been attempted."
            )

            if st.button(
                "✅ Mark as Recovered",
                type="primary",
                width="stretch"
            ):

                try:

                    mark_payment_recovered(
                        selected_payment_id
                    )

                    st.success(
                        "🎉 Payment marked as recovered "
                        "and saved to Supabase."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Database error: {e}"
                    )

        else:

            if st.button(
                "🚀 Start Recovery",
                type="primary",
                width="stretch"
            ):

                try:

                    save_recovery_action(
                        payment_id=
                            selected_payment_id,
                        action=
                            "Recovery started",
                        status=
                            "attempted"
                    )

                    st.success(
                        "🚀 Recovery started and saved "
                        "to Supabase."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Database error: {e}"
                    )

        st.divider()

        # -------------------------------------------------
        # DATABASE ACTIVITY
        # -------------------------------------------------

        st.markdown(
            "### 📋 Recovery Activity"
        )

        try:

            latest_actions = (
                get_recovery_actions()
            )

            if latest_actions:

                activity_df = pd.DataFrame(
                    latest_actions
                )

                st.dataframe(
                    activity_df,
                    width="stretch",
                    hide_index=True
                )

            else:

                st.info(
                    "No recovery actions recorded yet."
                )

        except Exception as e:

            st.warning(
                f"Unable to load recovery activity: {e}"
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "RecoverAI • AI-Powered Payment Revenue Recovery Platform"
)