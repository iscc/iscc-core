__version__ = "0.1.1"
from iscc_core.code_meta import gen_meta_code
from iscc_core.code_content_text import gen_text_code
from iscc_core.code_content_image import gen_image_code
from iscc_core.code_content_audio import gen_audio_code
from iscc_core.code_content_video import gen_video_code
from iscc_core.code_data import gen_data_code
from iscc_core.code_instance import gen_instance_code
from iscc_core.codec import Code, compose, decompose
