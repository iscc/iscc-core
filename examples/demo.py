import json
import iscc_core as ic

meta_code = ic.gen_meta_code(name="ISCC Test Document!")

print(f"Meta-Code:     {meta_code['iscc']}")
print(f"Structure:     {ic.iscc_explain(meta_code['iscc'])}\n")

# Extract text from file
with open("demo.txt", "rt", encoding="utf-8") as stream:
    text = stream.read()
    text_code = ic.gen_text_code_v0(text)
    print(f"Text-Code:     {text_code['iscc']}")
    print(f"Structure:     {ic.iscc_explain(text_code['iscc'])}\n")

# Process raw bytes of textfile
with open("demo.txt", "rb") as stream:
    data_code = ic.gen_data_code(stream)
    print(f"Data-Code:     {data_code['iscc']}")
    print(f"Structure:     {ic.iscc_explain(data_code['iscc'])}\n")

    stream.seek(0)
    instance_code = ic.gen_instance_code(stream)
    print(f"Instance-Code: {instance_code['iscc']}")
    print(f"Structure:     {ic.iscc_explain(instance_code['iscc'])}\n")

# Combine ISCC-UNITs into ISCC-CODE
iscc_code = ic.gen_iscc_code(
    (meta_code["iscc"], text_code["iscc"], data_code["iscc"], instance_code["iscc"])
)

# Create convenience `Code` object from ISCC string
iscc_obj = ic.Code(iscc_code["iscc"])
print(f"ISCC-CODE:     {ic.iscc_normalize(iscc_obj.code)}")
print(f"Structure:     {iscc_obj.explain}")
print(f"Multiformat:   {iscc_obj.mf_base32}\n")

# Compare with changed ISCC-CODE:
new_dc, new_ic = ic.Code.rnd(mt=ic.MT.DATA), ic.Code.rnd(mt=ic.MT.INSTANCE)
new_iscc = ic.gen_iscc_code((meta_code["iscc"], text_code["iscc"], new_dc.uri, new_ic.uri))
print(f"Compare ISCC-CODES:\n{iscc_obj.uri}\n{new_iscc['iscc']}")
print(json.dumps(ic.iscc_compare(iscc_obj.code, new_iscc["iscc"]), indent=2))
