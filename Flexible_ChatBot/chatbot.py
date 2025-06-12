import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local("vectordb", embedding, allow_dangerous_deserialization=True)
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})  # récupérer top 4 docs

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    language: str

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

# Prompt strict qui force le bot à ne répondre qu'à partir du contexte
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant qui répond uniquement avec les informations fournies dans le contexte ci-dessous. "
               "Si l'information n'est pas présente dans le contexte, dis simplement que tu ne sais pas."),
    MessagesPlaceholder(variable_name="messages"),
    ("user", "Voici le contexte du site :\n{context}\nQuestion: {question}")
])


def call_model(state: State):
    # Si state["messages"] est un ChatPromptValue ou un autre type LangChain,
    # essayons de récupérer le dernier message plus "safe"
    
    messages = state["messages"]
    
    # Si c’est une liste vraie, ça marche
    if isinstance(messages, list):
        query = messages[-1].content
    else:
        # Sinon essaye de convertir en liste ou accéder différemment
        try:
            query = list(messages)[-1].content
        except Exception:
            # Pour debug
            print("Type de messages:", type(messages))
            raise
    
    docs = retriever.invoke(query)
    
    print("\n=== Documents retrouvés ===")
    for i, doc in enumerate(docs):
        print(f"[{i+1}] {doc.page_content[:300]}...\n")

    doc_texts = "\n\n".join([d.page_content for d in docs])
    
    final_prompt = qa_prompt.invoke({
        "messages": messages,
        "context": doc_texts,
        "question": query
    })

    # Convertir en string si nécessaire
    final_prompt_str = final_prompt.to_string() if hasattr(final_prompt, "to_string") else str(final_prompt)

    print("\n=== Prompt envoyé au modèle ===\n", final_prompt_str[:1000], "\n")

    response = model.invoke(final_prompt_str)
    return {"messages": [response]}


workflow = StateGraph(state_schema=State)
workflow.add_node("model", call_model)
workflow.add_edge(START, "model")
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def ask_bot(question: str, thread_id="web-thread-1") -> str:
    config = {"configurable": {"thread_id": thread_id}}
    input_messages = [HumanMessage(content=question)]
    output = app.invoke({"messages": input_messages, "language": "fr"}, config)
    return output["messages"][-1].content
