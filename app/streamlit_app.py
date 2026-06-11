import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 確保能載入 src 模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from src.predict import predict_profit
except ModuleNotFoundError:
    from predict import predict_profit

st.title("Startup Profit Prediction App")
st.write("This app predicts startup profit based on R&D Spend, Administration Spend, Marketing Spend, and State.")

# 嘗試載入歷史資料以供繪圖
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', '50_Startups.csv'))
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    st.subheader("📊 歷史資料散佈圖 (Historical Data Scatter Plots)")
    tab1, tab2, tab3 = st.tabs(["研發支出 (R&D)", "行政支出 (Admin)", "行銷支出 (Marketing)"])
    with tab1:
        fig1 = px.scatter(df, x="R&D Spend", y="Profit", color="State", title="R&D Spend vs Profit")
        st.plotly_chart(fig1, use_container_width=True)
    with tab2:
        fig2 = px.scatter(df, x="Administration", y="Profit", color="State", title="Administration vs Profit")
        st.plotly_chart(fig2, use_container_width=True)
    with tab3:
        fig3 = px.scatter(df, x="Marketing Spend", y="Profit", color="State", title="Marketing Spend vs Profit")
        st.plotly_chart(fig3, use_container_width=True)
else:
    df = None
    st.warning("找不到歷史資料檔案 (data/50_Startups.csv)，無法顯示歷史圖表。")

st.markdown("---")
st.subheader("🔮 進行利潤預測 (Predict Profit)")

# 建立輸入欄位
col1, col2 = st.columns(2)
with col1:
    rd_spend = st.number_input("R&D Spend", min_value=0.0, value=100000.0)
    administration = st.number_input("Administration Spend", min_value=0.0, value=50000.0)
with col2:
    marketing_spend = st.number_input("Marketing Spend", min_value=0.0, value=150000.0)
    state = st.selectbox("State", ["New York", "California", "Florida"])

st.markdown("---")
x_axis_choice = st.selectbox("📉 請選擇預測結果圖的 X 軸 (Select X-axis for Plot):", ["R&D Spend", "Administration", "Marketing Spend"])

# 預測按鈕與輸出
if st.button("Predict Profit", type="primary"):
    try:
        predicted_profit = predict_profit(rd_spend, administration, marketing_spend, state)
        st.success(f"Predicted Profit: ${predicted_profit:,.2f}")
        
        # 根據使用者的選擇，決定預測點的 X 數值
        if x_axis_choice == "R&D Spend":
            input_x_val = rd_spend
        elif x_axis_choice == "Administration":
            input_x_val = administration
        else:
            input_x_val = marketing_spend

        # 預測結果圖 (將預測點標示在歷史資料上)
        if df is not None:
            st.write("**預測結果圖 (您的預測落點位置)：**")
            fig_result = go.Figure()
            # 歷史資料點
            fig_result.add_trace(go.Scatter(
                x=df[x_axis_choice], y=df["Profit"], mode='markers', 
                name='歷史資料 (Historical)', marker=dict(color='gray', opacity=0.5)
            ))
            # 新的預測點
            fig_result.add_trace(go.Scatter(
                x=[input_x_val], y=[predicted_profit], mode='markers', 
                name='您的預測 (Your Prediction)', marker=dict(color='red', size=15, symbol='star'),
                hovertemplate=(
                    "<b>您的輸入 (Your Input):</b><br>"
                    f"R&D Spend: {rd_spend:,.2f}<br>"
                    f"Administration: {administration:,.2f}<br>"
                    f"Marketing Spend: {marketing_spend:,.2f}<br>"
                    f"State: {state}<br>"
                    f"<b>預測利潤 (Profit): {predicted_profit:,.2f}</b><extra></extra>"
                )
            ))
            fig_result.update_layout(
                title=f"{x_axis_choice} 與利潤關係圖 ({x_axis_choice} vs Profit)", 
                xaxis_title=x_axis_choice, yaxis_title="利潤 (Profit)", hovermode="closest"
            )
            st.plotly_chart(fig_result, use_container_width=True)
            
    except FileNotFoundError:
        st.error("Error: Model files not found. Please train the model in the notebook first.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

st.markdown("---")