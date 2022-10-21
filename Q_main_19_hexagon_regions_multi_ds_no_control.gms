$ontext
This is the implementation of the MFD based perimeter control considering Instanteneous Dynamic User Equilibrium (DCS part)
Given the vehicle number, upstream queue length, downstream queue length, and demand profiles, this program aims to find the shortest paths and assign the traffic accordingly
July 26th, Qiangqiang Guo
$offtext

* settings and import parameters
option limrow = 300, limcol = 100, solprint = on;

$include Q_network_19_hexagon_regions_multi_ds_no_control.gms

*variables
nonnegative variable
         theta(i,j,d) 'the queue inflow of the boundary (i,j)',
         tau0(i,d) 'the minimum travel time from region i to destination';

equations
         theta_com(i,j,d) 'the complimentary term of theta(i,j,d)',
         tau0_com(i,d) 'the complimentary term of tau0(i,d)';


* the DCS formulation
theta_com(i,j,d)$region_communi(i,j) ..          MFD_Para(i, 'length')*sum(d2, m(i,d2))/(MFD_Para(i, 'm3')*power(sum(d2, m(i,d2)),3)+MFD_Para(i, 'm2')*power(sum(d2, m(i,d2)),2)+MFD_Para(i, 'm1')*sum(d2, m(i,d2)) + MFD_Para(i, 'm0')) + sum(d2, q(i,j,d2))/(u(i,j)+0.1) + tau0(j,d) - tau0(i,d) =g= 0;
tau0_com(i,d)..                                  sum(region_communi(i,j), theta(i,j,d))-sum(region_communi(k,i), v(k,i,d))-demand(i,d) =g= 0;

tau0.fx(i,d)$(sameas(i,d))=0;

* solve the problem
model mfd / theta_com.theta, tau0_com.tau0 /;
solve mfd using mcp

scalar Umodstat, Usolstat,Tmodstat, Tsolstat;
Umodstat = mfd.Modelstat;
Usolstat = mfd.solvestat;
