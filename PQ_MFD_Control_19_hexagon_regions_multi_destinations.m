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
run Demand_loading

cycle_length = 60;
cycle_index = 0;
q_all_out = [];
q_data_all =[];
q_data_all(1:size(region_communi,1),:) = 0;
u_data_real = [];
p_trans = zeros(19,19,19);
q_out = zeros(19,19,19);
p_region_in = zeros(1,num_reg);

%%
for t=1:T:T*7200
    %% specify the demand
    run TimeVariant_demand_loading_new;
    
    %% run the GAMS and get the route flow and control variable
    wgdx('MtoG2', n, q, v, demand, MFD_Para);
    system 'gams main_19_hexagon_regions_multi_ds_1012 lo=3 gdx=GtoM2';
%     system 'gams main_19_hexagon_regions_multi_ds_no_control_1012 lo=3 gdx=GtoM2';
    
    y.name = 'y';
    y = rgdx('GtoM2', y);
    theta.name = 'theta';
    theta = rgdx('GtoM2', theta);
    eta.name = 'eta';
    eta = rgdx('GtoM2', eta);
    
    %% transform the y and p to match the size of n and q in MATLAB matrixes
    theta_trans = zeros(19,19,19);
    y_trans = zeros(19,19);
    eta_trans = zeros(19,19);
    
    for m1 = 1:1:size(theta.val,1)
        theta_trans(theta.val(m1,1),theta.val(m1,2),theta.val(m1,3))=theta.val(m1,4);
    end
    for m2 = 1:1:size(y.val,1)
        y_trans(y.val(m2,1),y.val(m2,2))=y.val(m2,3);
    end
    for m3 =1:1:size(eta.val,1)
        eta_trans(eta.val(m3,1), eta.val(m3,2)) = eta.val(m3,3);
    end
    
    %% record the u, theta, and q
    n_data(:,t)= sum(n.val,2);
    
    for i=1:1:size(region_communi,1)
        u_data(i,t) = y_trans(region_communi(i,1),region_communi(i,2))*(n_bar(region_communi(i,2))-sum(n.val(region_communi(i,2),d)))+0.1;
        y_data(i,t) = y_trans(region_communi(i,1),region_communi(i,2));
        nbar_n_data(i,t) = (n_bar(region_communi(i,2))-sum(n.val(region_communi(i,2),d)));
        q_data_all(i,t) = sum(q.val(region_communi(i,1),region_communi(i,2),13:19));
        theta_data_all(i,t) = sum(theta_trans(region_communi(i,1),region_communi(i,2),13:19));
        for j=13:1:19
            theta_data(i,j,t) = theta_trans(region_communi(i,1),region_communi(i,2),j);
            q_data(i,j,t) = q.val(region_communi(i,1),region_communi(i,2),j);
        end
    end
    
    for i=1:1:num_reg
        eta_data(i,t) = eta_trans(i,19);
    end
    
    for i=1:1:size(region_communi,1)
        if t == 1
            u_data_real(i,t)=u_data(i,t);
            cycle_index = cycle_index +1;
        else
            if cycle_index >= cycle_length
                u_data_real(i,t)=u_data(i,t);
                cycle_index = 0;
            else
                u_data_real(i,t)=u_data_real(i,t-1);
                cycle_index = cycle_index +1;
            end
        end
    end
    
    %% calculate the p
    for i=1:1:size(region_communi,1)
        n_temp = sum(n.val(region_communi(i,1),d));
        for j=1:1:size(d,2)
            p_trans(region_communi(i,1),region_communi(i,2),d(j))=(mfd_common(1)*n_temp^2+mfd_common(2)*n_temp+mfd_common(3))/mfd_diff(region_communi(i,1))*n_div.val(region_communi(i,1),region_communi(i,2),d(j));
            p_data(i,d(j),t)=(mfd_common(1)*n_temp^2+mfd_common(2)*n_temp+mfd_common(3))/mfd_diff(region_communi(i,1))*n_div.val(region_communi(i,1),region_communi(i,2),d(j));
        end
        p_data_all(i,t) = sum(p_data(i,:,t));
    end

    for i = 1:1:num_reg
        n_temp = sum(n.val(i,d));
        p_region_in(i) = (mfd_common(1)*n_temp^2+mfd_common(2)*n_temp+mfd_common(3))/mfd_diff(i)*n_div.val(i,i,i);
    end
    
    %%
    % update vehicle number  
    for i=1:1:size(region_communi,1)
        n_temp = sum(n.val(region_communi(i,1),d));
        for j=1:1:size(d,2)
            region_in = theta_trans(region_communi(i,1),region_communi(i,2),d(j));
            region_out = p_trans(region_communi(i,1),region_communi(i,2),d(j));        
            n_div.val(region_communi(i,1), region_communi(i,2),d(j))=n_div.val(region_communi(i,1), region_communi(i,2),d(j))+region_in - region_out;
        end
    end
    
    for i = 1:1:num_reg
        region_in = sum(v.val(:,i,i))+demand.val(i,i);
        n_div.val(i,i,i)=n_div.val(i,i,i)+region_in - p_region_in(i);
    end
    
    for i=1:1:num_reg
        for j=1:1:size(d,2)
            n.val(i,d(j)) = sum(n_div.val(i,:,d(j)));
        end
    end
    n_div.val(19,19,19)
    n_data(19,t)  
     
    %% update the MFD dynamics
    % update q
    % the total queue length at boundary (i,j) is q_data_all
    % the total inflow to the boundary (i,j) is p_data_all
    % the controlled flow rate at the boundary (i,j) is u_data
    % Thus, update the total queue length. q_all_new is the queue length of
    % time t+1; q_all_out is the v_ij

    for i=1:1:size(region_communi,1)
        delta_q = q_data_all(i,t) + p_data_all(i,t) - u_data_real(i,t);
        if delta_q >=0
%             q_data_all(i,t+1) = delta_q;
%             q_all_out(i,t) = u_data_real(i,t);
            if q_data_all(i,t)>=u_data_real(i,t)
                % find t' for each boundary
                j_1 = t-1;
                u_back_add = q_all_out(i,j_1);
                while j_1>0 && u_back_add <= q_data_all(i,j_1)
                    j_1 = j_1-1;
                    u_back_add = u_back_add + q_all_out(i,j_1);
                end
                
                j_2 = j_1;
                p_forward_add = p_data_all(i,j_2);
                while p_forward_add <= q_data_all(i,t) && j_2<=t
                    j_2 = j_2+1;
                    p_forward_add = p_forward_add + sum(p_data(i,:,j_2));
                end

                for k = 1:1:size(d,2)
                    q_out(region_communi(i,1),region_communi(i,2),d(k)) = sum(p_data(i,d(k),j_1:j_2)) / (p_forward_add) *u_data_real(i,t);
                    v.val(region_communi(i,1),region_communi(i,2),d(k)) = q_out(region_communi(i,1),region_communi(i,2),d(k));
                    q.val(region_communi(i,1),region_communi(i,2),d(k)) = q.val(region_communi(i,1),region_communi(i,2),d(k))+ p_trans(region_communi(i,1),region_communi(i,2),d(k)) - q_out(region_communi(i,1),region_communi(i,2),d(k));
                end
            else
                for k = 1:1:size(d,2)
                    q_out(region_communi(i,1),region_communi(i,2),d(k)) = q.val(region_communi(i,1),region_communi(i,2),d(k))+ p_trans(region_communi(i,1),region_communi(i,2),d(k))/sum(p_trans(region_communi(i,1),region_communi(i,2),:)) * (u_data_real(i,t)-q_data_all(i,t));
                    v.val(region_communi(i,1),region_communi(i,2),d(k)) = q_out(region_communi(i,1),region_communi(i,2),d(k));
                    q.val(region_communi(i,1),region_communi(i,2),d(k)) = q.val(region_communi(i,1),region_communi(i,2),d(k))+ p_trans(region_communi(i,1),region_communi(i,2),d(k)) - q_out(region_communi(i,1),region_communi(i,2),d(k));
                end
            end  
        else  
%             q_data_all(i,t+1) = 0;
%             q_all_out(i,t) = q_data_all(i,t) + p_data_all(i,t);
            q_out(region_communi(i,1),region_communi(i,2),:)=q.val(region_communi(i,1),region_communi(i,2),:)+ p_trans(region_communi(i,1),region_communi(i,2),:);
            v.val(region_communi(i,1),region_communi(i,2),:) = q_out(region_communi(i,1),region_communi(i,2),:);
            q.val(region_communi(i,1),region_communi(i,2),:)=0;
        end
        q_all_out(i,t) = sum(q_out(region_communi(i,1),region_communi(i,2),:));
    end
   
    %%
    
    
    % clear y and p
    y=[];
    theta=[];
    eta =[];
    
    % show the time step
    t
end        
    
    
                        
