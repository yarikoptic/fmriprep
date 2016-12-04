#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Base fieldmap estimation
~~~~~~~~~~~~~~~~~~~~~~~~

* Subject can have no data for fieldmap estimation - unwarping should not modify
  the images.
* Subject can have phase-difference data.
* Subject can have a fieldmap acquisition.
* Subject can have :abbr:`pepolar (Phase-Encoding POLArity)` image series for a
  phase-encoding based estimation.
* Subject can have two or three of the above - return average.


"""
from __future__ import print_function, division, absolute_import, unicode_literals
from future.utils import raise_from

from nipype.interfaces import utility as niu
from nipype.pipeline import engine as pe
from nipype import logging

LOGGER = logging.getLogger('workflow')

def fmap_estimator(subject_data, settings=None):
    """
    This workflow selects the fieldmap estimation data available for the subject and
    returns the estimated fieldmap in Hz, along with a corresponding reference image.

    All estimation workflows must produce three outputs:

      * fmap: The estimated fieldmap itself
      * fmap_ref: the anatomical reference for the fieldmap (magnitude image, corrected SEm, etc.)
      * fmap_mask: a brain mask for the fieldmap


    """
    if subject_data['fmap'] == []:
        # When there is no data for fieldmap estimation, just return None
        return None

    # Otherwise, build the appropriate workflow(s)
    workflow = pe.Workflow(name='FieldmapEstimation')
    outputnode = pe.Node(niu.IdentityInterface(fields=['fmap', 'fmap_ref']),
                         name='outputnode')

    estimator_wfs = []
    if any(['phase' in fname for fname in subject_data['fmap']]):
        from .phdiff import phdiff_workflow
        phwf = phdiff_workflow()
        # set inputs
        # phdif.inputs.inputnode.input_images
        estimator_wfs.append(phwf)

    if any(['fieldmap' in fname for fname in subject_data['fmap']]):
        from .fmap import fmap_workflow
        fmapwf = fmap_workflow()
        # set inputs
        # phdif.inputs.inputnode.input_images
        estimator_wfs.append(fmapwf)

    if any(['epi' in fname for fname in subject_data['fmap']]):
        from .pepolar import pepolar_workflow
        pewf = pepolar_workflow()
        # set inputs
        # phdif.inputs.inputnode.input_images
        estimator_wfs.append(pewf)

    if len(estimator_wfs) > 1:
        # Average estimated workflows
        raise NotImplementedError
    else:
        workflow.connect([
            (estimator_wfs[0], outputnode, [
                ('outputnode.fmap', 'fmap'),
                ('outputnode.fmap_ref', 'fmap_ref'),
                ('outputnode.fmap_mask', 'fmap_mask')])
        ])


    return workflow
