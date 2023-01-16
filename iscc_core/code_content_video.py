# -*- coding: utf-8 -*-
"""*A similarity preserving hash for video content*

The **Content-Code Video** is generated from MPEG-7 video frame signatures.
The [iscc-sdk](https://github.com/iscc/iscc-sdk) uses [ffmpeg](https://www.ffmpeg.org) to
extract frame signatures with the following command line parameters:

`$ ffmpeg -i video.mpg -vf fps=fps=5,signature=format=xml:filename=sig.xml -f null -`

The relevant frame signatures can be parsed from the following elements in sig.xml:

`<FrameSignature>0  0  0  1  0  0  1  0  1  1  0  0  1  1 ...</FrameSignature>`

!!! tip
    It is also possible to extract the signatures in a more compact binary format.
    But the format requires a custom binary parser to decode the frame signaturs.
"""
from typing import Sequence, Tuple
import iscc_core as ic


def gen_video_code(frame_sigs, bits=ic.core_opts.video_bits):
    # type: (Sequence[ic.FrameSig], int) -> dict
    """
    Create an ISCC Video-Code with the latest standard algorithm.

    :param ic.FrameSig frame_sigs: Sequence of MP7 frame signatures
    :param int bits: Bit-length resulting Instance-Code (multiple of 64)
    :return: ISCC object with Video-Code
    :rtype: dict
    """
    return gen_video_code_v0(frame_sigs, bits)


def gen_video_code_v0(frame_sigs, bits=ic.core_opts.video_bits):
    # type: (Sequence[ic.FrameSig], int) -> dict
    """
    Create an ISCC Video-Code with algorithm v0.

    :param ic.FrameSig frame_sigs: Sequence of MP7 frame signatures
    :param int bits: Bit-length resulting Video-Code (multiple of 64)
    :return: ISCC object with Video-Code
    :rtype: dict
    """
    digest = soft_hash_video_v0(frame_sigs, bits=bits)
    video_code = ic.encode_component(
        mtype=ic.MT.CONTENT,
        stype=ic.ST_CC.VIDEO,
        version=ic.VS.V0,
        bit_length=bits,
        digest=digest,
    )
    iscc = "ISCC:" + video_code
    return dict(iscc=iscc)


def soft_hash_video_v0(frame_sigs, bits=ic.core_opts.video_bits):
    # type: (Sequence[ic.FrameSig], int) -> bytes
    """
    Compute video hash v0 from MP7 frame signatures.

    :param ic.FrameSig frame_sigs: 2D matrix of MP7 frame signatures
    :param int bits: Bit-length of resulting Video-Code (multiple of 64)
    """

    if not isinstance(frame_sigs[0], tuple):
        frame_sigs = [tuple(sig) for sig in frame_sigs]
    sigs = set(frame_sigs)
    vecsum = [sum(col) for col in zip(*sigs)]
    video_hash_digest = ic.alg_wtahash(vecsum, bits)
    return video_hash_digest
