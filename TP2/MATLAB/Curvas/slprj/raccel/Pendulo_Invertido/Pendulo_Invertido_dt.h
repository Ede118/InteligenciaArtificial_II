#include "ext_types.h"
static DataTypeInfo rtDataTypeInfoTable [ ] = { { "real_T" , 0 , 8 } , {
"real32_T" , 1 , 4 } , { "int8_T" , 2 , 1 } , { "uint8_T" , 3 , 1 } , {
"int16_T" , 4 , 2 } , { "uint16_T" , 5 , 2 } , { "int32_T" , 6 , 4 } , {
"uint32_T" , 7 , 4 } , { "boolean_T" , 8 , 1 } , { "fcn_call_T" , 9 , 0 } , {
"int_T" , 10 , 4 } , { "pointer_T" , 11 , 8 } , { "action_T" , 12 , 8 } , {
"timer_uint32_pair_T" , 13 , 8 } , { "physical_connection" , 14 , 8 } , {
"int64_T" , 15 , 8 } , { "uint64_T" , 16 , 8 } , {
"struct_xtQT47lHfr5Mo2IBULZqGH" , 17 , 96 } , {
"struct_nDiNttezQ8pHMZv76leKsH" , 18 , 56 } , {
"struct_lMtpFmLOVR7rlweqgH5LGF" , 19 , 400 } , {
"struct_dDSOYl9OoEyVp7RIL82ESF" , 20 , 4136 } , {
"struct_yoOojIVh9IDmOigOG4nqVE" , 21 , 96 } , { "uint64_T" , 22 , 8 } , {
"int64_T" , 23 , 8 } , { "uint_T" , 24 , 32 } , { "char_T" , 25 , 8 } , {
"uchar_T" , 26 , 8 } , { "time_T" , 27 , 8 } } ; static uint_T
rtDataTypeSizes [ ] = { sizeof ( real_T ) , sizeof ( real32_T ) , sizeof ( int8_T ) , sizeof ( uint8_T ) , sizeof ( int16_T ) , sizeof ( uint16_T ) , sizeof ( int32_T ) , sizeof ( uint32_T ) , sizeof ( boolean_T ) , sizeof ( fcn_call_T ) , sizeof ( int_T ) , sizeof ( pointer_T ) , sizeof ( action_T ) , 2 * sizeof ( uint32_T ) , sizeof ( int32_T ) , sizeof ( int64_T ) , sizeof ( uint64_T ) , sizeof ( struct_xtQT47lHfr5Mo2IBULZqGH ) , sizeof ( struct_nDiNttezQ8pHMZv76leKsH ) , sizeof ( struct_lMtpFmLOVR7rlweqgH5LGF ) , sizeof ( struct_dDSOYl9OoEyVp7RIL82ESF ) , sizeof ( struct_yoOojIVh9IDmOigOG4nqVE ) , sizeof ( uint64_T ) , sizeof ( int64_T ) , sizeof ( uint_T ) , sizeof ( char_T ) , sizeof ( uchar_T ) , sizeof ( time_T ) } ; static const char_T * rtDataTypeNames [ ] = { "real_T" , "real32_T" , "int8_T" , "uint8_T" , "int16_T" , "uint16_T" , "int32_T" , "uint32_T" , "boolean_T" , "fcn_call_T" , "int_T" , "pointer_T" , "action_T" , "timer_uint32_pair_T" , "physical_connection" , "int64_T" , "uint64_T" , "struct_xtQT47lHfr5Mo2IBULZqGH" , "struct_nDiNttezQ8pHMZv76leKsH" , "struct_lMtpFmLOVR7rlweqgH5LGF" , "struct_dDSOYl9OoEyVp7RIL82ESF" , "struct_yoOojIVh9IDmOigOG4nqVE" , "uint64_T" , "int64_T" , "uint_T" , "char_T" , "uchar_T" , "time_T" } ; static DataTypeTransition rtBTransitions [ ] = { { ( char_T * ) ( & rtB . blxaed2wc0 ) , 0 , 0 , 210 } , { ( char_T * ) ( & rtDW . bh3kv04epg . LoggedData [ 0 ] ) , 11 , 0 , 10 } , { ( char_T * ) ( & rtDW . awd4remi3d ) , 6 , 0 , 6 } , { ( char_T * ) ( & rtDW . hqc20cgd5s ) , 8 , 0 , 6 } } ; static DataTypeTransitionTable rtBTransTable = { 4U , rtBTransitions } ; static DataTypeTransition rtPTransitions [ ] = { { ( char_T * ) ( & rtP . G_F ) , 0 , 0 , 223 } } ; static DataTypeTransitionTable rtPTransTable = { 1U , rtPTransitions } ;
