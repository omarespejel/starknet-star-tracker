# import streamlit as st
# import matplotlib.pyplot as plt
# import seaborn as sns
# from lifelines import KaplanMeierFitter
# from matplotlib.colors import LinearSegmentedColormap
# from utils import save_plot

# def visualize_developer_retention(df):
#     cohort_counts = (
#         df[~df["Inactive_Month"]]
#         .groupby(["Cohort", "Order"])
#         .developer.nunique()
#         .unstack(0)
#     )

#     cohort_sizes = cohort_counts.iloc[0]
#     retention = cohort_counts.divide(cohort_sizes, axis=1)

#     colors = [(0, "#FF0000"), (0.15, "#FFA500"), (0.2, "#FFFF00"), (1, "#008000")]
#     cmap = LinearSegmentedColormap.from_list("custom_cmap", colors, N=256)
#     plt.figure(figsize=(12, 8))
#     sns.heatmap(retention.T, annot=False, cmap=cmap)
#     plt.title("Journey Through Code: Tracking Developer Engagement Over Time", pad=20)

#     plt.subplots_adjust(bottom=0.3)

#     description_text = (
#         "This heatmap visualizes the engagement journey of developers, tracked monthly across cohorts."
#         " Each cohort represents developers who began contributing in the same month."
#         " The color gradient from red to green signifies the evolution of active engagement over time,"
#         " with red indicating lower engagement levels and green denoting higher activity."
#         " Cohorts are plotted on the y-axis, and the actual months since the start of the cohort on the x-axis."
#         " This visualization offers insights into how developer activity trends evolve,"
#         " highlighting periods of increased or decreased engagement and aiding in understanding"
#         " the effectiveness of retention strategies over time."
#         " Parameters:"
#         "(a) A developer is considered inactive if they have at least 2 continuous inactive months."
#         "(b) With one commit in a month, the developer is considered active."
#         "(c) The data is filtered to include only entries from September 2021 onwards."
#     )
#     plt.figtext(0.5, -0.0001, description_text, ha="center", fontsize=9, wrap=True)

#     save_plot(plt, "developer_engagement_journey")

# def survival_curve_analysis_and_plot(df):
#     summary_df = (
#         df.groupby("developer")
#         .agg({"duration": "first", "inactive_for_two_months": "last"})
#         .reset_index()
#     )

#     kmf = KaplanMeierFitter()
#     kmf.fit(
#         durations=summary_df["duration"],
#         event_observed=summary_df["inactive_for_two_months"],
#         label="Developer Survival Probability",
#     )

#     plt.figure(figsize=(10, 6))
#     ax = plt.subplot(111)
#     kmf.plot_survival_function(ax=ax)

#     plt.title("Developer Survival Curve: Probability of Active Contribution Over Time")
#     plt.grid(True, which="both", linestyle="--", linewidth=0.5)
#     median_survival_time = kmf.median_survival_time_
#     ax.axhline(y=0.5, color="red", linestyle="--")
#     ax.text(
#         median_survival_time,
#         0.48,
#         "Median Survival Time",
#         verticalalignment="center",
#         color="red",
#         fontsize=8,
#     )
#     ax.axvline(x=3, color="green", linestyle="--")
#     ax.text(
#         3,
#         0.95,
#         "Inactive Month + 1",
#         verticalalignment="top",
#         horizontalalignment="center",
#         color="green",
#         fontsize=8,
#     )
#     ax.axvline(x=median_survival_time, color="green", linestyle="--")
#     ax.text(
#         len(df["duration"].unique()),
#         0.9,
#         f"After month {int(median_survival_time)} the probability of developers staying is lower than 50 percent",
#         verticalalignment="top",
#         horizontalalignment="right",
#         color="green",
#         fontsize=8,
#     )
#     ax.set_yticks(np.arange(0, 1.1, 0.1))

#     plt.xlabel("Months since the developer started committing code")
#     plt.ylabel("Probability of a developer staying in the ecosystem")

#     description_text = (
#         "The Kaplan-Meier survival curve shows the probability of developers continuing to contribute over time."
#         "Parameters:"
#         "(a) A developer is consider as inactive if they have at least 2 continuous inactive months."
#         "(b) With one commit in a month, the developer is considered active."
#         "(c) The data is filtered to include only entries from September 2021 onwards."
#         "The Kaplan-Meier estimator is a non-parametric statistic used to estimate the survival function from lifetime data."
#         "It requires to know  the duration each subject was observed for, and whether the event of interest"
#         "(in this case, becoming inactive for two months) was observed."
#         "The 'Median Survival Time' shows when the chance of further contributions drops below 50%. "
#         "This analysis helps in understanding the retention of developers and predicting future contribution patterns."
#     )
#     plt.figtext(0.1, -0.1, description_text, ha="left", fontsize=8, wrap=True)

#     save_plot(plt, "developer_survival_curve")

# def developer_engagement_journey(df):
#     try:
#         with open("./github-metrics/assets/style.css") as f:
#             st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#     except:
#         try:
#             with open("../assets/style.css") as f:
#                 st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#         except:
#             with open("assets/style.css") as f:
#                 st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#     st.title("Developer Engagement Journey and Survival Curve Analysis")

#     st.markdown("## Developer Engagement Journey")
#     visualize_developer_retention(df)
#     st.image("developer_engagement_journey.png", use_column_width=True)
#     st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
#     st.markdown("<p style='font-size: 12px;'><b>Description:</b> This heatmap visualizes the engagement journey of developers, tracked monthly across cohorts. Each cohort represents developers who began contributing in the same month. The color gradient from red to green signifies the evolution of active engagement over time, with red indicating lower engagement levels and green denoting higher activity. Cohorts are plotted on the y-axis, and the actual months since the start of the cohort on the x-axis. This visualization offers insights into how developer activity trends evolve, highlighting periods of increased or decreased engagement and aiding in understanding the effectiveness of retention strategies over time.</p>", unsafe_allow_html=True)

#     st.markdown("---")

#     st.markdown("## Developer Survival Curve Analysis")
#     survival_curve_analysis_and_plot(df)
#     st.image("developer_survival_curve.png", use_column_width=True)
#     st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
#     st.markdown("<p style='font-size: 12px;'><b>Description:</b> The Kaplan-Meier survival curve shows the probability of developers continuing to contribute over time. The Kaplan-Meier estimator is a non-parametric statistic used to estimate the survival function from lifetime data. It requires knowing the duration each subject was observed for, and whether the event of interest (in this case, becoming inactive for two months) was observed. The 'Median Survival Time' shows when the chance of further contributions drops below 50%. This analysis helps in understanding the retention of developers and predicting future contribution patterns.</p>", unsafe_allow_html=True)
