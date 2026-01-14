import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרות דף
st.set_page_config(page_title="Consumelator V2 - Pro Edition", layout="wide")

st.title("📊 Consumelator V2 - סימולטור רווחיות וצמיחה")
st.markdown("---")

# --- תפריט צד: הגדרות עלויות ופרמטרים ---
st.sidebar.header("⚙️ הגדרות מערכת")

with st.sidebar:
    st.subheader("💰 נתוני עלויות לעסקה")
    vat_pct = st.number_input("מע\"מ (%)", value=18.0) / 100
    gp_pct = st.slider("אחוז רווח גולמי", 0.1, 0.9, 0.4, step=0.01)
    credit_usage_pct = st.slider("אחוז שימוש באשראי (%)", 0, 100, 80) / 100
    credit_fee_pct = st.number_input("עמלת סליקה (%)", value=0.8) / 100
    pkg_fee_pct = st.number_input("עלות אריזה (%)", value=0.2) / 100

    st.subheader("🏠 הוצאות קבועות (חודשי)")
    rent = st.number_input("שכירות חודשית", value=16100)
    prop_tax = st.number_input("ארנונה (דו חודשי)", value=2800) / 2
    mgmt = st.number_input("דמי ניהול", value=100)
    elec = st.number_input("חשמל (דו חודשי)", value=2800) / 2
    water = st.number_input("מים (דו חודשי)", value=100) / 2
    maint = st.number_input("תחזוקה וניקיון", value=100)
    security = st.number_input("אבטחה", value=120)
    insurance = st.number_input("ביטוח", value=250)
    pos = st.number_input("קופה", value=370)
    comm = st.number_input("תקשורת", value=280)
    
    st.subheader("👥 שכר וניהול")
    salary_emp = st.number_input("שכר עובדים (עלות מעסיק)", value=13200)
    salary_owner = st.number_input("שכר בעלים", value=15000)
    consumrz_fee = st.number_input("Consumrz", value=659)
    ads = st.number_input("פרסום", value=4000)
    accounting = st.number_input("הנהלת חשבונות", value=2000)

    total_fixed_costs = (rent + prop_tax + mgmt + elec + water + maint + 
                        security + insurance + pos + comm + salary_emp + 
                        salary_owner + consumrz_fee + ads + accounting)

    st.subheader("🚀 פרמטרים של המועדון")
    conversion_rate = st.slider("יחס המרה למועדון (%)", 1, 50, 15) / 100
    freq_multiplier = st.slider("מכפיל תדירות ביקורים", 1.0, 3.0, 1.5)
    share_rate = st.slider("אחוז משתפים (%)", 0.0, 10.0, 2.0) / 100

# --- דף ראשי: נתוני עבר ---
st.subheader("📅 נתוני אמת מקדימים להשוואה (12 חודשים)")
st.write("הזן את נתוני המחזור והלקוחות של השנה האחרונה:")

hist_template = {
    "חודש": [f"חודש {i}" for i in range(1, 13)],
    "מחזור (כולל מע\"מ)": [184000, 129700, 201000, 188000, 144000, 125000, 164000, 171000, 121000, 138000, 133000, 145000],
    "כמות לקוחות": [761, 813, 881, 756, 711, 690, 777, 839, 865, 799, 856, 810]
}
df_hist = st.data_editor(pd.DataFrame(hist_template), use_container_width=True)

# חישוב נתוני בסיס מהיסטוריה
avg_monthly_traffic = df_hist["כמות לקוחות"].mean()
avg_basket = df_hist["מחזור (כולל מע\"מ)"].sum() / df_hist["כמות לקוחות"].sum()

# --- מנוע החישוב (36 חודשים קדימה) ---
def run_simulation():
    results = []
    current_members = 0
    
    for month in range(1, 37):
        # 1. גיוס לקוחות
        new_members = avg_monthly_traffic * conversion_rate
        referrals = current_members * share_rate * 2
        current_members += (new_members + referrals)
        
        # 2. הכנסות
        organic_rev = (avg_monthly_traffic * (1 - conversion_rate)) * avg_basket
        club_rev = current_members * (avg_basket * freq_multiplier)
        total_rev_with_vat = organic_rev + club_rev
        
        # 3. רווחיות
        rev_no_vat = total_rev_with_vat / (1 + vat_pct)
        gross_profit = rev_no_vat * gp_pct
        
        # עמלות משתנות (אשראי מחושב רק על אחוז השימוש באשראי)
        credit_cost = (rev_no_vat * credit_usage_pct) * credit_fee_pct
        pkg_cost = rev_no_vat * pkg_fee_pct
        
        net_profit = gross_profit - total_fixed_costs - credit_cost - pkg_cost
        
        results.append({
            "חודש": month,
            "חברי מועדון": int(current_members),
            "מחזור (כולל מע\"מ)": int(total_rev_with_vat),
            "רווח נקי": int(net_profit)
        })
    return pd.DataFrame(results)

df_future = run_simulation()

# --- תצוגת תוצאות ---
st.markdown("---")
st.subheader("📈 תחזית צמיחה ל-3 שנים")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("סל ממוצע (בסיס)", f"₪{avg_basket:.2f}")
with c2:
    st.metric("הוצאות קבועות (חודשי)", f"₪{total_fixed_costs:,.0f}")
with c3:
    st.metric("רווח נקי (חודש 36)", f"₪{df_future['רווח נקי'].iloc[-1]:,}")

fig = px.line(df_future, x="חודש", y=["רווח נקי", "מחזור (כולל מע\"מ)"], 
              title="צמיחה חזויה: מחזור מול רווח",
              labels={"value": "שקלים", "variable": "מדד"})
st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 טבלת תחזית מלאה")
st.dataframe(df_future, use_container_width=True)
