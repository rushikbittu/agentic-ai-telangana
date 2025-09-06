import typer
import yaml
import os
from datetime import datetime
from agents import llm_agent, logging_agent
from agents.provenance import save_run_metadata
from agents.orchestrator import Orchestrator  # NEW Orchestrator agent

app = typer.Typer()

@app.command()
def run_pipeline(config_path: str):
    # Load config
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Prepare output directory
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join("run_artifacts", today)
    os.makedirs(output_dir, exist_ok=True)

    logging_agent.log_event("Run started", output_dir)

    dataset_file = config["dataset_source"].get("location")
    llm_model = config.get("llm", {}).get("model")
    save_run_metadata(output_dir, config_path, dataset_file, llm_model)
    logging_agent.log_event("Saved run metadata", output_dir)

    # Initialize orchestrator
    llm = llm_agent.LLMAgent(model_name=llm_model)
    orchestrator = Orchestrator(llm, output_dir, config)

    typer.echo("🚀 Running agentic pipeline with dynamic orchestration...\n")
    transformed_df = orchestrator.run_pipeline()

    typer.echo("\n✅ Pipeline complete! Enter 'exit' to quit natural language Q&A.")

    # Interactive goal-driven Q&A
    while True:
        user_q = typer.prompt("\nAsk a question about the data")
        if user_q.lower() in ["exit", "quit"]:
            break
        answer = orchestrator.handle_query(user_q, transformed_df)
        typer.echo(f"\n🤖 LLM Answer:\n{answer}\n")

    logging_agent.log_event("Run completed", output_dir)


if __name__ == "__main__":
    app()
