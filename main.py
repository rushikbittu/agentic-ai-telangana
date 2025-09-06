import typer
import yaml
from agents import ingestion, standardization, cleaning, transformation, insights, llm_agent, logging_agent
import os
from datetime import datetime
from agents.provenance import save_run_metadata

app = typer.Typer()

@app.command()
def run_pipeline(config_path: str):

    with open(config_path) as f:
        config = yaml.safe_load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join("run_artifacts", today)
    os.makedirs(output_dir, exist_ok=True)

    logging_agent.log_event("Run started", output_dir)

    dataset_file = config["dataset_source"].get("location")
    llm_model = config.get("llm", {}).get("model")
    save_run_metadata(output_dir, config_path, dataset_file, llm_model)
    logging_agent.log_event("Saved run metadata", output_dir)

    raw_path = ingestion.load_dataset(config["dataset_source"], output_dir)
    logging_agent.log_event(f"Ingested data at {raw_path}", output_dir)

    std_path = standardization.standardize_data(raw_path, output_dir)
    logging_agent.log_event(f"Standardized data saved at {std_path}", output_dir)

    clean_path = cleaning.clean_data(std_path, config, output_dir)
    logging_agent.log_event(f"Cleaned data saved at {clean_path}", output_dir)

    transformed_path = transformation.transform_data(clean_path, config, output_dir)
    logging_agent.log_event(f"Transformed data saved at {transformed_path}", output_dir)

    summary_md, plot_path = insights.generate_insights(transformed_path, config, output_dir)
    logging_agent.log_event(f"Insights generated, summary: {summary_md}, plot: {plot_path}", output_dir)

    typer.echo("\nPipeline complete! Enter 'exit' to quit natural language Q&A.")
    while True:
        user_q = typer.prompt("Ask a question about the data")
        if user_q.lower() in ["exit", "quit"]:
            break
        answer = llm_agent.answer_question(user_q, transformed_path, config)
        typer.echo(f"LLM Answer:\n{answer}\n")

    logging_agent.log_event("Run completed", output_dir)

if __name__ == "__main__":
    app()
