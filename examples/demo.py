# -*- coding: utf-8 -*-
import iscc_core

image_path = "../docs/images/iscc-architecture.png"

meta_code = iscc_core.gen_meta_code(
    title="ISCC Architecure", extra="A schematic overview of the ISCC"
)

print(f"Meta-Code:     {meta_code.code}")
print(f"Structure:     {meta_code.code_obj.explain}\n")

with open(image_path, "rb") as stream:

    image_code = iscc_core.gen_image_code(stream)
    print(f"Image-Code:    {image_code.code}")
    print(f"Structure:     {image_code.code_obj.explain}\n")

    stream.seek(0)
    data_code = iscc_core.gen_data_code(stream)
    print(f"Data-Code:     {data_code.code}")
    print(f"Structure:     {data_code.code_obj.explain}\n")

    stream.seek(0)
    instance_code = iscc_core.gen_instance_code(stream)
    print(f"Instance-Code: {instance_code.code}")
    print(f"Structure:     {instance_code.code_obj.explain}\n")

iscc_code = iscc_core.gen_iscc_code(
    (meta_code.code, image_code.code, data_code.code, instance_code.code)
)
print(f"ISCC-CODE:     ISCC:{iscc_code}")
print(f"Structure:     {iscc_code.code_obj.explain}\n")

iscc_id = iscc_core.gen_iscc_id(chain=1, iscc_code=iscc_code.code, uc=7)
print(f"ISCC-ID:       ISCC:{iscc_id}")
print(f"Structure:     ISCC:{iscc_id.code_obj.explain}")
