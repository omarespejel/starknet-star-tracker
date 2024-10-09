import os
from datetime import datetime

import pandas as pd
from termcolor import colored


def load_all_developers_dataset():
    try:
        print(colored("Loading dataset...", "blue"))

        # DEBUG
        # print(os.getcwd())
        # print(os.listdir("."))
        # DEBUG

        try:
            df = pd.read_csv(
                "./github-metrics/data/source/all_networks_developer_commits_2024-10-09.csv"
            )
        except FileNotFoundError:
            try:
                df = pd.read_csv(
                    "../data/source/all_networks_developer_commits_2024-10-09.csv"
                )
            except FileNotFoundError:
                df = pd.read_csv(
                    "data/source/all_networks_developer_commits_2024-10-09.csv"
                )
        df["month_year"] = pd.to_datetime(df["month_year"], format="%B_%Y")
        return df
    except Exception as e:
        print(colored(f"Error loading dataset: {e}", "red"))
        raise


def save_plot(plt, base_filename):
    """
    Save a matplotlib plot to a file with a timestamped filename.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"data/figures/{base_filename}_{current_date}.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()
