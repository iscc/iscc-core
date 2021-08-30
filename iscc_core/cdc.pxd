import cython
from libc.stdint cimport uint8_t, uint32_t

cdef uint32_t CDC_AVG_CHUNK_SIZE = 1024
cdef uint32_t CDC_READ_SIZE = 262144
cdef uint32_t[256] GEAR

@cython.locals(pattern=uint32_t, i=uint32_t, size=uint32_t, barrier=uint32_t)
cdef uint32_t cdc_offset(const uint8_t[:], uint32_t mi, uint32_t ma, uint32_t cs, uint32_t mask_s, uint32_t mask_l)
