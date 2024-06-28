import streamlit as st
from program_evaluation import program_evaluation
from general_insights import homepage
from utils import load_all_developers_dataset
from developer_engagement import developer_engagement_journey
import plotly

plotly.io.json.config.default_engine = 'orjson'

def main():
    df = load_all_developers_dataset()
    # max_available_month = df["month_year"].max().strftime("%Y-%m")
    st.set_page_config(page_title="Starknet Star Tracker")
    st.sidebar.title("Menu")
    st.sidebar.markdown(
        """
        - **Homepage**: Explore developer insights and package downloads for the Starknet ecosystem.
        - **Program Evaluation**: Analyze the impact of specific programs or events on developer activity.
        - **Developer Engagement**: Visualize developer engagement journey and survival curve analysis.
        """
    )
    app_mode = st.sidebar.selectbox("Select Application", ["Homepage", "Program Evaluation", "Developer Engagement"])
    st.sidebar.markdown("---")
    st.sidebar.markdown("With love from [@espejelomar](https://twitter.com/espejelomar) at [Starknet](https://starknet.io)")

    if app_mode == "Homepage":
        homepage(df)
    elif app_mode == "Program Evaluation":
        program_evaluation()
    # elif app_mode == "Developer Engagement":
    #     developer_engagement_journey(df)

if __name__ == "__main__":
    main()
