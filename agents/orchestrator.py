# agents/orchestrator.py

import os
from agents import ingestion, standardization, cleaning, transformation, insights, logging_agent

class Orchestrator:
    def __init__(self, llm, output_dir, config):
        """
        Orchestrator manages the execution flow of all pipeline agents.
        """
        self.llm = llm
        self.output_dir = output_dir
        self.config = config

    def decide_next_step(self, context: dict) -> str:
        """
        Ask LLM which step to run next based on context.
        For now, fallback to static order.
        """
        prompt = f"""
        You are an AI orchestrator. 
        Current context: {context}.
        Decide which module to run next out of:
        [ingestion, standardization, cleaning, transformation, insights, stop].
        """
        try:
            decision = self.llm.ask(prompt)
            if decision:
                return decision.lower().strip()
        except Exception:
            pass

        # Fallback to static sequencing
        return context.get("next_step", "stop")

    def run_pipeline(self):
        """
        Runs the pipeline in sequence.
        Can later be replaced with fully agentic step-by-step planning.
        """
        logging_agent.log_event("Starting orchestration", self.output_dir)

        # Step 1: Ingestion
        raw_path = ingestion.load_dataset(self.config["dataset_source"], self.output_dir)
        logging_agent.log_event(f"Ingested data at {raw_path}", self.output_dir)

        # Step 2: Standardization
        std_path = standardization.standardize_data(raw_path, self.output_dir)
        logging_agent.log_event(f"Standardized data saved at {std_path}", self.output_dir)

        # Step 3: Cleaning
        clean_path = cleaning.clean_data(std_path, self.config, self.output_dir)
        logging_agent.log_event(f"Cleaned data saved at {clean_path}", self.output_dir)

        # Step 4: Transformation
        transformed_path = transformation.transform_data(clean_path, self.config, self.output_dir)
        logging_agent.log_event(f"Transformed data saved at {transformed_path}", self.output_dir)

        # Step 5: Insights
        summary_md, plot_path = insights.generate_insights(transformed_path, self.config, self.output_dir)
        logging_agent.log_event(f"Insights generated: {summary_md}, Plot: {plot_path}", self.output_dir)

        logging_agent.log_event("Pipeline orchestrated successfully", self.output_dir)

        return transformed_path

    def handle_query(self, user_question: str, transformed_path: str) -> str:
        """
        Handle natural language questions about the data by delegating to LLM.
        """
        try:
            with open(transformed_path, "r", encoding="utf-8") as f:
                data_snippet = "".join([next(f) for _ in range(20)])
        except Exception as e:
            data_snippet = f"[ERROR reading data: {e}]"

        prompt = f"""
        Dataset snippet:
        {data_snippet}

        User question: {user_question}

        Please answer concisely.
        """
        return self.llm.ask(prompt)
