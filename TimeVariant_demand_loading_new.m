
if t<cut
    demand.val(1:18,19) = d_medi;
    demand.val(1,13) = d_high; demand.val(1,14) = d_medi; demand.val(1,18) = d_medi;
    demand.val(1,15:17) = d_low;
    
    demand.val(2,13) = d_high; demand.val(2,14) = d_high; demand.val(2,15) = d_medi; demand.val(2,18) = d_medi;
    demand.val(2,16:17) = d_low;
    
    demand.val(3,13) = d_medi; demand.val(3,14) = d_high; demand.val(3,15) = d_medi;
    demand.val(3,16:18) = d_low;
    
    demand.val(4,13) = d_medi; demand.val(4,14) = d_high; demand.val(4,15) = d_high; demand.val(4,16) = d_medi;
    demand.val(4,17:18) = d_low;
    
    demand.val(5,14) = d_medi; demand.val(5,15) = d_high; demand.val(5,16) = d_medi;
    demand.val(5,17:18) = d_low; demand.val(5,13) = d_low;
    
    demand.val(6,14) = d_medi; demand.val(6,15) = d_high; demand.val(6,16) = d_high; demand.val(6,17) = d_medi;
    demand.val(6,13) = d_low; demand.val(6,18) = d_low;
    
    demand.val(7,15) = d_medi; demand.val(7,16) = d_high; demand.val(7,17) = d_medi;
    demand.val(7,13:14) = d_low; demand.val(7,18) = d_low;
    
    demand.val(8,15) = d_medi; demand.val(8,16) = d_high; demand.val(8,17) = d_high; demand.val(8,18) = d_medi; 
    demand.val(8,13:14) = d_low;
    
    demand.val(9,16) = d_medi; demand.val(9,17) = d_high; demand.val(9,18) = d_medi;
    demand.val(9,13:15) = d_low;
    
    demand.val(10,16) = d_medi; demand.val(10,17) = d_high; demand.val(10,18) = d_high; demand.val(10,13) = d_medi;
    demand.val(10,14:15) = d_low;
    
    demand.val(11,13) = d_medi; demand.val(11,17) = d_high; demand.val(11,18) = d_medi;
    demand.val(11,14:16) = d_low;
    
    demand.val(12,13) = d_medi; demand.val(12,14) = d_high; demand.val(12,17) = d_high; demand.val(12,18) = d_medi;
    demand.val(12,15:16) = d_low;
    
    demand.val(13,13) = d_high;
    demand.val(13,14) = d_medi; demand.val(13,18) = d_medi;
    demand.val(13,15:17) = d_low;
    
    demand.val(14,14) = d_high;
    demand.val(14,13) = d_medi; demand.val(14,15) = d_medi;
    demand.val(14,16:18) = d_low;
    
    demand.val(15,15) = d_high;
    demand.val(15,14) = d_medi; demand.val(15,16) = d_medi;
    demand.val(15,17:18) = d_low; demand.val(15,13) = d_low;
    
    demand.val(16,16) = d_high;
    demand.val(16,15) = d_medi; demand.val(16,17) = d_medi;
    demand.val(16,13:14) = d_low; demand.val(16,18) = d_low;
    
    demand.val(17,17) = d_high;
    demand.val(17,16) = d_medi; demand.val(17,18) = d_medi;
    demand.val(17,13:15) = d_low;
    
    demand.val(18,18) = d_high;
    demand.val(18,13) = d_medi; demand.val(18,17) = d_medi;
    demand.val(18,14:16) = d_low;
    
    demand.val(19,19) = d_high;
    demand.val(19,13:18) = d_medi;
else
    demand.val = zeros(19,19);
end