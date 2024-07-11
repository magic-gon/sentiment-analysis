# download_model.py
from transformers import BartTokenizerFast, BartForConditionalGeneration

def download_model_and_tokenizer():
    model_name = "facebook/bart-large-mnli"
    # Download and save the model
    model = BartForConditionalGeneration.from_pretrained(model_name)
    model.save_pretrained('/app/model')
    # Download and save the tokenizer
    tokenizer = BartTokenizerFast.from_pretrained(model_name)
    tokenizer.save_pretrained('/app/model')

if __name__ == "__main__":
    download_model_and_tokenizer()