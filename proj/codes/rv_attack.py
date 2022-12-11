from pythonrv import rv
import proj.codes.attack

rv.configure(error_handler=rv.LoggingErrorHandler())


@rv.monitor(ge=proj.codes.attack.generate_errors)
def positive_gcd_parameters(event):
    assert len(event.fn.ge.inputs[0]) > 0 and event.fn.ge.inputs[0]
    assert event.fn.ge.inputs[1] >= 0


@rv.monitor(atk=proj.codes.attack.attack_cipher)
def positive_gcd_parameters(event):
    assert len(event.fn.ge.inputs[0]) > 0 and len(event.fn.ge.inputs[1]) > 0 and event.fn.ge.inputs[2] and event.fn.ge.inputs[3]