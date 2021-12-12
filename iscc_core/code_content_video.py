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
from iscc_core.options import core_opts
from iscc_core.schema import ContentCodeVideo


FrameSig = Tuple[int]


def gen_video_code(frame_sigs, bits=core_opts.video_bits):
    # type: (Sequence[FrameSig], int) -> ContentCodeVideo
    """Create an ISCC Content-Code Video with the latest standard algorithm.

    :param FrameSig frame_sigs: Sequence of MP7 frame signatures
    :param int bits: Bit-length resulting Instance-Code (multiple of 64)
    :return: VideoCode object with code property set
    :rtype: ContentCodeVideo
    """
    return gen_video_code_v0(frame_sigs, bits)


def gen_video_code_v0(frame_sigs, bits=core_opts.video_bits):
    # type: (Sequence[FrameSig], int) -> ContentCodeVideo
    """Create an ISCC Content-Code Video with algorithm v0.

    :param FrameSig frame_sigs: Sequence of MP7 frame signatures
    :param int bits: Bit-length resulting Instance-Code (multiple of 64)
    :return: VideoCode object with code property set
    :rtype: ContentCodeVideo
    """
    digest = soft_hash_video_v0(frame_sigs, bits=bits)
    video_code = codec.encode_component(
        mtype=codec.MT.CONTENT,
        stype=codec.ST_CC.VIDEO,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    video_code_obj = ContentCodeVideo(iscc=video_code)
    return video_code_obj


def soft_hash_video_v0(frame_sigs, bits=core_opts.video_bits):
    # type: (Sequence[Sequence[int]], int) -> bytes
    """Compute video hash v0 from MP7 frame signatures.

    :param Sequence[Sequence[int]] frame_sigs: 2D matrix of MP7 frame signatures
    :param int bits: Bit-length resulting Instance-Code (multiple of 64)
    """

    if not isinstance(frame_sigs[0], tuple):
        frame_sigs = [tuple(sig) for sig in frame_sigs]
    sigs = set(frame_sigs)
    vecsum = [sum(col) for col in zip(*sigs)]
    video_hash_digest = wtahash(vecsum, bits)
    return video_hash_digest
