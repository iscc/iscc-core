# -*- coding: utf-8 -*-
import iscc_core
from iscc_core.code_content_image import normalize_image

image_path = "../docs/images/iscc-architecture.png"

meta_code = iscc_core.gen_meta_code(
    title="ISCC Architecure", extra="A schematic overview of the ISCC"
)

print(f"Meta-Code:     {meta_code.iscc}")
print(f"Structure:     {meta_code.code_obj.explain}\n")

with open(image_path, "rb") as stream:

    pixels = normalize_image(stream)
    image_code = iscc_core.gen_image_code(pixels)
    print(f"Image-Code:    {image_code.iscc}")
    print(f"Structure:     {image_code.code_obj.explain}\n")

    stream.seek(0)
    data_code = iscc_core.gen_data_code(stream)
    print(f"Data-Code:     {data_code.iscc}")
    print(f"Structure:     {data_code.code_obj.explain}\n")

    stream.seek(0)
    instance_code = iscc_core.gen_instance_code(stream)
    print(f"Instance-Code: {instance_code.iscc}")
    print(f"Structure:     {instance_code.code_obj.explain}\n")

iscc_code = iscc_core.gen_iscc_code(
    (meta_code.iscc, image_code.iscc, data_code.iscc, instance_code.iscc)
)
print(f"ISCC-CODE:     ISCC:{iscc_code.iscc}")
print(f"Structure:     {iscc_code.code_obj.explain}\n")

iscc_id = iscc_core.gen_iscc_id(chain=1, iscc_code=iscc_code.iscc, uc=7)
print(f"ISCC-ID:       ISCC:{iscc_id.iscc}")
print(f"Structure:     ISCC:{iscc_id.code_obj.explain}")
