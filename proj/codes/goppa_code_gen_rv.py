from pythonrv import rv
import goppa_code_gen


@rv.monitor(gcd=goppa_code_gen.extended_gcd)
def positive_gcd_parameters(event):
    assert event.fn.gcd.inputs[0] >= 0
    assert event.fn.gcd.inputs[1] >= 0


@rv.monitor(inv=goppa_code_gen.modinv)
def correct_inv_parameters(event):
    assert event.fn.inv.inputs[0] >= 0
    assert event.fn.inv.inputs[1] >= 0
    assert event.fn.inv.inputs[0] <= event.fn.inv.inputs[1]


@rv.monitor(inv=goppa_code_gen.modinv)
def lower_result_inv(event):
    assert event.fn.inv.result >= 0
    assert event.fn.inv.result < event.fn.inv.inputs[1]
