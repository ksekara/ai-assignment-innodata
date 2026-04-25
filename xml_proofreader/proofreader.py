"""GenAI-based proofreading using LangChain."""

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are an expert proofreader. Your task is to proofread text and annotate errors by wrapping the ORIGINAL erroneous text with <error> tags.

CRITICAL RULES:
1. The text inside <error>...</error> tags MUST be the EXACT original text (unchanged).
2. The correction goes in the "correction" attribute.
3. Each <error> tag MUST include:
   - type: one of [grammar, spelling, punctuation, capitalization, clarity, styleguide]
   - correction: the corrected form
   - reason: a short explanation
4. For styleguide errors, include a "reason" attribute with a brief description of the violated rule.
5. For non-styleguide errors, also include a "reason" attribute explaining the error.
6. Text that has no errors must remain EXACTLY as-is, character for character.
7. DO NOT change any whitespace, punctuation, or characters outside of <error> tags.
8. The ONLY change you make is wrapping erroneous text segments with <error> tags.
9. Return ONLY the annotated text, no explanations, no surrounding tags, no markdown.
10. If there are no errors, return the EXACT original text unchanged.
11. Follow the specific rule of the LANGUAGE also.

FORMAT:
<error type="TYPE" correction="CORRECTED" reason="REASON">original_text</error>

LANGUAGE: Proofread for {lang} language.

STYLE GUIDE RULES (apply these in addition to standard grammar/spelling/punctuation/capitalization):
{style_guide}

EXAMPLES:
Input: "My name is john."
Output: My name is <error type="capitalization" correction="John" reason="Proper nouns should be capitalized">john</error>.

Input: "The meeting is in January, 2024."
Output: The meeting is in <error type="styleguide" correction="January 2024" reason="No comma between month and year in dates">January, 2024</error>.

Input: "The report was filed on time."
Output: The report was filed on time.
"""


class Proofreader:
    """GenAI-based proofreader using LangChain."""

    def __init__(self, style_guide: str, lang: str = "en", model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.lang = lang
        self.style_guide = style_guide
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            lang=lang, style_guide=style_guide
        )

    def proofread(self, text: str) -> str:
        """Proofread a single text string and return annotated version."""
        if not text or not text.strip():
            return text

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(
                    content=f"Proofread the following text. Return ONLY the annotated text:\n\n{text}"
                ),
            ]
            response = self.llm.invoke(messages)
            result = response.content.strip()

            # Remove any surrounding quotes or code blocks the model might add
            if result.startswith("```") and result.endswith("```"):
                result = result[3:-3].strip()
                if result.startswith("xml"):
                    result = result[3:].strip()

            return result

        except Exception as e:
            logger.error(f"LangChain API call failed: {e}")
            raise
