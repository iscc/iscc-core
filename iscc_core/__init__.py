__version__ = "0.2.0"
from iscc_core import options


core_opts = options.CoreOptions()
options_conformant = options.check_options(core_opts)


from iscc_core import conformance

from iscc_core.iscc_code import (
    gen_iscc_code,
    gen_iscc_code_v0,
)
from iscc_core.iscc_id import (
    gen_iscc_id,
    gen_iscc_id_v0,
)
from iscc_core.code_meta import (
    gen_meta_code,
    gen_meta_code_v0,
)
from iscc_core.code_content_text import (
    gen_text_code,
    gen_text_code_v0,
)
from iscc_core.code_content_image import (
    gen_image_code,
    gen_image_code_v0,
)
from iscc_core.code_content_audio import (
    gen_audio_code,
    gen_audio_code_v0,
)
from iscc_core.code_content_video import (
    gen_video_code,
    gen_video_code_v0,
)
from iscc_core.code_content_mixed import (
    gen_mixed_code,
    gen_mixed_code_v0,
)
from iscc_core.code_data import (
    gen_data_code,
    gen_data_code_v0,
)
from iscc_core.code_instance import (
    gen_instance_code,
    gen_instance_code_v0,
)
from iscc_core.schema import (
    IsccCode,
    IsccID,
    MetaCode,
    ContentCodeText,
    ContentCodeImage,
    ContentCodeAudio,
    ContentCodeVideo,
    ContentCodeMixed,
    DataCode,
    InstanceCode,
)
from iscc_core.codec import (
    Code,
    MT,
    ST,
    ST_CC,
    ST_ISCC,
    ST_ID,
    VS,
    LN,
    encode_base32,
    encode_base64,
    decode_base32,
    decode_base64,
    encode_component,
    decompose,
    normalize,
    clean,
    read_header,
    write_header,
)

__all__ = [
    "core_opts",
    "options_conformant",
    "conformance",
    "gen_iscc_code",
    "gen_iscc_code_v0",
    "gen_iscc_id",
    "gen_iscc_id_v0",
    "gen_meta_code",
    "gen_meta_code_v0",
    "gen_text_code",
    "gen_text_code_v0",
    "gen_image_code",
    "gen_image_code_v0",
    "gen_audio_code",
    "gen_audio_code_v0",
    "gen_video_code",
    "gen_video_code_v0",
    "gen_mixed_code",
    "gen_mixed_code_v0",
    "gen_data_code",
    "gen_data_code_v0",
    "gen_instance_code",
    "gen_instance_code_v0",
    "IsccCode",
    "IsccID",
    "MetaCode",
    "ContentCodeText",
    "ContentCodeImage",
    "ContentCodeAudio",
    "ContentCodeVideo",
    "ContentCodeMixed",
    "DataCode",
    "InstanceCode",
    "Code",
    "MT",
    "ST",
    "ST_CC",
    "ST_ISCC",
    "ST_ID",
    "VS",
    "LN",
    "encode_base32",
    "encode_base64",
    "decode_base32",
    "decode_base64",
    "encode_component",
    "decompose",
    "normalize",
    "clean",
    "read_header",
    "write_header",
]
