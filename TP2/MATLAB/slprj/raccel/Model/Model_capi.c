#include "rtw_capi.h"
#ifdef HOST_CAPI_BUILD
#include "Model_capi_host.h"
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
#include "Model.h"
#include "Model_capi.h"
#include "Model_private.h"
#ifdef LIGHT_WEIGHT_CAPI
#define TARGET_CONST
#define TARGET_STRING(s)               ((NULL))
#else
#define TARGET_CONST                   const
#define TARGET_STRING(s)               (s)
#endif
#endif
static const rtwCAPI_Signals rtBlockSignals [ ] = { { 0 , 0 , TARGET_STRING ( "Model/Constant" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 0 } , { 1 , 0 , TARGET_STRING ( "Model/Constant1" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 0 } , { 2 , 0 , TARGET_STRING ( "Model/Constant3" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 0 } , { 3 , 0 , TARGET_STRING ( "Model/Constant4" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 0 } , { 4 , 0 , TARGET_STRING ( "Model/Fuzzy Controller/Factor de Fuerza" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 1 } , { 5 , 0 , TARGET_STRING ( "Model/Graphics/theta" ) , TARGET_STRING ( "&#x3B8;" ) , 0 , 0 , 0 , 0 , 1 } , { 6 , 0 , TARGET_STRING ( "Model/Planta/Gain5" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 1 } , { 7 , 0 , TARGET_STRING ( "Model/Planta/Integrator" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 1 } , { 8 , 0 , TARGET_STRING ( "Model/Planta/Integrator2" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 1 } , { 9 , 0 , TARGET_STRING ( "Model/Planta/Integrator3" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 1 } , { 10 , 0 , TARGET_STRING ( "Model/Planta/Divide" ) , TARGET_STRING ( "" ) , 0 , 0 , 0 , 0 , 1 } , { 11 , 3 , TARGET_STRING ( "Model/Fuzzy Controller/ThetaFuzzyController/Evaluate Rule Consequents" ) , TARGET_STRING ( "" ) , 0 , 0 , 1 , 0 , 1 } , { 12 , 7 , TARGET_STRING ( "Model/Fuzzy Controller/XFuzzyController/Evaluate Rule Consequents" ) , TARGET_STRING ( "" ) , 0 , 0 , 1 , 0 , 1 } , { 0 , 0 , ( NULL ) , ( NULL ) , 0 , 0 , 0 , 0 , 0 } } ; static const rtwCAPI_BlockParameters rtBlockParameters [ ] = { { 13 , TARGET_STRING ( "Model/Constant" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 14 , TARGET_STRING ( "Model/Constant1" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 15 , TARGET_STRING ( "Model/Constant2" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 16 , TARGET_STRING ( "Model/Constant3" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 17 , TARGET_STRING ( "Model/Constant4" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 18 , TARGET_STRING ( "Model/Fuzzy Controller/Constant2" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 19 , TARGET_STRING ( "Model/Fuzzy Controller/Constant3" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 20 , TARGET_STRING ( "Model/Fuzzy Controller/Gain" ) , TARGET_STRING ( "Gain" ) , 0 , 0 , 0 } , { 21 , TARGET_STRING ( "Model/Fuzzy Controller/Gain1" ) , TARGET_STRING ( "Gain" ) , 0 , 0 , 0 } , { 22 , TARGET_STRING ( "Model/Fuzzy Controller/Gain2" ) , TARGET_STRING ( "Gain" ) , 0 , 0 , 0 } , { 23 , TARGET_STRING ( "Model/Fuzzy Controller/Gain3" ) , TARGET_STRING ( "Gain" ) , 0 , 0 , 0 } , { 24 , TARGET_STRING ( "Model/Fuzzy Controller/Gain4" ) , TARGET_STRING ( "Gain" ) , 0 , 0 , 0 } , { 25 , TARGET_STRING ( "Model/Fuzzy Controller/rad2deg" ) , TARGET_STRING ( "Gain" ) , 0 , 0 , 0 } , { 26 , TARGET_STRING ( "Model/Graphics/theta" ) , TARGET_STRING ( "Gain" ) , 0 , 0 , 0 } , { 27 , TARGET_STRING ( "Model/Fuzzy Controller/ThetaFuzzyController/Output Sample Points" ) , TARGET_STRING ( "Value" ) , 0 , 2 , 0 } , { 28 , TARGET_STRING ( "Model/Fuzzy Controller/XFuzzyController/Output Sample Points" ) , TARGET_STRING ( "Value" ) , 0 , 2 , 0 } , { 29 , TARGET_STRING ( "Model/Graphics/Subsystem/Constant" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 30 , TARGET_STRING ( "Model/Graphics/Subsystem/Constant1" ) , TARGET_STRING ( "Value" ) , 0 , 0 , 0 } , { 31 , TARGET_STRING ( "Model/Graphics/Subsystem/rad2deg" ) , TARGET_STRING ( "Gain" ) , 0 , 0 , 0 } , { 0 , ( NULL ) , ( NULL ) , 0 , 0 , 0 } } ; static int_T rt_LoggedStateIdxList [ ] = { - 1 } ; static const rtwCAPI_Signals rtRootInputs [ ] = { { 0 , 0 , ( NULL ) , ( NULL ) , 0 , 0 , 0 , 0 , 0 } } ; static const rtwCAPI_Signals rtRootOutputs [ ] = { { 0 , 0 , ( NULL ) , ( NULL ) , 0 , 0 , 0 , 0 , 0 } } ; static const rtwCAPI_ModelParameters rtModelParameters [ ] = { { 32 , TARGET_STRING ( "F_equilibrium" ) , 0 , 0 , 0 } , { 33 , TARGET_STRING ( "alpha" ) , 0 , 0 , 0 } , { 34 , TARGET_STRING ( "b" ) , 0 , 0 , 0 } , { 35 , TARGET_STRING ( "beta" ) , 0 , 0 , 0 } , { 36 , TARGET_STRING ( "g" ) , 0 , 0 , 0 } , { 37 , TARGET_STRING ( "lambda" ) , 0 , 0 , 0 } , { 38 , TARGET_STRING ( "mu" ) , 0 , 0 , 0 } , { 39 , TARGET_STRING ( "x_ref" ) , 0 , 0 , 0 } , { 0 , ( NULL ) , 0 , 0 , 0 } } ;
#ifndef HOST_CAPI_BUILD
static void * rtDataAddrMap [ ] = { & rtB . oi4cubqypg , & rtB . pwovlhpygb ,
& rtB . jvak5lfibj , & rtB . jpfkxzwvew , & rtB . o2bkv5how4 , & rtB .
ijtouhsyxn , & rtB . oaoe1nh5ne , & rtB . huwdxda24q , & rtB . hodcriesct , &
rtB . p41hqe1owj , & rtB . acvw55fb1k , & rtB . fgymxyjrsj [ 0 ] , & rtB .
fsd5migfwm [ 0 ] , & rtP . Constant_Value_ljjrc4ac51 , & rtP .
Constant1_Value_kmf41b2fgv , & rtP . Constant2_Value , & rtP .
Constant3_Value , & rtP . Constant4_Value , & rtP .
Constant2_Value_kcodwcpjwp , & rtP . Constant3_Value_jqw25fydac , & rtP .
Gain_Gain , & rtP . Gain1_Gain , & rtP . Gain2_Gain , & rtP . Gain3_Gain , &
rtP . Gain4_Gain , & rtP . rad2deg_Gain_mjsljihjpc , & rtP . theta_Gain , &
rtP . OutputSamplePoints_Value [ 0 ] , & rtP .
OutputSamplePoints_Value_fi4mzupike [ 0 ] , & rtP . Constant_Value , & rtP .
Constant1_Value , & rtP . rad2deg_Gain , & rtP . F_equilibrium , & rtP .
alpha , & rtP . b , & rtP . beta , & rtP . g , & rtP . lambda , & rtP . mu ,
& rtP . x_ref , } ; static int32_T * rtVarDimsAddrMap [ ] = { ( NULL ) } ;
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
rtwCAPI_SampleTimeMap rtSampleTimeMap [ ] = { { ( NULL ) , ( NULL ) , 1 , 0 }
, { ( const void * ) & rtcapiStoredFloats [ 0 ] , ( const void * ) &
rtcapiStoredFloats [ 0 ] , ( int8_T ) 0 , ( uint8_T ) 0 } } ; static
rtwCAPI_ModelMappingStaticInfo mmiStatic = { { rtBlockSignals , 13 ,
rtRootInputs , 0 , rtRootOutputs , 0 } , { rtBlockParameters , 19 ,
rtModelParameters , 8 } , { ( NULL ) , 0 } , { rtDataTypeMap , rtDimensionMap
, rtFixPtMap , rtElementMap , rtSampleTimeMap , rtDimensionArray } , "float"
, { 448354238U , 2219375869U , 207525172U , 2147037880U } , ( NULL ) , 0 , ( boolean_T ) 0 , rt_LoggedStateIdxList } ; const rtwCAPI_ModelMappingStaticInfo * Model_GetCAPIStaticMap ( void ) { return & mmiStatic ; }
#ifndef HOST_CAPI_BUILD
void Model_InitializeDataMapInfo ( void ) { rtwCAPI_SetVersion ( ( *
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
void Model_host_InitializeDataMapInfo ( Model_host_DataMapInfo_T * dataMap ,
const char * path ) { rtwCAPI_SetVersion ( dataMap -> mmi , 1 ) ;
rtwCAPI_SetStaticMap ( dataMap -> mmi , & mmiStatic ) ;
rtwCAPI_SetDataAddressMap ( dataMap -> mmi , ( NULL ) ) ;
rtwCAPI_SetVarDimsAddressMap ( dataMap -> mmi , ( NULL ) ) ; rtwCAPI_SetPath
( dataMap -> mmi , path ) ; rtwCAPI_SetFullPath ( dataMap -> mmi , ( NULL ) )
; rtwCAPI_SetChildMMIArray ( dataMap -> mmi , ( NULL ) ) ;
rtwCAPI_SetChildMMIArrayLen ( dataMap -> mmi , 0 ) ; }
#ifdef __cplusplus
}
#endif
#endif
