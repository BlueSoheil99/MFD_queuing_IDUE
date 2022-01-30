clear;clc
close all
%% plot hexagon regions
load('n_19_hexagon_regions_multi_ds_withdemand_7200_2_5300_DQ.mat');
%load('n_19_hexagon_regions_multi_ds_withdemand_1000_2_5300_DQ_backup.mat');
n_data = n_region;
n_max = max(max(n_data));
p_max = max(max(max(p_all)));

% region_communi = [1 2; 1 4; 1 13; 2 1; 2 3; 2 13; 2 14; 3 2; 3 4; 3 14; 4 3; 4 5; 4 14; 4 15; 5 4; 5 6; 5 15;...   
%     6 5; 6 7; 6 15; 6 16; 7 6; 7 8; 7 16; 8 7; 8 9; 8 16; 8 17; 9 8; 9 10; 9 17; 10 9; 10 11; 10 17; 10 18; 11 10;...   
%     11 12; 11 18; 12 1; 12 11; 12 13; 12 18; 13 1; 13 2; 13 12; 13 14; 13 18; 13 19; 14 2; 14 3; 14 4; 14 13; 14 15;...   
%     14 19; 15 4; 15 5; 15 6; 15 14; 15 16; 15 19; 16 6; 16 7; 16 8; 16 15; 16 17; 16 19; 17 8; 17 9; 17 10; 17 16;...   
%     17 18; 17 19; 18 10; 18 11; 18 12; 18 13; 18 17; 18 19];
center = [0, -2*3^0.5; 1.5, -1.5*3^0.5; 3, -3^0.5; 3, 0; 3, 3^0.5; 1.5, 1.5*3^0.5; 0, 2*3^0.5; -1.5, 1.5*3^0.5; -3, 3^0.5;...
    -3, 0; -3, -3^0.5; -1.5, -1.5*3^0.5; 0, -3^0.5; 1.5, -0.5*3^0.5; 1.5, 0.5*3^0.5; 0, 3^0.5; -1.5, 0.5*3^0.5;...
    -1.5, -0.5*3^0.5; 0, 0];
colormap(flipud(gray))
a = colormap;

p_data = zeros(19,19,N);
for tt = 1:N
    for j =1:1:size(region_communi, 1)
        p_data(region_communi(j,1),region_communi(j,2),tt) = sum(p(region_communi(j,1),region_communi(j,2),:,tt));
    end
end

t_matrix = [1 500 1000 1500 2000 3000 4000 5000 7000];
% t_matrix = [1 500 1000 1100 1020 1030 1035 1040 1060];
for i=1:1:length(t_matrix)
    tt=t_matrix(i); % chose a time
    figure(i)
    % region 19
    t = (0:1/6:1)'*2*pi;
    x = cos(t);
    y = sin(t);
    color = a(ceil(max( n_data(19,tt)/n_max*64,1) ),:);
    fill(x,y,color)
    axis image
    set(gca, 'FontName', 'Times New Roman', 'FontSize', 12);
%     colormap(flipud(gray))
%     colorbar
    caxis([0 n_max]);
    set(gca,'ytick',[], 'xtick',[])
    hold on

    % region 15
    x = cos(t)+1.5;
    y = sin(t)+sqrt(3)/2;
    color = a(ceil(max( n_data(15,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 16
    x = cos(t);
    y = sin(t)+sqrt(3);
    color = a(ceil(max( n_data(16,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 17
    x = cos(t)-1.5;
    y = sin(t)+sqrt(3)/2;
    color = a(ceil(max( n_data(17,tt)/n_max*64,1)),:);
    fill(x,y,color)

    % region 18
    x = cos(t)-1.5;
    y = sin(t)-sqrt(3)/2;
    color = a(ceil(max( n_data(18,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 13
    x = cos(t);
    y = sin(t)-sqrt(3);
    color = a(ceil(max( n_data(13,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 14
    x = cos(t)+1.5;
    y = sin(t)-0.5*sqrt(3);
    color = a(ceil(max( n_data(14,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 1
    x = cos(t);
    y = sin(t)-2*sqrt(3);
    color = a(ceil(max( n_data(1,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 2
    x = cos(t)+1.5;
    y = sin(t)-1.5*sqrt(3);
    color = a(ceil(max( n_data(2,tt)/n_max*64,1 )),:);
    fill(x,y,color)

    % region 3
    x = cos(t)+3;
    y = sin(t)-sqrt(3);
    color = a(ceil(max( n_data(3,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 4
    x = cos(t)+3;
    y = sin(t);
    color = a(ceil(max( n_data(4,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 5
    x = cos(t)+3;
    y = sin(t)+sqrt(3);
    color = a(ceil(max( n_data(5,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 6
    x = cos(t)+1.5;
    y = sin(t)+1.5*sqrt(3);
    color = a(ceil(max( n_data(6,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 7
    x = cos(t);
    y = sin(t)+2*sqrt(3);
    color = a(ceil(max( n_data(7,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 8
    x = cos(t)-1.5;
    y = sin(t)+1.5*sqrt(3);
    color = a(ceil(max( n_data(8,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 9
    x = cos(t)-3;
    y = sin(t)+sqrt(3);
    color = a(ceil(max( n_data(9,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 10
    x = cos(t)-3;
    y = sin(t);
    color = a(ceil(max( n_data(10,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 11
    x = cos(t)-3;
    y = sin(t)-sqrt(3);
    color = a(ceil(max( n_data(11,tt)/n_max*64,1) ),:);
    fill(x,y,color)

    % region 11
    x = cos(t)-1.5;
    y = sin(t)-1.5*sqrt(3);
    color = a(ceil(max( n_data(12,tt)/n_max*64,1) ),:);
    fill(x,y,color)
    
    xlabel(strcat('t=',num2str(t_matrix(i)),'s'))
    

    for j =1:1:size(region_communi, 1)
        if p_all(region_communi(j,1),19,tt)/p_max > 0.1
%             lineW = ceil(sum(p(region_communi(j,1),19,:,tt)))*5;
            lineW = 3;  
            line([center(region_communi(j,1),1),center(region_communi(j,2),1)],[center(region_communi(j,1),2),center(region_communi(j,2),2)],'Color','k', 'LineWidth',lineW);
        else
        end
    end
    set(gca, 'FontName', 'Times New Roman', 'FontSize', 10);
    set(gcf,'unit','centimeters','position',[11 6 4 4]);
    
end

% set(gca, 'Position',[0.5, 0.5, 24, 9])

