%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
%%%% Main file of the MFD based perimeter control considering Instanteneous Dynamic User Equilibrium
%%%% Qiangqiang Guo, July 27th, 2018
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clc
clear all

n_bar =4200*ones(1,19); % 20000 for no control, 4000 for control
d_central_t = 0.3; % 0.2 for light demand, 0.3 for mild demand, 0.4 for high demand
d_rural_suburban = 0.2; %0.1 0.2 0.3
d_rural_far_suburban = 0.1; % 0.1 0.1 0.2

run Demand_loading

%% the main program
% at each time step, do the following
% step 1: write the vehicle number, queue length, and demand to GAMS gdx
% step 2: solve the DCS problem by calling GAMS program, and get the result
% step 3: update the vehicle number, queue length
% step 4: go back to step 1
q_all_new = zeros(size(region_communi,1),1);
q_all_out = [];

for t=1:T:T*7200
    %% specify the demand
%     if t<=cut
%         demand.val(1:12,19) = 0.5;
%     else
%         demand.val(1:12,19) = 0;
%     end
    run TimeVariant_demand_loading;
    
    %% run the GAMS and get the route flow and control variable
    wgdx('MtoG2', n, q, demand);
    system 'gams main_19_hexagon_regions_multi_ds_1012 lo=3 gdx=GtoM2';
%     system 'gams main_19_hexagon_regions_multi_ds_no_control_1012 lo=3 gdx=GtoM2';
    
    y.name = 'y';
    y = rgdx('GtoM2', y);
    p.name = 'p';
    p = rgdx('GtoM2', p);
    
    %% transform the y and p to match the size of n and q in MATLAB matrixes
    p_trans = zeros(19,19,19);
    y_trans = zeros(19,19);
    q_out = zeros(19,19,19);
    for m1 = 1:1:size(p.val,1)
        p_trans(p.val(m1,1),p.val(m1,2),p.val(m1,3))=p.val(m1,4);
    end
    for m2 = 1:1:size(y.val,1)
        y_trans(y.val(m2,1),y.val(m2,2))=y.val(m2,3);
    end
    
    %% record the n, u, p, and q
    
    n_data(:,t)= sum(n.val,2);
    q_data_all(:,t) = q_all_new';
    
    for i=1:1:size(region_communi,1)
        u_data(i,t) = y_trans(region_communi(i,1),region_communi(i,2))*(n_bar(region_communi(i,2))-sum(n.val(region_communi(i,2),d)))+0.0001;
        y_data(i,t) = y_trans(region_communi(i,1),region_communi(i,2));
        nbar_n_data(i,t) = (n_bar(region_communi(i,2))-sum(n.val(region_communi(i,2),d)));
%         q_data_all(i,t) = sum(q.val(region_communi(i,1),region_communi(i,2),13:19));
        p_data_all(i,t) = sum(p_trans(region_communi(i,1),region_communi(i,2),13:19));
        for j=13:1:19
            p_data(i,j,t) = p_trans(region_communi(i,1),region_communi(i,2),j);
            q_data(i,j,t) = q.val(region_communi(i,1),region_communi(i,2),j);
        end
    end
    
    %% update the MFD dynamics
    % update q
    % the total queue length at boundary (i,j) is q_data_all
    % the total inflow to the boundary (i,j) is p_data_all
    % the controlled flow rate at the boundary (i,j) is u_data
    % Thus, update the total queue length. q_all_new is the queue length of
    % time t+1; q_all_out is the v_ij
    q_all_new = [];
    for i=1:1:size(region_communi,1)
        delta_q = q_data_all(i,t) + p_data_all(i,t) - u_data(i,t);
        if delta_q >=0
            q_all_new(i) = delta_q;
            q_all_out(i,t) = u_data(i,t);
            if q_all_out(i,t)>=0.01
                % find t' for each boundary
                u_back_add = 0;
                j_1 = t;
                while j_1>0 && u_back_add <= q_data_all(i,j_1) 
                    u_back_add = u_back_add + u_data(i,j_1);
                    j_1 = j_1-1;
                end

                p_forward_add = 0;
                j_1 = j_1+1;
                j_2 = j_1;
                while p_forward_add <= q_data_all(i,t) && j_2<=t && j_2>0
                    p_forward_add = p_forward_add + sum(p_data(i,:,j_2));
                    j_2 = j_2+1;
                end
                j_2 = j_2-1;

                for k = 1:1:size(d,2)
                    q_out(region_communi(i,1),region_communi(i,2),d(k)) = (sum(p_data(i,d(k),j_1:j_2)) + 10e-7) / (p_forward_add) *q_all_out(i,t);
                    q.val(region_communi(i,1),region_communi(i,2),d(k)) = q.val(region_communi(i,1),region_communi(i,2),d(k))+ p_trans(region_communi(i,1),region_communi(i,2),d(k)) - q_out(region_communi(i,1),region_communi(i,2),d(k));
                end
            else
                q_out(region_communi(i,1),region_communi(i,2),:)=0;
                q.val(region_communi(i,1),region_communi(i,2),:)=q.val(region_communi(i,1),region_communi(i,2),:)+ p_trans(region_communi(i,1),region_communi(i,2),:);
            end
            
        else
            q_all_new(i) = 0;
            q_all_out(i,t) = q_data_all(i,t) + p_data_all(i,t);
            
            q_out(region_communi(i,1),region_communi(i,2),:)=q.val(region_communi(i,1),region_communi(i,2),:)+ p_trans(region_communi(i,1),region_communi(i,2),:);
            q.val(region_communi(i,1),region_communi(i,2),:)=0;
        end
    end
   
    
%     for i=1:1:num_reg
%         for j=1:1:num_reg
%             for k=1:1:size(d,2)
%                 delta_q = q.val(i,j,d(k))+ p_trans(i,j,d(k))-(y_trans(i,j)*(n_bar(j)-sum(n.val(j,d)))+0.5)*(q.val(i,j,d(k))+10e-7)/(sum(q.val(i,j,d))+10e-7);
%                 if delta_q >=0
%                     q.val(i,j,d(k))=delta_q;
%                     q_out(i,j,d(k))=(y_trans(i,j)*(n_bar(j)-sum(n.val(j,d)))+0.5)*(q.val(i,j,d(k))+10e-7)/(sum(q.val(i,j,d))+10e-7);
%                 else
%                     q.val(i,j,d(k))=0;
%                     q_out(i,j,d(k))=q.val(i,j,d(k))+ p_trans(i,j,d(k));
%                 end
%             end
%         end
%     end
    %%
    % update vehicle number         
    for i=1:1:num_reg
        for j=1:1:size(d,2)
            region_in =0;
            region_out=0;
            for k=1:1:size(region_communi,1)
                if region_communi(k,2)==i
                    % input of region i
                    region_in = region_in + q_out(region_communi(k,1),i,d(j));
                else
                end

                if region_communi(k,1)==i
                    % output of region i
                    region_out = region_out + p_trans(i,region_communi(k,2),d(j));
                else
                end
            end

            if i==d(j)
                n_temp = sum(n.val(i,d));
                region_out = (mfd_common(1)*n_temp^2+mfd_common(2)*n_temp+mfd_common(3))/mfd_diff(i)*n.val(i,d(j));
            else
            end
            n.val(i,d(j)) = n.val(i,d(j))+ region_in - region_out + demand.val(i,d(j));
        end
    end
    % clear y and p
    y=[];
    p=[];
    
    % show the time step
    t
end        
    
    
                        
