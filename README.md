# ai-utils
A collection of AI-powered scripts for diverse tasks. From transcript processing to data manipulation, these tools harness AI to simplify and enhance workflows. Dive in and discover indispensable utilities for AI enthusiasts and developers.

## Transcripts

The `Transcripts` script is a utility that cleans an auto generated transcript in any format - as a file or directly from Youtube. It translates from spoken language to grammatically correct sentences, and also assigns speaker labels.

### Requirements

```bash
pip install langchain
pip install youtube-transcript-api
pip install pytube
```

### Environment Variables

Create a .env file with your OpenAI API key in the root folder:
```bash
OPENAI_API_KEY=xxx
```

### Usage

1. **YouTube Video Transcripts**:
    - To fetch and process transcripts from a YouTube video, use the script `transcripts.py`.
    - Example usage:
      ```bash
      python transcripts.py <youtube_video_id_or_filename> <speaker_info>
      ```

2. **File-Based Transcripts**:
    - If you have a local transcript file, the same `transcripts.py` script can process it.
    - Example usage:
      ```bash
      python transcripts.py transcript.txt 'Speaker details or context'
      ```

### Features

- **Speaker Identification**: Based on the provided speaker info, the script can enhance the transcript's clarity by identifying and labeling speakers.
- **Transcript Cleaning**: Redundant or unnecessary content is filtered out, leaving a clean and readable transcript.
- **Cost Calculation**: The script outputs the cost when it is finished.

### Limitations

- **Chunks**: The transcripts are split into 3950 character chunks with a 100 character overlap because it is not possible to send an entire transcript in a single message due to token limitations. This means that occasionally there will be repeated text and the LLM may be confused about who is speaking. ========== is used to delimit the chunks so it is easier to scan the cleaned transcript for issues.

## Assistant API demo

### Requirements

```bash
pip install openai
```

### Environment Variables

To run this script, you need to set the following environment variables in `.env` and `assistant.env` files:

Create a .env file with your OpenAI API key in the root folder:
```bash
OPENAI_API_KEY=xxx
```

Create a assistant.env file with the details about your assistant in the root folder:
```bash
ASSISTANT_NAME=
ASSISTANT_INSTRUCTIONS=
ASSISTANT_OPENING_QUESTION=
ASSISTANT_MODEL=
ASSISTANT_TOOLS=
ASSISTANT_FILE_FOLDER=
ASSISTANT_FILE_IDS=
ASSISTANT_ID=
```

- **ASSISTANT_NAME**: Name of your OpenAI assistant. [required]
- **ASSISTANT_INSTRUCTIONS**: Specific instructions or guidelines for the assistant. [required]
- **ASSISTANT_OPENING_QUESTION**: An opening question or message that the assistant will use to start the conversation. [required]
- **ASSISTANT_MODEL**: The model used by the assistant (e.g. "gpt-3.5-turbo"). [required]
- **ASSISTANT_TOOLS**: A comma separated list of the tools used by the assistant (e.g. "retrieval, code_interpreter"). [optional]
- **ASSISTANT_FILE_FOLDER**: Path to the folder containing files to upload for the assistant. [optional]
- **ASSISTANT_FILE_IDS**: A comma-separated list of file IDs to be associated with the assistant. [optional]
- **ASSISTANT_ID**: The unique identifier of the assistant [optional, if already created].

### Usage

1. Ensure all required environment variables are set in the .env and assistant.env files.
2. Run the script: python assistant.py.
  * If the assistant is not already set up, the script will guide you through the process.
  * Once the assistant is set up, you can start chatting by typing your questions or messages. The assistant will respond accordingly.

Type "exit" to end the chat session.

### Features

- **Assistant Setup**: Guides you through the process of setting up an assistant
- **Basic assistant customization**: Allows customization of the assistant’s name, model, and initial questions.
- **File upload**: Uploads files in a specified folder to be used by the assistant
- **Basic conversation management**: Maintains a conversation thread, allowing for a seamless chat experience.

### Limitations

- **Error Handling**: The script currently has basic error handling. In case of API failure or network issues, it might not respond as expected.
- **File Types**: The script is designed to upload PDF files. Other file types have not been tested.
- **Thread Management**: The conversation thread is maintained in a single session. Restarting the script will create a new conversation thread, and the thread may get impossibly large during a long conversation