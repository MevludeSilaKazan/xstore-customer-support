"""
XStore Customer Support Agent
Main LangGraph agent implementation.
"""

import os
from typing import TypedDict, Optional
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Import prompts
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.store_config import STORE, CATEGORIES
from src.prompts.tr_prompts import get_tr_prompts, TR_METADATA
from src.prompts.en_prompts import get_en_prompts, EN_METADATA


# Language configuration
LANG = {
    "tr": {
        "name": TR_METADATA["name"],
        "cat": TR_METADATA["categories"],
        "sent": TR_METADATA["sentiments"],
        "prompts": get_tr_prompts()
    },
    "en": {
        "name": EN_METADATA["name"],
        "cat": EN_METADATA["categories"],
        "sent": EN_METADATA["sentiments"],
        "prompts": get_en_prompts()
    }
}


class State(TypedDict):
    """State for the customer support agent."""
    query: str
    language: str
    category: str
    sentiment: str
    response: str


def get_llm():
    """Get the LLM instance."""
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0
    )


def normalize_category(category: str) -> str:
    """Normalize category to standard format."""
    c = category.lower().strip()
    mapping = {
        "product": "product", "ürün": "product", "beden": "product", "size": "product",
        "order": "order", "sipariş": "order", "kargo": "order", "shipping": "order",
        "return": "return", "iade": "return", "değişim": "return", "exchange": "return",
        "payment": "payment", "ödeme": "payment", "fatura": "payment", "taksit": "payment",
        "account": "account", "hesap": "account", "şifre": "account",
        "campaign": "campaign", "kampanya": "campaign", "indirim": "campaign",
        "general": "general", "genel": "general"
    }
    return mapping.get(c, "general")


def normalize_sentiment(sentiment: str) -> str:
    """Normalize sentiment to standard format."""
    s = sentiment.lower().strip()
    mapping = {
        "pozitif": "positive", "positive": "positive",
        "nötr": "neutral", "neutral": "neutral",
        "negatif": "negative", "negative": "negative"
    }
    return mapping.get(s, "neutral")


# Node functions
def detect_language(state: State) -> State:
    """Detect the language of the query."""
    if state.get("language") in ["tr", "en"]:
        return {"language": state["language"]}
    
    prompt = ChatPromptTemplate.from_template(
        "Is this Turkish or English? Reply ONLY 'tr' or 'en': {query}"
    )
    result = (prompt | get_llm()).invoke({"query": state["query"]}).content.strip().lower()
    return {"language": result if result in ["tr", "en"] else "tr"}


def categorize(state: State) -> State:
    """Categorize the customer query."""
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["categorize"])
    result = (prompt | get_llm()).invoke({"query": state["query"]}).content
    return {"category": normalize_category(result)}


def analyze_sentiment(state: State) -> State:
    """Analyze the sentiment of the query."""
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["sentiment"])
    result = (prompt | get_llm()).invoke({"query": state["query"]}).content
    return {"sentiment": normalize_sentiment(result)}


def handle_product(state: State) -> State:
    """Handle product-related queries."""
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["product"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}


def handle_order(state: State) -> State:
    """Handle order-related queries."""
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["order"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}


def handle_return(state: State) -> State:
    """Handle return-related queries."""
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["return"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}


def handle_payment(state: State) -> State:
    """Handle payment-related queries."""
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["payment"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}


def handle_account(state: State) -> State:
    """Handle account-related queries."""
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["account"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}


def handle_campaign(state: State) -> State:
    """Handle campaign-related queries."""
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["campaign"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}


def handle_general(state: State) -> State:
    """Handle general queries."""
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["general"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}


def escalate(state: State) -> State:
    """Escalate to human agent."""
    lang = state.get("language", "tr")
    return {"response": LANG[lang]["prompts"]["escalate"]}


def route(state: State) -> str:
    """Route based on sentiment and category."""
    if state["sentiment"] == "negative":
        return "escalate"
    return f"handle_{state['category']}"


def build_graph():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("detect_language", detect_language)
    workflow.add_node("categorize", categorize)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("handle_product", handle_product)
    workflow.add_node("handle_order", handle_order)
    workflow.add_node("handle_return", handle_return)
    workflow.add_node("handle_payment", handle_payment)
    workflow.add_node("handle_account", handle_account)
    workflow.add_node("handle_campaign", handle_campaign)
    workflow.add_node("handle_general", handle_general)
    workflow.add_node("escalate", escalate)
    
    # Add edges
    workflow.add_edge("detect_language", "categorize")
    workflow.add_edge("categorize", "analyze_sentiment")
    workflow.add_conditional_edges("analyze_sentiment", route, {
        "handle_product": "handle_product",
        "handle_order": "handle_order",
        "handle_return": "handle_return",
        "handle_payment": "handle_payment",
        "handle_account": "handle_account",
        "handle_campaign": "handle_campaign",
        "handle_general": "handle_general",
        "escalate": "escalate"
    })
    
    # Connect all handlers to END
    for cat in CATEGORIES:
        workflow.add_edge(f"handle_{cat}", END)
    workflow.add_edge("escalate", END)
    
    # Set entry point
    workflow.set_entry_point("detect_language")
    
    return workflow.compile()


# Build the app
app = build_graph()


def ask(query: str, language: Optional[str] = None) -> dict:
    """
    Process a customer query and return the response.
    
    Args:
        query: The customer's question
        language: Optional language code ('tr' or 'en'). Auto-detected if not provided.
    
    Returns:
        Dictionary with language, category, sentiment, and response.
    """
    state = {"query": query}
    if language and language in ["tr", "en"]:
        state["language"] = language
    
    result = app.invoke(state)
    lang = result["language"]
    
    return {
        "query": query,
        "language": LANG[lang]["name"],
        "language_code": lang,
        "category": LANG[lang]["cat"][result["category"]],
        "category_code": result["category"],
        "sentiment": LANG[lang]["sent"][result["sentiment"]],
        "sentiment_code": result["sentiment"],
        "response": result["response"]
    }


def print_response(result: dict):
    """Pretty print the response."""
    print("=" * 70)
    print(f"🛒 {STORE['name']} | {result['language']}")
    print("=" * 70)
    print(f"👤 Customer: {result['query']}")
    print(f"🏷️  Category: {result['category']}")
    print(f"📊 Sentiment: {result['sentiment']}")
    print(f"\n🤖 Assistant:\n")
    print(result['response'])
    print("=" * 70 + "\n")


# Convenience function
def chat(query: str, language: Optional[str] = None):
    """Ask a question and print the formatted response."""
    result = ask(query, language)
    print_response(result)
    return result


if __name__ == "__main__":
    # Test
    print(f"✅ {STORE['name']} Customer Support Agent loaded!")
    print("\nTest queries:")
    
    chat("M beden tişört alacağım, kalıbı nasıl?")
    chat("What is your return policy?")
