# -*- coding: utf-8 -*-
import iscc_core


meta_code = iscc_core.gen_meta_code(title="ISCC Test Document!")

print(f"Meta-Code:     ISCC:{meta_code.iscc}")
print(f"Structure:     {meta_code.code_obj.explain}\n")

# Extract text from file
with open("demo.txt", "rt", encoding="utf-8") as stream:
    text = stream.read()
    text_code = iscc_core.gen_text_code_v0(text)
    print(f"Text-Code:     ISCC:{text_code.iscc}")
    print(f"Structure:     {text_code.code_obj.explain}\n")

# Process raw bytes of textfile
with open("demo.txt", "rb") as stream:
    data_code = iscc_core.gen_data_code(stream)
    print(f"Data-Code:     ISCC:{data_code.iscc}")
    print(f"Structure:     {data_code.code_obj.explain}\n")

    stream.seek(0)
    instance_code = iscc_core.gen_instance_code(stream)
    print(f"Instance-Code: ISCC:{instance_code.iscc}")
    print(f"Structure:     {instance_code.code_obj.explain}\n")

iscc_code = iscc_core.gen_iscc_code(
    (meta_code.iscc, text_code.iscc, data_code.iscc, instance_code.iscc)
)
print(f"ISCC-CODE:     ISCC:{iscc_code.iscc}")
print(f"Structure:     {iscc_code.code_obj.explain}\n")

iscc_id = iscc_core.gen_iscc_id(chain=1, iscc_code=iscc_code.iscc, uc=7)
print(f"ISCC-ID:       ISCC:{iscc_id.iscc}")
print(f"Structure:     ISCC:{iscc_id.code_obj.explain}")
