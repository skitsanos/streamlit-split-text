from dataclasses import dataclass
from typing import List, Optional
import re
import tiktoken


@dataclass
class Chunk:
    text: str
    token_count: int
    overlap_token_count: Optional[int] = None
    paragraph_count: int = 0
    sentence_count: int = 0


def count_sentences(
        text: str
        ) -> int:
    """
    Count sentences using a simpler, more robust regex pattern.
    """
    # This pattern matches common sentence endings followed by spaces and capital letters
    return len(re.findall(r'[.!?]+[\s]+', text)) + 1


def split_into_sentences(
        text: str
        ) -> List[str]:
    """
    Split text into sentences using a more robust approach.
    """
    # First, split on common sentence endings
    segments = re.split(r'([.!?]+[\s]+)', text)

    # Recombine segments with their endings
    sentences = []
    for i in range(0, len(segments) - 1, 2):
        if i + 1 < len(segments):
            sentences.append(segments[i] + segments[i + 1])

    # Add the last segment if it exists and isn't empty
    if segments and segments[-1].strip():
        sentences.append(segments[-1])

    return [s.strip() for s in sentences if s.strip()]


def splitText(
        text,
        context_window_size=128000,
        overlap_tokens=200,
        tokenizer_name='gpt-4'
        ) -> List[Chunk]:
    try:
        import tiktoken
    except ImportError:
        raise ImportError("The 'tiktoken' library is required for this function.")

    enc = tiktoken.encoding_for_model(tokenizer_name)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    paragraphs = re.split(r'\n\s*\n', text)

    chunks = []
    current_chunk_tokens = []
    current_chunk_text = ''
    current_paragraph_count = 0
    current_sentence_count = 0
    i = 0

    while i < len(paragraphs):
        paragraph = paragraphs[i].strip()
        if not paragraph:
            i += 1
            continue

        paragraph_tokens = enc.encode(paragraph)
        paragraph_token_len = len(paragraph_tokens)
        paragraph_sentence_count = count_sentences(paragraph)

        if len(current_chunk_tokens) + paragraph_token_len <= context_window_size:
            current_chunk_tokens.extend(paragraph_tokens + enc.encode('\n\n'))
            current_chunk_text += paragraph + '\n\n'
            current_paragraph_count += 1
            current_sentence_count += paragraph_sentence_count
            i += 1
        else:
            if len(current_chunk_tokens) == 0:
                sentences = split_into_sentences(paragraph)
                j = 0
                while j < len(sentences):
                    sentence = sentences[j]
                    sentence_tokens = enc.encode(sentence)
                    if len(current_chunk_tokens) + len(sentence_tokens) <= context_window_size:
                        current_chunk_tokens.extend(sentence_tokens + [enc.encode(' ')[0]])
                        current_chunk_text += sentence + ' '
                        current_sentence_count += 1
                        j += 1
                    else:
                        if current_chunk_text.strip():
                            chunks.append(Chunk(
                                text=current_chunk_text.strip(),
                                token_count=len(current_chunk_tokens),
                                overlap_token_count=0,
                                paragraph_count=current_paragraph_count,
                                sentence_count=current_sentence_count
                            ))

                        overlap_chunk_tokens = current_chunk_tokens[
                                               -overlap_tokens:] if overlap_tokens > 0 else []
                        overlap_chunk_text = enc.decode(overlap_chunk_tokens)
                        current_chunk_tokens = overlap_chunk_tokens
                        current_chunk_text = overlap_chunk_text
                        current_paragraph_count = 0
                        current_sentence_count = 0
                i += 1
            else:
                chunks.append(Chunk(
                    text=current_chunk_text.strip(),
                    token_count=len(current_chunk_tokens),
                    overlap_token_count=overlap_tokens if overlap_tokens > 0 else 0,
                    paragraph_count=current_paragraph_count,
                    sentence_count=current_sentence_count
                ))

                overlap_chunk_tokens = current_chunk_tokens[
                                       -overlap_tokens:] if overlap_tokens > 0 else []
                overlap_chunk_text = enc.decode(overlap_chunk_tokens)
                current_chunk_tokens = overlap_chunk_tokens
                current_chunk_text = overlap_chunk_text
                current_paragraph_count = 0
                current_sentence_count = 0

    if current_chunk_text.strip():
        chunks.append(Chunk(
            text=current_chunk_text.strip(),
            token_count=len(current_chunk_tokens),
            overlap_token_count=overlap_tokens if overlap_tokens > 0 else 0,
            paragraph_count=current_paragraph_count,
            sentence_count=current_sentence_count
        ))

    return chunks