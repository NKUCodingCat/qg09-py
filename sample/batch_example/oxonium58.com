%mem=5120mb
%NProcShared=16
# b3lyp/genecp opt(MaxC=80) scfcyc=256

Coal_kick_v2_Trial # 58

0 1
C   -1.299553    1.892758   -6.890046
H   -1.713396    0.896904   -7.093333
O   -1.491994    2.532499   -5.894349
O   -0.541646    2.287922   -7.930065
O   -0.528016    4.408013   -4.982074
H   -0.029346    4.917290   -5.628221
H    0.031233    3.653648   -4.772996
O   -0.357711   -0.528384   -7.118820
H    0.296063   -1.226685   -7.221267
H    0.073837    0.140670   -6.578753
O    1.687495    2.490710   -7.603708
H    1.979563    2.750623   -6.724685
H    2.491340    2.244751   -8.071551
O   -2.635523    1.510096  -12.204221
H   -2.584966    2.006888  -11.381918
H   -1.867934    1.789393  -12.712493
O   -1.540444    0.790577   -9.710221
H   -2.496859    0.613564   -9.597745
H   -1.093266    0.679736   -8.841498
H   -1.403657    1.696331   -9.995385

C O 0
6-31+G*
****
H 0
3-21g
****



