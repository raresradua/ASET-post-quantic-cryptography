from pythonrv import rv
import proj.codes.goppa_code

rv.configure(error_handler=rv.LoggingErrorHandler())


@rv.monitor(gcd=proj.codes.goppa_code.extended_gcd)
def positive_gcd_parameters(event):
    assert event.fn.gcd.inputs[0] >= 0
    assert event.fn.gcd.inputs[1] >= 0


@rv.monitor(inv_=proj.codes.goppa_code.get_random_msg)
def correct_inv_parameters(event):
    assert event.fn.inv_.inputs[0] > 0


@rv.monitor(inv=proj.codes.goppa_code.get_random_error)
def lower_result_inv(event):
    assert event.fn.inv.inputs[0] > 0
    assert event.fn.inv.inputs[1] > 0


@rv.monitor(inv_mat=proj.codes.goppa_code.random_inv_matrix)
def random_inv(event):
    assert event.fn.inv_mat.inputs[0] > 0


@rv.monitor(poww=proj.codes.goppa_code.pow_)
def poww(event):
    assert len(event.fn.poww.inputs) == 2


@rv.monitor(mod_inv=goppa_code.mod_inv)
def mod_inv(event):
    if event.fn.inv.result is None:
        assert event.fn.inv.result, 'Result of modinv is None'
    else:
        assert event.fn.inv.result >= 0, 'Result of modinv is not >= 0'
        assert event.fn.inv.result < event.fn.inv.inputs[1], 'Not ok'
        event.success('Everyting is fine. Result of modinv is {}'.format(event.fn.inv.result))
