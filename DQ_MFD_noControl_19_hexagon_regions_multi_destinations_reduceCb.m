%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
%%%% Main file of the MFD based perimeter control considering Instanteneous Dynamic User Equilibrium
%%%% Qiangqiang Guo, July 27th, 2018
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% the main program
% at each time step, do the following
% step 1: write the vehicle number, queue length, and demand to GAMS gdx
% step 2: solve the DCS problem by calling GAMS program, and get the result
% step 3: update the vehicle number, queue length
% step 4: go back to step 1
run DQ_Demand_loading

% buffer zone
pTilda = zeros(19,19,19); % pTilda_ijs
pTilda_all = zeros(19,19);
p_all = zeros(19,19,N); % pij
p = zeros(19,19,19,N); % pijst
n_trans = zeros(19,19,19,N); % nijst
v_trans = zeros(19,19,19,N); % vijst
v_all = zeros(19,19,N); % vijN
qU = zeros(19,19,19,N); % qUijst
qD_trans = zeros(19,19,19,N); % qDijst
qU_all = zeros(19,19,N); % qUijt
qD_all = zeros(19,19,N); % qDijt
withheld = zeros(19,19,19,N); % withheld_ijst
withheld_all = zeros(19,19);

% region
p_region_in = zeros(1,num_reg);
n_region = zeros(19,N); % nit: number of vehicles in each region
theta_region_to_19 = zeros(19,19,19,N); % thata_it: inflow of each region with destination 19

% tempo
Cbar_trans = [];
tauOBZ = tau0BZ.val * 2;
tau0BZFix = tau0BZ.val;

%% begin
qD_trans(:,:,:,1) = 0;
for t=1:T:T*N
    %% specify the demand
    run TimeVariant_demand_loading_new;
    
    %% run the GAMS and get the route flow, i.e., theta
    wgdx('MtoG2', n, qD, v, demand, MFD_Para, tau0BZ);
    system 'gams DQ_main_19_hexagon_regions_multi_ds_no_control_1012_new_reduceCbar lo=3 gdx=GtoM2';
    
    theta.name = 'theta';
    theta = rgdx('GtoM2', theta);
    tau0.name = 'tau0';
    tau0 = rgdx('GtoM2', tau0);
    Cbar.name = 'Cbar';
    Cbar = rgdx('GtoM2', Cbar);
    Cbar_trans = Cbar.val;

    %% update the theta_ijs to match the size of n, qU, and qD_trans in MATLAB matrixes
    theta_trans = zeros(19,19,19); % theta_ijs
    for m1 = 1:1:size(theta.val,1)
        theta_trans(theta.val(m1,1),theta.val(m1,2),theta.val(m1,3)) = theta.val(m1,4);
        % record inflow of each region with destination 19
        theta_region_to_19(theta.val(m1,1),theta.val(m1,2),theta.val(m1,3),t) = theta.val(m1,4);
    end

    %% record data for plotting
    for i=1:1:num_reg
        % number of vehicles in each region
        n_region(i,t) = sum(n.val(i,:));
    end

    %% prepare Cbar_trans_trans for calculating v
    Cbar_trans_trans = zeros(19,19);
    for m1 = 1:1:size(Cbar.val,1)
        Cbar_trans_trans(Cbar.val(m1,1),Cbar.val(m1,2)) = Cbar.val(m1,3);
    end

    %% calculate Qbar, i.e., Qbar_ij
    Qbar = zeros(19,19);
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1); 
        pairj = region_communi(i,2);
        Qbar(pairi,pairj) = Cbar_trans(i,3)*(tauOBZ(pairi,pairj) + tau0BZFix(pairi,pairj));
    end

    %% calculate the pTilda using theta: equation (8)
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        n_regioni = sum(n.val(pairi,d)); % ni
        for j=1:1:size(d,2)
            pTilda(pairi,pairj,d(j)) = (mfd_common(1)*n_regioni^2+mfd_common(2)*n_regioni+mfd_common(3))...
                                        /mfd_diff(pairi)*n_div.val(pairi,pairj,d(j));
        end
    end

    %% transform the tau0 to match the size of n, qU, and qD_trans in MATLAB matrixes
    tau0_trans = zeros(19,19); 
    for m1 =1:1:size(tau0.val,1)
        tau0_trans(tau0.val(m1,1), tau0.val(m1,2)) = tau0.val(m1,3);
    end

    %% calculate p_all, i.e., pij: equation (13-15)
    for i = 1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        pTilda_all(pairi,pairj) = sum(pTilda(pairi,pairj,:));
        % equation: p = min(p, Cbar, Qbar-qU)
        if t > 1
            p_all(pairi,pairj,t) = min([pTilda_all(pairi,pairj) ...
                                  Cbar_trans(i,3) ...
                                  ( Qbar(pairi,pairj)-qU_all(pairi,pairj,t-1) )/T]);
        else
            p_all(pairi,pairj,t) = min([pTilda_all(pairi,pairj) ...
                                  Cbar_trans(i,3)]);
        end
    end
    
    withheld_all = pTilda_all - p_all(:,:,t);

    %% calculate v_all, i.e., vij: equation (11)
    for i = 1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        % equation: v = min(qD/T + p(t-tau0BZFix), Cbar)
        if t > tau0BZFix(pairi, pairj)
            v_all(pairi,pairj,t) = min([qD_all(pairi,pairj,t-1)/T + p_all(pairi,pairj,t-tau0BZFix(pairi, pairj)) ...
                                  Cbar_trans(i,3)]);
        end
    end

    %% calculate p, i.e., pijs at equation (9)
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        for j=1:1:size(d,2)
            if pTilda_all(pairi,pairj) > 0
                p(pairi,pairj,d(j),t) = pTilda(pairi,pairj,d(j)) / pTilda_all(pairi,pairj) * p_all(pairi,pairj,t);
            end
            withheld(pairi,pairj,d(j),t) = pTilda(pairi,pairj,d(j)) - p(pairi,pairj,d(j),t);
        end
    end

    %% calculate exit flow, i.e., vijs at equation (10)
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        if t > tau0BZFix(pairi, pairj)
            % use capacity to distribute the flow
            total_cap_downstream = sum(Cbar_trans_trans(pairj,d));
            for j=1:1:size(d,2)
                if v_all(pairi,pairj,t) > 0
                    % need to distribute the v
                    v_trans(pairi,pairj,d(j),t) = (p(pairi,pairj,d(j),t-tau0BZFix(pairi, pairj)) + qD_trans(pairi,pairj,d(j),t-1)) / ...
                                                    (p_all(pairi,pairj,t-tau0BZFix(pairi, pairj)) + qD_all(pairi,pairj,t-1)) * ...
                                                    v_all(pairi,pairj,t);
                end
            end
        end
    end

    %% update n.val in region i, i.e., nii^(s=i) by equation (5)
    for i = 1:1:num_reg
        % first, calculate c_i^(s=i)
        n_temp = sum(n.val(i,d));
        p_region_in(i) = (mfd_common(1)*n_temp^2+mfd_common(2)*n_temp+mfd_common(3))/mfd_diff(i)*n_div.val(i,i,i);
        % second, calculate nii^(s=i)
        region_in = sum(v.val(:,i,i)) + demand.val(i,i);
        n_div.val(i,i,i) = n_div.val(i,i,i) + region_in*T - p_region_in(i)*T;
    end

    %% update the MFD dynamics: update n.div, i.e., nijs by equation (6)
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1); 
        pairj = region_communi(i,2);
        for j=1:1:size(d,2)
            delta = theta_trans(pairi,pairj,d(j)) - p(pairi,pairj,d(j),t);
            if delta > 0 && delta < 0.0001
                delta = 0;
            end
            n_div.val(pairi,pairj,d(j)) = n_div.val(pairi,pairj,d(j)) + T*delta;
            n_trans(pairi,pairj,d(j),t) = n_div.val(pairi,pairj,d(j));
        end
    end

    %% update n.val in other regions, i.e., nijs by equation (5) 
    for i=1:1:num_reg
        for j=1:1:size(d,2)
            n.val(i,d(j)) = sum(n_div.val(i,:,d(j)));
        end
    end

    %% calculate qU, i.e., qUijs: equation (10)
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1); 
        pairj = region_communi(i,2);
        
        if t <= tauOBZ(pairi,pairj)
            if t-1 > 0
                % equation (9)
                qU(:,:,:,t) = qU(:,:,:,t-1) + T*p(:,:,:,t);
            else
                % equation (9)
                qU(:,:,:,t) = T*p(:,:,:,t);% + ones(19,19,19)*0.00001;
            end
        else
            for j=1:1:size(d,2)
                % equation (10)
                qU(pairi,pairj,d(j),t) = qU(pairi,pairj,d(j),t-1) + T*( p(pairi,pairj,d(j),t) - v_trans(pairi,pairj,d(j),t-tauOBZ(pairi,pairj)) );
                if qU(pairi,pairj,d(j),t) < 0
                    qU(pairi,pairj,d(j),t) = 0;
                end
            end
        end
    end

    %% calculate qD_trans, i.e., qD at equation (12)
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1); 
        pairj = region_communi(i,2);
        for j=1:1:size(d,2)
            if t > tau0BZFix(pairi,pairj)
                if p(pairi,pairj,d(j),t-tau0BZFix(pairi, pairj)) - v_trans(pairi,pairj,d(j),t) > 0
                    'k'
                end
                qD_trans(pairi,pairj,d(j),t) = qD_trans(pairi,pairj,d(j),t-1) + T * ( p(pairi,pairj,d(j),t-tau0BZFix(pairi, pairj)) - v_trans(pairi,pairj,d(j),t) );
            end
            if qD_trans(pairi,pairj,d(j),t) < 0
                qD_trans(pairi,pairj,d(j),t) = 0;
            end
        end
    end

    %% compute qD_all and qU_all
    for i=1:1:num_reg
        for j=1:1:num_reg
            qD_all(i,j,t) = sum(qD_trans(i,j,:,t));
            % update qU_all, i.e., qUij
            qU_all(i,j,t) = sum(qU(i,j,:,t));
        end
    end

    qD.val = qD_trans(:,:,:,t);

    %% update v.val
    v.val = v_trans(:,:,:,t);

    n_div.val(19,19,19)
    n_region(19,t)
    n_region(12,t)
    n_div.val(13,19,19)

    %% clear tau0 and theta
    theta = [];
    tau0 = [];
    Cbar = [];
    tau0BZ.val = tau0BZFix;
    
    % show the time step
    t
end
    
                        
