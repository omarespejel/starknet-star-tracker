import requests
import pypistats
import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go


def total_commits_per_month(df):
    df["month_year"] = pd.to_datetime(df["month_year"], format="%B_%Y")
    current_month = pd.Timestamp.now().strftime("%Y-%m")
    total_commits_df = (
        df[(df["month_year"] >= "2023-01-01") & (df["month_year"].dt.strftime("%Y-%m") != current_month)]
        .groupby([pd.Grouper(key="month_year", freq="M"), "developer"])
        .agg({"total_commits": "sum"})
        .reset_index()
    )
    total_commits_df["classification"] = pd.cut(
        total_commits_df["total_commits"],
        bins=[-1, 9, 19, float("inf")],
        labels=[
            "Low-level active (<10 commits)",
            "Moderately active (10-19 commits)",
            "Highly involved (20+ commits)",
        ],
    )
    total_commits_df = (
        total_commits_df.groupby(["month_year", "classification"],  observed=False)["total_commits"]
        .sum()
        .reset_index()
    )
    total_commits_df["month_year"] = total_commits_df["month_year"].dt.strftime("%B %Y")
    return total_commits_df


def commits_growth_rate(df):
    total_commits_df = total_commits_per_month(df)
    current_month = pd.Timestamp.now().strftime("%B %Y")
    total_commits_df = total_commits_df[total_commits_df["month_year"] != current_month]
    total_commits_df["month_year"] = pd.to_datetime(total_commits_df["month_year"], format="%B %Y")
    total_commits_df["year"] = total_commits_df["month_year"].dt.year
    total_commits_df["growth_rate"] = total_commits_df.groupby("year")[
        "total_commits"
    ].pct_change()
    total_commits_df["month_year"] = total_commits_df["month_year"].dt.strftime("%B %Y")
    return total_commits_df


def total_developers_per_month(df):
    df["month_year"] = pd.to_datetime(df["month_year"], format="%B_%Y")
    current_month = pd.Timestamp.now().strftime("%Y-%m")
    total_developers_df = (
        df[(df["month_year"] >= "2023-01-01") & (df["month_year"].dt.strftime("%Y-%m") != current_month)]
        .groupby([pd.Grouper(key="month_year", freq="M"), "developer"])
        .agg({"total_commits": "sum"})
        .reset_index()
    )
    total_developers_df = total_developers_df[total_developers_df["total_commits"] > 0]
    total_developers_df["classification"] = pd.cut(
        total_developers_df["total_commits"],
        bins=[-1, 9, 19, float("inf")],
        labels=[
            "Low-level active (<10 commits)",
            "Moderately active (10-19 commits)",
            "Highly involved (20+ commits)",
        ],
    )
    total_developers_df = (
        total_developers_df.groupby(["month_year", "classification"], observed=False)
        .size()
        .reset_index(name="total_developers")
    )
    total_developers_df["month_year"] = total_developers_df["month_year"].dt.strftime(
        "%B %Y"
    )
    return total_developers_df


def developers_growth_rate(df):
    total_developers_df = total_developers_per_month(df)
    current_month = pd.Timestamp.now().strftime("%B %Y")
    total_developers_df = total_developers_df[total_developers_df["month_year"] != current_month]
    total_developers_df["month_year"] = pd.to_datetime(total_developers_df["month_year"], format="%B %Y")
    total_developers_df["year"] = total_developers_df["month_year"].dt.year
    total_developers_df["growth_rate"] = total_developers_df.groupby(
        ["year", "classification"],  observed=False
    )["total_developers"].pct_change()
    total_developers_df["month_year"] = total_developers_df["month_year"].dt.strftime(
        "%B %Y"
    )
    return total_developers_df


def classify_developers_per_month(df):
    df["month_year"] = pd.to_datetime(df["month_year"], format="%B_%Y")
    last_month = df["month_year"].max()
    last_month_df = df[df["month_year"] == last_month]
    classification_df = (
        last_month_df.groupby("developer")["total_commits"].sum().reset_index()
    )
    classification_df["classification"] = pd.cut(
        classification_df["total_commits"],
        bins=[-1, 9, 19, float("inf")],
        labels=[
            "Low-level active (<10 commits)",
            "Moderately active (10-19 commits)",
            "Highly involved (20+ commits)",
        ],
    )
    classification_df = classification_df[classification_df["total_commits"] > 0]
    classification_df["sort_key"] = classification_df["classification"].map({
        "Highly involved (20+ commits)": 0,
        "Moderately active (10-19 commits)": 1,
        "Low-level active (<10 commits)": 2
    })
    classification_df = classification_df.sort_values(by=["sort_key", "total_commits"], ascending=[False, False])
    classification_df = classification_df[["developer", "classification", "total_commits"]]
    return classification_df


def developer_flow_plot(df):
    df["month_year"] = pd.to_datetime(df["month_year"], format="%B_%Y")
    last_month = df["month_year"].max()
    prev_month = last_month - pd.DateOffset(months=1)

    def get_classification(commits):
        if commits == 0:
            return "Not active"
        elif commits < 10:
            return "Low-level active (<10 commits)"
        elif commits < 20:
            return "Moderately active (10-19 commits)"
        else:
            return "Highly involved (20+ commits)"

    last_month_df = df[df["month_year"] == last_month]
    prev_month_df = df[df["month_year"] == prev_month]

    last_month_classification = last_month_df.groupby("developer")["total_commits"].sum().apply(get_classification)
    prev_month_classification = prev_month_df.groupby("developer")["total_commits"].sum().apply(get_classification)

    flow_data = pd.concat([prev_month_classification, last_month_classification], axis=1)
    flow_data.columns = ["Previous Month", "Current Month"]
    flow_data = flow_data.reset_index()

    labels = list(set(flow_data["Previous Month"].unique()) | set(flow_data["Current Month"].unique()))
    labels_prev = [f"{label} (Previous Month)" for label in labels]
    labels_curr = [f"{label} (Current Month)" for label in labels]
    labels = labels_prev + labels_curr

    source = [labels_prev.index(f"{prev} (Previous Month)") for prev in flow_data["Previous Month"]]
    target = [labels_curr.index(f"{curr} (Current Month)") for curr in flow_data["Current Month"]]
    value = flow_data.groupby(["Previous Month", "Current Month"]).size().values

    node_colors = ["#fe4a49", "#28286e", "#74b0ff", "#808080"]
    node_colors_dict = {}
    for i, label in enumerate(labels):
        node_colors_dict[label] = node_colors[i % len(node_colors)]

    fig_flow = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=[node_colors_dict[label] for label in labels]
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])

    # fig_flow.update_layout(title_text="Developer Flow: Category Changes (Last Two Months)", font_size=10)
    # st.plotly_chart(fig_flow)
    # st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
    # st.markdown("<p style='font-size: 12px;'><b>Description:</b> The flow of developers between different activity categories (low-level activity, moderately active, highly involved, and not active) from the previous month to the current month.</p>", unsafe_allow_html=True)
    
def developer_commits_difference(df):
    df["month_year"] = pd.to_datetime(df["month_year"], format="%B_%Y")
    current_month = pd.Timestamp.now().strftime("%B_%Y")
    
    current_month_dt = pd.to_datetime(current_month, format="%B_%Y")
    prev_month_dt = current_month_dt - pd.DateOffset(months=1)
    prev_prev_month_dt = current_month_dt - pd.DateOffset(months=2)
    
    prev_month_df = df[df["month_year"] == prev_month_dt]
    prev_prev_month_df = df[df["month_year"] == prev_prev_month_dt]
    
    prev_month_commits = prev_month_df.groupby("developer")["total_commits"].sum()
    prev_prev_month_commits = prev_prev_month_df.groupby("developer")["total_commits"].sum()
    
    commits_difference_df = pd.concat([prev_month_commits, prev_prev_month_commits], axis=1)
    commits_difference_df.columns = [prev_month_dt.strftime("%B_%Y"), prev_prev_month_dt.strftime("%B_%Y")]
    commits_difference_df["commits_difference"] = commits_difference_df[prev_month_dt.strftime("%B_%Y")] - commits_difference_df[prev_prev_month_dt.strftime("%B_%Y")]
    
    commits_difference_df = commits_difference_df.reset_index()
    commits_difference_df = commits_difference_df[["developer", "commits_difference"]]
    commits_difference_df = commits_difference_df[commits_difference_df["commits_difference"].notnull()]
    commits_difference_df = commits_difference_df.sort_values("commits_difference")
    commits_difference_df = commits_difference_df.rename(columns={"commits_difference": "How many more commits they had this month compared to the last one?"})
    
    return commits_difference_df, prev_month_dt.strftime("%B_%Y"), prev_prev_month_dt.strftime("%B_%Y")

def calculate_developer_tenure(df):
    df['month_year'] = pd.to_datetime(df['month_year'], format='%B_%Y')
    df = df.sort_values('month_year')
    first_commit = df.groupby('developer')['month_year'].min().reset_index()
    first_commit.columns = ['developer', 'first_commit']
    df = pd.merge(df, first_commit, on='developer', how='left')
    df['tenure'] = (df['month_year'] - df['first_commit']).dt.days / 365.25
    return df

def monthly_active_devs_by_tenure(df):
    df = calculate_developer_tenure(df)
    df['tenure_category'] = pd.cut(df['tenure'], 
                                   bins=[-float('inf'), 1, 2, float('inf')],
                                   labels=['0-1y', '1y-2y', '2y+'])
    
    # Get the first day of the previous month
    last_complete_month = pd.Timestamp.now().replace(day=1) - pd.DateOffset(days=1)
    last_complete_month = last_complete_month.replace(day=1)
    
    # Exclude the current month and any future months
    df = df[df['month_year'] < last_complete_month]
    
    monthly_active = df[df['total_commits'] > 0].groupby(['month_year', 'tenure_category']).size().unstack(fill_value=0)
    monthly_active = monthly_active.reset_index()
    monthly_active['month_year'] = pd.to_datetime(monthly_active['month_year'])
    monthly_active = monthly_active.sort_values('month_year')
    
    return monthly_active

def plot_monthly_active_devs_by_tenure(monthly_active):
    monthly_active['month_year'] = pd.to_datetime(monthly_active['month_year'])
    
    last_complete_month = pd.Timestamp.now().replace(day=1) - pd.DateOffset(days=1)
    last_complete_month = last_complete_month.replace(day=1)
    
    monthly_active = monthly_active[monthly_active['month_year'] < last_complete_month]
    monthly_active = monthly_active[monthly_active['month_year'] >= '2022-01-01']
    last_month = monthly_active['month_year'].max()

    fig = go.Figure()
    
    colors = {'0-1y': '#74b0ff', '1y-2y': '#28286e', '2y+': '#fe4a49'}
    
    for category in ['2y+', '1y-2y', '0-1y']:
        fig.add_trace(go.Scatter(
            x=monthly_active['month_year'],
            y=monthly_active[category],
            mode='lines',
            name=category,
            line=dict(width=2, color=colors[category]),
        ))
    
    fig.update_layout(
        title='Monthly Active Devs by Tenure',
        xaxis_title='Date',
        yaxis_title='Number of Devs',
        yaxis_range=[0, 500],
        legend_title_text='Tenure',
        hovermode='x unified',
        xaxis=dict(
            range=[pd.Timestamp('2022-01-01'), last_month],
            dtick='M3'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='black'),
        legend=dict(bgcolor='rgba(255,255,255,0.5)'),
    )
    
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(0, 0, 0, 0.1)'
    )
    
    return fig

def calculate_developer_retention(df):
    df['month_year'] = pd.to_datetime(df['month_year'], format='%B_%Y')
    df = df.sort_values('month_year')
    
    first_activity = df.groupby('developer')['month_year'].min()
    last_activity = df.groupby('developer')['month_year'].max()
    
    retention_data = []
    for months in [3, 6, 9, 12]:  # Added 9 months
        still_active = ((last_activity - first_activity) >= pd.Timedelta(days=30*months)).sum()
        total_devs = len(first_activity)
        retention_rate = still_active / total_devs
        retention_data.append({'months': months, 'retention_rate': retention_rate})
    
    return pd.DataFrame(retention_data)

def plot_developer_retention(retention_df):
    fig = go.Figure(data=[
        go.Bar(x=retention_df['months'], y=retention_df['retention_rate'], 
               text=retention_df['retention_rate'].apply(lambda x: f'{x:.2%}'),
               textposition='auto',
               marker_color='#74b0ff')
    ])
    
    fig.update_layout(
        title='Developer Retention Rate',
        xaxis_title='Months After First Contribution',
        yaxis_title='Retention Rate',
        yaxis_tickformat=',.0%',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='black'),
        xaxis=dict(tickmode='array', tickvals=[3, 6, 9, 12]),
        yaxis_range=[0, 1]
    )
    
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(0, 0, 0, 0.1)'
    )
    
    return fig


def homepage(df):
    try:
        with open("./github-metrics/assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        try:
            with open("../assets/style.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except:
            with open("assets/style.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title("Starknet Star Tracker: GitHub Starknet Developer Insights")
    st.markdown(
        """
        This tool is maintained and created by Omar Espejel ([@espejelomar](https://twitter.com/espejelomar) on Twitter and Telegram). Feel free to contact him for feedback or comments.
        """
    )

    total_developers_df = total_developers_per_month(df)
    fig_total_developers = px.bar(
        total_developers_df,
        x="month_year",
        y="total_developers",
        color="classification",
        title="Total Developers per Month",
        color_discrete_sequence=["#fe4a49", "#28286e", "#74b0ff"],
    )
    fig_total_developers.update_yaxes(rangemode="tozero", title="Number of Developers")
    fig_total_developers.update_layout(
        xaxis=dict(categoryorder='array', categoryarray=sorted(total_developers_df['month_year'].unique(), key=lambda x: pd.to_datetime(x, format='%B %Y')))
    )
    fig_total_developers.update_layout(legend_title_text='Classification')
    st.plotly_chart(fig_total_developers)
    st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px;'><b>Description:</b> Number of developers active per month by three different groups of developers: those with low-level activity (<10 commits), moderately active (10-19 commits), and highly involved (20+ commits).</p>", unsafe_allow_html=True)

    st.markdown("---")


    total_commits_df = total_commits_per_month(df)
    fig_total_commits = px.bar(
        total_commits_df,
        x="month_year",
        y="total_commits",
        color="classification",
        title="Total Commits per Month",
        color_discrete_sequence=["#fe4a49", "#28286e", "#74b0ff"],
    )
    fig_total_commits.update_yaxes(rangemode="tozero", title="Open Source Repos Commits")
    fig_total_commits.update_layout(
        xaxis=dict(categoryorder='array', categoryarray=sorted(total_commits_df['month_year'].unique(), key=lambda x: pd.to_datetime(x, format='%B %Y')))
    )
    fig_total_commits.update_layout(legend_title_text='Classification')
    st.plotly_chart(fig_total_commits)
    st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px;'><b>Description:</b> The total number of commits done per month by three different groups of developers: those with low-level activity (<10 commits), moderately active (10-19 commits), and highly involved (20+ commits).</p>", unsafe_allow_html=True)

    st.markdown("---")

    monthly_active = monthly_active_devs_by_tenure(df)
    fig_monthly_active = plot_monthly_active_devs_by_tenure(monthly_active)
    st.plotly_chart(fig_monthly_active, use_container_width=True)
    st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px;'><b>Description:</b> Number of active developers per month categorized by their tenure in the project, from 2022 to the most recent data available. Each line represents a different tenure category.</p>", unsafe_allow_html=True)
 
    retention_df = calculate_developer_retention(df)
    fig_retention = plot_developer_retention(retention_df)
    st.plotly_chart(fig_retention, use_container_width=True)
    st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px;'><b>Description:</b> Percentage of developers who remain active 3, 6, and 12 months after their first contribution.</p>", unsafe_allow_html=True)

    st.subheader("Last Month's Active Developers by Category")
    classification_df = classify_developers_per_month(df)
    st.dataframe(classification_df)
    st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px;'><b>Description:</b> The specific GitHub handles of the users and their activity. This is useful to identify the most active developers during the last month.</p>", unsafe_allow_html=True)

    st.markdown("---")

    commits_difference_df, prev_month, prev_prev_month = developer_commits_difference(df)

    if not commits_difference_df.empty:
        st.subheader(f"Developer Commits Difference: {prev_month} vs {prev_prev_month}")
        st.dataframe(commits_difference_df)
        st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 12px;'><b>Description:</b> The difference in the number of commits for each developer compared to the previous month. Negative values indicate fewer commits than the previous month.</p>", unsafe_allow_html=True)
    else:
        st.subheader(f"Developer Commits Difference: {prev_month} vs {prev_prev_month}")
        st.write("No data available for the selected months.")
    
    st.markdown("---")

    developer_flow_plot(df)

    st.markdown("---")

    # Get monthly download stats for starknet-py package
    package = "starknet-py"
    end_date = pd.Timestamp.now().strftime("%Y-%m-%d")
    start_date = (pd.Timestamp.now() - pd.DateOffset(months=5)).strftime("%Y-%m-%d")
    downloads_list = []

    for i in range(5, 0, -1):
        start_month = pd.Timestamp(end_date) - pd.DateOffset(months=i)
        end_month = pd.Timestamp(end_date) - pd.DateOffset(months=i - 1)
        start_month_str = start_month.strftime("%Y-%m-%d")
        end_month_str = end_month.strftime("%Y-%m-%d")
        downloads = pypistats.overall(
            package,
            start_date=start_month_str,
            end_date=end_month_str,
            format="pandas",
        )
        downloads = downloads[downloads["category"] == "without_mirrors"]
        total_downloads = downloads["downloads"].sum()
    
        downloads_list.append(
            {"month": start_month.strftime("%B %Y"), "downloads": total_downloads}
        )
    downloads_py = pd.DataFrame(downloads_list)

    # Starknet Package Downloads from npm
    package = "starknet"
    downloads_npm = pd.read_json(
        f"https://api.npmjs.org/downloads/range/{start_date}:{end_date}/{package}"
    )
    if "downloads" in downloads_npm.columns:
        downloads_npm["day"] = downloads_npm["downloads"].apply(lambda x: x["day"])
        downloads_npm["downloads"] = downloads_npm["downloads"].apply(
            lambda x: x["downloads"]
        )
        downloads_npm["day"] = pd.to_datetime(downloads_npm["day"])
        downloads_npm = (
            downloads_npm.groupby(pd.Grouper(key="day", freq="M"))["downloads"]
            .sum()
            .reset_index()
        )
        downloads_npm["day"] = downloads_npm["day"].dt.strftime("%B %Y")
    else:
        st.write("No download data available for starknet npm package.")

    # Starknet Package Downloads from Cargo
    package = "starknet"
    url = f"https://crates.io/api/v1/crates/{package}/downloads"
    response = requests.get(url)
    if response.status_code == 200:
        downloads_cargo = response.json()
        downloads_cargo_df = pd.DataFrame(downloads_cargo["version_downloads"])
        downloads_cargo_df["date"] = pd.to_datetime(downloads_cargo_df["date"])
        downloads_cargo_df = (
            downloads_cargo_df.groupby(pd.Grouper(key="date", freq="M"))[
                "downloads"
            ]
            .sum()
            .reset_index()
        )
        downloads_cargo_df["date"] = downloads_cargo_df["date"].dt.strftime("%B %Y")
    else:
        st.write("No download data available for starknet Cargo package.")

    # Combine download data from all sources
    downloads_combined = pd.DataFrame(columns=["month"])

    if not downloads_py.empty:
        downloads_combined = downloads_combined.merge(
            downloads_py.rename(columns={"date": "month", "downloads": "Python (PyPI)"}),
            on="month",
            how="outer",
        )

    if not downloads_npm.empty:
        downloads_combined = downloads_combined.merge(
            downloads_npm.rename(columns={"day": "month", "downloads": "JavaScript (NPM)"}),
            on="month",
            how="outer",
        )

    if not downloads_cargo_df.empty:
        downloads_combined = downloads_combined.merge(
            downloads_cargo_df.rename(
                columns={"date": "month", "downloads": "Rust (Cargo)"}
            ),
            on="month",
            how="outer",
        )

    downloads_combined = downloads_combined.fillna(0)
    downloads_combined = downloads_combined.melt(
        id_vars=["month"], var_name="source", value_name="downloads"
    )
    
    # Exclude the current month from the downloads data
    current_month = pd.Timestamp.now().strftime("%B %Y")
    downloads_combined = downloads_combined[downloads_combined["month"] != current_month]

    # Create a stacked bar chart for combined downloads
    fig_starknet_downloads = px.bar(
        downloads_combined,
        x="month",
        y="downloads",
        color="source",
        title="Monthly Downloads of Starknet Packages (Cargo only shows 3 months)",
        color_discrete_sequence=["#fe4a49", "#28286e", "#74b0ff"],
    )
    fig_starknet_downloads.update_layout(
        xaxis=dict(categoryorder='array', categoryarray=sorted(downloads_combined['month'].unique(), key=lambda x: pd.to_datetime(x, format='%B %Y')))
    )
    fig_starknet_downloads.update_layout(legend_title_text='Package')
    fig_starknet_downloads.update_yaxes(title="Downloads")
    st.plotly_chart(fig_starknet_downloads)
    st.markdown("<p style='font-size: 12px;'><b>Source:</b> NPM, PyPI, and Cargo</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px;'><b>Description:</b> The total downloads of Starknet packages in different languages.</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px;'><b>Disclaimer:</b> The different languages provide access to different months, so take into account that Cargo may show fewer months and Python may not have the most updated data.</p>", unsafe_allow_html=True)
