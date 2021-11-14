# -*- coding: utf-8 -*-
from iscc_core import (
    gen_meta_code,
    gen_image_code,
    gen_data_code,
    gen_instance_code,
    compose,
)

image_path = "../docs/images/iscc-architecture.png"

meta_code = gen_meta_code(
    title="ISCC Architecure", extra="A schematic overview of the ISCC"
)

print("Meta-Code:\t\t", meta_code.code)
print("Structure:\t\t", meta_code.code_obj.explain, end="\n\n")

with open(image_path, "rb") as stream:

    image_code = gen_image_code(stream)
    print("Image-Code:\t\t", image_code.code)
    print("Structure:\t\t", image_code.code_obj.explain, end="\n\n")

    stream.seek(0)
    data_code = gen_data_code(stream)
    print("Data-Code:\t\t", data_code.code)
    print("Structure:\t\t", data_code.code_obj.explain, end="\n\n")

    stream.seek(0)
    instance_code = gen_instance_code(stream)
    print("Instance-Code:\t", instance_code.code)
    print("Structure:\t\t", instance_code.code_obj.explain, end="\n\n")

iscc_code = compose(
    (meta_code.code, image_code.code, data_code.code, instance_code.code)
)
print("Canonical ISCC:\t ISCC:{}".format(iscc_code.code))
print("Structure:\t\t", iscc_code.explain)
