# -*- coding: utf-8 -*-
"""Options for the iscc-core package can be configured using environment variables. Variables are
loaded as class-attributes on the `CoreOptions` instance. Environment variables are named like
the class-attribute but prefixed with `ISCC_CORE_` and upper-cased.

!!! example "Example how to access configuration options"
    ```python
    import iscc_core as ic

    # To access ISCC_CORE_TEXT_NGRAM_SIZE setting use
    text_ngram_size: int = ic.core_opts.text_ngram_size
    ```
"""
from typing import Tuple
from loguru import logger as log

try:
    from pydantic.v1 import BaseSettings, Field
except ImportError:  # pragma: no cover
    from pydantic import BaseSettings, Field


class CoreOptions(BaseSettings):
    """Parameters with defaults for ISCC calculations."""

    class Config:
        env_prefix = "ISCC_CORE_"
        env_file = "iscc-core.env"
        env_file_encoding = "utf-8"

    meta_bits: int = Field(64, description="Default length of generated Meta-Code in bits")
    meta_trim_name: int = Field(128, description="Trim `name` to this mumber of bytes")
    meta_trim_description: int = Field(
        4096, description="Trim `description` to this number of bytes"
    )
    meta_ngram_size_text: int = Field(
        3, description="Sliding window width (characters) for metadata"
    )
    meta_ngram_size_bytes: int = Field(4, description="Sliding window width (bytes) for metadata")

    text_bits: int = Field(64, description="Default length of generated Content-Code Text in bits")

    text_ngram_size: int = Field(
        13, description="Number of characters per feature hash (size of sliding window)"
    )

    text_unicode_filter: frozenset = Field(
        frozenset(
            {
                "C",
                "M",
                "P",
            }
        ),
        description="Unicode categories to remove during text normalization",
    )

    text_newlines: frozenset = Field(
        frozenset(
            {
                "\u000a",  # Line Feed
                "\u000b",  # Vertical Tab
                "\u000c",  # Form Feed
                "\u000d",  # Carriage Return
                "\u0085",  # Next Line
                "\u2028",  # Line Separator
                "\u2029",  # Paragraph Separator
            }
        ),
        description="Characters regarded as newline characters for normalization purposes",
    )

    image_bits: int = Field(
        64, description="Default length of generated Content-Code Image in bits"
    )

    audio_bits: int = Field(
        64, description="Default length of generated Content-Code Audio in bits"
    )

    video_bits: int = Field(
        64, description="Default length of generated Content-Code Video in bits"
    )

    data_bits: int = Field(64, description="Default length of generated Data-Code in bits")

    flake_bits: int = Field(64, description="Default length of generated Flake-Code in bits")

    data_avg_chunk_size: int = Field(
        1024, description="Target chunk size for data chunking in number of bytes."
    )

    instance_bits: int = Field(64, description="Default length of generated Instance-Code in bits")

    mixed_bits: int = Field(64, description="Default length of generated Mixed-Code in bits")

    io_read_size: int = Field(
        2097152, description="File read buffer size in bytes for hashing operations"
    )

    cdc_gear: Tuple = Field(
        (
            1553318008,
            574654857,
            759734804,
            310648967,
            1393527547,
            1195718329,
            694400241,
            1154184075,
            1319583805,
            1298164590,
            122602963,
            989043992,
            1918895050,
            933636724,
            1369634190,
            1963341198,
            1565176104,
            1296753019,
            1105746212,
            1191982839,
            1195494369,
            29065008,
            1635524067,
            722221599,
            1355059059,
            564669751,
            1620421856,
            1100048288,
            1018120624,
            1087284781,
            1723604070,
            1415454125,
            737834957,
            1854265892,
            1605418437,
            1697446953,
            973791659,
            674750707,
            1669838606,
            320299026,
            1130545851,
            1725494449,
            939321396,
            748475270,
            554975894,
            1651665064,
            1695413559,
            671470969,
            992078781,
            1935142196,
            1062778243,
            1901125066,
            1935811166,
            1644847216,
            744420649,
            2068980838,
            1988851904,
            1263854878,
            1979320293,
            111370182,
            817303588,
            478553825,
            694867320,
            685227566,
            345022554,
            2095989693,
            1770739427,
            165413158,
            1322704750,
            46251975,
            710520147,
            700507188,
            2104251000,
            1350123687,
            1593227923,
            1756802846,
            1179873910,
            1629210470,
            358373501,
            807118919,
            751426983,
            172199468,
            174707988,
            1951167187,
            1328704411,
            2129871494,
            1242495143,
            1793093310,
            1721521010,
            306195915,
            1609230749,
            1992815783,
            1790818204,
            234528824,
            551692332,
            1930351755,
            110996527,
            378457918,
            638641695,
            743517326,
            368806918,
            1583529078,
            1767199029,
            182158924,
            1114175764,
            882553770,
            552467890,
            1366456705,
            934589400,
            1574008098,
            1798094820,
            1548210079,
            821697741,
            601807702,
            332526858,
            1693310695,
            136360183,
            1189114632,
            506273277,
            397438002,
            620771032,
            676183860,
            1747529440,
            909035644,
            142389739,
            1991534368,
            272707803,
            1905681287,
            1210958911,
            596176677,
            1380009185,
            1153270606,
            1150188963,
            1067903737,
            1020928348,
            978324723,
            962376754,
            1368724127,
            1133797255,
            1367747748,
            1458212849,
            537933020,
            1295159285,
            2104731913,
            1647629177,
            1691336604,
            922114202,
            170715530,
            1608833393,
            62657989,
            1140989235,
            381784875,
            928003604,
            449509021,
            1057208185,
            1239816707,
            525522922,
            476962140,
            102897870,
            132620570,
            419788154,
            2095057491,
            1240747817,
            1271689397,
            973007445,
            1380110056,
            1021668229,
            12064370,
            1186917580,
            1017163094,
            597085928,
            2018803520,
            1795688603,
            1722115921,
            2015264326,
            506263638,
            1002517905,
            1229603330,
            1376031959,
            763839898,
            1970623926,
            1109937345,
            524780807,
            1976131071,
            905940439,
            1313298413,
            772929676,
            1578848328,
            1108240025,
            577439381,
            1293318580,
            1512203375,
            371003697,
            308046041,
            320070446,
            1252546340,
            568098497,
            1341794814,
            1922466690,
            480833267,
            1060838440,
            969079660,
            1836468543,
            2049091118,
            2023431210,
            383830867,
            2112679659,
            231203270,
            1551220541,
            1377927987,
            275637462,
            2110145570,
            1700335604,
            738389040,
            1688841319,
            1506456297,
            1243730675,
            258043479,
            599084776,
            41093802,
            792486733,
            1897397356,
            28077829,
            1520357900,
            361516586,
            1119263216,
            209458355,
            45979201,
            363681532,
            477245280,
            2107748241,
            601938891,
            244572459,
            1689418013,
            1141711990,
            1485744349,
            1181066840,
            1950794776,
            410494836,
            1445347454,
            2137242950,
            852679640,
            1014566730,
            1999335993,
            1871390758,
            1736439305,
            231222289,
            603972436,
            783045542,
            370384393,
            184356284,
            709706295,
            1453549767,
            591603172,
            768512391,
            854125182,
        ),
        description="Random gear vector",
    )


# Conformance critical options that produce non-interoperable codes if changed
conformanc_critical = {
    "meta_trim_name",
    "meta_trim_description",
    "meta_ngram_size_text",
    "meta_ngram_size_bytes",
    "text_ngram_size",
    "text_unicode_filter",
    "text_newlines",
    "data_avg_chunk_size",
    "cdc_gear",
}
has_logged_confromance = False


def conformance_check_options(opts):
    # type: (CoreOptions) -> bool
    """Check and log if options have non-default conformance critical values"""
    global has_logged_confromance
    result = True
    for key, value in opts.dict(exclude_defaults=True).items():
        if key in conformanc_critical:
            if not has_logged_confromance:
                log.warning(f"Non-interoperable custom option {key}={value}")
                result = False
    has_logged_confromance = True
    return result


core_opts = CoreOptions()
conformant_options = conformance_check_options(core_opts)
