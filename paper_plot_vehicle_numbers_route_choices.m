%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%plot the figures needed for paper
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
close all
clear
%% MFD functions
a = 1.4877e-7;
b = -2.9815e-3;
c = 15.0912;

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
% plot(x, s1)
set(gca, 'FontName', 'Times New Roman', 'FontSize', 12);
set(gcf,'unit','centimeters','position',[10 5 15 10]);
%set(gca,'Position',[.1 .1 .7 .65]);
xlabel('vehicle number [veh]');
ylabel('completion rate [veh/s]');
legend('region 19', 'region 15/16/17/18', 'region 13/14', 'region 7/8/9', 'region 4/5/6/10/11/12', 'region 1/2/3')
ylimit = get(gca, 'Ylim');
hold on
plot([4000,4000], ylimit);

figure(2)
plot(x, t1, x, t2, x, t3, x, t4, x, t5, x, t6)
%% plot vehicle number in each region
% controlled
load('n_19_hexagon_regions_multi_ds_withdemand_7200_252520_4000.mat');
% load('n_19_hexagon_regions_multi_ds_500_700_300_8000_withdemand.mat');
q_max = max(max(q_data_all));

figure(2)
plot(n_data','LineWidth',1.5)
set(gca, 'FontName', 'Times New Roman', 'FontSize', 11);
set(gcf,'unit','centimeters','position',[11 6 15 9]);
legend('region 1', 'region 2', 'region 3', 'region 4', 'region 5', 'region 6', 'region 7', 'region 8', 'region 9', ...
    'region 10', 'region 11', 'region 12', 'region 13', 'region 14', 'region 15', 'region 16', 'region 17', 'region 18', ...
    'region 19')
xlim([0 7200])
ylim([0 6000])
xlabel('time [s]');
ylabel('vehicle number [veh]');
vt_control = sum(sum(n_data))+sum(sum(q_data_all));

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
load('n_19_hexagon_regions_multi_ds_withdemand_7200_300_300_200_3_4000.mat');
n_c = n_data;
q_c = q_data;
p_c = p_data;
u_c = u_data;
load('n_19_hexagon_regions_multi_ds_withdemand_7200_300_300_200_3_10000.mat');
n_nc = n_data;
q_nc = q_data;
p_nc = p_data;
u_nc = u_data;

% extract the route choice information to region 19
% controlled condition
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
%%
route_12_c=[];
for i=1:1:7200
    route_12_c(i,:) = routes(12, :, i);
end
%uncontrolled condition
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
route_12_c(:,all(route_12_c==0,1))=[];
route_12_c(all(route_12_c==0,2),:)=[];

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
