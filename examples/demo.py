# -*- coding: utf-8 -*-
import iscc_core


meta_code = iscc_core.gen_meta_code(name="ISCC Test Document!")

print(f"Meta-Code:     {meta_code.iscc}")
print(f"Structure:     {meta_code.code_obj.explain}\n")

# Extract text from file
with open("demo.txt", "rt", encoding="utf-8") as stream:
    text = stream.read()
    text_code = iscc_core.gen_text_code_v0(text)
    print(f"Text-Code:     {text_code.iscc}")
    print(f"Structure:     {text_code.code_obj.explain}\n")

# Process raw bytes of textfile
with open("demo.txt", "rb") as stream:
    data_code = iscc_core.gen_data_code(stream)
    print(f"Data-Code:     {data_code.iscc}")
    print(f"Structure:     {data_code.code_obj.explain}\n")

    stream.seek(0)
    instance_code = iscc_core.gen_instance_code(stream)
    print(f"Instance-Code: {instance_code.iscc}")
    print(f"Structure:     {instance_code.code_obj.explain}\n")

iscc_code = iscc_core.gen_iscc_code(
    (meta_code.iscc, text_code.iscc, data_code.iscc, instance_code.iscc)
)
print(f"ISCC-CODE:     {iscc_code.iscc}")
print(f"Structure:     {iscc_code.code_obj.explain}")
print(f"Multiformat:   {iscc_code.code_obj.mf_base32}\n")

iscc_id = iscc_core.gen_iscc_id(chain=1, iscc_code=iscc_code.iscc, uc=7)
print(f"ISCC-ID:       {iscc_id.iscc}")
print(f"Structure:     {iscc_id.code_obj.explain}")
print(f"Multiformat:   {iscc_id.code_obj.mf_base32}")
