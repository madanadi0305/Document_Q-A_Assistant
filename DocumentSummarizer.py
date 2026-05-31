import pandas as pd
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from datetime import datetime
import json

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import traceback

USER_LOG_FILE = "user_logs.txt"
OUTPUT_LOG_FILE = "output_logs.txt"
ERROR_LOG_FILE = "error_logs.txt"
PROMPT_VERSION_FILE = "prompt_versions.json"


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_user_action(message):
    with open(USER_LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{get_timestamp()}] {message}\n")


def log_output(message):
    with open(OUTPUT_LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{get_timestamp()}] {message}\n")


def log_error(message):
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{get_timestamp()}] {message}\n")


def load_prompt_template():
    with open(PROMPT_VERSION_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    active_version = config.get("active_version")
    versions = config.get("versions", {})
    template_path = versions.get(active_version)

    if not active_version or not template_path:
        raise ValueError(
            "Invalid prompt version config. Ensure 'active_version' exists and maps to a template path."
        )

    with open(template_path, "r", encoding="utf-8") as file:
        template_content = file.read()

    return template_content, active_version, template_path

# Load environment variables
load_dotenv()
OPENAI_SECRET_KEY = os.getenv("OPENAI_SECRET_KEY")

# Initialize LLM
llm = ChatOpenAI(
    openai_api_key=OPENAI_SECRET_KEY,
    model_name="gpt-3.5-turbo",
    temperature=0.1
)

while True:
    user_input = input("Enter a key q to quit and c to continue: ")
    log_user_action(f"User pressed key: {user_input}")

    if user_input == "q":
        print("User quit the conversation")
        break

    elif user_input == "c":
        print("User initiated the conversation")
        log_user_action("User started a new request.")

        document_path = input("Attach the document to be summarized by providing the path (or q to cancel): ").strip()
        document_name=os.path.basename(document_path)
        log_user_action(f"User entered document path input: {document_name}")
        if document_path.lower() == "q":
            print("Document selection cancelled. Returning to main menu.")
            continue
        if not document_path:
            print("No document path provided. Returning to main menu.")
            continue
        if not os.path.exists(document_path):
            print(f"File not found: {document_path}. Please provide a valid path.")
            continue
        log_user_action(f"User attached document: {document_name}")

        # Load document (use PyPDFLoader for PDFs, TextLoader for .txt)
        if document_path.lower().endswith(".pdf"):
            loader = PyPDFLoader(document_path)
        else:
            loader = TextLoader(document_path)
        try:
            documents = loader.load()
        except Exception as exc:
            print(f"Unable to load document: {exc}")
            log_output("Failed to provide context")
            log_error(
                f"Document loading failed for '{document_path}': {exc}\n"
                f"{traceback.format_exc()}"
            )
            continue

        # Split document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        try:
            template_file, prompt_version, prompt_path = load_prompt_template()
            log_user_action(f"Active prompt version: {prompt_version} ({prompt_path})")
        except Exception as exc:
            print(f"Unable to load prompt version/template: {exc}")
            log_output("Failed to provide context")
            log_error(f"Prompt version/template load failed: {exc}\n{traceback.format_exc()}")
            continue

        user_query = input("Enter your question (or press Enter for summary): ").strip()
        if not user_query:
            user_query = "Please summarize the provided document content."
            log_user_action("User requested summary.")
        else:
            log_user_action(f"User asked: {user_query}")
        print("\nFirst chunk preview:\n")
        if chunks:
            print(chunks[0].page_content)
        else:
            no_chunk_message = "No readable content found in the document."
            print(no_chunk_message)
            log_output("Failed to provide context")
            log_error(f"No chunks produced for document: {document_path}")
            continue

        # Create prompt template
        prompt = PromptTemplate(
            input_variables=["text", "user_query"],
            template=template_file
        )

        # Create chain
        chain = prompt | llm

        # Stuff documents: join all chunks into one string (same as StuffDocumentsChain)
        combined_text = "\n\n".join(doc.page_content for doc in chunks)

        # Generate summary
        print("\nGenerating summary...\n")

        try:
            response = chain.invoke({"text": combined_text, "user_query": user_query})
        except Exception as exc:
            print(f"Unable to generate response: {exc}")
            log_output("Failed to provide context")
            log_error(f"Response generation failed: {exc}\n{traceback.format_exc()}")
            continue
        response_text = response.content if hasattr(response, "content") else str(response)
        if response_text.strip() == "I am sorry, I don't have the necessary information to answer this.":
            log_output("Failed to provide context")
        else:
            log_output("Summary was provided")

        print("\n===== DOCUMENT SUMMARY =====\n")
        print(response_text)
        #HTML format
        print(f"""
        <html>
        <body>
        <h1>Document Summary</h1>
        <p>{response_text}</p>
        </body>
        </html>
        """)
        print("\n============================\n")

        continue

    else:
        print("Invalid input. Press 'c' to continue or 'q' to quit.")