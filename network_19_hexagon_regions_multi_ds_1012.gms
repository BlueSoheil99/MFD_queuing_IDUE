$ontext
Network configuration data file
region and link sets are defined in this file, together with the data needed to define the MFD function
$offtext

set nodes 'nodes set' /1*19/;
alias(nodes, i, j, h, k);
set desti(i) 'destination set' /13, 14, 15, 16, 17, 18, 19/;
alias(desti, d, d2);
set coff 'cofficient set' / m3, m2, m1, length, n_bar, m0/;

parameter
         n(i,d) 'vehicle numbers in region i with destination d',
         q(i,j,d) 'queued vehicle numbers at the boundary of (i,j) with destination d',
         v(i,j,d) 'region-inflow of region j from region i for vehicles with destination d',
         demand(i,d) 'demand from region i to d',
         MFD_Para(i, coff) 'cost parameter table';

$GDXIN MtoG2
$LOAD n q v demand MFD_Para

MFD_Para(j, 'm3')$(sum(d2, n(j,d2))>10000)=0;
MFD_Para(j, 'm2')$(sum(d2, n(j,d2))>10000)=0;
MFD_Para(j, 'm1')$(sum(d2, n(j,d2))>10000)=0;
MFD_Para(j, 'm0')$(sum(d2, n(j,d2))>10000)=4256;

parameter u_bar(i,j) 'the control limit at boundary (i,j)'
/
1.2   3
1.12  3
1.13  3
2.1   3
2.3   3
2.13  3
2.14  3
3.2   3
3.4   3
3.14  3
4.3   3
4.5   3
4.14  3
4.15  3
5.4   3
5.6   3
5.15  3
6.5   3
6.7   3
6.15  3
6.16  3
7.6   3
7.8   3
7.16  3
8.7   3
8.9   3
8.16  3
8.17  3
9.8   3
9.10  3
9.17  3
10.9  3
10.11 3
10.17 3
10.18 3
11.10 3
11.12 3
11.18 3
12.1  3
12.11 3
12.13 3
12.18 3
13.1  3
13.2  3
13.12 3
13.14 4
13.18 4
13.19 5
14.2  3
14.3  3
14.4  3
14.13 4
14.15 4
14.19 4
15.4  3
15.5  3
15.6  3
15.14 4
15.16 4
15.19 5
16.6  3
16.7  3
16.8  3
16.15 4
16.17 5
16.19 5
17.8  3
17.9  3
17.10 3
17.16 4
17.18 4
17.19 5
18.10 3
18.11 3
18.12 3
18.13 4
18.17 4
18.19 5
19.13 5
19.14 5
19.15 5
19.16 5
19.17 5
19.18 5
/;

set region_communi(i,j) /
1.2
1.12
1.13
2.1
2.3
2.13
2.14
3.2
3.4
3.14
4.3
4.5
4.14
4.15
5.4
5.6
5.15
6.5
6.7
6.15
6.16
7.6
7.8
7.16
8.7
8.9
8.16
8.17
9.8
9.10
9.17
10.9
10.11
10.17
10.18
11.10
11.12
11.18
12.1
12.11
12.13
12.18
13.1
13.2
13.12
13.14
13.18
13.19
14.2
14.3
14.4
14.13
14.15
14.19
15.4
15.5
15.6
15.14
15.16
15.19
16.6
16.7
16.8
16.15
16.17
16.19
17.8
17.9
17.10
17.16
17.18
17.19
18.10
18.11
18.12
18.13
18.17
18.19
19.13
19.14
19.15
19.16
19.17
19.18
/;
