import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרות דף RTL ומראה מקצועי
st.set_page_config(page_title="Consumelator V2 - Pro System", layout="wide")

# הזרקת CSS לתמיכה ביישור לימין (RTL)
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    div[data-testid="stSidebar"] { direction: rtl; }
    .stMetric { text-align: right; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("📊 Consumelator V2 - מערכת ניהול, צמיחה ו-ROI")
st.markdown("---")

# --- תפריט צד: הזנת נתונים ---
st.sidebar.header("🛠️ הגדרות ונתוני עסק")

with st.sidebar:
    st.subheader("🏠 הוצאות קבועות")
    rent = st.number_input("שכירות חודשית", value=16100)
    prop_tax = st.number_input("ארנונה (דו חודשי)", value=2800)
    mgmt = st.number_input("דמי ניהול", value=100)
    elec = st.number_input("חשמל (דו חודשי)", value=2800)
    water = st.number_input("מים (דו חודשי)", value=100)
    maint = st.number_input("תחזוקה וניקיון", value=100)
    security = st.number_input("אבטחה", value=120)
    insurance = st.number_input("ביטוח", value=250)
    pos = st.number_input("קופה", value=370)
    comm = st.number_input("תקשורת", value=280)
    salary_emp = st.number_input("שכר עובדים (עלות מעסיק)", value=13200)
    salary_owner = st.number_input("שכר בעלים", value=15000)
    consumrz_fee = st.number_input("Consumrz", value=659)
    ads = st.number_input("פרסום", value=4000)
    accounting = st.number_input("הנהלת חשבונות", value=2000)
    
    # חישוב סך הוצאות קבועות לחודש
    total_fixed = (rent + (prop_tax/2) + mgmt + (elec/2) + (water/2) + 
                   maint + security + insurance + pos + comm + 
                   salary_emp + salary_owner + consumrz_fee + ads + accounting)

    st.subheader("💰 נתוני עלויות לעסקה")
    vat_pct = st.number_input("אחוז מע\"מ (%)", value=18.0) / 100
    gp_pct = st.number_input("אחוז רווח גולמי (%)", value=40.0) / 100
    credit_ratio = st.number_input("אחוז אשראי מסך עסקאות (%)", value=80.0) / 100
    credit_fee = st.number_input("עלות עמלת אשראי (%)", value=0.8) / 100
    pkg_cost = st.number_input("עלויות אריזה (%)", value=0.2) / 100

    st.subheader("🎁 הגדרות מועדון Consumrz")
    conv_rate = st.slider("לקוחות מגויסים בחודש (%)", 0, 100, 15) / 100
    gift_pts = st.number_input("מתנת הצטרפות (₪)", value=10)
    cashback_pct = st.slider("אחוז קאשבק (%)", 0, 20, 5) / 100
    redemption_limit = st.slider("מגבלת מימוש (%)", 0, 100, 20) / 100
    freq_mult = st.slider("מכפיל ביקורים לחודש", 1.0, 5.0, 1.5)
    
    st.subheader("🔗 נתוני שיתופים (Viral)")
    share_rate = st.slider("אחוז משתפים (%)", 0, 20, 2) / 100
    share_mult = st.number_input("מכפיל משתפים (כמה מביא כל אחד)", value=2)
    share_gift = st.number_input("מתנה עבור שיתוף (₪)", value=20)
    share_repeat = st.slider("אחוז משתפים חוזר (%)", 0, 100, 60) / 100

# --- חלק ראשי: נתוני עבר ---
st.subheader("📈 נתוני אמת מקדימים להשוואה (12 חודשים)")
st.write("הזן את נתוני המקור של העסק מהשנה האחרונה:")

# יצירת טבלת נתוני עבר עם המספרים שסיפקת
hist_data = {
    "חודש": [f"חודש {i}" for i in range(1, 13)],
    "מחזור כולל מע\"מ": [184000, 129700, 201000, 188000, 144000, 125000, 164000, 171000, 121000, 138000, 133000, 191000],
    "מס עסקאות": [761, 813, 881, 756, 711, 690, 777, 839, 865, 799, 856, 919]
}
df_hist = st.data_editor(pd.DataFrame(hist_data), use_container_width=True)

# חישוב נתוני בסיס
avg_traffic = df_hist["מס עסקאות"].mean()
avg_basket = df_hist["מחזור כולל מע\"מ"].sum() / df_hist["מס עסקאות"].sum()
pre_club_annual_profit = (df_hist["מחזור כולל מע\"מ"].sum() / (1+vat_pct) * gp_pct) - (total_fixed * 12)

# --- מנוע הסימולציה ---
def run_simulation():
    res = []
    members = 0
    points_pool = 0 # יתרת נקודות מצטברת (Liability)
    
    for m in range(1, 37):
        # 1. גיוס חברים ושיתופים
        new_members = avg_traffic * conv_rate
        referral_members = members * share_rate * share_mult
        members += (new_members + referral_members)
        
        # 2. חישוב הכנסות
        rev_organic = (avg_traffic - new_members) * avg_basket
        rev_club = members * (avg_basket * freq_mult)
        total_rev = rev_organic + rev_club
        rev_no_vat = total_rev / (1 + vat_pct)
        
        # 3. לוגיקת נקודות וקאשבק
        # צבירה (מתנות + אחוז מהקנייה)
        earned = (rev_club / (1 + vat_pct) * cashback_pct) + (new_members * gift_pts) + (referral_members * share_gift)
        points_pool += earned
        
        # מימוש (עד המגבלה או עד גמר היתרה)
        max_redemption = (rev_club / (1 + vat_pct)) * redemption_limit
        redeemed = min(points_pool, max_redemption)
        points_pool -= redeemed
        
        # 4. הוצאות משתנות ורווח
        var_costs = (rev_no_vat * credit_ratio * credit_fee) + (rev_no_vat * pkg_cost)
        gross_profit = (rev_no_vat * gp_pct) - redeemed
        net_profit = gross_profit - total_fixed - var_costs
        
        res.append({
            "חודש": m,
            "חברי מועדון": int(members),
            "מחזור (כולל מע\"מ)": int(total_rev),
            "רווח נקי": int(net_profit),
            "מימוש נקודות": int(redeemed),
            "יתרת נקודות (חוב)": int(points_pool)
        })
    return pd.DataFrame(res)

df_sim = run_simulation()

# --- הצגת תוצאות ---
st.markdown("---")
st.subheader("🔮 תחזית צמיחה ל-36 חודשים (עם מועדון Consumrz)")

c1, c2, c3, c4 = st.columns(4)
c1.metric("סל ממוצע (מנתוני עבר)", f"₪{avg_basket:.2f}")
c2.metric("הוצאות קבועות (חודשי)", f"₪{total_fixed:,.0f}")
c3.metric("רווח נקי (חודש 36)", f"₪{df_sim['רווח נקי'].iloc[-1]:,}")
c4.metric("חברי מועדון (חודש 36)", f"{df_sim['חברי מועדון'].iloc[-1]:,}")

# גרף השוואתי
fig = px.line(df_sim, x="חודש", y=["רווח נקי", "מחזור (כולל מע\"מ)"], 
              labels={"value": "שקלים", "variable": "מדד"},
              title="צמיחה חזויה: מחזור מול רווח נקי")
st.plotly_chart(fig, use_container_width=True)

# טבלת נתונים מלאה
with st.expander("לצפייה בטבלת הנתונים המלאה של הסימולציה"):
    st.dataframe(df_sim, use_container_width=True)

# סיכום השוואתי
st.success(f"לפי נתוני העבר, הרווח השנתי ללא מועדון עומד על ₪{pre_club_annual_profit:,.0f}. "
           f"עם המועדון, בתוך 3 שנים המחזור החודשי צפוי לצמוח ל-₪{df_sim['מחזור (כולל מע\'מ)'].iloc[-1]:,}.")
