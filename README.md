# Starknet Star Tracker: GitHub Starknet Developer Insights

Access it live in: https://starknetstartracker.streamlit.app/

Starknet Star Tracker is a tool that allows you to analyze the GitHub activity of developers within the Starknet ecosystem. It provides insights into their monthly commit activity, involvement classification, and comparisons with other developers.

## Features

- Enter GitHub handles or upload a CSV file to specify the developers to analyze
- Visualize monthly commit activity using line plots
- Compare commit activity before and after a specified program end date
- Classify developers based on their recent activity level
- Identify new developers who started committing code after the program
- Compare the commit activity and growth rate of specified developers with other Starknet developers
- Generate a summary report in PowerPoint format

## Usage

1. Enter the GitHub handles of the developers you want to analyze, separated by commas, or upload a CSV file containing the handles in a single column.

2. (Optional) Specify a program end date in the format YYYY-MM-DD to analyze the impact of events like Basecamp or Hackathons on developer activity. Leave it blank to analyze overall activity.

3. (Optional) Enter an event name to associate with the analysis.

4. Click the "Analyze" button to generate the insights.

5. Explore the generated visualizations, classifications, and comparisons using the expandable sections.

6. The app automatically generates a PowerPoint report named `developer_insights_report.pptx` containing the summary and key findings.


## Run locally

1. Clone the repository:
   
   ```
   git clone https://github.com/omarespejel/starknet-star-tracker.git
   ```

2. Install the required dependencies:
3. 
   ```
   pip install -r requirements.txt
   ```

4. Run the Streamlit app:
5. 
   ```
   streamlit run main.py
   ```

6. Access the app in your web browser at `http://localhost:8501`


## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## Contact

For any questions or feedback, please contact Omar Espejel from the Starknet Foundation:
- Telegram: @espejelomar

## License

This project is licensed under the [MIT License](LICENSE).