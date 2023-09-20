"""
https://python.langchain.com/docs/integrations/document_loaders/youtube_transcript

# pip install langchain
# pip install youtube-transcript-api
# pip install pytube
"""
import sys
import os

from dotenv import load_dotenv
load_dotenv()

from typing import List, Tuple

from langchain.callbacks import get_openai_callback
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.youtube import YoutubeLoader
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
GPT4 = "gpt-4"
GPT3 = "gpt-3.5-turbo"

fix_prompt_template = """Please process the partial video transcript provided below. First clean the transcript, 
and then reformat the text into a dialogue format with speaker labels.

Cleaning Instructions:
1. Add punctuation.
2. Remove ums, uhs, stuttering and stammering.
3. Remove extra whitespace.
4. Fix typos, especially those caused by accent misinterpretations. 
5. Add capitalisation.
6. Ensure grammar is correct but also retains the naturalness of spoken dialogue.

Reformatting Instructions:
Format the cleaned transcript into a dialogue using the speaker labels provided. If the transcript starts 
mid-sentence, refer to the previous conversation to maintain continuity.

About the speakers: ```{speaker_info}```

Previous Conversation: ```{last_paragraph}```

Transcript: ```{page_content}```

Important Notes:
- Retain the original intent and meaning of the sentences.
- Only make minor changes to sentences. Do not substitute words unless fixing accent misinterpretations.
- If there's a contradiction between grammar and natural speech, prioritize grammar.
"""
fix_prompt = PromptTemplate(
    input_variables=["page_content", "speaker_info", "last_paragraph"],
    template=fix_prompt_template,
)
llm = ChatOpenAI(temperature=0, model_name=GPT4)
fix_chain = LLMChain(llm=llm, prompt=fix_prompt)


def get_video_transcript(video_id: str) -> List[Document]:
    loader = YoutubeLoader(video_id)
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " "], chunk_size=3950, chunk_overlap=100)
    docs = loader.load_and_split(text_splitter)
    return docs

def get_transcript_from_file(filename: str) -> List[Document]:
    with open(filename) as f:  
        file_text = f.read()  
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " "], chunk_size=3950, chunk_overlap=100)
    return text_splitter.create_documents([file_text])  

def fix_transcript(page_content, speaker_info, last_paragraph) -> Tuple[str, float]:
    llm_inputs = {
        "speaker_info": speaker_info,
        "page_content": page_content,
        "last_paragraph": last_paragraph,
    }
    with get_openai_callback() as cb:
        response = fix_chain.predict(**llm_inputs)
    cleaned_page_content = response.strip()
    return cleaned_page_content, cb.total_cost

def get_last_paragraph(page_content) -> str:
    paragraphs = page_content.split("\n\n")
    if paragraphs:
        last_paragraph = paragraphs[-1]
        return last_paragraph
    return page_content

def main():
    if len(sys.argv) != 3:
        print("Usage: python transcripts.py <youtube_video_id_or_filename> <speaker_info>")
        print("E.g. `python transcripts.py '1234' 'Fred is interviewing Martha about her new book.'`")
        print("Or:  `python transcripts.py 'transcript.txt' 'Fred is interviewing Martha about her new book.'`")
        return
    
    input_id_or_file = sys.argv[1]
    speaker_info = sys.argv[2]

    if os.path.isfile(input_id_or_file):
        docs = get_transcript_from_file(input_id_or_file)
        output_file_prefix = os.path.splitext(input_id_or_file)[0]
    else:
        docs = get_video_transcript(input_id_or_file)
        output_file_prefix = input_id_or_file

    total_cost = 0
    cleaned_transcript = ""
    last_paragraph = None
    
    for idx, document in enumerate(docs, start=1):
        sys.stdout.write(f"\rProcessing chunk {idx}/{len(docs)}...")
        sys.stdout.flush()
        page_content = document.page_content
        result = fix_transcript(page_content, speaker_info, last_paragraph)
        cleaned_transcript += result[0]
        cleaned_transcript += "\n"
        cleaned_transcript += "="*10
        cleaned_transcript += "\n"
        last_paragraph = get_last_paragraph(result[0])
        total_cost += result[1]

    output_file_name = f"{output_file_prefix}_cleaned_transcript.txt"
    with open(output_file_name, "w") as output_file:
        output_file.write(cleaned_transcript)
    
    print("\nProcessing complete.")
    print("="*80)
    print("Cleaned transcript:")
    print(cleaned_transcript)
    print("="*80)
    print(f"Cost=${total_cost}")
    print("="*80)
    print(f"Saved to {output_file_name}")
    print("="*80)

if __name__ == "__main__":
    main()