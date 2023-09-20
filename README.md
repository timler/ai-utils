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