clear
clc
%% Mode
limit_n = [5300];
%demand_choice = [0.3, 0.3, 0.2]; % 0.275, 0.275, 0.2]; %0.3, 0.2, 0.1];
% demand_choice = [0.3, 0.3, 0.2; 0.275, 0.275, 0.2; 0.25, 0.25, 0.2];
% demand_choice =[0.3, 0.25, 0.15; 0.325, 0.275, 0.15; 0.275, 0.225, 0.15];

% demand_choice =[0.35, 0.25, 0.15; 0.325, 0.225, 0.125; 0.3, 0.2, 0.1];
% [0.25, 0.225, 0.2] low
% [0.3, 0.25, 0.2] high
%  [0.28, 0.24, 0.2] high
demand_choice =[0.35, 0.25, 0.15; 0.3, 0.25, 0.15];
demand_choice =[0.3, 0.25, 0.15];

queueType = 'PQ'; % DQ

for ite_num =1:1:length(limit_n)
    for ite_dem =1:1:size(demand_choice,1)
        % define the MFD parameter (change the average trip length)
        region.name = 'i';
        region.uels = {'1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19'};
        coff.name = 'coff';
        coff.uels = {'m3', 'm2', 'm1', 'length', 'n_bar', 'm0'};
        MFD_Para.name = 'MFD_Para';
        MFD_Para.val = [
            1.4877e-7, -2.9815e-3, 15.0912, 6100, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 6100, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 6100, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 5800, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 5800, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 5800, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 5500, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 5500, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 5500, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 5800, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 5800, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 5800, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 4800, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 4800, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 4500, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 4500, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 4500, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 4500, limit_n(ite_num), 1;...
            1.4877e-7, -2.9815e-3, 15.0912, 3600, limit_n(ite_num), 1];
        MFD_Para.type = 'parameter';
        MFD_Para.form = 'full';
        MFD_Para.dim = 2;
        MFD_Para.uels = {region.uels, coff.uels};

        n_bar = limit_n(ite_num)*ones(1,19); % 20000 for no control, 4000 for control
        d_high = demand_choice(ite_dem, 1); % 0.2 for light demand, 0.3 for mild demand, 0.4 for high demand
        d_medi = demand_choice(ite_dem, 2); %0.1 0.2 0.3
        d_low = demand_choice(ite_dem, 3); % 0.1 0.1 0.2

        filename = '';
        if strcmp(queueType,'DQ')
            run DQ_MFD_noControl_19_hexagon_regions_multi_destinations.m
            filename = strcat('n_19_hexagon_regions_multi_ds_withdemand_7200_',num2str(ite_dem+1),'_', num2str(limit_n(ite_num)),'_DQ.mat');
        elseif strcmp(queueType,'PQ')
            run PQ_MFD_Control_19_hexagon_regions_multi_destinations.m
            filename = strcat('n_19_hexagon_regions_multi_ds_withdemand_7200_',num2str(ite_dem+1),'_', num2str(limit_n(ite_num)),'_PQ.mat');
        end

        save(filename)
        clearvars -except limit_n ite_num ite_dem demand_choice
    end
end
%fixfare
