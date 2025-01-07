import streamlit as st
import pandas as pd
from dataclasses import dataclass

# Set page configuration
st.set_page_config(
    page_title="Margin Calculator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@dataclass
class MarginPosition:
    amount: float
    ltv: float
    leverage: float
    collateral_rate: float
    borrow_rate: float
    
    @property
    def max_leverage(self) -> float:
        return 1 / (1 - self.ltv)
    
    @property
    def collateral(self) -> float:
        return self.amount
    
    @property
    def borrow(self) -> float:
        return self.amount * (self.leverage - 1)
    
    @property
    def deposit(self) -> float:
        return self.collateral + self.borrow
    
    @property
    def net_apy(self) -> float:
        return (self.collateral_rate * self.collateral * self.leverage - 
                self.borrow_rate * self.borrow) / self.collateral * 100
    
    @property
    def annual_earnings(self) -> float:
        return (self.collateral_rate * self.collateral * self.leverage - 
                self.borrow_rate * self.borrow)
    
    @property
    def monthly_earnings(self) -> float:
        return self.annual_earnings / 12
    
    @property
    def daily_earnings(self) -> float:
        return self.annual_earnings / 365

def main():
    st.title("Margin Calculator")
    
    # Parameters input in a compact layout
    c1, c2, c3 = st.columns(3)
    
    with c1:
        amount = st.number_input("Amount", min_value=1.0, value=100.0, step=10.0, format="%0.2f")
        ltv = st.number_input("LTV", min_value=0.1, max_value=0.95, value=0.8, step=0.05, format="%0.2f")
    
    with c2:
        max_lev = 1 / (1 - ltv)
        leverage = st.number_input("Leverage", min_value=1.0, max_value=float(max_lev), 
                                 value=min(5.0, max_lev), step=0.1, format="%0.2f")
        st.text(f"Max Leverage: {max_lev:.2f}x")
    
    with c3:
        collateral_rate = st.number_input("Collateral Rate %", min_value=0.0, max_value=100.0, value=13.76, 
                                        step=0.01, format="%0.2f") / 100
        borrow_rate = st.number_input("Borrow Rate %", min_value=0.0, max_value=100.0, value=10.97, 
                                    step=0.01, format="%0.2f") / 100

    position = MarginPosition(
        amount=amount,
        ltv=ltv,
        leverage=leverage,
        collateral_rate=collateral_rate,
        borrow_rate=borrow_rate
    )
    
    # Key metrics
    st.divider()
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric("Total Position", f"${position.deposit:,.2f}")
        st.metric("Initial Amount", f"${position.collateral:,.2f}")
        st.metric("Borrowed", f"${position.borrow:,.2f}")
    
    with m2:
        st.metric("Net APY", f"{position.net_apy:,.2f}%")
        st.metric("Collateral Rate", f"{position.collateral_rate*100:.2f}%")
        st.metric("Borrow Rate", f"{position.borrow_rate*100:.2f}%")
    
    with m3:
        st.metric("Earnings/Year", f"${position.annual_earnings:,.2f}")
        st.metric("Earnings/Month", f"${position.monthly_earnings:,.2f}")
        st.metric("Earnings/Day", f"${position.daily_earnings:,.2f}")

    # Sensitivity analysis
    st.divider()
    st.subheader("Leverage Sensitivity")
    
    leverages = [1.0, 2.0, 3.0, 4.0, 5.0, position.max_leverage]
    sensitivity_data = []
    
    for lev in leverages:
        if lev <= position.max_leverage:
            test_pos = MarginPosition(
                amount=position.amount,
                ltv=position.ltv,
                leverage=lev,
                collateral_rate=position.collateral_rate,
                borrow_rate=position.borrow_rate
            )
            sensitivity_data.append({
                "Leverage": f"{lev:.2f}x",
                "Position Size": f"${test_pos.deposit:,.2f}",
                "Net APY": f"{test_pos.net_apy:.2f}%",
                "Annual $": f"${test_pos.annual_earnings:,.2f}",
                "Monthly $": f"${test_pos.monthly_earnings:,.2f}",
                "Daily $": f"${test_pos.daily_earnings:,.2f}"
            })
    
    # Display sensitivity table with custom formatting
    df = pd.DataFrame(sensitivity_data)
    st.dataframe(
        df,
        hide_index=True,
        column_config={
            "Leverage": st.column_config.TextColumn("Leverage", width="small"),
            "Position Size": st.column_config.TextColumn("Size", width="medium"),
            "Net APY": st.column_config.TextColumn("APY", width="small"),
            "Annual $": st.column_config.TextColumn("Year $", width="medium"),
            "Monthly $": st.column_config.TextColumn("Month $", width="medium"),
            "Daily $": st.column_config.TextColumn("Day $", width="medium")
        }
    )

if __name__ == "__main__":
    main()
