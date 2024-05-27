import requests
import pypistats
import pandas as pd
import plotly.express as px
import streamlit as st

def total_commits_per_month(df):
    df["month_year"] = pd.to_datetime(df["month_year"], format="%B_%Y")
    total_commits_df = (
        df[df["month_year"] >= "2023-01-01"]
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
    total_commits_df["month_year"] = pd.to_datetime(total_commits_df["month_year"], format="%B %Y")
    total_commits_df["year"] = total_commits_df["month_year"].dt.year
    total_commits_df["growth_rate"] = total_commits_df.groupby("year")[
        "total_commits"
    ].pct_change()
    total_commits_df["month_year"] = total_commits_df["month_year"].dt.strftime("%B %Y")
    return total_commits_df


def total_developers_per_month(df):
    df["month_year"] = pd.to_datetime(df["month_year"], format="%B_%Y")
    total_developers_df = (
        df[df["month_year"] >= "2023-01-01"]
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
    classification_df = classification_df.sort_values(by=["sort_key", "total_commits"], ascending=[True, False])
    classification_df = classification_df[["developer", "classification", "total_commits"]]
    return classification_df

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
    st.markdown("<p style='font-size: 12px;'><b>Description:</b> Number of developers classified by their activity, similar to the total commits plot.</p>", unsafe_allow_html=True)

    st.markdown("---")

    developers_growth_df = developers_growth_rate(df)
    fig_developers_growth = px.bar(
        developers_growth_df,
        x="month_year",
        y="growth_rate",
        color="classification",
        title="Developers Growth Rate (Year-over-Year)",
        color_discrete_sequence=["#fe4a49", "#28286e", "#74b0ff"],
    )
    fig_developers_growth.update_yaxes(rangemode="tozero", title="Growth Rate")
    fig_developers_growth.update_layout(
        xaxis=dict(categoryorder='array', categoryarray=sorted(developers_growth_df['month_year'].unique(), key=lambda x: pd.to_datetime(x, format='%B %Y')))
    )
    fig_developers_growth.update_layout(legend_title_text='Classification')
    st.plotly_chart(fig_developers_growth)
    st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px;'><b>Description:</b> The year-over-year growth rate of developers for each activity group (low-level activity, moderately active, and highly involved) based on the total developers per month.</p>", unsafe_allow_html=True)

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

    commits_growth_df = commits_growth_rate(df)
    fig_commits_growth = px.bar(
        commits_growth_df,
        x="month_year",
        y="growth_rate",
        color="classification",
        title="Commits Growth Rate (Year-over-Year)",
        color_discrete_sequence=["#fe4a49", "#28286e", "#74b0ff"],
    )
    fig_commits_growth.update_yaxes(rangemode="tozero", title="Growth Rate")
    fig_commits_growth.update_layout(
        xaxis=dict(categoryorder='array', categoryarray=sorted(commits_growth_df['month_year'].unique(), key=lambda x: pd.to_datetime(x, format='%B %Y')))
    )
    fig_commits_growth.update_layout(legend_title_text='Classification')
    st.plotly_chart(fig_commits_growth)
    st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px;'><b>Description:</b> The year-over-year growth rate of commits for each developer group (low-level activity, moderately active, and highly involved) based on the total commits per month.</p>", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Last Month's Active Developers by Category")
    classification_df = classify_developers_per_month(df)
    st.dataframe(classification_df)
    st.markdown("<p style='font-size: 12px;'><b>Source:</b> Open Source repositories in GitHub</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px;'><b>Description:</b> The specific GitHub handles of the users and their activity. This is useful to identify the most active developers during the last month.</p>", unsafe_allow_html=True)

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
