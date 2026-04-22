#ifndef Model_h_
#define Model_h_
#ifndef Model_COMMON_INCLUDES_
#define Model_COMMON_INCLUDES_
#include <stdlib.h>
#include "sl_AsyncioQueue/AsyncioQueueCAPI.h"
#include "rtwtypes.h"
#include "sigstream_rtw.h"
#include "simtarget/slSimTgtSigstreamRTW.h"
#include "simtarget/slSimTgtSlioCoreRTW.h"
#include "simtarget/slSimTgtSlioClientsRTW.h"
#include "simtarget/slSimTgtSlioSdiRTW.h"
#include "simstruc.h"
#include "fixedpoint.h"
#include "raccel.h"
#include "slsv_diagnostic_codegen_c_api.h"
#include "rt_logging_simtarget.h"
#include "rt_nonfinite.h"
#include "math.h"
#include "dt_info.h"
#include "ext_work.h"
#endif
#include "Model_types.h"
#include <stddef.h>
#include "rtw_modelmap_simtarget.h"
#include "rt_defines.h"
#include <string.h>
#include "rtGetInf.h"
#define MODEL_NAME Model
#define NSAMPLE_TIMES (2) 
#define NINPUTS (0)       
#define NOUTPUTS (0)     
#define NBLOCKIO (19) 
#define NUM_ZC_EVENTS (0) 
#ifndef NCSTATES
#define NCSTATES (4)   
#elif NCSTATES != 4
#error Invalid specification of NCSTATES defined in compiler command
#endif
#ifndef rtmGetDataMapInfo
#define rtmGetDataMapInfo(rtm) (*rt_dataMapInfoPtr)
#endif
#ifndef rtmSetDataMapInfo
#define rtmSetDataMapInfo(rtm, val) (rt_dataMapInfoPtr = &val)
#endif
#ifndef IN_RACCEL_MAIN
#endif
typedef struct { real_T outputMFCache [ 707 ] ; real_T ijtouhsyxn ; real_T
huwdxda24q ; real_T p41hqe1owj ; real_T hodcriesct ; real_T o2bkv5how4 ;
real_T acvw55fb1k ; real_T oaoe1nh5ne ; real_T oi4cubqypg ; real_T pwovlhpygb
; real_T jvak5lfibj ; real_T jpfkxzwvew ; real_T fsd5migfwm [ 101 ] ; real_T
fgymxyjrsj [ 101 ] ; } B ; typedef struct { struct { void * LoggedData [ 2 ]
; } jpvjgti2ju ; struct { void * AQHandles ; } d4tg3oq402 ; struct { void *
LoggedData [ 2 ] ; } hyu31ldq2t ; struct { void * LoggedData ; } gvjlmgo4qr ;
int32_T pmtqx3h1e3 ; int32_T n4pvolfz54 ; int32_T hsjxaf4xuu ; int32_T
jcwkxcjazh ; int32_T b3pat3zjtu ; int32_T mcc443bqjq ; boolean_T aezhyafilx ;
boolean_T apfxvndcfy ; boolean_T pzz1vpadaz ; boolean_T eipmzcijh3 ;
boolean_T f5jgkvark0 ; boolean_T gyiyn3pusw ; boolean_T ohadoud2hj ;
boolean_T irjp15fgq3 ; boolean_T i3r1o4qdrs ; boolean_T kkyqcp3sdb ; } DW ;
typedef struct { real_T o3ofixikp3 ; real_T cwuheycmjj ; real_T aydnqerphz ;
real_T etgzzckpuj ; } X ; typedef struct { real_T o3ofixikp3 ; real_T
cwuheycmjj ; real_T aydnqerphz ; real_T etgzzckpuj ; } XDot ; typedef struct
{ boolean_T o3ofixikp3 ; boolean_T cwuheycmjj ; boolean_T aydnqerphz ;
boolean_T etgzzckpuj ; } XDis ; typedef struct { real_T o3ofixikp3 ; real_T
cwuheycmjj ; real_T aydnqerphz ; real_T etgzzckpuj ; } CStateAbsTol ; typedef
struct { real_T o3ofixikp3 ; real_T cwuheycmjj ; real_T aydnqerphz ; real_T
etgzzckpuj ; } CXPtMin ; typedef struct { real_T o3ofixikp3 ; real_T
cwuheycmjj ; real_T aydnqerphz ; real_T etgzzckpuj ; } CXPtMax ; typedef
struct { rtwCAPI_ModelMappingInfo mmi ; } DataMapInfo ; struct P_ { real_T
F_equilibrium ; real_T alpha ; real_T b ; real_T beta ; real_T g ; real_T
lambda ; real_T mu ; real_T x_ref ; real_T OutputSamplePoints_Value [ 101 ] ;
real_T OutputSamplePoints_Value_fi4mzupike [ 101 ] ; real_T theta_Gain ;
real_T rad2deg_Gain ; real_T rad2deg_Gain_mjsljihjpc ; real_T Gain2_Gain ;
real_T Gain3_Gain ; real_T Gain4_Gain ; real_T Gain_Gain ; real_T Gain1_Gain
; real_T Constant_Value ; real_T Constant1_Value ; real_T
Constant_Value_ljjrc4ac51 ; real_T Constant1_Value_kmf41b2fgv ; real_T
Constant2_Value ; real_T Constant3_Value ; real_T Constant4_Value ; real_T
Constant2_Value_kcodwcpjwp ; real_T Constant3_Value_jqw25fydac ; } ; extern
const char_T * RT_MEMORY_ALLOCATION_ERROR ; extern B rtB ; extern X rtX ;
extern DW rtDW ; extern P rtP ; extern mxArray * mr_Model_GetDWork ( ) ;
extern void mr_Model_SetDWork ( const mxArray * ssDW ) ; extern mxArray *
mr_Model_GetSimStateDisallowedBlocks ( ) ; extern const
rtwCAPI_ModelMappingStaticInfo * Model_GetCAPIStaticMap ( void ) ; extern
SimStruct * const rtS ; extern DataMapInfo * rt_dataMapInfoPtr ; extern
rtwCAPI_ModelMappingInfo * rt_modelMapInfoPtr ; void MdlOutputs ( int_T tid )
; void MdlOutputsParameterSampleTime ( int_T tid ) ; void MdlUpdate ( int_T
tid ) ; void MdlTerminate ( void ) ; void MdlInitializeSizes ( void ) ; void
MdlInitializeSampleTimes ( void ) ; SimStruct * raccel_register_model ( ssExecutionInfo * executionInfo ) ;
#endif
