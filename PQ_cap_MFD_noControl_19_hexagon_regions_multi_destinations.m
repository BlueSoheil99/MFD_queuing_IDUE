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
run PQ_cap_Demand_loading

% buffer zone
% I modified 19s into 'num_reg' to be consistent
p = zeros(num_reg,num_reg,num_reg,N); % p_ijst
pTilde = zeros(num_reg,num_reg,num_reg,N); % pTilde_ijst
p_all = zeros(num_reg,num_reg,N); % p_ijt
pTilde_all = zeros(num_reg,num_reg,N); % pTilde_ijt
v_all = zeros(num_reg,num_reg,N); % vijt
q_all = zeros(num_reg,num_reg,N); % qijt

% region
n_region = zeros(num_reg,N); % nit: number of vehicles in each region
theta_region_to_19 = zeros(num_reg,num_reg,num_reg,N); % thata_ijst: inflow of each region with destination 19, note that this is just for debugging and plotting

% assume the travel time without traffic in the buffer zone is fixed
tau0BZFix = tau0BZ.val;

% assume max number of vehicles in buffer zone is 10% of the upstream
% region
proportion = 0.1;

%% begin
for t=1:T:T*N
    %% specify the demand
    run TimeVariant_demand_loading_new;
    
    %% run the GAMS and get the route flow, i.e., theta
    wgdx('MtoG', n, q, v, demand, MFD_Para, Cbar, tau0BZ);
    system 'gams PQ_cap_main_19_hexagon_regions_multi_ds_no_control_1012 lo=3 gdx=GtoM';
    
    theta.name = 'theta';
    theta = rgdx('GtoM', theta);
    tau0.name = 'tau0';
    tau0 = rgdx('GtoM', tau0);

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

    %% calculate pTilde using theta and vacancy
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        n_regioni = sum(n.val(pairi,d)); % ni
        for j=1:1:size(d,2)
            % pTilde_ijst = nijst*Pit / (nit*li) <-- completion rate
            pTilde(pairi,pairj,d(j),t) = (mfd_common(1)*n_regioni^2+mfd_common(2)*n_regioni+mfd_common(3))...
                                        /mfd_diff(pairi)*n_div.val(pairi,pairj,d(j));
        end
        pTilde_all(pairi,pairj,t) = sum(pTilde(pairi,pairj,:,t));
    end
    % calculate pTilde_iiit using theta and vacancy
    for i=1:1:num_reg
        n_regioni = sum(n.val(i,d)); % ni
        % pTilde_iiit = niiit*Pit / (nit*li) <-- completion rate
        pTilde(i,i,i,t) = (mfd_common(1)*n_regioni^2+mfd_common(2)*n_regioni+mfd_common(3))...
                                    /mfd_diff(i)*n_div.val(i,i,i);
        pTilde_all(i,i,t) = sum(pTilde(i,i,:,t));
    end
    
    %% check whetehr the buffer zone has enough space to accommodate pTilde
    for i=1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        lambda = proportion * n_bar(pairi) - q_all(pairi,pairj,t);
        if lambda >= pTilde_all(pairi,pairj,t)
            % pijt = pTilde_ijt
            for j=1:1:size(d,2)
                p(pairi,pairj,d(j),t) = pTilde(pairi,pairj,d(j),t);
            end
        else
            % pijt = lambda
            % pijst = pijt * pTilde_ijst/pTilde_ijt
            for j=1:1:size(d,2)
                p(pairi,pairj,d(j),t) = lambda * pTilde(pairi,pairj,d(j),t) / pTilde_all(pairi,pairj,t);
            end
        end
    end
    % check whetehr the buffer zone has enough space to accommodate
    % pTilde_iiit
    for i=1:1:num_reg
        lambda = proportion * n_bar(i) - q_all(i,i,t);
        if lambda >= pTilde_all(i,i,t)
            % pijt = pTilde_iit
            p(i,i,i,t) = pTilde(i,i,i,t);
        else
            % piit = lambda
            % piist = piit * pTilde_iiit/pTilde_iit
            p(i,i,i,t) = lambda * pTilde(i,i,i,t) / pTilde_all(i,i,t);
        end
    end
    
    %% record p_all, i.e., pij, and update n_div, i.e., nijs
    for i = 1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);
        p_all(pairi,pairj,t) = sum(p(pairi,pairj,:,t));
        
        n_tmp = sum(n.val(pairi,d));
        for j=1:1:size(d,2)
            region_in = theta_gams(pairi,pairj,d(j));
            region_out = v.val(pairi,pairj,d(j));
            n_div.val(pairi,pairj,d(j)) = n_div.val(pairi,pairj,d(j)) + region_in - region_out;
        end
    end
    
    %% update p_all_iit and update n_div_iii, i.e., niii
    for i = 1:1:num_reg
        p_all(i,i,t) = sum(p(i,i,:,t));
        region_in = demand.val(i,i);
        region_out = v.val(i,i,i);
        n_div.val(i,i,i) = n_div.val(i,i,i) + region_in - region_out;
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
    
    %% update capacity of each buffer zone
    if t > 1
        for i = 1:1:size(region_communi,1)
            pairi = region_communi(i,1);
            pairj = region_communi(i,2);
            flow_waiting_up = 0;
            if t <= tau0BZFix(pairi,pairj)
                % compute how much flow is waiting for going out at buffer ij
                flow_waiting_ij = q_all(pairi,pairj,t-1);
                % compute how much flow is waiting for going out at all upstreams
                upstreams = region_communi(:,2) == pairj;
                upstreams = region_communi(upstreams,:);
                for h = 1:1:size(upstreams,1)
                    flow_waiting_up = flow_waiting_up + ...
                                      q_all(upstreams(h,1),pairj,t-1);
                end
            else
                % compute how much flow is waiting for going out at buffer ij
                flow_waiting_ij = p_all(pairi,pairj,t-tau0BZFix(pairi,pairj)) + q_all(pairi,pairj,t-1);
                % compute how much flow is waiting for going out at all upstreams
                upstreams = region_communi(:,2) == pairj;
                upstreams = region_communi(upstreams,:);
                for h = 1:1:size(upstreams,1)
                    flow_waiting_up = flow_waiting_up + ...
                                      p_all(upstreams(h,1),pairj,t-tau0BZFix(upstreams(h,1),pairj)) + ...
                                      q_all(upstreams(h,1),pairj,t-1);
                end
            end
            % distribute capacities
            if flow_waiting_up == 0
                Cbar.val(pairi,pairj) = 20000;
            else
                Cbar.val(pairi,pairj) = ( n_bar(pairj) - sum(n.val(pairj,d)) ) * ...
                                        flow_waiting_ij / flow_waiting_up;
            end
                                
            % update v and q
            if Cbar.val(pairi,pairj) >= flow_waiting_ij
                % vijt = flow_waiting_ij
                if t <= tau0BZFix(pairi,pairj)
                    for j=1:1:size(d,2)
                        v.val(pairi,pairj,d(j)) = q.val(pairi,pairj,d(j));
                        % clean up the previous queue
                        q.val(pairi,pairj,d(j)) = 0;
                    end
                else
                    for j=1:1:size(d,2)
                        v.val(pairi,pairj,d(j)) = q.val(pairi,pairj,d(j)) + ...
                                                  p(pairi,pairj,d(j),t-tau0BZFix(pairi,pairj));
                        % clean up the previous queue
                        q.val(pairi,pairj,d(j)) = 0;
                    end
                end
            else
                % vijt = Cbar_ijt
                % vijst = vijt * flow_waiting_ijs/flow_waiting_ij
                if t <= tau0BZFix(pairi,pairj)
                    q_sum = sum(q.val(pairi,pairj,d));
                    for j=1:1:size(d,2)
                        v.val(pairi,pairj,d(j)) = Cbar.val(pairi,pairj) * ...
                                                  q.val(pairi,pairj,d(j)) / q_sum;
                        % clean up the previous queue
                        q.val(pairi,pairj,d(j)) = 0;
                    end
                else
                    q_sum = sum(q.val(pairi,pairj,d)) + sum(p(pairi,pairj,d,t-tau0BZFix(pairi,pairj)));
                    for j=1:1:size(d,2)
                        flow_waiting_ij = q.val(pairi,pairj,d(j)) + p(pairi,pairj,d(j),t-tau0BZFix(pairi,pairj));
                        v.val(pairi,pairj,d(j)) = Cbar.val(pairi,pairj) * ...
                                                  flow_waiting_ij / q_sum;
                        % the remaining flow+queue forms a new queue
                        q.val(pairi,pairj,d(j)) = q.val(pairi,pairj,d(j)) + flow_waiting_ij - v.val(pairi,pairj,d(j));
                    end
                end
                
            end
            q_all(pairi,pairj,t) = sum(q.val(pairi,pairj,:));
            v_all(pairi,pairj,t) = sum(v.val(pairi,pairj,:));
        end
        
        % update viiit and qiiit
        for i = 1:1:num_reg
            flow_waiting_up = 0;
            % compute how much flow is waiting for going out at buffer ii
            flow_waiting_ij = p_all(i,i,t) + q_all(i,i,t-1);
            % compute how much flow is waiting for going out at all upstreams
            upstreams = region_communi(:,2) == i;
            upstreams = region_communi(upstreams,:);
            for h = 1:1:size(upstreams,1)
                flow_waiting_up = flow_waiting_up + ...
                                  p_all(upstreams(h,1),i,t) + ...
                                  q_all(upstreams(h,1),i,t-1);
            end
            % distribute capacities Cbar_ii
            if flow_waiting_up == 0
                Cbar.val(i,i) = 20000;
            else
                Cbar.val(i,i) = ( n_bar(i) - sum(n.val(i,d)) ) * ...
                                flow_waiting_ij / flow_waiting_up;
            end
                                
            % update vii and qii
            if Cbar.val(i,i) >= flow_waiting_ij
                % viit = flow_waiting_ii
                v.val(i,i,i) = q.val(i,i,i) + p(i,i,i,t); 
                % clean up the previous queue
                q.val(i,i,i) = 0;
            else
                % viit = Cbar_iit
                % viiit = viit * flow_waiting_iii/flow_waiting_ii
                q_sum = sum(q.val(i,i,d)) + sum(p(i,i,d,t));
                flow_waiting_ij = q.val(i,i,i) + p(i,i,i,t);
                v.val(i,i,i) = Cbar.val(i,i) * flow_waiting_ij / q_sum;
                % the remaining flow+queue forms a new queue
                q.val(i,i,i) = q.val(i,i,i) + flow_waiting_ij - v.val(i,i,i);
                
            end
            q_all(i,i,t) = sum(q.val(i,i,:));
            v_all(i,i,t) = sum(v.val(i,i,:));
        end
    end
    
    %% clear tau0 and theta
    theta = [];
    tau0 = [];
    tau0BZ.val = tau0BZFix;
    
    % show the time step
    ['t: ' num2str(t)]
end
    
                        