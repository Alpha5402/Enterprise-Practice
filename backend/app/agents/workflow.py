"""LangGraph workflow for competitive intelligence analysis."""

import json
from typing import Any, Protocol, TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from app.agents.prompts import load_prompt
from app.schemas.analysis import StructuredAnalysisOutput


class ChatInvoker(Protocol):
    """Protocol for chat model invocations used by the workflow."""

    def invoke(self, input: list[SystemMessage | HumanMessage]) -> Any:
        """Invoke the model with chat messages."""


class AnalysisWorkflowState(TypedDict, total=False):
    """Mutable state passed across the LangGraph workflow."""

    competitor: str
    context: str
    sentiment: StructuredAnalysisOutput
    price: StructuredAnalysisOutput
    product: StructuredAnalysisOutput
    summary: StructuredAnalysisOutput


class AnalysisWorkflow:
    """Run multi-agent competitive analysis with LangGraph."""

    def __init__(self, chat_model: BaseChatModel | ChatInvoker) -> None:
        """Initialize the workflow with a LangChain chat model."""
        self.chat_model = chat_model
        self.graph = self._build_graph()

    def run(self, competitor: str, context: str) -> list[StructuredAnalysisOutput]:
        """Run the workflow and return all structured agent outputs."""
        result = self.graph.invoke({"competitor": competitor, "context": context})
        return [result["sentiment"], result["price"], result["product"], result["summary"]]

    def _build_graph(self) -> Any:
        """Build the LangGraph analysis workflow."""
        graph = StateGraph(AnalysisWorkflowState)
        graph.add_node("sentiment_agent", self._sentiment_agent)
        graph.add_node("price_agent", self._price_agent)
        graph.add_node("product_agent", self._product_agent)
        graph.add_node("summary_agent", self._summary_agent)
        graph.add_edge(START, "sentiment_agent")
        graph.add_edge(START, "price_agent")
        graph.add_edge(START, "product_agent")
        graph.add_edge("sentiment_agent", "summary_agent")
        graph.add_edge("price_agent", "summary_agent")
        graph.add_edge("product_agent", "summary_agent")
        graph.add_edge("summary_agent", END)
        return graph.compile()

    def _sentiment_agent(self, state: AnalysisWorkflowState) -> dict[str, StructuredAnalysisOutput]:
        """Run the sentiment analysis agent."""
        return {"sentiment": self._run_agent("sentiment", state["competitor"], state["context"])}

    def _price_agent(self, state: AnalysisWorkflowState) -> dict[str, StructuredAnalysisOutput]:
        """Run the pricing analysis agent."""
        return {"price": self._run_agent("price", state["competitor"], state["context"])}

    def _product_agent(self, state: AnalysisWorkflowState) -> dict[str, StructuredAnalysisOutput]:
        """Run the product analysis agent."""
        return {"product": self._run_agent("product", state["competitor"], state["context"])}

    def _summary_agent(self, state: AnalysisWorkflowState) -> dict[str, StructuredAnalysisOutput]:
        """Run the summary analysis agent."""
        agent_outputs = {
            "sentiment": state["sentiment"].model_dump(),
            "price": state["price"].model_dump(),
            "product": state["product"].model_dump(),
        }
        context = (
            f"Source context:\n{state['context']}\n\n"
            f"Agent outputs:\n{json.dumps(agent_outputs, ensure_ascii=False)}"
        )
        return {"summary": self._run_agent("summary", state["competitor"], context)}

    def _run_agent(
        self,
        prompt_name: str,
        competitor: str,
        context: str,
    ) -> StructuredAnalysisOutput:
        """Invoke one agent and parse strict JSON output."""
        prompt = load_prompt(prompt_name)
        response = self.chat_model.invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(content=self._user_message(competitor, context)),
            ]
        )
        content = response.content if hasattr(response, "content") else str(response)
        return StructuredAnalysisOutput.model_validate_json(str(content))

    def _user_message(self, competitor: str, context: str) -> str:
        """Create the user message shared by analysis agents."""
        return (
            f"Competitor: {competitor}\n\n"
            f"Context:\n{context}\n\n"
            "Return strict JSON only."
        )
