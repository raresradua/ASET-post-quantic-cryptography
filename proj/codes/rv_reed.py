from pythonrv import rv
import proj.codes.reed_solomon

rv.configure(error_handler=rv.LoggingErrorHandler())


@rv.monitor(inv_=proj.codes.reed_solomon.get_random_msg)
def correct_inv_parameters(event):
    assert event.fn.inv_.inputs[0] > 0


@rv.monitor(inv=proj.codes.reed_solomon.get_random_error)
def lower_result_inv(event):
    assert event.fn.inv.inputs[0] > 0
    assert event.fn.inv.inputs[1] > 0


@rv.monitor(inv_mat=proj.codes.reed_solomon.random_inv_matrix)
def random_inv(event):
    assert event.fn.inv_mat.inputs[0] > 0


@rv.monitor(rpm=proj.codes.reed_solomon.random_perm_matrix)
def poww(event):
    assert len(event.fn.rpm.inputs) == 1
    assert event.fn.rpm.inputs[0] > 0
