__version__ = "0.1.2"
from iscc_core.code_meta import gen_meta_code, gen_meta_code_v0, soft_hash_meta_v0
from iscc_core.code_content_text import (
    gen_text_code,
    gen_text_code_v0,
    soft_hash_text_v0,
)
from iscc_core.code_content_image import (
    gen_image_code,
    gen_image_code_v0,
    soft_hash_image_v0,
)
from iscc_core.code_content_audio import (
    gen_audio_code,
    gen_audio_code_v0,
    soft_hash_audio_v0,
)
from iscc_core.code_content_video import (
    gen_video_code,
    gen_video_code_v0,
    soft_hash_video_v0,
)
from iscc_core.code_data import gen_data_code, gen_data_code_v0, soft_hash_data_v0
from iscc_core.code_instance import (
    gen_instance_code,
    gen_instance_code_v0,
    hash_instance_v0,
)
from iscc_core.codec import Code, compose, decompose
