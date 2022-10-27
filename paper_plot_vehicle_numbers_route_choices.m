%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%plot the figures needed for paper
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
close all
clear

% load('n_19_hexagon_regions_multi_ds_withdemand_8000_2_20000_PQ_cap.mat');

%% temp
pp = zeros(1,N);
qqD = zeros(1,N);
qqU = zeros(1,N);
for i = 1:N
    pp(1,i) = sum(p(2,13,19,i));
    qqD(1,i) = sum(qD_trans(2,13,19,i));
    qqU(1,i) = sum(qU(2,13,19,i));
end
plot(1:N,pp)
hold on
plot(1:N,qqD)
plot(1:N,qqU)
hold off

%% MFD functions
coef = 1;
a = 1.4877e-7*coef;
b = -2.9815e-3*coef;
c = 15.0912*coef;

x = 0:100:10000;

s1 = (a*x.^3 + b*x.^2 + c*x)/3600;
s2 = (a*x.^3 + b*x.^2 + c*x)/4500;
s3 = (a*x.^3 + b*x.^2 + c*x)/4800;
s4 = (a*x.^3 + b*x.^2 + c*x)/5500;
s5 = (a*x.^3 + b*x.^2 + c*x)/5800;
s6 = (a*x.^3 + b*x.^2 + c*x)/6100;

t1 = 2500*1./(a*x.^2 + b*x + c);
t2 = 9000*1./(a*x.^2 + b*x + c);
t3 = 10000*1./(a*x.^2 + b*x + c);
t4 = 12000*1./(a*x.^2 + b*x + c);
t5 = 12500*1./(a*x.^2 + b*x + c);
t6 = 13000*1./(a*x.^2 + b*x + c);

figure(1)
plot(x, s1, x, s2, x, s3, x, s4, x, s5, x, s6)
set(gca, 'FontName', 'Times New Roman', 'FontSize', 12);
set(gcf,'unit','centimeters','position',[10 5 15 10]);
%set(gca,'Position',[.1 .1 .7 .65]);
xlabel('Density [veh/m]');
% xlabel('Number of vehicles [veh]');
ylabel('Completion rate [veh/s]');
legend('region 19', 'region 15/16/17/18', 'region 13/14', 'region 7/8/9', 'region 4/5/6/10/11/12', 'region 1/2/3')
%ylimit = get(gca, 'Ylim');
%hold on
%plot([4000,4000], ylimit);

%% Flow rates and Queues
figure(2)
in = 15;
out = 19;
for t = 1:N
    plot_p(t) = p_all(in,out,t);
    plot_v(t) = v_all(in,out,t);
    plot_qD(t) = qD_all(in,out,t);
%     plot_qU1(t) = qU_all1(in,out,t);
    plot_qU(t) = qU_all(in,out,t);% + plot_p(t);
    plot_withheld(t) = sum(withheld(in,out,:,t));
    plot_pTilda(t) = min(plot_withheld(t) + plot_p(t), CbarIn_trans_trans(in,out));
    plot_withheld(t) = plot_pTilda(t) - plot_p(t);
end
hold on
yyaxis left
% plot(plot_p,'LineWidth',1.5,'LineStyle','--','Marker','*','Color','b');
% plot(plot_v,'LineWidth',1.5,'LineStyle','--','Marker','+','Color','k');
% plot(plot_withheld,'LineWidth',1.5,'LineStyle','--','Marker','square','Color','[0.5 0 0.8]');
plot(plot_p,'LineWidth',2,'LineStyle','--','Color','b');
plot(plot_v,'LineWidth',1.5,'LineStyle',':','Color','k');
plot(plot_pTilda,'LineWidth',1.5);
plot(plot_withheld,'LineWidth',1.5,'LineStyle','--','Color','[0.5 0 0.8]');
% ylimit = 5;
% plot(1:N, ones(1,N)*ylimit,'LineStyle','--','Color',[0.5,0.5,0.5]);
ylabel('Flow rate[veh/s]');
ylim([0,4]);
% yticks(0:0.5:3);

yyaxis right
% plot(plot_qD,'LineWidth',1.5,'LineStyle','--','Marker','v','Color','r');
% plot(plot_qU,'LineWidth',1.5,'LineStyle','--','Marker','^','Color','#00841a');
plot(plot_qD,'LineWidth',1.5,'LineStyle','--','Color','r');
plot(plot_qU,'LineWidth',1.5,'LineStyle','--','Color','#00841a');
set(gca, 'FontName', 'Times New Roman', 'FontSize', 18);
set(gcf,'unit','centimeters','position',[10 5 15 10]);
xlabel('Time [s]');
ylabel('Queue length [veh]');
legend(['Buffer zone inflow via link (' num2str(in) ',' num2str(out) ')'], ['Buffer zone outflow via link (' num2str(in) ',' num2str(out) ')'],...
        ['Region outflow to link (' num2str(in) ',' num2str(out) ')'], ['Withheld flow via link (' num2str(in) ',' num2str(out) ')'],...
        ['Buffer zone qD via link (' num2str(in) ',' num2str(out) ')'], ['Buffer zone qU via link (' num2str(in) ',' num2str(out) ')'])
ylim([0,250]);
% yticks(0:1:5);
xlim([0,N]);
% plot(plot_qU1)
hold off

%% Flow rates and Queues - PQ
figure(2)
in = 6;
out = 16;
for it = 1:N
    plot_p(it) = p_all(in,out,it);
    plot_v(it) = v_all(in,out,it);
    plot_q(it) = q_all(in,out,it);
    if it > 1
        plot_Q(it) = ( n_bar(in) - sum(m.val(in,:)) ) * ( p_all(in,out,it) + q_all(in,out,it-1) ) / sum(p_all(in,:,it) + q_all(in,:,it-1));
    else
        plot_Q(it) = 0;
    end
    plot_vacancy(it) = plot_Q(it) - plot_q(it);
end

hold on
yyaxis left
plot(plot_p,'LineWidth',2,'LineStyle','--','Color','b');
plot(plot_v,'LineWidth',1.5,'LineStyle',':','Color','k');
% plot(plot_vacancy,'LineWidth',1.5,'LineStyle','--','Color','#00841a');
ylim([0,3.5]);
ylabel('Flow rate[veh/s]');

yyaxis right
plot(plot_q,'LineWidth',1.5,'LineStyle','--','Color','r');
xlabel('Time [s]');
ylabel('Queue length [veh]');
ylim([0,600]);
hold off

legend(['Boundary inflow via link (' num2str(in) ',' num2str(out) ')'], ['Boundary outflow via link (' num2str(in) ',' num2str(out) ')'],...
        ['Boundary q between link (' num2str(in) ',' num2str(out) ')'])


%% number of vehicles over time
load('n_19_hexagon_regions_multi_ds_withdemand_7200_2_20000_Q.mat');
figure(3)
plot(n_region(1,:),'LineWidth',1.5,'LineStyle','-.')
hold on
for ix = 2:num_reg
    if ix <= 12
        if mod(ix,2) == 1
            plot(n_region(ix,:),'LineWidth',1.5,'LineStyle','-.')
        else
            plot(n_region(ix,:),'LineWidth',1.5,'LineStyle','--')
        end
    else
        plot(n_region(ix,:),'LineWidth',1.5)
    end
end
hold off
set(gca, 'FontName', 'Times New Roman', 'FontSize', 18);
set(gcf,'unit','centimeters','position',[11 6 15 9]);
legend('region 1', 'region 2', 'region 3', 'region 4', 'region 5', 'region 6', 'region 7', 'region 8', 'region 9', ...
    'region 10', 'region 11', 'region 12', 'region 13', 'region 14', 'region 15', 'region 16', 'region 17', 'region 18', ...
    'region 19')
xlim([0 N])
ylim([0 6000])
xlabel('Time [s]');
ylabel('Number of vehicles [veh]');

%% DQ-PQ comparison
plot_p_DQ = plot_p;
plot_v_DQ = plot_v;
plot_qD_DQ = plot_qD;
load('n_19_hexagon_regions_multi_ds_withdemand_7200_2_20000_PQ_RawCb.mat');
communi = 48; %in = 13;out = 19;
for t = 1:N
    plot_p_PQ(t) = p_data_all(communi,t);
    plot_v_PQ(t) = min(u_data(communi,t), p_data_all(communi,t)+q_data_all(communi,t));
    plot_qD_PQ(t) = q_data_all(communi,t);
end

hold on
yyaxis left
plot(plot_p_DQ-plot_p_PQ,'LineWidth',2,'LineStyle','--','Color','b');
plot(plot_v_DQ-plot_v_PQ,'LineWidth',1.5,'LineStyle',':','Color','k');
ylabel('Flow rate[veh/s]');
% ylim([0,4]);
% yticks(0:1:4);

yyaxis right
plot(plot_qD_DQ-plot_qD_PQ,'LineWidth',1.5,'LineStyle','--','Color','r');
plot(plot_qU,'LineWidth',1.5,'Color','#00841a');
set(gca, 'FontName', 'Times New Roman', 'FontSize', 18);
set(gcf,'unit','centimeters','position',[10 5 15 10]);
xlabel('Time [s]');
ylabel('Queue length [veh]');
legend('Buffer zone inflow difference (DQ-PQ) via link (13,19)', 'Buffer zone outflow difference (DQ-PQ) via link (13,19)',...
        'Buffer zone qD difference (DQ-PQ) via link (13,19)', 'Buffer zone qU (DQ) via link (13,19)')
ylim([0,5]);
yticks(0:1:5);
xlim([0,N]);
hold off

%% IDUE flow rates
figure(4)
from = 16;
to1 = 19;
to2 = 15;
dest = 14;
for t = 1:N
    plot_theta_19(t) = theta_region_to_19(from,to1,dest,t)*3600;
    plot_theta_15(t) = theta_region_to_19(from,to2,dest,t)*3600;
end
plot(plot_theta_19,'LineWidth',1.5)
set(gca, 'FontName', 'Times New Roman', 'FontSize', 18);
set(gcf,'unit','centimeters','position',[11 6 15 9]);
xlabel('Time [s]');
ylabel(['\theta^{' num2str(dest) '}_{' num2str(from) ',' num2str(to1) '} [veh/h]']);

figure(5)
plot(plot_theta_15,'LineWidth',1.5)
set(gca, 'FontName', 'Times New Roman', 'FontSize', 18);
set(gcf,'unit','centimeters','position',[11 6 15 9]);
xlabel('Time [s]');
ylabel(['\theta^{' num2str(dest) '}_{' num2str(from) ',' num2str(to2) '} [veh/h]']);

% ylabel(['\theta^{' num2str(dest) ';SAC1}_{' num2str(from) ',' num2str(to1) '} - \theta^{' num2str(dest) ';CC1}_{' num2str(from) ',' num2str(to1) '} [veh/h]']);

%% IDUE flow rates
figure(5)
from = 6;
to1 = 15;

for t = 1:N
    plot_theta(t) = sum(theta_region_to_19(from,to1,:,t))*3600;
end
plot(plot_theta,'LineWidth',1.5)
set(gca, 'FontName', 'Times New Roman', 'FontSize', 18);
set(gcf,'unit','centimeters','position',[11 6 15 9]);
legend('region 1', 'region 2', 'region 3', 'region 4', 'region 5', 'region 6', 'region 7', 'region 8', 'region 9', ...
    'region 10', 'region 11', 'region 12', 'region 13', 'region 14', 'region 15', 'region 16', 'region 17', 'region 18', ...
    'region 19')
xlim([0 N])
ylim([0 450])
xlabel('Time [s]');
ylabel('Queue Length [veh]');


%% TODO: shortest path

%% check completion rate is consistent with 
% the sum of inflow and withheld flow
for i = 1:num_reg
    for it = 2:N
        pAndBlocked(i,it) = sum(sum(p(i,:,:,it))) + sum(sum(withheld(i,:,:,it)));
        pRegionOut(i,it) = (mfd_common(1)*n_region(i,it)^3+mfd_common(2)*n_region(i,it)^2+mfd_common(3)*n_region(i,it))...
                                        /mfd_diff(i);
        pDiff(i,it) = pAndBlocked(i,it) - pRegionOut(i,it);
    end
end


figure(7)
reg = 15;
plot(n_region(reg,:),pDiff(reg,:),'LineWidth',1.5,'LineStyle','-.')
set(gca, 'FontName', 'Times New Roman', 'FontSize', 18);
set(gcf,'unit','centimeters','position',[11 6 15 9]);
xlabel('Number of Vehicles [veh]');
ylabel('({$p + \eta) - c$} [veh/s]','Interpreter','latex');
title(['Region' num2str(reg)])

figure(8)
reg = 15;
plot(n_region(reg,:),pRegionOut(reg,:),'LineWidth',1.5,'LineStyle','-.')
set(gca, 'FontName', 'Times New Roman', 'FontSize', 18);
set(gcf,'unit','centimeters','position',[11 6 15 9]);
xlabel('Number of Vehicles [veh]');
ylabel('({$p + \eta) - c$} [veh/s]','Interpreter','latex');
title(['Region' num2str(reg)])

figure(9)
plot(pDiff(1,:),'LineWidth',1.5,'LineStyle','-.')
hold on
for ix = 2:num_reg
    if ix <= 12
        if mod(ix,2) == 1
            plot(pDiff(ix,:),'LineWidth',1.5,'LineStyle','-.')
        else
            plot(pDiff(ix,:),'LineWidth',1.5,'LineStyle','--')
        end
    else
        plot(pDiff(ix,:),'LineWidth',1.5)
    end
end
hold off
set(gca, 'FontName', 'Times New Roman', 'FontSize', 18);
set(gcf,'unit','centimeters','position',[11 6 15 9]);
legend('region 1', 'region 2', 'region 3', 'region 4', 'region 5', 'region 6', 'region 7', 'region 8', 'region 9', ...
    'region 10', 'region 11', 'region 12', 'region 13', 'region 14', 'region 15', 'region 16', 'region 17', 'region 18', ...
    'region 19')
xlim([0 N])
xlabel('Time [s]');
ylabel('Flow Diff [veh/s]');

%%


%%
for i = 1:19
    for t = 1:7200
        plot_p(i,t) = sum(p_all(i,:,t));
        plot_v(i,t) = sum(v_all(i,:,t));
    end
end
plot(plot_p','LineWidth',1.5);
hold on
plot(plot_v','LineWidth',1.5);
hold off

for t = 1:7200
    plot_qD(t) = sum(qD_all(13,:,t));
    plot_qU(t) = sum(qU_all(13,:,t));
end
plot(plot_qD,'LineWidth',1.5);
hold on
plot(plot_qU,'LineWidth',1.5);
hold off
%%
for i = 1:19
    for t = 1:7200
        plot_qD(i,t) = sum(qD_all(i,:,t));
        plot_qU(i,t) = sum(qU_all(i,:,t));
    end
end
plot(plot_qD','LineWidth',1.5);
hold on
plot(plot_qU','LineWidth',1.5,'LineWidth',1.5,'LineStyle','-.');
set(gca, 'FontName', 'Times New Roman', 'FontSize', 18);
set(gcf,'unit','centimeters','position',[11 6 15 9]);
xlim([0 N]);
xlabel('Time [s]');
ylabel('Queue Length [veh]');
hold off


%% Below is by Qiangqiang
figure(2)
plot(x, t1, x, t2, x, t3, x, t4, x, t5, x, t6)
%% plot vehicle number in each region
% controlled
%load('n_19_hexagon_regions_multi_ds_withdemand_7200_252520_4000.mat');
% load('n_19_hexagon_regions_multi_ds_500_700_300_8000_withdemand.mat');
qD_max = max(max(qD_all));

figure(2)
plot(n_region','LineWidth',1.5)
set(gca, 'FontName', 'Times New Roman', 'FontSize', 11);
set(gcf,'unit','centimeters','position',[11 6 15 9]);
legend('region 1', 'region 2', 'region 3', 'region 4', 'region 5', 'region 6', 'region 7', 'region 8', 'region 9', ...
    'region 10', 'region 11', 'region 12', 'region 13', 'region 14', 'region 15', 'region 16', 'region 17', 'region 18', ...
    'region 19')
xlim([0 7200])
%ylim([0 6000])
xlabel('time [s]');
ylabel('vehicle number [veh]');
vt_control = sum(sum(n_region))+sum(sum(qD_all));

% no control
load('n_19_hexagon_regions_multi_ds_withdemand_7200_252520_10000.mat');

figure(3)
plot(n_data','LineWidth',1.5)
set(gca, 'FontName', 'Times New Roman', 'FontSize', 11);
set(gcf,'unit','centimeters','position',[12 7 15 9]);
legend('region 1', 'region 2', 'region 3', 'region 4', 'region 5', 'region 6', 'region 7', 'region 8', 'region 9', ...
    'region 10', 'region 11', 'region 12', 'region 13', 'region 14', 'region 15', 'region 16', 'region 17', 'region 18', ...
    'region 19')
xlim([0 7200])
xlabel('time [s]');
ylabel('vehicle number [veh]');
vt_no_control = sum(sum(n_data))+sum(sum(q_data_all));

% calculate the improvement
fprintf('the total veh.s saved by the method is:')
vt_control
vt_no_control
q_max
(vt_no_control-vt_control)/vt_no_control

%% show the route choice behavior change
%load('n_19_hexagon_regions_multi_ds_withdemand_7200_300_300_200_3_4000.mat');
%n_c = n_data;
%q_c = q_data;
%p_c = p_data;
%u_c = u_data;
%load('n_19_hexagon_regions_multi_ds_withdemand_7200_300_300_200_3_10000.mat');
n_nc = n_region;
q_nc = q_data;
p_nc = p_data;
u_nc = u_data;

% extract the route choice information to region 19
%% controlled condition
routes = zeros(18,84,7200);
for k=1:1:7200
    jj=1;
    for j=1:1:size(region_communi,1)
        if p_c(j,19,k) > 0
            region_temp(jj,:) = region_communi(j,:);
            jj=jj+1;
        else
        end
    end
    for i=1:1:18
        kk=2;
        for iii = 1:1:size(region_temp,1)
            if region_temp(iii,1) == i
                routes(i, 1:2, k) = region_temp(iii,:);
            else
            end
        end
        judge = routes(i, 2, k);
        while judge ~= 19 && judge ~=0
            for ii=1:1:size(region_temp,1)
                if region_temp(ii,1) == routes(i, kk, k)
                    routes(i,kk+1:kk+2,k) = region_temp(ii,:);
                    kk=kk+2;
                    judge = region_temp(ii,2);
                else
                end
            end
            %judge
        end
    end
    k
end
%
route_12_c=[];
for i=1:1:7200
    route_12_c(i,:) = routes(12, :, i);
end
%% uncontrolled condition
routes = zeros(18,84,7200);
for k=1:1:7200
    jj=1;
    for j=1:1:size(region_communi,1)
        if p_nc(j,19,k) > 0
            region_temp(jj,:) = region_communi(j,:);
            jj=jj+1;
        else
        end
    end
    for i=1:1:18
        kk=2;
        for iii = 1:1:size(region_temp,1)
            if region_temp(iii,1) == i
                routes(i, 1:2, k) = region_temp(iii,:);
            else
            end
        end
        judge = routes(i, 2, k);
        while judge ~= 19 && judge ~=0
            for ii=1:1:size(region_temp,1)
                if region_temp(ii,1) == routes(i, kk, k)
                    routes(i,kk+1:kk+2,k) = region_temp(ii,:);
                    kk=kk+2;
                    judge = region_temp(ii,2);
                else
                end
            end
            %judge
        end
    end
end
route_12_nc=[];
for i=1:1:7200
    route_12_nc(i,:) = routes(12, :, i);
end

% purify
%% control condition
route_12_c(:,all(route_12_c==0,1))=[];
route_12_c(all(route_12_c==0,2),:)=[];
%% uncontrol condition
route_12_nc(:,all(route_12_nc==0,1))=[];
route_12_nc(all(route_12_nc==0,2),:)=[];

% mark the route choice: 1--12-18-19; 2--12-13-19; 3--12-11-18-19; 4--12-1-13-19
for i=1:1:size(route_12_c,1)
    if route_12_c(i,2)==18
        route_12_c(i,7) =1;
    elseif route_12_c(i,2)==13
        route_12_c(i,7) = 2;
    elseif route_12_c(i,2)==11
        route_12_c(i,7) = 3;
    elseif route_12_c(i,2)==1
        route_12_c(i,7) = 4;
    else
    end
end
for i=1:1:size(route_12_nc,1)
    if route_12_nc(i,2)==18
        route_12_nc(i,7) =1;
    elseif route_12_nc(i,2)==13
        route_12_nc(i,7) = 2;
    elseif route_12_nc(i,2)==11
        route_12_nc(i,7) = 3;
    elseif route_12_nc(i,2)==1
        route_12_nc(i,7) = 4;
    else
    end
end

% show the route choice
figure(4)
plot(route_12_nc(:,7)')
ylim([0 5])
figure(5)
plot(route_12_c(:,7)')
ylim([0 5])
%% show the travel time in region 13 and 14 along time (4800m for region 13 and 4500 for region 18)
t_13_c = 4800./(a*n_c(13,:).^2 + b*n_c(13,:) + c);
t_18_c = 4500./(a*n_c(18,:).^2 + b*n_c(18,:) + c);

t_13_nc = 4800./(a*n_nc(13,:).^2 + b*n_nc(13,:) + c);
t_18_nc = 4500./(a*n_nc(18,:).^2 + b*n_nc(18,:) + c);

t=1:1:7200;
figure(6) 
plot(t, t_13_c, t,t_18_c)
ylim([0 1100])
grid on
figure(7) 
plot(t, t_13_nc, t,t_18_nc)
ylim([0 1100])
grid on
%%
figure(8)
plot(t, t_13_c,'b', t,t_18_c,'r', 'LineWidth', 1.5)
ylim([0 1100])
% xlim([-200 9000])
hold on
plot(t, t_13_nc,'b--', t,t_18_nc, 'r--','LineWidth', 1.5)
set(gca, 'FontName', 'Times New Roman', 'FontSize', 11);
set(gcf,'unit','centimeters','position',[12 7 8 6]);

figure(9)
plot(t, n_c(13,:),'b', t,n_c(18,:),'r', 'LineWidth', 1.5)
% ylim([0 1100])
% xlim([-200 9000])
hold on
plot(t, n_nc(13,:),'b--', t,n_nc(18,:), 'r--','LineWidth', 1.5)
set(gca,'ydir','reverse')
set(gca,'xtick',[])
set(gca, 'FontName', 'Times New Roman', 'FontSize', 11);
set(gcf,'unit','centimeters','position',[12 7 8 6]);

figure(10)
x = 0:100:10000;
c13 = (a*x.^3 + b*x.^2 + c*x)/4800;
c18 = (a*x.^3 + b*x.^2 + c*x)/4500;
t_13 = 4800./(a*x.^2 + b*x + c);
t_18 = 4500./(a*x.^2 + b*x + c);
yyaxis left
plot(x, c13,'b', x,c18,'r', 'LineWidth', 1.5)
set(gca,'xdir','reverse')
% set(gca,'ytick','Color','black')
set(gca, 'FontName', 'Times New Roman', 'FontSize', 11);
set(gcf,'unit','centimeters','position',[12 7 16 6]);

yyaxis right
plot(x, t_13,'b', x,t_18,'r', 'LineWidth', 1.5)
ylim([0 1100])
