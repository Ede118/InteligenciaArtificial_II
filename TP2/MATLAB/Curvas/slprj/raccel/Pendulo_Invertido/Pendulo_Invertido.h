#ifndef Pendulo_Invertido_h_
#define Pendulo_Invertido_h_
#ifndef Pendulo_Invertido_COMMON_INCLUDES_
#define Pendulo_Invertido_COMMON_INCLUDES_
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
#include "Pendulo_Invertido_types.h"
#include <stddef.h>
#include "rtw_modelmap_simtarget.h"
#include "rt_defines.h"
#include <string.h>
#include "rtGetInf.h"
#define MODEL_NAME Pendulo_Invertido
#define NSAMPLE_TIMES (3) 
#define NINPUTS (0)       
#define NOUTPUTS (0)     
#define NBLOCKIO (16) 
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
typedef struct { real_T outputMFCache [ 707 ] ; real_T blxaed2wc0 ; real_T
k5illwhoex ; real_T jicflel3c3 ; real_T ofs3mtvtjb ; real_T k1yzzvuzag ;
real_T j2kuyafaot ; real_T eb55xegd4r ; real_T l5ohccctkt ; real_T e25rqytwh3
[ 101 ] ; real_T pf4lo52t41 [ 101 ] ; } B ; typedef struct { struct { void *
LoggedData [ 2 ] ; } bh3kv04epg ; struct { void * LoggedData [ 2 ] ; }
i2g3ohyvfw ; struct { void * LoggedData ; } ey3q1tzi13 ; struct { void *
AQHandles ; } evkzwszu40 ; struct { void * AQHandles ; } ppmdczu4mp ; struct
{ void * AQHandles ; } cnpw23eeqs ; struct { void * AQHandles ; } fpohlb5inb
; struct { void * AQHandles ; } amui5p22zh ; int32_T awd4remi3d ; int32_T
l5jlrwfo5p ; int32_T ajuu4o34d4 ; int32_T afjwwbd1zg ; int32_T muilfja3py ;
int32_T po0gdatv5f ; boolean_T hqc20cgd5s ; boolean_T hv33d2cjoh ; boolean_T
d3vmlwb11k ; boolean_T huvrv5yhg5 ; boolean_T dzlklt2yro ; boolean_T
ni4srgylnb ; } DW ; typedef struct { real_T bdpgmhanly ; real_T hknrf2m3fn ;
real_T ocrtvyfusb ; real_T cigppkynts ; } X ; typedef struct { real_T
bdpgmhanly ; real_T hknrf2m3fn ; real_T ocrtvyfusb ; real_T cigppkynts ; }
XDot ; typedef struct { boolean_T bdpgmhanly ; boolean_T hknrf2m3fn ;
boolean_T ocrtvyfusb ; boolean_T cigppkynts ; } XDis ; typedef struct {
real_T bdpgmhanly ; real_T hknrf2m3fn ; real_T ocrtvyfusb ; real_T cigppkynts
; } CStateAbsTol ; typedef struct { real_T bdpgmhanly ; real_T hknrf2m3fn ;
real_T ocrtvyfusb ; real_T cigppkynts ; } CXPtMin ; typedef struct { real_T
bdpgmhanly ; real_T hknrf2m3fn ; real_T ocrtvyfusb ; real_T cigppkynts ; }
CXPtMax ; typedef struct { rtwCAPI_ModelMappingInfo mmi ; } DataMapInfo ;
struct P_ { real_T G_F ; real_T G_omega ; real_T G_theta ; real_T G_theta_ref
; real_T G_v ; real_T G_x ; real_T alpha ; real_T b ; real_T beta ; real_T
dtheta_0 ; real_T dx_0 ; real_T g ; real_T lambda ; real_T mu ; real_T
theta_0 ; real_T x_ref ; real_T OutputSamplePoints_Value [ 101 ] ; real_T
OutputSamplePoints_Value_fi4mzupike [ 101 ] ; real_T theta_Gain ; real_T
rad2deg_Gain ; real_T Constant2_Value ; real_T Constant2_Value_kcodwcpjwp ;
real_T Constant3_Value ; } ; extern const char_T * RT_MEMORY_ALLOCATION_ERROR
; extern B rtB ; extern X rtX ; extern DW rtDW ; extern P rtP ; extern
mxArray * mr_Pendulo_Invertido_GetDWork ( ) ; extern void
mr_Pendulo_Invertido_SetDWork ( const mxArray * ssDW ) ; extern mxArray *
mr_Pendulo_Invertido_GetSimStateDisallowedBlocks ( ) ; extern const
rtwCAPI_ModelMappingStaticInfo * Pendulo_Invertido_GetCAPIStaticMap ( void )
; extern SimStruct * const rtS ; extern DataMapInfo * rt_dataMapInfoPtr ;
extern rtwCAPI_ModelMappingInfo * rt_modelMapInfoPtr ; void MdlOutputs ( int_T
tid ) ; void MdlOutputsParameterSampleTime ( int_T tid ) ; void MdlUpdate ( int_T tid ) ; void MdlTerminate ( void ) ; void MdlInitializeSizes ( void ) ; void MdlInitializeSampleTimes ( void ) ; SimStruct * raccel_register_model ( ssExecutionInfo * executionInfo ) ;
#endif
