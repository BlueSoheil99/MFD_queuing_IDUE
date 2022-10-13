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
run Copy_of_DQ_Demand_loading

% buffer zone
% I modified 19s into 'num_reg' to be consistent
p = zeros(num_reg,num_reg,num_reg,N); % p_ijst
p_all = zeros(num_reg,num_reg,N); % p_ijt
v_all = zeros(num_reg,num_reg,N); % vijt
q_all = zeros(num_reg,num_reg,N); % qijt

% region
p_region_in = zeros(num_reg, 1); % flow rate out from each region
n_region = zeros(num_reg,N); % nit: number of vehicles in each region
theta_region_to_19 = zeros(num_reg,num_reg,num_reg,N); % thata_ijst: inflow of each region with destination 19, note that this is just for debugging and plotting

% assume the travel time without traffic in the buffer zone is fixed
tau0BZFix = tau0BZ.val;

%% begin
for t=1:T:T*N
    %% specify the demand
    run Copy_of_TimeVariant_demand_loading_new;
    
    %% run the GAMS and get the route flow, i.e., theta
    wgdx('MtoG2', n, q, v, demand, MFD_Para);
    system 'gams Copy_of_DQ_main_19_hexagon_regions_multi_ds_no_control_1012_new lo=3 gdx=GtoM2';
    
    theta.name = 'theta';
    theta = rgdx('GtoM2', theta);
    tau0.name = 'tau0';
    tau0 = rgdx('GtoM2', tau0);
    % Now we can retain only one Cbar at downstream - Ohay
    Cbar.name = 'Cbar';
    Cbar = rgdx('GtoM2', Cbar);

    %% update the theta_ijs to match the size of n, qU, and qD_trans in MATLAB matrixes
    % this is from KKT function of the IDUE (eq. 31 in Qiangqiang's paper)
    theta_gams = zeros(num_reg,num_reg,num_reg); % theta_ijs
    tau0_gams = zeros(num_reg, num_reg); % tau0_ij
    for m1 = 1:1:size(theta.val,1)
        theta_gams(theta.val(m1,1),theta.val(m1,2),theta.val(m1,3)) = theta.val(m1,4);
        % record inflow of each region with destination 19
        theta_region_to_19(theta.val(m1,1),theta.val(m1,2),theta.val(m1,3),t) = theta.val(m1,4);
    end
    for m3 =1:1:size(tau0.val,1)
        tau0_gams(tau0.val(m3,1), tau0.val(m3,2)) = tau0.val(m3,3);
    end

    %% record n_region for plotting
    n_region(:,t)= sum(n.val,2);

    %% calculate p using theta
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        n_regioni = sum(n.val(pairi,d)); % ni
        for j=1:1:size(d,2)
            % pijst = nijst*Pit / (nit*li) <-- completion rate
            p(pairi,pairj,d(j),t) = (mfd_common(1)*n_regioni^2+mfd_common(2)*n_regioni+mfd_common(3))...
                                        /mfd_diff(pairi)*n_div.val(pairi,pairj,d(j));
        end
    end

    %% update p_region_in
    for i = 1:1:num_reg
        n_regioni = sum(n.val(i,d)); % ni
        p_region_in(i) = (mfd_common(1)*n_regioni^2+mfd_common(2)*n_regioni+mfd_common(3))...
                                        /mfd_diff(i)*n_div.val(i,i,i);
    end
    
    %% record p_all, i.e., pij, and update n_div, i.e., nijs
    for i = 1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        p_all(pairi,pairj,t) = sum(p(pairi,pairj,:,t));
        
        n_tmp = sum(n.val(pairi,d));
        for j=1:1:size(d,2)
            region_in = theta_gams(pairi,pairj,d(j));
            region_out = p(pairi,pairj,d(j),t);        
            n_div.val(pairi, pairj,d(j)) = n_div.val(pairi, pairj,d(j)) + region_in - region_out;
        end
    end
    
    %% update flows going into each region
    for i = 1:1:num_reg
        region_in = sum(v.val(:,i,i)) + demand.val(i,i);
        n_div.val(i,i,i) = n_div.val(i,i,i) + region_in - p_region_in(i);
    end

    %% update n.val, i.e., nis
    for i=1:1:num_reg
        for j=1:1:size(d,2)
            n.val(i,d(j)) = sum(n_div.val(i,:,d(j)));
        end
    end
    
    %% check the live number of vehicles
    ['n(19,19,19): ' num2str(n_div.val(19,19,19))] % nijs
    ['n(19): ' num2str(n_region(19,t))] % nit
    
    %% update v and q
    q_out = zeros(num_reg,num_reg,num_reg); % flow out from the queue, a temporary variable helping calculate v
    
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        mask = Cbar.val(:, 1)==pairi;
        Cbar_i = sum(Cbar.val(mask, 3));
        
        % according to the point queue model
        if t > tau0BZFix(pairi,pairj)
            delta_q_i = sum(p_all(pairi,:,t-tau0BZFix(pairi,pairj))) - Cbar_i;
        else
            delta_q_i = 0;
        end
        
        if delta_q_i >= 0
            for k = 1:1:size(d,2)
                % preparing to update v
                if t > tau0BZFix(pairi,pairj)
                    % queue outgoing is proportional to the inflow rate (pijs/pij)
                    q_out(pairi,pairj,d(k)) = q.val(pairi,pairj,d(k)) + p(pairi,pairj,d(k),t-tau0BZFix(pairi,pairj)) / sum(p(pairi,pairj,:,t)) * (Cbar_i-sum(q_all(pairi,:,t)));
                else
                    q_out(pairi,pairj,d(k)) = q.val(pairi,pairj,d(k));
                end
                
                % then we can update v
                v.val(pairi,pairj,d(k)) = q_out(pairi,pairj,d(k));
                
                % update q
                if t > tau0BZFix(pairi,pairj)
                    % update queue: current_queue + inflow - outflow
                    q.val(pairi,pairj,d(k)) = q.val(pairi,pairj,d(k))+ p(pairi,pairj,d(k),t-tau0BZFix(pairi,pairj)) - v.val(pairi,pairj,d(k));
                else
                    q.val(pairi,pairj,d(k)) = q.val(pairi,pairj,d(k)) - q_out(pairi,pairj,d(k));
                end
            end
        else
            % everything flows out
            if t > tau0BZFix(pairi,pairj)
                q_out(pairi,pairj,:) = q.val(pairi,pairj,:) + p(pairi,pairj,:,t-tau0BZFix(pairi,pairj));
            else
                q_out(pairi,pairj,:) = q.val(pairi,pairj,:);
            end
            v.val(pairi,pairj,:) = q_out(pairi,pairj,:);
            q.val(pairi,pairj,:) = 0;
        end
        q_all(pairi,pairj,t) = sum(q.val(pairi,pairj,:));
        v_all(pairi,pairj,t) = sum(v.val(pairi,pairj,:));
    end
    
    


    %% clear tau0 and theta
    y = [];
    theta = [];
    tau0 = [];
    Cbar = [];
    tau0BZ.val = tau0BZFix;
    
    % show the time step
    ['t: ' num2str(t)]
end
    
                        
