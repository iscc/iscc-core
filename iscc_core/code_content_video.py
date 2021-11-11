# -*- coding: utf-8 -*-
"""
# ISCC Content-Code Video

The **Content-Code Video** is generated from MPEG-7 Video Frame Signatures.
Frame Signatures can be extracted with ffmpeg (see: https://www.ffmpeg.org/) using the
following command line parameters:

`$ ffmpeg -i video.mpg -vf fps=fps=5,signature=format=xml:filename=sig.xml -f null -`

The relevant frame signatures can be parsed from the following elements in sig.xml:

`<FrameSignature>0  0  0  1  0  0  1  0  1  1  0  0  1  1 ...</FrameSignature>`

!!! note
    it is also possible to extract the signatures in a more compact binary format
    but it requires a custom binary parser to decode the frame signaturs.
"""
from typing import Sequence, Tuple
from iscc_core.wtahash import wtahash
from iscc_core import codec
from iscc_core.options import opts


def gen_video_code(frame_signatures, bits=opts.video_bits):
    # type: (Sequence[Tuple[int]], int) -> str
    """Create an ISCC Content-Code Video with the latest standard algorithm."""
    return gen_video_code_v0(frame_signatures, bits)


def gen_video_code_v0(frame_signatures, bits=opts.video_bits):
    # type: (Sequence[Tuple[int]], int) -> str
    """Create an ISCC Content-Code Video with algorithm v0."""
    digest = hash_video_v0(frame_signatures)
    video_code = codec.encode_component(
        mtype=codec.MT.CONTENT,
        stype=codec.ST_CC.VIDEO,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    return video_code


def hash_video_v0(frame_signatures):
    # type: (Sequence[Tuple[int]]) -> bytes
    """Compute 256-bit video hash v0 from MP7 frame signatures."""
    sigs = set(frame_signatures)
    vecsum = [sum(col) for col in zip(*sigs)]
    video_hash_digest = wtahash(vecsum)
    return video_hash_digest
