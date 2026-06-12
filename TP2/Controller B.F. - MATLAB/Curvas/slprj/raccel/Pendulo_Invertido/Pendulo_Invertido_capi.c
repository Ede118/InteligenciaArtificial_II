#include "rtw_capi.h"
#ifdef HOST_CAPI_BUILD
#include "Pendulo_Invertido_capi_host.h"
#define sizeof(...) ((size_t)(0xFFFF))
#undef rt_offsetof
#define rt_offsetof(s,el) ((uint16_T)(0xFFFF))
#define TARGET_CONST
#define TARGET_STRING(s) (s)
#ifndef SS_UINT64
#define SS_UINT64 22
#endif
#ifndef SS_INT64
#define SS_INT64 23
#endif
#else
#include "builtin_typeid_types.h"
#include "Pendulo_Invertido.h"
#include "Pendulo_Invertido_capi.h"
#include "Pendulo_Invertido_private.h"
#ifdef LIGHT_WEIGHT_CAPI
#define TARGET_CONST
#define TARGET_STRING(s)               ((NULL))
#else
#define TARGET_CONST                   const
#define TARGET_STRING(s)               (s)
#endif
#endif
static const rtwCAPI_Signals rtBlockSignals [ ] = { { 0 , 0 , TARGET_STRING ( "Pendulo_Invertido/Fuzzy Controller/Factor de Fuerza" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 0 } , { 1 , 0 , TARGET_STRING ( "Pendulo_Invertido/Planta/Gain5" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 0 } , { 2 , 0 , TARGET_STRING ( "Pendulo_Invertido/Planta/Integrator" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 0 } , { 3 , 0 , TARGET_STRING ( "Pendulo_Invertido/Planta/Integrator1" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 0 } , { 4 , 0 , TARGET_STRING ( "Pendulo_Invertido/Planta/Integrator2" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 0 } , { 5 , 0 , TARGET_STRING ( "Pendulo_Invertido/Planta/Integrator3" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 0 } , { 6 , 0 , TARGET_STRING ( "Pendulo_Invertido/Planta/Divide" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 0 } , { 7 , 0 , TARGET_STRING ( "Pendulo_Invertido/Plots/theta" ) , TARGET_STRING ( "theta_deg" ) , 0 , 0 , 0 , 0 , 0 } , { 8 , 3 , TARGET_STRING ( "Pendulo_Invertido/Fuzzy Controller/ThetaFuzzyController/Evaluate Rule Consequents" ) , TARGET_STRING ( "" ) , 0 , 0 , 1 , 0 , 0 } , { 9 , 7 , TARGET_STRING ( "Pendulo_Invertido/Fuzzy Controller/XFuzzyController/Evaluate Rule Consequents" ) , TARGET_STRING ( "" ) , 0 , 0 , 1 , 0 , 0 } , { 0 , 0 , ( NULL ) , ( NULL ) , 0 , 0 , 0 , 0 , 0 } } ; static const rtwCAPI_BlockParameters rtBlockParameters [ ] = { { 10 , TARGET_STRING ( "Pendulo_Invertido/Constant2" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 11 , TARGET_STRING ( "Pendulo_Invertido/Fuzzy Controller/Constant2" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 12 , TARGET_STRING ( "Pendulo_Invertido/Fuzzy Controller/Constant3" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 13 , TARGET_STRING ( "Pendulo_Invertido/Fuzzy Controller/rad2deg" ) , TARGET_STRING ( "Gain" ) , 0 , 0 , 0 } , { 14 , TARGET_STRING ( "Pendulo_Invertido/Plots/theta" ) , TARGET_STRING ( "Gain" ) , 0 , 0 , 0 } , { 15 , TARGET_STRING ( "Pendulo_Invertido/Fuzzy Controller/ThetaFuzzyController/Output Sample Points" ) , TARGET_STRING ( "Value" ) , 0 , 2 , 0 } , { 16 , TARGET_STRING ( "Pendulo_Invertido/Fuzzy Controller/XFuzzyController/Output Sample Points" ) , TARGET_STRING ( "Value" ) , 0 , 2 , 0 } , { 0 , ( NULL ) , ( NULL ) , 0 , 0 , 0 } } ; static int_T rt_LoggedStateIdxList [ ] = { - 1 } ; static const rtwCAPI_Signals rtRootInputs [ ] = { { 0 , 0 , ( NULL ) , ( NULL ) , 0 , 0 , 0 , 0 , 0 } } ; static const rtwCAPI_Signals rtRootOutputs [ ] = { { 0 , 0 , ( NULL ) , ( NULL ) , 0 , 0 , 0 , 0 , 0 } } ; static const rtwCAPI_ModelParameters rtModelParameters [ ] = { { 17 , TARGET_STRING ( "G_F" ) , 0 , 0 , 0 } , { 18 , TARGET_STRING ( "G_omega" ) , 0 , 0 , 0 } , { 19 , TARGET_STRING ( "G_theta" ) , 0 , 0 , 0 } , { 20 , TARGET_STRING ( "G_theta_ref" ) , 0 , 0 , 0 } , { 21 , TARGET_STRING ( "G_v" ) , 0 , 0 , 0 } , { 22 , TARGET_STRING ( "G_x" ) , 0 , 0 , 0 } , { 23 , TARGET_STRING ( "alpha" ) , 0 , 0 , 0 } , { 24 , TARGET_STRING ( "b" ) , 0 , 0 , 0 } , { 25 , TARGET_STRING ( "beta" ) , 0 , 0 , 0 } , { 26 , TARGET_STRING ( "dtheta_0" ) , 0 , 0 , 0 } , { 27 , TARGET_STRING ( "dx_0" ) , 0 , 0 , 0 } , { 28 , TARGET_STRING ( "g" ) , 0 , 0 , 0 } , { 29 , TARGET_STRING ( "lambda" ) , 0 , 0 , 0 } , { 30 , TARGET_STRING ( "mu" ) , 0 , 0 , 0 } , { 31 , TARGET_STRING ( "theta_0" ) , 0 , 0 , 0 } , { 32 , TARGET_STRING ( "x_ref" ) , 0 , 0 , 0 } , { 0 , ( NULL ) , 0 , 0 , 0 } } ;
#ifndef HOST_CAPI_BUILD
static void * rtDataAddrMap [ ] = { & rtB . j2kuyafaot , & rtB . l5ohccctkt ,
& rtB . jicflel3c3 , & rtB . blxaed2wc0 , & rtB . k1yzzvuzag , & rtB .
ofs3mtvtjb , & rtB . eb55xegd4r , & rtB . k5illwhoex , & rtB . pf4lo52t41 [ 0
] , & rtB . e25rqytwh3 [ 0 ] , & rtP . Constant2_Value , & rtP .
Constant2_Value_kcodwcpjwp , & rtP . Constant3_Value , & rtP . rad2deg_Gain ,
& rtP . theta_Gain , & rtP . OutputSamplePoints_Value [ 0 ] , & rtP .
OutputSamplePoints_Value_fi4mzupike [ 0 ] , & rtP . G_F , & rtP . G_omega , &
rtP . G_theta , & rtP . G_theta_ref , & rtP . G_v , & rtP . G_x , & rtP .
alpha , & rtP . b , & rtP . beta , & rtP . dtheta_0 , & rtP . dx_0 , & rtP .
g , & rtP . lambda , & rtP . mu , & rtP . theta_0 , & rtP . x_ref , } ;
static int32_T * rtVarDimsAddrMap [ ] = { ( NULL ) } ;
#endif
static TARGET_CONST rtwCAPI_DataTypeMap rtDataTypeMap [ ] = { { "double" ,
"real_T" , 0 , 0 , sizeof ( real_T ) , ( uint8_T ) SS_DOUBLE , 0 , 0 , 0 } }
;
#ifdef HOST_CAPI_BUILD
#undef sizeof
#endif
static TARGET_CONST rtwCAPI_ElementMap rtElementMap [ ] = { { ( NULL ) , 0 ,
0 , 0 , 0 } , } ; static const rtwCAPI_DimensionMap rtDimensionMap [ ] = { {
rtwCAPI_SCALAR , 0 , 2 , 0 } , { rtwCAPI_MATRIX_COL_MAJOR , 2 , 2 , 0 } , {
rtwCAPI_VECTOR , 4 , 2 , 0 } } ; static const uint_T rtDimensionArray [ ] = {
1 , 1 , 101 , 1 , 1 , 101 } ; static const real_T rtcapiStoredFloats [ ] = {
0.0 } ; static const rtwCAPI_FixPtMap rtFixPtMap [ ] = { { ( NULL ) , ( NULL
) , rtwCAPI_FIX_RESERVED , 0 , 0 , ( boolean_T ) 0 } , } ; static const
rtwCAPI_SampleTimeMap rtSampleTimeMap [ ] = { { ( const void * ) &
rtcapiStoredFloats [ 0 ] , ( const void * ) & rtcapiStoredFloats [ 0 ] , ( int8_T ) 0 , ( uint8_T ) 0 } } ; static rtwCAPI_ModelMappingStaticInfo mmiStatic = { { rtBlockSignals , 10 , rtRootInputs , 0 , rtRootOutputs , 0 } , { rtBlockParameters , 7 , rtModelParameters , 16 } , { ( NULL ) , 0 } , { rtDataTypeMap , rtDimensionMap , rtFixPtMap , rtElementMap , rtSampleTimeMap , rtDimensionArray } , "float" , { 4282916287U , 3083900022U , 1133230755U , 431433518U } , ( NULL ) , 0 , ( boolean_T ) 0 , rt_LoggedStateIdxList } ; const rtwCAPI_ModelMappingStaticInfo * Pendulo_Invertido_GetCAPIStaticMap ( void ) { return & mmiStatic ; }
#ifndef HOST_CAPI_BUILD
void Pendulo_Invertido_InitializeDataMapInfo ( void ) { rtwCAPI_SetVersion ( ( *
rt_dataMapInfoPtr ) . mmi , 1 ) ; rtwCAPI_SetStaticMap ( ( *
rt_dataMapInfoPtr ) . mmi , & mmiStatic ) ; rtwCAPI_SetLoggingStaticMap ( ( *
rt_dataMapInfoPtr ) . mmi , ( NULL ) ) ; rtwCAPI_SetDataAddressMap ( ( *
rt_dataMapInfoPtr ) . mmi , rtDataAddrMap ) ; rtwCAPI_SetVarDimsAddressMap ( ( *
rt_dataMapInfoPtr ) . mmi , rtVarDimsAddrMap ) ;
rtwCAPI_SetInstanceLoggingInfo ( ( * rt_dataMapInfoPtr ) . mmi , ( NULL ) ) ;
rtwCAPI_SetChildMMIArray ( ( * rt_dataMapInfoPtr ) . mmi , ( NULL ) ) ;
rtwCAPI_SetChildMMIArrayLen ( ( * rt_dataMapInfoPtr ) . mmi , 0 ) ; }
#else
#ifdef __cplusplus
extern "C" {
#endif
void Pendulo_Invertido_host_InitializeDataMapInfo ( Pendulo_Invertido_host_DataMapInfo_T * dataMap , const char * path ) { rtwCAPI_SetVersion ( dataMap -> mmi , 1 ) ; rtwCAPI_SetStaticMap ( dataMap -> mmi , & mmiStatic ) ; rtwCAPI_SetDataAddressMap ( dataMap -> mmi , ( NULL ) ) ; rtwCAPI_SetVarDimsAddressMap ( dataMap -> mmi , ( NULL ) ) ; rtwCAPI_SetPath ( dataMap -> mmi , path ) ; rtwCAPI_SetFullPath ( dataMap -> mmi , ( NULL ) ) ; rtwCAPI_SetChildMMIArray ( dataMap -> mmi , ( NULL ) ) ; rtwCAPI_SetChildMMIArrayLen ( dataMap -> mmi , 0 ) ; }
#ifdef __cplusplus
}
#endif
#endif
