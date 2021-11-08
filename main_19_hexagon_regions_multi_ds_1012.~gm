$ontext
This is the implementation of the MFD based perimeter control considering Instanteneous Dynamic User Equilibrium (DCS part)
Given the vehicle number, queue length, and demand profiles, this program aims to find the shortest paths and assign the traffic accordingly
July 26th, Qiangqiang Guo
$offtext

* settings and import parameters
option limrow = 300, limcol = 100, solprint = on;

$include network_19_hexagon_regions_multi_ds_1012.gms

*variables
nonnegative variable
         theta(i,j,d) 'the queue inflow of the boundary (i,j)',
         eta(i,d) 'the minimum travel time from region i to destination',
         y(i,j) 'auxiliary variable for u(i,j)',
         lamda(i,j) 'auxiliary variable for u(i,j)',
         mu(i,j) 'auxiliary variable for u(i,j)' ;

equations
         theta_com(i,j,d) 'the complimentary term of p(i,j,d)',
         eta_com(i,d) 'the complimentary term of eta(i,d)',
         y_com(i,j) 'the complimentary term of y(i,j)',
         lamda_com(i,j) 'the complimentary term of lamda(i,j)',
         mu_com(i,j) 'the complimentary term of mu(i,j)';


* the DCS formulation
theta_com(i,j,d)$region_communi(i,j) ..          MFD_Para(i, 'length')*sum(d2, n(i,d2))/(MFD_Para(i, 'm3')*power(sum(d2, n(i,d2)),3)+MFD_Para(i, 'm2')*power(sum(d2, n(i,d2)),2)+MFD_Para(i, 'm1')*sum(d2, n(i,d2)) + MFD_Para(i, 'm0'))+ sum(d2, q(i,j,d2))/(y(i,j)*(MFD_Para(j, 'n_bar')-sum(d2, n(j,d2)))+0.1)+eta(j,d)-eta(i,d) =g= 0;
eta_com(i,d)..                                   sum(region_communi(i,j), theta(i,j,d))-sum(region_communi(k,i), v(k,i,d))-demand(i,d) =g= 0;
*eta_com(i,d)..                                   (MFD_Para(i, 'm3')*power(sum(d2, n(i,d2)),3)+MFD_Para(i, 'm2')*power(sum(d2, n(i,d2)),2)+MFD_Para(i, 'm1')*sum(d2, n(i,d2)) + MFD_Para(i, 'm0'))/sum(d2, n(i,d2))*n(i,d)/MFD_Para(i, 'length') - sum(region_communi(i,j), p(i,j,d))=g= 0;
y_com(i,j)$region_communi(i,j)..                 (lamda(i,j)-mu(i,j)-1)*(MFD_Para(j, 'n_bar')-sum(d2, n(j,d2))) =g= 0;
lamda_com(i,j)$region_communi(i,j)..             u_bar(i,j)-y(i,j)*(MFD_Para(j, 'n_bar')-sum(d2, n(j,d2))) =g= 0;
mu_com(i,j)$region_communi(i,j)..                y(i,j)*(MFD_Para(j, 'n_bar')-sum(d2, n(j,d2))) =g= 0;

eta.fx(i,d)$(sameas(i,d))=0;

* solve the problem
model mfd / theta_com.theta, eta_com.eta, y_com.y, lamda_com.lamda, mu_com.mu /;
solve mfd using mcp

scalar Umodstat, Usolstat,Tmodstat, Tsolstat;
Umodstat = mfd.Modelstat;
Usolstat = mfd.solvestat;