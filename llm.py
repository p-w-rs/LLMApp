from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import torch
from typing import Iterator, Optional, Dict, List
import queue
import threading

class LLMAssistant:
    def __init__(self, model_name: str = "NousResearch/Hermes-3-Llama-3.1-8B", system_prompt: str = "You are a helpful AI assistant. You aim to give accurate, helpful responses.", max_context_length: int = 32768):
        self.device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device in ["mps", "cuda"] else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=self.dtype, device_map=self.device, max_memory={self.device: "80GB"}
        )
        self.streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        self.system_prompt = system_prompt
        self.max_context_length = max_context_length
        self.conversations: Dict[str, List[Dict]] = {}
        self.lock = threading.Lock()

    def _generate_stream(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, max_new_tokens: int = 4096, temperature: float = 0.7, top_p: float = 0.9) -> Iterator[str]:
        generation_kwargs = dict(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            streamer=self.streamer
        )

        thread = threading.Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        for new_text in self.streamer:
            yield new_text

    def chat(self, messages: List[Dict], conversation_id: Optional[str] = None, **kwargs) -> Iterator[str]:
        with self.lock:
            if conversation_id:
                if conversation_id not in self.conversations:
                    self.conversations[conversation_id] = []
                conversation = self.conversations[conversation_id]
                conversation.extend(messages)

            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": self.system_prompt})

            inputs = self.tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")
            attention_mask = torch.ones_like(inputs)
            inputs = inputs.to(self.device)
            attention_mask = attention_mask.to(self.device)

            response_text = ""
            for chunk in self._generate_stream(inputs, attention_mask, **kwargs):
                response_text += chunk
                yield chunk

            if conversation_id:
                self.conversations[conversation_id].append({"role": "assistant", "content": response_text})
