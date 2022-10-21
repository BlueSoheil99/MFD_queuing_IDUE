%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
%%%% Main file of the MFD based Queueing Model Considering Instanteneous Dynamic User Equilibrium
%%%% Ohay Angah, October 18th, 2022
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% the main program
% at each time step, do the following
% step 1: write the vehicle number, queue length, and demand to GAMS gdx
% step 2: solve the DCS problem by calling GAMS program, and get the result
% step 3: update the vehicle number, queue length
% step 4: go to step 1
run Q_Demand_loading

% buffer zone
% I modified 19s into 'num_reg' to be consistent
p = zeros(num_reg,num_reg,num_reg,N); % p_ijst
w = zeros(num_reg,num_reg,num_reg); %w_ijt, note that we don't record w at every time step
p_all = zeros(num_reg,num_reg,N); % p_ijt
v_all = zeros(num_reg,num_reg,N); % vijt
q_all = zeros(num_reg,num_reg,N); % qijt
w_all = zeros(num_reg,num_reg,N); % wijt

% region
n_region = zeros(num_reg,N); % nit: number of vehicles in each region
theta_region_to_19 = zeros(num_reg,num_reg,num_reg,N); % thata_ijst: inflow of each region with destination 19, note that this is just for debugging and plotting

%% begin
for t=1:T:T*N
    %% specify the demand
    run TimeVariant_demand_loading_new;
    
    %% run the GAMS and get the route flow, i.e., theta
    wgdx('MtoG2', m, q, v, demand, MFD_Para, u);
    system 'gams Q_main_19_hexagon_regions_multi_ds_no_control lo=3 gdx=GtoM2';
    
    theta.name = 'theta';
    theta = rgdx('GtoM2', theta);
    tau0.name = 'tau0';
    tau0 = rgdx('GtoM2', tau0);

    %% update the theta_ijs to match the size of n, q into MATLAB matrixes
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
    
    %% update pijst
    if t > 1
        % update pijst
        for i=1:1:size(region_communi,1)
            pairi = region_communi(i,1);
            pairj = region_communi(i,2);
            m_regioni = sum(m.val(pairi,d)); % mi_t-1: without counting vehicles in queue
            % pijst = mijst*Pit / (mit*li) <-- completion rate
            p_all(pairi,pairj,t) = (mfd_common(1)*m_regioni^2+mfd_common(2)*m_regioni+mfd_common(3)) ...
                                   /mfd_diff(pairi)*m_div.val(pairi,pairj,d(j));
            
            if p_all(pairi,pairj,t) >= ( Qij - q.val(pairi,pairj,d(j)) )
            for j=1:1:size(d,2)
                % pijst = mijst*Pit / (mit*li) <-- completion rate
                p(pairi,pairj,d(j),t) = 
            end
        end
        
        % update wijst
        for i=1:1:size(region_communi,1)
            pairi = region_communi(i,1);
            pairj = region_communi(i,2);
            n_regioni = sum(n.val(pairi,d)); % ni_t-1
            flow_waiting_ij = p_all(pairi,pairj,t) * T + q_all(pairi,pairj,t-1);
            % check whether queue has enough room for pijst
            for j=1:1:size(d,2)
                flow_waiting_ijs = p(pairi,pairj,d(j),t) * T + q.val(pairi,pairj,d(j));
                % calculate Qijst
                if flow_waiting_ij == 0
                    Qijs = ( n_bar(pairi) - n_regioni );
                else
                    Qijs = ( n_bar(pairi) - n_regioni ) * flow_waiting_ijs / flow_waiting_ij;
                end
                % when pijst * dT >= Qijst - qijst
                if p(pairi,pairj,d(j),t) * T >= ( Qijs - q.val(pairi,pairj,d(j)) )
                    w(pairi,pairj,d(j)) = Qijs / T;
                % when pijst * dT < Qijst - qijst
                elseif p(pairi,pairj,d(j),t) * T < ( Qijs - q.val(pairi,pairj,(j)) )
                   w(pairi,pairj,d(j)) = p(pairi,pairj,d(j),t) + q.val(pairi,pairj,(j));
                end
            end
            w_all(pairi,pairj,t) = sum(w(pairi,pairj,:));
        end

        % calculate p_iiit
        for i=1:1:num_reg
            n_regioni = sum(n.val(i,d)); % ni
            if n_regioni < n_bar(i)
                m_regioni = sum(m.val(i,d)); % mi
                % p_iiit = niiit*Pit / (mit*li) <-- completion rate
                % assume qiiit = 0: no queue for iii
                p(i,i,i,t) = (mfd_common(1)*m_regioni^2+mfd_common(2)*m_regioni+mfd_common(3))...
                                            /mfd_diff(i)*n_div.val(i,i,i);
                p_all(i,i,t) = sum(p(i,i,:,t));
            end
        end
    end
    
    %% update n_div, i.e., nijs
    for i = 1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);        
        for j=1:1:size(d,2)
            region_in = theta_gams(pairi,pairj,d(j));
            region_out = v.val(pairi,pairj,d(j));
            if region_out > region_in + n_div.val(pairi,pairj,d(j))
                n_div.val(pairi,pairj,d(j)) = 0;
            else
                n_div.val(pairi,pairj,d(j)) = n_div.val(pairi,pairj,d(j)) + region_in - region_out;
            end
        end
    end
    
    %% update n_div_iii, i.e., niii
    for i = 1:1:num_reg
        region_in = sum(v.val(:,i,i)) + demand.val(i,i);
        region_out = p(i,i,i,t);
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
    
    %% check whether Cbar can be accommodated by the downstream region
    if t > 1
        for j = 1:1:num_reg
            % check sum_i Cbar_ij *T + njt <= Nj
            upstreams = region_communi(:,2) == j;
            upstreams = region_communi(upstreams,:);
            Cbar_up = sum(Cbar.val(upstreams(:,1),j));
            n_regionj = sum(n.val(j,d));
            if n_bar(j) >= Cbar_up * T + n_regionj
                % uij = Cbar_ij
                u.val(upstreams(:,1),j) = Cbar.val(upstreams(:,1),j);
            else
                % uij = (Nj - njt) * w_ij / (sum_i w_ij)
                flow_waiting_up = w_all(upstreams(:,1),j,t);
                if flow_waiting_up == 0 % no waiting flow at upstream
                    u.val(upstreams(:,1),j) = Cbar.val(upstreams(:,1),j);
                else
                    for h = 1:1:size(upstreams,1)
                        % distribute current flow capacity
                        u.val(upstreams(h,1),j) = ( n_bar(j) - n_regionj ) * w_all(upstreams(h,1),j,t) / flow_waiting_up;
                    end
                end
            end
        end
    end
    
    %% check whether the current flow capacity, uijt, can accommodate qijt
    if t > 1
        for i = 1:1:size(region_communi,1)
            pairi = region_communi(i,1);
            pairj = region_communi(i,2);                                
            % update v and q
            if u.val(pairi,pairj) >= w_all(pairi,pairj,t)
                % vijt = wijt
                v.val(pairi,pairj,d) = w(pairi,pairj,d) ;
                % clean up the previous queue
                q.val(pairi,pairj,d) = 0;
            else
                % vijt = u_ij
                % vijst = vijt * w_ijst/w_ijt
				for j=1:1:size(d,2)
					% update vijst
					v.val(pairi,pairj,d(j)) = u.val(pairi,pairj) * w(pairi,pairj,d(j)) / w_all(pairi,pairj,t);
					if v.val(pairi,pairj,d(j)) > w(pairi,pairj,d(j))
						v.val(pairi,pairj,d(j)) = w(pairi,pairj,d(j));
					end
					% update qijs
					q.val(pairi,pairj,d(j)) = w(pairi,pairj,d(j)) - v.val(pairi,pairj,d(j));
				end
            end
            q_all(pairi,pairj,t) = sum(q.val(pairi,pairj,:));
            v_all(pairi,pairj,t) = sum(v.val(pairi,pairj,:));
        end
    end

    %% update vehicle numbers without vehicle in queue
    for i = 1:1:size(region_communi,1)
        pairi = region_communi(i,1);
        pairj = region_communi(i,2);   
        for j=1:1:size(d,2)
            m_div.val(pairi,pairj,d(j)) = n_div.val(pairi,pairj,d(j)) - q.val(pairi,pairj,d(j));
        end
    end

    %% update m_div_iii, i.e., miii
    for i = 1:1:num_reg
        m_div.val(i,i,i) = n_div.val(i,i,i);
    end

    %% update m.val, i.e., mis
    for i=1:1:num_reg
        for j=1:1:size(d,2)
            m.val(i,d(j)) = sum(m_div.val(i,:,d(j)));
        end
    end
    
    %% clear tau0 and theta
    theta = [];
    tau0 = [];
    
    % show the time step
    ['t: ' num2str(t)]
end
