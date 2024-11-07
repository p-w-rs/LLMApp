from llm import LLMAssistant

# Initialize with custom system prompt
assistant = LLMAssistant(
    system_prompt="You are an AI assistant with expertise in Python programming. Provide clear, efficient code solutions."
)

# Example conversation
messages = [
    {"role": "user", "content": "Write a function to calculate fibonacci numbers."}
]

# Stream the response
for chunk in assistant.chat(messages):
    print(chunk, end="", flush=True)
