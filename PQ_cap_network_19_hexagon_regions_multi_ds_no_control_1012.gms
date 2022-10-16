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
         q(i,j,d) 'downstream queued vehicle numbers at the boundary of (i,j) with destination d',
         v(i,j,d) 'region-inflow of region j from region i for vehicles with destination d',
         demand(i,d) 'demand from region i to d',
         MFD_Para(i,coff) 'cost parameter table',
         Cbar(i,j) 'capacity of buffer zone (i,j)',
         tau0BZ(i,j) '';

$GDXIN MtoG
$LOAD n q v demand MFD_Para Cbar tau0BZ

MFD_Para(j, 'm3')$(sum(d2, n(j,d2))>10000)=0;
MFD_Para(j, 'm2')$(sum(d2, n(j,d2))>10000)=0;
MFD_Para(j, 'm1')$(sum(d2, n(j,d2))>10000)=0;
MFD_Para(j, 'm0')$(sum(d2, n(j,d2))>10000)=4256;


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
