#include "Pendulo_Invertido_capi_host.h"
static Pendulo_Invertido_host_DataMapInfo_T root;
static int initialized = 0;
rtwCAPI_ModelMappingInfo *getRootMappingInfo()
{
    if (initialized == 0) {
        initialized = 1;
        Pendulo_Invertido_host_InitializeDataMapInfo(&(root), "Pendulo_Invertido");
    }
    return &root.mmi;
}

rtwCAPI_ModelMappingInfo *mexFunction(){return(getRootMappingInfo());}
