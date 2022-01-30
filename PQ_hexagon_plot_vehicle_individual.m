% clear;clc
% close all
% %% plot hexagon regions
% load('n_19_hexagon_regions_multi_ds_withdemand_7200_300_300_200_321_4000.mat');
% n_max_control = max(max(n_data));
% load('n_19_hexagon_regions_multi_ds_withdemand_no_control_7200_300_300_200_321_4000.mat');
% n_max_no_control = max(max(n_data));
% 
% load('n_19_hexagon_regions_multi_ds_withdemand_7200_2_20000_PQ_RawCb.mat');
load('n_19_hexagon_regions_multi_ds_withdemand_7200_2_20000_PQ_Reduce.mat');

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

% n_max = max(n_max_control,n_max_no_control);
n_max = max(max(n_data));

t_matrix = [1 500 1000 1500 2000 3000 4000 5000 7000];
for i=1:1:length(t_matrix)
    tt=t_matrix(i); % chose a time
    figure(i)
    % region 19
    t = (0:1/6:1)'*2*pi;
    x = cos(t);
    y = sin(t);
    color = a(max(ceil(n_data(19,tt)/n_max*256),1),:);
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
    color = a(max(ceil(n_data(15,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 16
    x = cos(t);
    y = sin(t)+sqrt(3);
    color = a(max(ceil(n_data(16,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 17
    x = cos(t)-1.5;
    y = sin(t)+sqrt(3)/2;
    color = a(max(ceil(n_data(17,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 18
    x = cos(t)-1.5;
    y = sin(t)-sqrt(3)/2;
    color = a(max(ceil(n_data(18,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 13
    x = cos(t);
    y = sin(t)-sqrt(3);
    color = a(max(ceil(n_data(13,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 14
    x = cos(t)+1.5;
    y = sin(t)-0.5*sqrt(3);
    color = a(max(ceil(n_data(13,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 1
    x = cos(t);
    y = sin(t)-2*sqrt(3);
    color = a(max(ceil(n_data(1,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 2
    x = cos(t)+1.5;
    y = sin(t)-1.5*sqrt(3);
    color = a(max(ceil(n_data(2,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 3
    x = cos(t)+3;
    y = sin(t)-sqrt(3);
    color = a(max(ceil(n_data(3,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 4
    x = cos(t)+3;
    y = sin(t);
    color = a(max(ceil(n_data(4,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 5
    x = cos(t)+3;
    y = sin(t)+sqrt(3);
    color = a(max(ceil(n_data(5,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 6
    x = cos(t)+1.5;
    y = sin(t)+1.5*sqrt(3);
    color = a(max(ceil(n_data(6,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 7
    x = cos(t);
    y = sin(t)+2*sqrt(3);
    color = a(max(ceil(n_data(7,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 8
    x = cos(t)-1.5;
    y = sin(t)+1.5*sqrt(3);
    color = a(max(ceil(n_data(8,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 9
    x = cos(t)-3;
    y = sin(t)+sqrt(3);
    color = a(max(ceil(n_data(9,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 10
    x = cos(t)-3;
    y = sin(t);
    color = a(max(ceil(n_data(10,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 11
    x = cos(t)-3;
    y = sin(t)-sqrt(3);
    color = a(max(ceil(n_data(11,tt)/n_max*256),1),:);
    fill(x,y,color)

    % region 12
    x = cos(t)-1.5;
    y = sin(t)-1.5*sqrt(3);
    color = a(max(ceil(n_data(12,tt)/n_max*256),1),:);
    fill(x,y,color)
    
    xlabel(strcat('t=',num2str(t_matrix(i)),'s'))
    

    for j =1:1:size(region_communi, 1)
        if p_data(j,19,tt) > 0.015
            line([center(region_communi(j,1),1),center(region_communi(j,2),1)],[center(region_communi(j,1),2),center(region_communi(j,2),2)],'Color','k', 'LineWidth',3);
        else
        end
    end
    set(gca, 'FontName', 'Times New Roman', 'FontSize', 10);
    set(gcf,'unit','centimeters','position',[11 6 4 4]);
    
end

% set(gca, 'Position',[0.5, 0.5, 24, 9])

