/*
Copyright (c) 2012-2022 Carsten Burstedde, Donna Calhoun, Scott Aiton
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#ifndef FCLAW_SERIALIZATION_H
#define FCLAW_SERIALIZATION_H

#include <fclaw_base.h>

#ifdef __cplusplus
extern "C"
{
#if 0
}                               /* need this because indent is dumb */
#endif
#endif

/* these are dimension-specific functions */

/**
 * @brief Pack userdata into a buffer
 * @param userdata pointer to userdata
 * @param buffer buffer to pack into
 */
typedef size_t (*fclaw_userdata_pack_t)(void* userdata,
                                     char* buffer);
/**
 * @brief Unpack userdata from buffer 
 * @param buffer buffer to unpack from
 * @return newly create userdata
 */
typedef size_t (*fclaw_userdata_unpack_t)(char* buffer,void**);
/**
 * @brief Get the size needed to pack userdata
 * @return the size
 */
typedef size_t (*fclaw_userdata_packsize_t)(void* userdata);


typedef struct fclaw_userdata_vtable
{
  fclaw_userdata_pack_t pack;
  fclaw_userdata_pack_t unpack;
  fclaw_userdata_packsize_t size;
} fclaw_useradata_vtable_t;

size_t fclaw_pack_string(char * buffer, const char*);

size_t fclaw_pack_int(char * buffer, int value);

size_t fclaw_unpack_int(char * buffer, int* value);

#ifdef __cplusplus
#if 0
{                               /* need this because indent is dumb */
#endif
}
#endif

#endif /* !FCLAW2D_GLOBAL_H */
