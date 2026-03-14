"""E2E test: create conversation → chat with LLM → assess understanding"""
import httpx
import json
import sys

API = "http://127.0.0.1:8000/api"
LLM_HEADERS = {
    "X-LLM-Provider": "custom",
    "X-LLM-API-Key": "a12488be-58bb-4f52-93d0-26fee71d5507",
    "X-LLM-Model": "mihoyo.claude-4-6-sonnet",
    "X-LLM-Base-URL": "https://llm-open-ai.mihoyo.com/v1",
}


def step(label):
    print(f"\n{'='*60}\n  {label}\n{'='*60}")


def main():
    # Step 1: Create conversation
    step("Step 1: Create conversation for 'prompt-basics'")
    r = httpx.post(f"{API}/dialogue/conversations", json={"concept_id": "prompt-basics"})
    assert r.status_code == 200, f"Failed: {r.status_code} {r.text}"
    data = r.json()
    conv_id = data["conversation_id"]
    print(f"  conv_id: {conv_id}")
    print(f"  opening: {data['opening_message'][:100]}...")

    # Step 2: Send user message (stream)
    step("Step 2: Chat — user explains prompt basics")
    user_msg = (
        "Prompt就是给AI的指令文本。你需要告诉AI你想要什么输出。"
        "比如'帮我写首关于春天的诗'就是一个prompt。"
        "好的prompt要清晰、具体，给足上下文，才能得到高质量回复。"
    )
    print(f"  User: {user_msg[:80]}...")

    headers = {"Content-Type": "application/json", **LLM_HEADERS}
    body = {"conversation_id": conv_id, "message": user_msg}

    full_response = ""
    with httpx.stream("POST", f"{API}/dialogue/chat", headers=headers, json=body, timeout=60.0) as r:
        print(f"  HTTP Status: {r.status_code}")
        for line in r.iter_lines():
            if line.startswith("data: "):
                d = json.loads(line[6:])
                if d["type"] == "chunk":
                    full_response += d["content"]
                elif d["type"] == "done":
                    print(f"  [DONE] suggest_assess={d.get('suggest_assess')}, turn={d.get('turn')}")

    print(f"  AI response ({len(full_response)} chars):")
    print(f"  {full_response[:300]}...")

    if not full_response:
        print("\n  *** ERROR: Empty AI response! Check server logs. ***")
        sys.exit(1)

    # Step 3-5: More rounds to trigger assessment suggestion
    more_msgs = [
        "清晰具体意味着要告诉AI确切的格式、长度、风格。比如'用200字总结这篇文章，用bullet points列出要点'。避免模糊词如'写点什么'。",
        "Prompt Engineering有几个高级技巧：Chain of Thought让AI一步步推理，Few-shot给AI几个示例，Role Playing让AI扮演专家角色。这些都能显著提升输出质量。",
        "总结一下：Prompt是人与AI沟通的桥梁。核心要素是角色、任务、上下文、格式。高级技巧包括CoT推理链、Few-shot示例、角色扮演。好的Prompt = 好的输出。",
    ]

    for i, msg in enumerate(more_msgs, start=3):
        step(f"Step {i}: Round {i-1} chat")
        body = {"conversation_id": conv_id, "message": msg}
        resp_text = ""
        with httpx.stream("POST", f"{API}/dialogue/chat", headers=headers, json=body, timeout=60.0) as r:
            for line in r.iter_lines():
                if line.startswith("data: "):
                    d = json.loads(line[6:])
                    if d["type"] == "chunk":
                        resp_text += d["content"]
                    elif d["type"] == "done":
                        print(f"  [DONE] suggest_assess={d.get('suggest_assess')}, turn={d.get('turn')}")
        print(f"  AI ({len(resp_text)} chars): {resp_text[:150]}...")

    # Step 6: Assessment
    step("Step 6: Request understanding assessment")
    body = {"conversation_id": conv_id}
    r = httpx.post(f"{API}/dialogue/assess", headers=headers, json=body, timeout=60.0)
    print(f"  HTTP Status: {r.status_code}")
    result = r.json()
    print(f"  Overall Score: {result.get('overall_score')}")
    print(f"  Mastered: {result.get('mastered')}")
    print(f"  Completeness: {result.get('completeness')}")
    print(f"  Accuracy: {result.get('accuracy')}")
    print(f"  Depth: {result.get('depth')}")
    print(f"  Examples: {result.get('examples')}")
    print(f"  Feedback: {result.get('feedback', '')[:200]}")
    if result.get("gaps"):
        print(f"  Gaps: {result['gaps']}")

    print(f"\n{'='*60}")
    print(f"  ✅ FULL E2E TEST PASSED")
    print(f"  Score: {result.get('overall_score')}/100  Mastered: {result.get('mastered')}")
    print(f"{'='*60}")
    return conv_id


if __name__ == "__main__":
    main()