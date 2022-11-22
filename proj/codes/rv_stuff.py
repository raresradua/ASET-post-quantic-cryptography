from pythonrv import rv
import goppa_code

rv.configure(error_handler=rv.LoggingErrorHandler())


@rv.monitor(gcd=goppa_code.extended_gcd)
def positive_gcd_parameters(event):
    assert event.fn.gcd.inputs[0] >= 0
    assert event.fn.gcd.inputs[1] >= 0


@rv.monitor(inv_=goppa_code.modinv)
def correct_inv_parameters(event):
    assert event.fn.inv_.inputs[0] >= 0
    assert event.fn.inv_.inputs[1] >= 0
    assert event.fn.inv_.inputs[0] <= event.fn.inv_.inputs[1]


@rv.monitor(inv=goppa_code.modinv)
def lower_result_inv(event):
    if event.fn.inv.result is None:
        assert event.fn.inv.result, 'Result of modinv is None'
    else:
        assert event.fn.inv.result >= 0, 'Result of modinv is not >= 0'
        assert event.fn.inv.result < event.fn.inv.inputs[1], 'Not ok'
        event.success('Everyting is fine. Result of modinv is {}'.format(event.fn.inv.result))