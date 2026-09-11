"""Graph nodes that touch the machine rather than the model.

``preflight`` opens the graph, ``render`` closes it (ADR-0002, item 5). Both
are driven by state fields and skip when the state does not ask for them, so
a calibration run or a test with a fake model never probes ``vm_stat`` or
loads the voice model. The writing nodes still live in ``factory.pipeline.graph``
until step 5 splits them.
"""
