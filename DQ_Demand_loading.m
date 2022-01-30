%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
%%%% Main file of the MFD based perimeter control considering Instanteneous Dynamic User Equilibrium
%%%% Qiangqiang Guo, July 27th, 2018
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% parameter setting
T = 1;          % simulate time interval (s)
N = 8000;       % simulate steps
cut = 2700;     % demand stop time
% cut = 1800;     % demand stop time
num_reg = 19;   % region number
d = [13, 14, 15, 16, 17, 18, 19];       % destination

% n_bar = 4000*ones(1,19);    % n_bar
%n_bar = 4000*ones(1,19);    % n_bar
% destination mfd
%length1
% len = [7000, 6500, 6000, 5000, 4500, 2500];
% length2
len = [6100, 5800, 5500, 4800, 4500, 3600]; % trip length
mfd_common =[1.4877e-7, -2.9815e-3, 15.0912];
mfd_diff = [len(1), len(1), len(1), len(2), len(2), len(2), len(3), len(3), len(3), len(2), len(2), len(2),...
    len(4), len(4), len(5), len(5), len(5), len(5), len(6)];
% mfd_14 =[1.4877e-7, -2.9815e-3, 15.0912, len(1), n_bar(14)];
% mfd_15 =[1.4877e-7, -2.9815e-3, 15.0912, len(2), n_bar(15)];
% mfd_16 =[1.4877e-7, -2.9815e-3, 15.0912, len(2), n_bar(16)];
% mfd_17 =[1.4877e-7, -2.9815e-3, 15.0912, len(2), n_bar(17)];
% mfd_18 =[1.4877e-7, -2.9815e-3, 15.0912, len(2), n_bar(18)];
% mfd_19 =[1.4877e-7, -2.9815e-3, 15.0912, len(3), n_bar(19)];

% region community
region_communi = [1 2; 1 12; 1 13; 2 1; 2 3; 2 13; 2 14; 3 2; 3 4; 3 14; 4 3; 4 5; 4 14; 4 15; 5 4; 5 6; 5 15;...   
    6 5; 6 7; 6 15; 6 16; 7 6; 7 8; 7 16; 8 7; 8 9; 8 16; 8 17; 9 8; 9 10; 9 17; 10 9; 10 11; 10 17; 10 18; 11 10;...   
    11 12; 11 18; 12 1; 12 11; 12 13; 12 18; 13 1; 13 2; 13 12; 13 14; 13 18; 13 19; 14 2; 14 3; 14 4; 14 13; 14 15;...   
    14 19; 15 4; 15 5; 15 6; 15 14; 15 16; 15 19; 16 6; 16 7; 16 8; 16 15; 16 17; 16 19; 17 8; 17 9; 17 10; 17 16;...   
    17 18; 17 19; 18 10; 18 11; 18 12; 18 13; 18 17; 18 19; 19 13; 19 14; 19 15; 19 16; 19 17; 19 18];

% initial vehicle numbers in each region
i1.name = 'i1';
i1.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
i2.name = 'i2';
i2.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
n.name = 'n';
n.type = 'parameter';
n.form = 'full';
n.uels = {i1.uels,i2.uels};
% 
% n_rural_suburban =200;
% n_rural_far_suburban =200;
% n.val(1:19,19) = 200;
n_rural_suburban =1;
n_rural_far_suburban =1;
n.val(1:19,19) = 1;
n.val(1,13) = n_rural_suburban; n.val(1,14) = n_rural_suburban; n.val(1,18) = n_rural_suburban;
n.val(1,15:17) = n_rural_far_suburban;
n.val(2,13) = n_rural_suburban; n.val(2,14) = n_rural_suburban; n.val(2,15) = n_rural_suburban; n.val(2,18) = n_rural_suburban;
n.val(2,16:17) = n_rural_far_suburban;
n.val(3,13) = n_rural_suburban; n.val(3,14) = n_rural_suburban; n.val(3,15) = n_rural_suburban;
n.val(3,16:18) = n_rural_far_suburban;
n.val(4,13) = n_rural_suburban; n.val(4,14) = n_rural_suburban; n.val(4,15) = n_rural_suburban; n.val(4,16) = n_rural_suburban;
n.val(4,17:18) = n_rural_far_suburban;
n.val(5,14) = n_rural_suburban; n.val(5,15) = n_rural_suburban; n.val(5,16) = n_rural_suburban;
n.val(5,17:18) = n_rural_far_suburban; n.val(5,13) = n_rural_far_suburban;
n.val(6,14) = n_rural_suburban; n.val(6,15) = n_rural_suburban; n.val(6,16) = n_rural_suburban; n.val(6,17) = n_rural_suburban;
n.val(6,13) = n_rural_far_suburban; n.val(6,18) = n_rural_far_suburban;
n.val(7,15) = n_rural_suburban; n.val(7,16) = n_rural_suburban; n.val(7,17) = n_rural_suburban;
n.val(7,13:14) = n_rural_far_suburban; n.val(7,18) = n_rural_far_suburban;
n.val(8,15) = n_rural_suburban; n.val(8,16) = n_rural_suburban; n.val(8,17) = n_rural_suburban; n.val(8,18) = n_rural_suburban; 
n.val(8,13:14) = n_rural_far_suburban;
n.val(9,16) = n_rural_suburban; n.val(9,17) = n_rural_suburban; n.val(9,18) = n_rural_suburban;
n.val(9,13:15) = n_rural_far_suburban;
n.val(10,16) = n_rural_suburban; n.val(10,17) = n_rural_suburban; n.val(10,18) = n_rural_suburban; n.val(10,13) = n_rural_suburban;
n.val(10,14:15) = n_rural_far_suburban;
n.val(11,13) = n_rural_suburban; n.val(11,17) = n_rural_suburban; n.val(11,18) = n_rural_suburban;
n.val(11,14:16) = n_rural_far_suburban;
n.val(12,13) = n_rural_suburban; n.val(12,14) = n_rural_suburban; n.val(12,17) = n_rural_suburban; n.val(12,18) = n_rural_suburban;
n.val(12,15:16) = n_rural_far_suburban;

n.val(13,13:18) = n_rural_far_suburban;
n.val(13,13) = n_rural_suburban;
n.val(14,13:18) = n_rural_far_suburban;
n.val(14,14) = n_rural_suburban;
n.val(15,13:18) = n_rural_far_suburban;
n.val(15,15) = n_rural_suburban;
n.val(16,13:18) = n_rural_far_suburban;
n.val(16,16) = n_rural_suburban;
n.val(17,13:18) = n_rural_far_suburban;
n.val(17,17) = n_rural_suburban;
n.val(18,13:18) = n_rural_far_suburban;
n.val(18,18) = n_rural_suburban;
n.val(19,13:18) = n_rural_far_suburban;
n.val(19,19) = n_rural_suburban;
% n.val(13,14:18) = n_rural_far_suburban;
% n.val(14,15:18) = n_rural_far_suburban; n.val(14,13) = n_rural_far_suburban;
% n.val(15,16:18) = n_rural_far_suburban; n.val(15,13:14) = n_rural_far_suburban;
% n.val(16,17:18) = n_rural_far_suburban; n.val(16,13:15) = n_rural_far_suburban;
% n.val(17,18) = n_rural_far_suburban; n.val(17,13:16) = n_rural_far_suburban;
% n.val(18,13:17) = n_rural_far_suburban;
% n.val(19,13:18) = n_rural_far_suburban;

%initial destination and boundary specified vehicle
j1.name = 'j1';
j1.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
j2.name = 'j2';
j2.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
j3.name = 'j3';
j3.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
n_div.name = 'n_div';
n_div.type = 'parameter';
n_div.form = 'full';
n_div.uels = {j1.uels, j2.uels, j3.uels};
n_div.val = zeros(19,19,19);%ones(19,19,19);%zeros(19,19,19);

for i=1:1:num_reg
    for j=1:1:size(d,2)
        n.val(i,d(j)) = sum(n_div.val(i,:,d(j))) + 1;
    end
end


%initial queue length at each boundary
k1.name = 'k1';
k1.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
k2.name = 'k2';
k2.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
k3.name = 'k3';
k3.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
qD.name = 'qD';
qD.type = 'parameter';
qD.form = 'full';
qD.uels = {k1.uels, k2.uels, k3.uels};
qD.val = zeros(19,19,19);%ones(19,19,19)*0.00001;%zeros(19,19,19);%ones(19,19,19);

%initial exit flow at the boundaries
l1.name = 'l1';
l1.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
l2.name = 'l2';
l2.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
l3.name = 'l3';
l3.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
v.name = 'v';
v.type = 'parameter';
v.form = 'full';
v.uels = {l1.uels, l2.uels, l3.uels};
v.val = zeros(19,19,19);

% the minimum travel time at each boundary
% assume all the buffe zones share the same travel time
m1.name = 'm1';
m1.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
m2.name = 'm2';
m2.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
m3.name = 'm3';
m3.uels = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'};
tau0BZ.name = 'tau0BZ';
tau0BZ.type = 'parameter';
tau0BZ.form = 'full';
tau0BZ.uels = {m1.uels, m2.uels};
tau0BZ.val = ones(19,19); % 1 second

% demand
demand.name = 'demand';
demand.type = 'parameter';
demand.form = 'full';
demand.uels = {i1.uels,i2.uels};
demand.val = zeros(19,19);
    
                        
