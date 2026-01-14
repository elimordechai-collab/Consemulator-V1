import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרות דף
st.set_page_config(page_title="Consumelator V2 - Full Edition", layout="wide")

st.title("📊 Consumelator V2 - סימולטור צמיחה מלא")
st.markdown("---")

# --- תפריט צד (Inputs) ---
st.sidebar.header("📋 הזנת נתונים מפורטת")

with st.sidebar:
    st.subheader("🏠 הוצאות קבועות (חודשי/דו-חודשי)")
    rent = st.number_input("שכירות חודשית", value=16100)
    prop_tax_bi = st.number_input("ארנונה (דו חודשי)", value=2800)
    mgmt_fees = st.number_input("דמי ניהול", value=100)
    elec_bi = st.number_input("חשמל (דו חודשי)", value=2800)
    water_bi = st.number_input("מים (דו חודשי)", value=100)
    maint = st.number_input("תחזוקה וניקיון", value=100)
    security = st.number_input("אבטחה", value=120)
    insurance = st.number_input("ביטוח", value=250)
    pos_fee = st.number_input("קופה", value=370)
    comm = st.number_input("תקשורת", value=280)
    
    st.subheader("👥 שכר וניהול")
    emp_salaries = st.number_input("שכר עובדים (עלות מעסיק)", value=13200)
    owner_salary = st.number_input("שכר בעלים", value=15000)
    consumrz_fee = st.number_input("Consumrz", value=659)
    
    st.subheader("📢 שיווק ומטה")
    ads = st.number_input("פרסום", value=4000)
    accounting = st.number_input("הנהלת חשבונות", value=2000)

    # חישוב סך הוצאות קבועות לחודש (כולל המרה מדו-חודשי לחודשי)
    total_fixed_costs = (
        rent + (prop_tax_bi/2) + mgmt_fees + (elec_bi/2) + (water_bi/2) + 
        maint + security + insurance + pos_fee + comm + 
        emp_salaries + owner_salary + consumrz_fee + ads + accounting
    )

    st.markdown("---")
    st.subheader("📈 פרמטרים של העסק")
    gp_pct = st.slider("אחוז רווח גולמי", 0.1, 0.8, 0.4, format="%.2f")
    avg_basket = st.number_input("סל ממוצע (כולל מע\"מ)", value=195)
    monthly_traffic = st.number_input("כמות לקוחות אורגנית בחודש", value=806)
    conversion_rate = st.slider("יחס המרה למועדון (%)", 0.01, 0.5, 0.15)
    share_rate = st.slider("אחוז משתפים (Referral)", 0.0, 0.1, 0.02)
    freq_multiplier = st.slider("מכפיל תדירות חברי מועדון", 1.0, 3.0, 1.5)

# --- מנוע החישוב ---
def run_simulation():
    data = []
    current_members = 0
    vat_factor = 1.18
    
    for month in range(1, 37):
        # 1. גיוס לקוחות (כולל ויראליות)
        new_from_organic = monthly_traffic * conversion_rate
        referrals = current_members * share_rate * 2
        current_members += (new_from_organic + referrals)
        
        # 2. חישוב הכנסות
        organic_rev = (monthly_traffic * (1 - conversion_rate)) * avg_basket
        club_rev = current_members * (avg_basket * freq_multiplier)
        total_rev = organic_rev + club_rev
        
        # 3. רווחיות (נטו ממע"מ ועמלות)
        rev_no_vat = total_rev / vat_factor
        gross_profit = rev_no_vat * gp_pct
        
        # ניכוי עמלות (אשראי 0.8% + אריזה 0.2% - לפי האקסל)
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
st.info(f"סך הוצאות קבועות חודשיות שחושבו: ₪{total_fixed_costs:,.0f}")

col1, col2, col3 = st.columns(3)
col1.metric("חברי מועדון (חודש 36)", f"{df_results['חברי מועדון'].iloc[-1]:,}")
col2.metric("מחזור (חודש 36)", f"₪{df_results['מחזור חודשי'].iloc[-1]:,}")
col3.metric("רווח נקי (חודש 36)", f"₪{df_results['רווח נקי'].iloc[-1]:,}")

st.subheader("📈 גרף צמיחה רב-שנתי")
fig = px.line(df_results, x="חודש", y=["רווח נקי", "מחזור חודשי"], 
              labels={"value": "שקלים", "variable": "מדד"},
              title="תחזית הכנסות ורווח לאורך 36 חודשים")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 טבלת נתונים מלאה")
st.dataframe(df_results, use_container_width=True)
