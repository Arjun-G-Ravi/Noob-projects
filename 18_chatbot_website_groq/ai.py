class LLM:
    def __init__(self, api_key):
        import os
        from groq import Groq
        self.client = Groq(api_key=api_key)

    def generate(self, inp):
        '''Generates output using Google API, given the input.'''
        chat_completion = self.client.chat.completions.create(
            messages=[{"role": "user","content": "Explain the importance of fast language models"}],
            model="mixtral-8x7b-32768",)
        return chat_completion.choices[0].message.content