"""
This script allows you to interact with an OpenAI-powered assistant. It handles the setup of the assistant, 
manages file uploads, and facilitates a chat-like conversation between the user and the assistant.

Environment Files:
1. .env: This file should contain global environment variables. 
   Variables:
   - OPENAI_API_KEY: Your OpenAI API key.

2. assistant.env: This file is specific to the assistant's configuration.
   Variables:
   - ASSISTANT_NAME: Name of your OpenAI assistant. [required]
   - ASSISTANT_INSTRUCTIONS: Specific instructions or guidelines for the assistant. [required]
   - ASSISTANT_OPENING_QUESTION: An opening question or message that the assistant will use to start the conversation. [required]
   - ASSISTANT_MODEL: The model used by the assistant (e.g. "gpt-3.5-turbo"). [required]
   - ASSISTANT_TOOLS = A comma separated list of the tools used by the assistant (e.g. "retrieval, code_interpreter"). [optional]
   - ASSISTANT_FILE_FOLDER: Path to the folder containing files to upload for the assistant. [optional]
   - ASSISTANT_FILE_IDS: A comma-separated list of file IDs to be associated with the assistant. [optional]
   - ASSISTANT_ID: The unique identifier of the assistant [optional, if already created].

Usage:
1. Set up the required environment variables in the .env and assistant.env files.
2. Run the script. If the assistant is not already set up, the script will guide you through the process.
3. Once the assistant is set up, you can start chatting. Type your questions or messages, and the assistant will respond.
4. To exit the chat, type "exit".

Note: The script is designed to maintain the flow of conversation within a single thread for a seamless interaction experience.
"""
import sys
import os
from dotenv import load_dotenv
load_dotenv()
load_dotenv(dotenv_path='assistant.env')

import time
from datetime import datetime
from openai import OpenAI
client = OpenAI()

def upload_files(folder):
    """
    Uploads all files in the specified folder to OpenAI and returns their file IDs.

    :param folder: Path to the folder containing the files to be uploaded.
    :return: List of file IDs after uploading.
    """
    print(f"- Start uploading files from `{folder}`")
    file_ids = []

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            with open(file_path, "rb") as file:
                response = client.files.create(
                    file=file,
                    purpose="assistants"
                )
                file_id = response.id
                file_ids.append(file_id)
                print(".", end="", flush=True)

    print(f"\r- Finished uploading files. file_ids={file_ids}")
    return file_ids

def create_assistant(name, instructions, file_ids, model, tools_str):
    """
    Creates an OpenAI assistant with the specified parameters.

    :param name: Name of the assistant.
    :param instructions: Instructions for the assistant.
    :param file_ids: List of file IDs to be associated with the assistant.
    :param model: Model to be used by the assistant.
    :return: Created assistant object.
    """
    print(f"- Creating `{name}`\n")
    tools = [{"type": tool.strip()} for tool in tools_str.split(',') if tool.strip()]
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        file_ids=file_ids,
        tools=tools,
        model=model
    )
    print(f"- Finished creating the assistant")
    return assistant

def get_conversation_header(name, date):
    """
    Generates a conversation header with a name and timestamp.

    :param name: Name to include in the header.
    :param date: Timestamp for the header.
    :return: Formatted conversation header string.
    """
    timestamp = datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
    return f"[{name.upper()} - {timestamp}]"

def wait_for_run_completion(thread_id, run_id, sleep=1, timeout=300):
    """
    Waits for the completion of a run in a thread.

    :param thread_id: ID of the thread.
    :param run_id: ID of the run.
    :param sleep: Sleep time between checks.
    :param timeout: Maximum waiting time before timing out.
    :return: Status of the run if completed; None otherwise.
    """
    start_time = time.time()
    while True:
        try:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run_status.status == 'completed':
                return run_status
            elif time.time() - start_time > timeout:
                return None
        except Exception as e:
            print(f"Error retrieving run status: {e}")
        print(".", end="", flush=True)
        time.sleep(sleep)

def ask_assistant(assistant_id, thread_id, question, user_information):
    """
    Asks a question to the assistant and waits for the reply.

    :param assistant_id: ID of the assistant to ask the question.
    :param thread_id: ID of the thread for the conversation.
    :param question: Question to be asked.
    :param user_information: Additional information about the user.
    :return: ID of the thread containing the assistant's reply.
    """
    if thread_id is None:
        thread = client.beta.threads.create()
        thread_id = thread.id
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=user_information
    )
    if wait_for_run_completion(thread_id, run.id):
        return thread_id
    else:
        return None

def display_reply(thread_id):
    """
    Displays the latest reply from the assistant in the specified thread.

    :param thread_id: ID of the thread to display the reply from.
    """
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    if messages.data:
        message = messages.data[0]
        print(f"\r\n{get_conversation_header(message.role, message.created_at)}")
        for content in message.content:
            if content.type == 'text':
                print(content.text.value)
            else:
                print(content.type)

def setup_assistant(name):
    """
    Sets up the OpenAI assistant by either using pre-loaded file IDs from
    the environment or by uploading files from a specified folder.

    :param name: Name of the assistant to set up.
    """
    print(f"- Setting up the OpenAI assistant")

    file_ids_str = os.getenv('ASSISTANT_FILE_IDS')
    files_folder = os.getenv('ASSISTANT_FILE_FOLDER')
    if file_ids_str:
        file_ids = file_ids_str.split(',')
    elif files_folder:
        file_ids = upload_files(files_folder)
    else:
        file_ids = []

    instructions = os.getenv('ASSISTANT_INSTRUCTIONS')
    model = os.getenv('ASSISTANT_MODEL')
    tools = os.getenv('ASSISTANT_TOOLS')
    assistant = create_assistant(name, instructions, file_ids, model, tools)

    print(f"- Finished setting up the OpenAI assistant. Please save the id in the assistant.env file and run this script again.")
    print(f"ASSISTANT_ID = {assistant.id}")

def chat_with_assistant(assistant_id, name, opening_question, user_information, user_name):
    """
    Initiates a chat session with the AI assistant.

    :param assistant_id: ID of the assistant to chat with.
    :param name: Name of the assistant.
    :param opening_question: Opening question for the chat.
    :param user_information: Additional information about the user.
    :param user_name: Name of the user chatting with the assistant.
    """
    print(f"{get_conversation_header('assistant', time.time())}\nHello! {opening_question}")

    thread_id = None
    while True:
        print(f"\n{get_conversation_header(user_name, time.time())}")
        question = input()

        if question.strip().lower() == "exit":
            print("Exiting the chat. Goodbye!")
            break

        return_thread_id = ask_assistant(assistant_id, thread_id, question, user_information)
        if return_thread_id:
            thread_id = return_thread_id
            display_reply(thread_id)
        else:
            print(f"\r{get_conversation_header('assistant', time.time())}")
            print("I'm sorry, I'm currently experiencing difficulties and can't process your request right now. Please try again later or contact support if the issue persists.")

def main():
    """
    Main function to run the assistant setup and chat.
    """
    assistant_name = os.getenv('ASSISTANT_NAME')
    assistant_id = os.getenv('ASSISTANT_ID')

    print(f"{assistant_name}\n")

    if assistant_id:
        user_name = "Jane Doe"
        user_information = f"Please address the user as {user_name}. They are a premium customer."
        opening_question = os.getenv('ASSISTANT_OPENING_QUESTION')
        chat_with_assistant(assistant_id, assistant_name, opening_question, user_information, user_name)
    else:
        setup_assistant(assistant_name)

if __name__ == "__main__":
    main()