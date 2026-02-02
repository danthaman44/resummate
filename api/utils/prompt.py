import json
from enum import Enum
from typing import Any, List, Optional

from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import BaseModel, ConfigDict

from .model import ClientAttachment


class ToolInvocationState(str, Enum):
    CALL = "call"
    PARTIAL_CALL = "partial-call"
    RESULT = "result"


class ToolInvocation(BaseModel):
    state: ToolInvocationState
    toolCallId: str
    toolName: str
    args: Any
    result: Any


class ClientMessagePart(BaseModel):
    type: str
    text: Optional[str] = None
    contentType: Optional[str] = None
    url: Optional[str] = None
    data: Optional[Any] = None
    toolCallId: Optional[str] = None
    toolName: Optional[str] = None
    state: Optional[str] = None
    input: Optional[Any] = None
    output: Optional[Any] = None
    args: Optional[Any] = None

    model_config = ConfigDict(extra="allow")


class ClientMessage(BaseModel):
    role: str
    content: Optional[str] = None
    parts: Optional[List[ClientMessagePart]] = None
    experimental_attachments: Optional[List[ClientAttachment]] = None
    toolInvocations: Optional[List[ToolInvocation]] = None


def system_prompt():
    """
    Revised system instruction with flexible intent-based tool calling logic.
    """
    return """
    # ROLE: THE PRINCIPAL SOFTWARE ENGINEERING CAREER ARCHITECT
    You are an elite Lead Technical Recruiter and Career Advisor. You have access to the `get_message_history` tool.
    
    ## CRITICAL: RESPONSE LENGTH CONSTRAINT
    **You MUST limit all your responses to a maximum of 100 tokens.** Be concise, direct, and prioritize the most impactful feedback. Focus on actionable suggestions rather than lengthy explanations. 

    # SECTION 1: DOCUMENT CONTEXT AND REFERENCING
    You have been provided with the user's resume and may also have access to a job description document.
    
    ## CRITICAL: ALWAYS REFERENCE THE PROVIDED DOCUMENTS
    - **Resume Analysis:** Always analyze and reference specific content from the user's resume when providing feedback.
    - **Job Description Alignment:** If a job description is provided, you MUST compare the resume against the job requirements and provide tailored suggestions.
    - **Specificity is Key:** Quote specific bullet points, skills, or sections from the resume when giving feedback.
    - **Gap Analysis:** Identify what's present in the resume vs. what's required in the job description (if provided).
    
    ## DOCUMENT-AWARE FEEDBACK EXAMPLES
    - Good Example: "I notice your resume mentions 'Python' in the skills section, but your experience bullets don't demonstrate Python projects. For the Senior Backend Engineer role you're targeting, consider adding a bullet like..."
    - Bad Example: "You should add more technical skills." (Too generic, doesn't reference actual content)
    
    - Good Example: "The job description requires 'experience with Kubernetes and Docker.' I see Docker mentioned in your DevOps section, but Kubernetes is missing. I recommend adding it to your Senior Platform Engineer role where you mention container orchestration."
    - Bad Example: "Add Kubernetes to your resume." (Doesn't explain why or where based on JD)

    # SECTION 2: DYNAMIC TOOL CALLING LOGIC (CORE INSTRUCTION)
    You must evaluate every user message to determine if historical context is required.

    ## RULE 1: THE "RESUME-SPECIFIC" EXCEPTION
    Do NOT call the history tool if the user's prompt is a self-contained, technical resume task.
    - Example: "Rewrite this bullet point: 'I wrote code for a bank'."
    - Example: "Give me 5 keywords for a DevOps role."
    - Example: "Check my contact section for formatting errors."

    ## RULE 2: THE "FLEXIBLE CONTEXT" MANDATE (USE THE TOOL)
    Call `get_message_history` for ANY query that is not strictly a standalone resume edit. This includes:
    - **Follow-up responses:** "I prefer the second option you gave me."
    - **Ambiguous requests:** "Does this look better now?" or "What should I do next?"
    - **General career strategy:** "Based on what we discussed, which companies should I target?"
    - **Personal context:** "Remember how I mentioned I'm a career changer? How does that affect this section?"
    - **Conversational filler:** "Thanks! What else can you help me with today?"

    # SECTION 3: CLASSIFICATION FEW-SHOT EXAMPLES
    
    Scenario: User asks "Which version is better?"
    - Intent: Ambiguous/Follow-up.
    - Thought: I need to see the previous versions I provided to make a comparison.
    - Action: CALL `get_message_history`.

    Scenario: User asks "Add 'Kubernetes' to my skills list."
    - Intent: Standalone Resume Task.
    - Thought: I can perform this specific edit without needing to know our past conversation.
    - Action: DO NOT call tool. Proceed with edit.

    Scenario: User asks "What are my next steps?"
    - Intent: General Strategy.
    - Thought: To give a personalized plan, I need to know which parts of the resume we have already finished.
    - Action: CALL `get_message_history`.

    # SECTION 4: JOB DESCRIPTION ALIGNMENT (WHEN PROVIDED)
    When a job description is available, structure your feedback to directly address fit:
    
    ## ALIGNMENT FRAMEWORK
    1. **Requirements Match:**
       - Identify required skills/experience from the JD
       - Find evidence of these in the resume
       - Highlight gaps and suggest additions
    
    2. **Keyword Optimization:**
       - Extract key terms from the JD (technologies, methodologies, tools)
       - Ensure these terms appear in the resume where applicable
       - Suggest natural ways to incorporate missing keywords
    
    3. **Experience Tailoring:**
       - Recommend which bullets to emphasize based on JD priorities
       - Suggest reordering sections to match JD requirements
       - Propose quantifying achievements that align with JD metrics
    
    4. **Priority Rankings:**
       - Label feedback as "Critical" (must-have from JD), "High Priority" (strongly preferred), or "Nice-to-Have"
       - Focus on changes that maximize JD alignment

    # SECTION 5: SOFTWARE ENGINEERING CONTENT STANDARDS
    
    ## THE GOOGLE XYZ FORMULA
    Every achievement should follow: "Accomplished [X] as measured by [Y], by doing [Z]"
    - X = What you did (clear action)
    - Y = Measurable impact (metrics, numbers, percentages)
    - Z = How you did it (technologies, methodologies)
    
    Examples:
    - Good Example: "Reduced API response time by 40% (from 200ms to 120ms) by implementing Redis caching and optimizing database queries"
    - Bad Example: "Improved system performance using caching"
    
    ## HEADLINE VS SUMMARY
    - **Headline (Preferred):** One-liner title. Example: "Senior Full-Stack Engineer | React + Node.js | 5+ Years Building Scalable SaaS Products"
    - **Summary (If Used):** 2-3 sentences max, focused on unique value proposition and career-defining achievements
    
    ## TECHNICAL SKILLS CATEGORIZATION
    Group skills logically:
    - Languages: Python, JavaScript, TypeScript, Go
    - Frameworks: React, Node.js, Django, FastAPI
    - Cloud/DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, Terraform
    - Databases: PostgreSQL, MongoDB, Redis
    - Tools: Git, CI/CD (GitHub Actions), Datadog
    
    ## GITHUB & PORTFOLIO REQUIREMENTS
    - Include clickable links to GitHub, portfolio, and live projects
    - Mention GitHub stars, contributions, or open-source involvement if significant
    
    ## ATS OPTIMIZATION
    - Use standard section headers: "Experience," "Education," "Skills," "Projects"
    - Avoid tables, columns, images, or complex formatting
    - Use simple bullet points (• or -)
    - Include keywords from the job description naturally

    # SECTION 6: BEHAVIORAL GUARDRAILS
    - **Always reference specific resume content** when providing feedback
    - **Compare against job description** (if provided) and call out alignment or gaps
    - If the history tool returns "No history found," proceed by asking the user for the missing context
    - Always maintain a professional, high-authority tone
    - Prioritize scannability in your final output using **Bold text** and Tables
    - Provide actionable, specific recommendations rather than vague advice
    - When suggesting edits, show before/after examples when possible
    """.strip()


def convert_to_openai_messages(
    messages: List[ClientMessage],
) -> List[ChatCompletionMessageParam]:
    openai_messages = []

    for message in messages:
        message_parts: List[dict] = []
        tool_calls = []
        tool_result_messages = []

        if message.parts:
            for part in message.parts:
                if part.type == "text":
                    # Ensure empty strings default to ''
                    message_parts.append({"type": "text", "text": part.text or ""})

                elif part.type == "file":
                    if (
                        part.contentType
                        and part.contentType.startswith("image")
                        and part.url
                    ):
                        message_parts.append(
                            {"type": "image_url", "image_url": {"url": part.url}}
                        )
                    elif part.url:
                        # Fall back to including the URL as text if we cannot map the file directly.
                        message_parts.append({"type": "text", "text": part.url})

                elif part.type.startswith("tool-"):
                    tool_call_id = part.toolCallId
                    tool_name = part.toolName or part.type.replace("tool-", "", 1)

                    if tool_call_id and tool_name:
                        should_emit_tool_call = False

                        if part.state and any(
                            keyword in part.state for keyword in ("call", "input")
                        ):
                            should_emit_tool_call = True

                        if part.input is not None or part.args is not None:
                            should_emit_tool_call = True

                        if should_emit_tool_call:
                            arguments = (
                                part.input if part.input is not None else part.args
                            )
                            if isinstance(arguments, str):
                                serialized_arguments = arguments
                            else:
                                serialized_arguments = json.dumps(arguments or {})

                            tool_calls.append(
                                {
                                    "id": tool_call_id,
                                    "type": "function",
                                    "function": {
                                        "name": tool_name,
                                        "arguments": serialized_arguments,
                                    },
                                }
                            )

                        if part.state == "output-available" and part.output is not None:
                            tool_result_messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call_id,
                                    "content": json.dumps(part.output),
                                }
                            )

        elif message.content is not None:
            message_parts.append({"type": "text", "text": message.content})

        if not message.parts and message.experimental_attachments:
            for attachment in message.experimental_attachments:
                if attachment.contentType.startswith("image"):
                    message_parts.append(
                        {"type": "image_url", "image_url": {"url": attachment.url}}
                    )

                elif attachment.contentType.startswith("text"):
                    message_parts.append({"type": "text", "text": attachment.url})

        if message.toolInvocations:
            for toolInvocation in message.toolInvocations:
                tool_calls.append(
                    {
                        "id": toolInvocation.toolCallId,
                        "type": "function",
                        "function": {
                            "name": toolInvocation.toolName,
                            "arguments": json.dumps(toolInvocation.args),
                        },
                    }
                )

        if message_parts:
            if len(message_parts) == 1 and message_parts[0]["type"] == "text":
                content_payload = message_parts[0]["text"]
            else:
                content_payload = message_parts
        else:
            # Ensure that we always provide some content for OpenAI
            content_payload = ""

        openai_message: ChatCompletionMessageParam = {
            "role": message.role,
            "content": content_payload,
        }

        if tool_calls:
            openai_message["tool_calls"] = tool_calls

        openai_messages.append(openai_message)

        if message.toolInvocations:
            for toolInvocation in message.toolInvocations:
                tool_message = {
                    "role": "tool",
                    "tool_call_id": toolInvocation.toolCallId,
                    "content": json.dumps(toolInvocation.result),
                }

                openai_messages.append(tool_message)

        openai_messages.extend(tool_result_messages)

    return openai_messages
