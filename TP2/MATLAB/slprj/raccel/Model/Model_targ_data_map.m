    function targMap = targDataMap(),

    ;%***********************
    ;% Create Parameter Map *
    ;%***********************
    
        nTotData      = 0; %add to this count as we go
        nTotSects     = 1;
        sectIdxOffset = 0;

        ;%
        ;% Define dummy sections & preallocate arrays
        ;%
        dumSection.nData = -1;
        dumSection.data  = [];

        dumData.logicalSrcIdx = -1;
        dumData.dtTransOffset = -1;

        ;%
        ;% Init/prealloc paramMap
        ;%
        paramMap.nSections           = nTotSects;
        paramMap.sectIdxOffset       = sectIdxOffset;
            paramMap.sections(nTotSects) = dumSection; %prealloc
        paramMap.nTotData            = -1;

        ;%
        ;% Auto data (rtP)
        ;%
            section.nData     = 30;
            section.data(30)  = dumData; %prealloc

                    ;% rtP.F_equilibrium
                    section.data(1).logicalSrcIdx = 0;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.alpha
                    section.data(2).logicalSrcIdx = 1;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.b
                    section.data(3).logicalSrcIdx = 2;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.beta
                    section.data(4).logicalSrcIdx = 3;
                    section.data(4).dtTransOffset = 3;

                    ;% rtP.g
                    section.data(5).logicalSrcIdx = 4;
                    section.data(5).dtTransOffset = 4;

                    ;% rtP.lambda
                    section.data(6).logicalSrcIdx = 5;
                    section.data(6).dtTransOffset = 5;

                    ;% rtP.mu
                    section.data(7).logicalSrcIdx = 6;
                    section.data(7).dtTransOffset = 6;

                    ;% rtP.x_ref
                    section.data(8).logicalSrcIdx = 7;
                    section.data(8).dtTransOffset = 7;

                    ;% rtP.OutputSamplePoints_Value
                    section.data(9).logicalSrcIdx = 8;
                    section.data(9).dtTransOffset = 8;

                    ;% rtP.OutputSamplePoints_Value_fi4mzupike
                    section.data(10).logicalSrcIdx = 9;
                    section.data(10).dtTransOffset = 109;

                    ;% rtP.x_Gain
                    section.data(11).logicalSrcIdx = 10;
                    section.data(11).dtTransOffset = 210;

                    ;% rtP.v_Gain
                    section.data(12).logicalSrcIdx = 11;
                    section.data(12).dtTransOffset = 211;

                    ;% rtP.theta_Gain
                    section.data(13).logicalSrcIdx = 12;
                    section.data(13).dtTransOffset = 212;

                    ;% rtP.omega_Gain
                    section.data(14).logicalSrcIdx = 13;
                    section.data(14).dtTransOffset = 213;

                    ;% rtP.rad2deg_Gain
                    section.data(15).logicalSrcIdx = 14;
                    section.data(15).dtTransOffset = 214;

                    ;% rtP.Gain2_Gain
                    section.data(16).logicalSrcIdx = 15;
                    section.data(16).dtTransOffset = 215;

                    ;% rtP.Gain3_Gain
                    section.data(17).logicalSrcIdx = 16;
                    section.data(17).dtTransOffset = 216;

                    ;% rtP.Gain4_Gain
                    section.data(18).logicalSrcIdx = 17;
                    section.data(18).dtTransOffset = 217;

                    ;% rtP.Gain_Gain
                    section.data(19).logicalSrcIdx = 18;
                    section.data(19).dtTransOffset = 218;

                    ;% rtP.Gain1_Gain
                    section.data(20).logicalSrcIdx = 19;
                    section.data(20).dtTransOffset = 219;

                    ;% rtP.rad2deg_Gain_lxjc2yxzwi
                    section.data(21).logicalSrcIdx = 20;
                    section.data(21).dtTransOffset = 220;

                    ;% rtP.Constant_Value
                    section.data(22).logicalSrcIdx = 21;
                    section.data(22).dtTransOffset = 221;

                    ;% rtP.Constant1_Value
                    section.data(23).logicalSrcIdx = 22;
                    section.data(23).dtTransOffset = 222;

                    ;% rtP.Constant_Value_ljjrc4ac51
                    section.data(24).logicalSrcIdx = 23;
                    section.data(24).dtTransOffset = 223;

                    ;% rtP.Constant1_Value_kmf41b2fgv
                    section.data(25).logicalSrcIdx = 24;
                    section.data(25).dtTransOffset = 224;

                    ;% rtP.Constant2_Value
                    section.data(26).logicalSrcIdx = 25;
                    section.data(26).dtTransOffset = 225;

                    ;% rtP.Constant3_Value
                    section.data(27).logicalSrcIdx = 26;
                    section.data(27).dtTransOffset = 226;

                    ;% rtP.Constant4_Value
                    section.data(28).logicalSrcIdx = 27;
                    section.data(28).dtTransOffset = 227;

                    ;% rtP.Constant2_Value_kcodwcpjwp
                    section.data(29).logicalSrcIdx = 28;
                    section.data(29).dtTransOffset = 228;

                    ;% rtP.Constant3_Value_jqw25fydac
                    section.data(30).logicalSrcIdx = 29;
                    section.data(30).dtTransOffset = 229;

            nTotData = nTotData + section.nData;
            paramMap.sections(1) = section;
            clear section


            ;%
            ;% Non-auto Data (parameter)
            ;%


        ;%
        ;% Add final counts to struct.
        ;%
        paramMap.nTotData = nTotData;



    ;%**************************
    ;% Create Block Output Map *
    ;%**************************
    
        nTotData      = 0; %add to this count as we go
        nTotSects     = 1;
        sectIdxOffset = 0;

        ;%
        ;% Define dummy sections & preallocate arrays
        ;%
        dumSection.nData = -1;
        dumSection.data  = [];

        dumData.logicalSrcIdx = -1;
        dumData.dtTransOffset = -1;

        ;%
        ;% Init/prealloc sigMap
        ;%
        sigMap.nSections           = nTotSects;
        sigMap.sectIdxOffset       = sectIdxOffset;
            sigMap.sections(nTotSects) = dumSection; %prealloc
        sigMap.nTotData            = -1;

        ;%
        ;% Auto data (rtB)
        ;%
            section.nData     = 15;
            section.data(15)  = dumData; %prealloc

                    ;% rtB.i4ibtq5tq2
                    section.data(1).logicalSrcIdx = 0;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.hodcriesct
                    section.data(2).logicalSrcIdx = 1;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.fnz2ukyuey
                    section.data(3).logicalSrcIdx = 2;
                    section.data(3).dtTransOffset = 2;

                    ;% rtB.bae3kxdkxa
                    section.data(4).logicalSrcIdx = 3;
                    section.data(4).dtTransOffset = 3;

                    ;% rtB.huwdxda24q
                    section.data(5).logicalSrcIdx = 4;
                    section.data(5).dtTransOffset = 4;

                    ;% rtB.ef22fglmc4
                    section.data(6).logicalSrcIdx = 5;
                    section.data(6).dtTransOffset = 5;

                    ;% rtB.o2bkv5how4
                    section.data(7).logicalSrcIdx = 6;
                    section.data(7).dtTransOffset = 6;

                    ;% rtB.acvw55fb1k
                    section.data(8).logicalSrcIdx = 7;
                    section.data(8).dtTransOffset = 7;

                    ;% rtB.oaoe1nh5ne
                    section.data(9).logicalSrcIdx = 8;
                    section.data(9).dtTransOffset = 8;

                    ;% rtB.oi4cubqypg
                    section.data(10).logicalSrcIdx = 9;
                    section.data(10).dtTransOffset = 9;

                    ;% rtB.pwovlhpygb
                    section.data(11).logicalSrcIdx = 10;
                    section.data(11).dtTransOffset = 10;

                    ;% rtB.jvak5lfibj
                    section.data(12).logicalSrcIdx = 11;
                    section.data(12).dtTransOffset = 11;

                    ;% rtB.jpfkxzwvew
                    section.data(13).logicalSrcIdx = 12;
                    section.data(13).dtTransOffset = 12;

                    ;% rtB.fsd5migfwm
                    section.data(14).logicalSrcIdx = 13;
                    section.data(14).dtTransOffset = 13;

                    ;% rtB.fgymxyjrsj
                    section.data(15).logicalSrcIdx = 17;
                    section.data(15).dtTransOffset = 114;

            nTotData = nTotData + section.nData;
            sigMap.sections(1) = section;
            clear section


            ;%
            ;% Non-auto Data (signal)
            ;%


        ;%
        ;% Add final counts to struct.
        ;%
        sigMap.nTotData = nTotData;



    ;%*******************
    ;% Create DWork Map *
    ;%*******************
    
        nTotData      = 0; %add to this count as we go
        nTotSects     = 3;
        sectIdxOffset = 1;

        ;%
        ;% Define dummy sections & preallocate arrays
        ;%
        dumSection.nData = -1;
        dumSection.data  = [];

        dumData.logicalSrcIdx = -1;
        dumData.dtTransOffset = -1;

        ;%
        ;% Init/prealloc dworkMap
        ;%
        dworkMap.nSections           = nTotSects;
        dworkMap.sectIdxOffset       = sectIdxOffset;
            dworkMap.sections(nTotSects) = dumSection; %prealloc
        dworkMap.nTotData            = -1;

        ;%
        ;% Auto data (rtDW)
        ;%
            section.nData     = 4;
            section.data(4)  = dumData; %prealloc

                    ;% rtDW.hyu31ldq2t.LoggedData
                    section.data(1).logicalSrcIdx = 0;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.j0ia4lh5q0.LoggedData
                    section.data(2).logicalSrcIdx = 1;
                    section.data(2).dtTransOffset = 2;

                    ;% rtDW.gvjlmgo4qr.LoggedData
                    section.data(3).logicalSrcIdx = 2;
                    section.data(3).dtTransOffset = 4;

                    ;% rtDW.d4tg3oq402.AQHandles
                    section.data(4).logicalSrcIdx = 3;
                    section.data(4).dtTransOffset = 5;

            nTotData = nTotData + section.nData;
            dworkMap.sections(1) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtDW.pmtqx3h1e3
                    section.data(1).logicalSrcIdx = 4;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.n4pvolfz54
                    section.data(2).logicalSrcIdx = 5;
                    section.data(2).dtTransOffset = 1;

                    ;% rtDW.hsjxaf4xuu
                    section.data(3).logicalSrcIdx = 6;
                    section.data(3).dtTransOffset = 2;

                    ;% rtDW.jcwkxcjazh
                    section.data(4).logicalSrcIdx = 7;
                    section.data(4).dtTransOffset = 3;

                    ;% rtDW.b3pat3zjtu
                    section.data(5).logicalSrcIdx = 8;
                    section.data(5).dtTransOffset = 4;

                    ;% rtDW.mcc443bqjq
                    section.data(6).logicalSrcIdx = 9;
                    section.data(6).dtTransOffset = 5;

            nTotData = nTotData + section.nData;
            dworkMap.sections(2) = section;
            clear section

            section.nData     = 10;
            section.data(10)  = dumData; %prealloc

                    ;% rtDW.pzz1vpadaz
                    section.data(1).logicalSrcIdx = 10;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.eipmzcijh3
                    section.data(2).logicalSrcIdx = 11;
                    section.data(2).dtTransOffset = 1;

                    ;% rtDW.aezhyafilx
                    section.data(3).logicalSrcIdx = 12;
                    section.data(3).dtTransOffset = 2;

                    ;% rtDW.apfxvndcfy
                    section.data(4).logicalSrcIdx = 13;
                    section.data(4).dtTransOffset = 3;

                    ;% rtDW.f5jgkvark0
                    section.data(5).logicalSrcIdx = 14;
                    section.data(5).dtTransOffset = 4;

                    ;% rtDW.gyiyn3pusw
                    section.data(6).logicalSrcIdx = 15;
                    section.data(6).dtTransOffset = 5;

                    ;% rtDW.ohadoud2hj
                    section.data(7).logicalSrcIdx = 16;
                    section.data(7).dtTransOffset = 6;

                    ;% rtDW.irjp15fgq3
                    section.data(8).logicalSrcIdx = 17;
                    section.data(8).dtTransOffset = 7;

                    ;% rtDW.i3r1o4qdrs
                    section.data(9).logicalSrcIdx = 18;
                    section.data(9).dtTransOffset = 8;

                    ;% rtDW.kkyqcp3sdb
                    section.data(10).logicalSrcIdx = 19;
                    section.data(10).dtTransOffset = 9;

            nTotData = nTotData + section.nData;
            dworkMap.sections(3) = section;
            clear section


            ;%
            ;% Non-auto Data (dwork)
            ;%


        ;%
        ;% Add final counts to struct.
        ;%
        dworkMap.nTotData = nTotData;



    ;%
    ;% Add individual maps to base struct.
    ;%

    targMap.paramMap  = paramMap;
    targMap.signalMap = sigMap;
    targMap.dworkMap  = dworkMap;

    ;%
    ;% Add checksums to base struct.
    ;%


    targMap.checksum0 = 582358476;
    targMap.checksum1 = 735546513;
    targMap.checksum2 = 3805285384;
    targMap.checksum3 = 3614979379;

