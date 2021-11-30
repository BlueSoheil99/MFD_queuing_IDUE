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
p_all = zeros(19,19); % pij
p = zeros(19,19,19,N); % pijst
v_trans = zeros(19,19,19,N); % vijst
v_all = zeros(19,19,N); % vijN
p_all_plot = zeros(19,19,N);
qU = zeros(19,19,19,N); % qUijst
qD_trans = zeros(19,19,19,N); % qDijst
qU_all = zeros(19,19,N); % qUijt
qD_all = zeros(19,19,N); % qDijt
withheld = zeros(19,19,19,N); % withheld_ijst
withheld_all = zeros(19,19);

% region
p_region_in = zeros(1,num_reg);
n_region = zeros(19,N); % nit: number of vehicles in each region
theta_region_to_19 = zeros(19,N); % thata_it: inflow of each region with destination 19

% IDUE
theta_trans = zeros(19,19,19); % theta_ijs

% tempo
Cbar_trans = [];
tauOBZ = tau0BZ.val * 2;

%% begin
qD_trans(:,:,:,1) = qD.val;
for t=1:T:T*N
    %% specify the demand
    run TimeVariant_demand_loading_new;
    
    %% run the GAMS and get the route flow
    wgdx('MtoG2', n, qD, v, demand, MFD_Para, tau0BZ);
    system 'gams DQ_main_19_hexagon_regions_multi_ds_no_control_1012 lo=3 gdx=GtoM2';

    n.val(n.val<=0.001) = 0;
    
    theta.name = 'theta';
    theta = rgdx('GtoM2', theta);
    tau0.name = 'tau0';
    tau0 = rgdx('GtoM2', tau0);
    Cbar.name = 'Cbar';
    Cbar = rgdx('GtoM2', Cbar);
    Cbar_trans = Cbar.val;

    %% calculate Qbar, i.e., Qbar_ij
    Qbar = zeros(19,19);
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1); 
        pairj = region_communi(i,2);
        Qbar(pairi,pairj) = Cbar_trans(i,3)*(tauOBZ(pairi,pairj) + tau0BZ.val(pairi,pairj));
    end

    %% transform the tau0 to match the size of n, qU, and qD_trans in MATLAB matrixes
    if ~isempty(tau0.val)
        tau0_trans = zeros(19,19); 
        for m1 =1:1:size(tau0.val,1)
            tau0_trans(tau0.val(m1,1), tau0.val(m1,2)) = tau0.val(m1,3);
        end
    end

    %% record data for plotting
    for i=1:1:num_reg
        % record inflow of each region with destination 19
        theta_region_to_19(i,t) = sum(theta_trans(i,:,19));
        % number of vehicles in each region
        n_region(i,t) = sum(n.val(i,:));
    end

    %% update the MFD dynamics: update n.div, i.e., nijs by equation (6)
    for i=1:1:size(region_communi,1)
        for j=1:1:size(d,2)
            pairi = region_communi(i,1); 
            pairj = region_communi(i,2);
            n_div.val(pairi,pairj,d(j)) = n_div.val(pairi,pairj,d(j)) + T* ( theta_trans(pairi,pairj,d(j)) - p(pairi,pairj,d(j),t) );
        end
    end

    %% update n.val in region i, i.e., nii^(s=i) by equation (5)
    for i = 1:1:num_reg
        % first, calculate c_i^(s=i)
        n_temp = sum(n.val(i,d));
        p_region_in(i) = (mfd_common(1)*n_temp^2+mfd_common(2)*n_temp+mfd_common(3))/mfd_diff(i)*n_div.val(i,i,i);
        % second, calculate nii^(s=i)
        region_in = sum(v_trans(:,i,i,t)) + demand.val(i,i);
        n_div.val(i,i,i) = n_div.val(i,i,i) + region_in - p_region_in(i);
    end

    %% update n.val in other regions, i.e., nijs by equation (5) 
    for i=1:1:num_reg
        for j=1:1:size(d,2)
            n.val(i,d(j)) = sum(n_div.val(i,:,d(j)));
        end
    end
    
    %% calculate the pTilda using theta: equation (8)
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        n_regioni = sum(n.val(pairi,:)); % ni
        for j=1:1:size(d,2)
            pairj = region_communi(i,2);
            pTilda(pairi,pairj,d(j)) = (mfd_common(1)*n_regioni^2+mfd_common(2)*n_regioni+mfd_common(3))/mfd_diff(pairi)*n_div.val(pairi,pairj,d(j));
        end
    end

    %% calculate p_all, i.e., pij: equation (13-15)
    for i = 1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        pTilda_all(pairi,pairj) = sum(pTilda(pairi,pairj,:));
        % equation: p = min(p, Cbar, Qbar-qU)
        p_all(pairi,pairj) = min([pTilda_all(pairi,pairj) ...
                              Cbar_trans(i,3) ...
                              ( Qbar(pairi,pairj)-qU_all(pairi,pairj,t) )/T]);
    end
    
    withheld_all = pTilda_all - p_all;

    %% calculate p, i.e., pijs at equation (9)
    for i=1:1:size(region_communi,1)
        for j=1:1:size(d,2)
            pairi = region_communi(i,1);
            if pTilda_all(pairi,pairj) > 0
                p(pairi,pairj,d(j),t) = pTilda(pairi,pairj,d(j)) / pTilda_all(pairi,pairj) * p_all(pairi,pairj);
            end
            withheld(pairi,pairj,d(j),t) = pTilda(pairi,pairj,d(j)) - p(pairi,pairj,d(j),t);
        end
        % calculate p_all_plot, i.e., pij
        p_all_plot(pairi,pairj,t) = sum(p(pairi,pairj,:,t));
    end

    %% calculate qU, i.e., qUijs: equation (10)
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1); 
        pairj = region_communi(i,2);

        if t <= tauOBZ(pairi,pairj)
            % equation (9)
            if t-1 > 0
                qU(:,:,:,t) = T*p(:,:,:,t) + qU(:,:,:,t-1);
                % update qU_all, i.e., qUij
                qU_all(pairi,pairj,t) = sum(qU(pairi,pairj,:,t));
                % calculate exit flow
                if t > tau0BZ.val(pairi, pairj)
                    for j=1:1:size(d,2)
                        v_trans(pairi,pairj,d(j),t) = p(pairi,pairj,d(j),t-tau0BZ.val(pairi, pairj));
                    end
                end
            else
                qU(:,:,:,t) = T*p(:,:,:,t);
                % update qU_all, i.e., qUij
                qU_all(pairi,pairj,t) = sum(qU(pairi,pairj,:,t));
            end
        else
            % equation (10)
            qD_all(pairi,pairj,t) = sum(qD_trans(pairi,pairj,:,t));
            for j=1:1:size(d,2)
                % second, calculate v_trans, i.e., vijs
                if qD_all > 0
                    v_trans(pairi,pairj,d(j),t) = qD_trans(pairi,pairj,d(j),t) / qD_all(pairi,pairj,t) * v_all(pairi,pairj,t);
                end
                % third, calculate qU, i.e., qUijs
                qU(pairi,pairj,d(j),t) = qU(pairi,pairj,d(j),t-1) + T * ( p(pairi,pairj,d(j),t) - v_trans(pairi,pairj,d(j),t-tauOBZ(pairi,pairj)) );
            end
            % update qU_all, i.e., qUij
            qU_all(pairi,pairj,t) = sum(qU(pairi,pairj,:,t));
        end
        % calculate v_all, i.e., vij
        v_all(pairi,pairj,t) = sum(v_trans(pairi,pairj,:,t));
    end

    %% calculate qD, i.e., qD_trans
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1); 
        pairj = region_communi(i,2);
        if t > tau0_trans(pairi,pairj)
            % equation (12)
            for j=1:1:size(d,2)
                % first, check if vijs reaches Cbar
                if v_trans(pairi,pairj,d(j),t) == Cbar_trans(i,3)
                    % second, calculate qD_trans
                    qD_trans(pairi,pairj,d(j),t) = qD_trans(pairi,pairj,d(j),t-1) + T * ( p(pairi,pairj,d(j),t-tau0_trans(pairi,pairj)) - v_trans(pairi,pairj,d(j),t) );
                end
            end
        end
    end

    qD.val = qD_trans(:,:,:,t);

    %% update v.val
    v.val = v_trans(:,:,:,t);
    
    %% update the theta_ijs to match the size of n, qU, and qD_trans in MATLAB matrixes
    for m1 = 1:1:size(theta.val,1)
        theta_trans(theta.val(m1,1),theta.val(m1,2),theta.val(m1,3)) = theta.val(m1,4);
    end

    n_div.val(19,19,19)
    n_region(19,t)

    %% clear tau0 and theta
    theta = [];
    tau0 = [];
    Cbar = [];
    n.val(n.val<=1e-4) = 0.0001;
    
    % show the time step
    t
end   
    
                        
