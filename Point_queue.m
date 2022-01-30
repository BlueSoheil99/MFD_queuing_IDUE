%% illustrate the point queue model
q_temp=0;
q=zeros(40,1);
q(1)=0;
for t=1:1:40
    p(t+1) = 2;
    if t<=10
        u(t+1) = 1;
    elseif t<=20
        u(t+1) = 4;
    else
        u(t+1) = 1;
    end
    
    delta_q = q_temp+p(t+1)-u(t+1);
    if delta_q >=0
        q(t+1) = delta_q;
        v(t+1) = u(t+1);
    else
        q(t+1) = 0;
        v(t+1) = q(t+1)+p(t+1);
    end
    q_temp = q(t+1);
end


t=0:1:40;
figure(1)
yyaxis left
plot(t,p, '-^b', 'linewidth', 1.5)
hold on
plot(t,v, '-sg', 'linewidth', 1.5)
plot(t,u, '-dr', 'linewidth', 1.5)
set(gca, 'FontName', 'Times New Roman', 'FontSize', 11);
set(gcf,'unit','centimeters','position',[11 6 12 9]);
set(gca,'ycolor','k');
xlabel('Time [t]');
ylabel('p(t), v(t), u(t) [veh/s]');
grid on
axis([0,30, 0, 10]);
yyaxis right
plot(t,q, '-*m', 'linewidth', 1.5)
set(gca,'ycolor','k');
ylabel('q(t) [veh]');
legend('p(t)', 'v(t)', 'u(t)', 'q(t)')
axis([0,30, 0, 10]);
