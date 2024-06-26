class LLM:
    def __init__(self, api_key):
        import google.generativeai as genai
        genai.configure(api_key=api_key) # API Key

        safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE"}]

        self.model = genai.GenerativeModel('gemini-pro', safety_settings)
        self.generation_config=genai.types.GenerationConfig(candidate_count=1, max_output_tokens=900, temperature=0.1, top_p=.9)
    
    def generate(self, inp):
        '''Generates output using Google API, given the input.'''
        try:
            response = self.model.generate_content(inp+"Answer in one sentences.", generation_config=self.generation_config)
        except:
            return 'Failed to fetch data from API'
        return response.text
