#ifndef Pendulo_Invertido_types_h_
#define Pendulo_Invertido_types_h_
#include "rtwtypes.h"
#ifndef DEFINED_TYPEDEF_FOR_struct_xtQT47lHfr5Mo2IBULZqGH_
#define DEFINED_TYPEDEF_FOR_struct_xtQT47lHfr5Mo2IBULZqGH_
typedef struct { uint8_T SimulinkDiagnostic ; uint8_T Model [ 34 ] ; uint8_T
Block [ 55 ] ; uint8_T OutOfRangeInputValue ; uint8_T NoRuleFired ; uint8_T
EmptyOutputFuzzySet ; uint8_T sl_padding0 [ 3 ] ; }
struct_xtQT47lHfr5Mo2IBULZqGH ;
#endif
#ifndef DEFINED_TYPEDEF_FOR_struct_nDiNttezQ8pHMZv76leKsH_
#define DEFINED_TYPEDEF_FOR_struct_nDiNttezQ8pHMZv76leKsH_
typedef struct { uint8_T type [ 6 ] ; uint8_T sl_padding0 [ 2 ] ; int32_T
origTypeLength ; uint8_T sl_padding1 [ 4 ] ; real_T params [ 4 ] ; int32_T
origParamLength ; uint8_T sl_padding2 [ 4 ] ; } struct_nDiNttezQ8pHMZv76leKsH
;
#endif
#ifndef DEFINED_TYPEDEF_FOR_struct_lMtpFmLOVR7rlweqgH5LGF_
#define DEFINED_TYPEDEF_FOR_struct_lMtpFmLOVR7rlweqgH5LGF_
typedef struct { struct_nDiNttezQ8pHMZv76leKsH mf [ 7 ] ; int32_T origNumMF ;
uint8_T sl_padding0 [ 4 ] ; } struct_lMtpFmLOVR7rlweqgH5LGF ;
#endif
#ifndef DEFINED_TYPEDEF_FOR_struct_dDSOYl9OoEyVp7RIL82ESF_
#define DEFINED_TYPEDEF_FOR_struct_dDSOYl9OoEyVp7RIL82ESF_
typedef struct { uint8_T type [ 7 ] ; uint8_T andMethod [ 3 ] ; uint8_T
orMethod [ 3 ] ; uint8_T defuzzMethod [ 8 ] ; uint8_T impMethod [ 3 ] ;
uint8_T aggMethod [ 3 ] ; uint8_T sl_padding0 [ 5 ] ; real_T inputRange [ 4 ]
; real_T outputRange [ 2 ] ; struct_lMtpFmLOVR7rlweqgH5LGF inputMF [ 2 ] ;
struct_lMtpFmLOVR7rlweqgH5LGF outputMF ; real_T antecedent [ 98 ] ; real_T
consequent [ 49 ] ; real_T connection [ 49 ] ; real_T weight [ 49 ] ; int32_T
numSamples ; int32_T numInputs ; int32_T numOutputs ; int32_T numRules ;
int32_T numInputMFs [ 2 ] ; int32_T numCumInputMFs [ 2 ] ; int32_T
numOutputMFs ; int32_T numCumOutputMFs ; real_T outputSamplePoints [ 101 ] ;
int32_T orrSize [ 2 ] ; int32_T aggSize [ 2 ] ; int32_T irrSize [ 2 ] ;
int32_T rfsSize [ 2 ] ; int32_T sumSize [ 2 ] ; int32_T inputFuzzySetType ;
uint8_T sl_padding1 [ 4 ] ; } struct_dDSOYl9OoEyVp7RIL82ESF ;
#endif
#ifndef DEFINED_TYPEDEF_FOR_struct_yoOojIVh9IDmOigOG4nqVE_
#define DEFINED_TYPEDEF_FOR_struct_yoOojIVh9IDmOigOG4nqVE_
typedef struct { uint8_T SimulinkDiagnostic ; uint8_T Model [ 34 ] ; uint8_T
Block [ 51 ] ; uint8_T OutOfRangeInputValue ; uint8_T NoRuleFired ; uint8_T
EmptyOutputFuzzySet ; uint8_T sl_padding0 [ 7 ] ; }
struct_yoOojIVh9IDmOigOG4nqVE ;
#endif
#ifndef SS_UINT64
#define SS_UINT64 22
#endif
#ifndef SS_INT64
#define SS_INT64 23
#endif
typedef struct P_ P ;
#endif
