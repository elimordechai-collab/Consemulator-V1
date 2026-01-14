import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרות דף
st.set_page_config(page_title="Consumelator V2 - Dynamic Simulator", layout="wide")

st.title("📊 Consumelator V2 - סימולטור צמיחה דינמי")
st.markdown("---")

# --- תפריט צד (Input - עמודות A עד E מה-Dynamic Form) ---
st.sidebar.header("📋 הזנת נתוני העסק")

with st.sidebar:
    st.subheader("הוצאות קבועות")
    rent = st.number_input("שכירות (חודשי)", value=16100)
    property_tax = st.number_input("ארנונה (חודשי)", value=1400)
    salaries = st.number_input("שכר עובדים", value=13200)
    consumrz_fee = st.number_input("עלות מערכת Consumrz", value=659)
    other_fixed = st.number_input("הוצאות קבועות נוספות", value=23670)
    
    total_fixed_costs = rent + property_tax + salaries + consumrz_fee + other_fixed
    
    st.subheader("נתוני עסקה ורווחיות")
    gp_pct = st.slider("אחוז רווח גולמי", 0.1, 0.8, 0.4, format="%.2f")
    avg_basket = st.number_input("סל ממוצע (כולל מע\"מ)", value=195)
    conversion_rate = st.slider("יחס המרה למועדון (%)", 0.01, 0.5, 0.15)
    
    st.subheader("נתוני צמיחה")
    monthly_traffic = st.number_input("כמות לקוחות אורגנית בחודש", value=806)
    share_rate = st.slider("אחוז משתפים (Referral)", 0.0, 0.1, 0.02)
    freq_multiplier = st.slider("מכפיל תדירות חברי מועדון", 1.0, 3.0, 1.5)

# --- מנוע החישוב ---
def run_simulation():
    data = []
    current_members = 0
    vat = 1.18
    
    for month in range(1, 37):
        # 1. גיוס לקוחות (כולל ויראליות)
        new_from_organic = monthly_traffic * conversion_rate
        referrals = current_members * share_rate * 2
        current_members += (new_from_organic + referrals)
        
        # 2. חישוב הכנסות (אורגני + מועדון)
        organic_rev = (monthly_traffic * (1 - conversion_rate)) * avg_basket
        club_rev = current_members * (avg_basket * freq_multiplier)
        total_rev = organic_rev + club_rev
        
        # 3. רווחיות (נטו ממע"מ ועמלות)
        rev_no_vat = total_rev / vat
        gross_profit = rev_no_vat * gp_pct
        
        # ניכוי עמלות (אשראי 0.8% + אריזה 0.2%)
        variable_costs = rev_no_vat * 0.01 
        
        # רווח נקי
        net_profit = gross_profit - total_fixed_costs - variable_costs
        
        data.append({
            "חודש": month,
            "חברי מועדון": int(current_members),
            "מחזור חודשי": int(total_rev),
            "רווח נקי": int(net_profit)
        })
    return pd.DataFrame(data)

df_results = run_simulation()

# --- תצוגת תוצאות ---
col1, col2, col3 = st.columns(3)
col1.metric("סה\"כ חברים (סוף שנה 3)", f"{df_results['חברי מועדון'].iloc[-1]:,}")
col2.metric("מחזור חודשי (חודש 36)", f"₪{df_results['מחזור חודשי'].iloc[-1]:,}")
col3.metric("רווח נקי (חודש 36)", f"₪{df_results['רווח נקי'].iloc[-1]:,}")

st.subheader("📈 גרף צמיחה רב-שנתי")
fig = px.line(df_results, x="חודש", y=["רווח נקי", "מחזור חודשי"], 
              labels={"value": "שקלים", "variable": "מדד"},
              title="תחזית הכנסות ורווח לאורך 36 חודשים")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 טבלת נתונים גולמיים")
st.dataframe(df_results, use_container_width=True)