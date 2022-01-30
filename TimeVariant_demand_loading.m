
if t<cut
    demand.val(1:18,19) = d_central_t;
    demand.val(1,13) = d_rural_suburban; demand.val(1,14) = d_rural_suburban; demand.val(1,18) = d_rural_suburban;
    demand.val(1,15:17) = d_rural_far_suburban;
    demand.val(2,13) = d_rural_suburban; demand.val(2,14) = d_rural_suburban; demand.val(2,15) = d_rural_suburban; demand.val(2,18) = d_rural_suburban;
    demand.val(2,16:17) = d_rural_far_suburban;
    demand.val(3,13) = d_rural_suburban; demand.val(3,14) = d_rural_suburban; demand.val(3,15) = d_rural_suburban;
    demand.val(3,16:18) = d_rural_far_suburban;
    demand.val(4,13) = d_rural_suburban; demand.val(4,14) = d_rural_suburban; demand.val(4,15) = d_rural_suburban; demand.val(4,16) = d_rural_suburban;
    demand.val(4,17:18) = d_rural_far_suburban;
    demand.val(5,14) = d_rural_suburban; demand.val(5,15) = d_rural_suburban; demand.val(5,16) = d_rural_suburban;
    demand.val(5,17:18) = d_rural_far_suburban; demand.val(5,13) = d_rural_far_suburban;
    demand.val(6,14) = d_rural_suburban; demand.val(6,15) = d_rural_suburban; demand.val(6,16) = d_rural_suburban; demand.val(6,17) = d_rural_suburban;
    demand.val(6,13) = d_rural_far_suburban; demand.val(6,18) = d_rural_far_suburban;
    demand.val(7,15) = d_rural_suburban; demand.val(7,16) = d_rural_suburban; demand.val(7,17) = d_rural_suburban;
    demand.val(7,13:14) = d_rural_far_suburban; demand.val(7,18) = d_rural_far_suburban;
    demand.val(8,15) = d_rural_suburban; demand.val(8,16) = d_rural_suburban; demand.val(8,17) = d_rural_suburban; demand.val(8,18) = d_rural_suburban; 
    demand.val(8,13:14) = d_rural_far_suburban;
    demand.val(9,16) = d_rural_suburban; demand.val(9,17) = d_rural_suburban; demand.val(9,18) = d_rural_suburban;
    demand.val(9,13:15) = d_rural_far_suburban;
    demand.val(10,16) = d_rural_suburban; demand.val(10,17) = d_rural_suburban; demand.val(10,18) = d_rural_suburban; demand.val(10,13) = d_rural_suburban;
    demand.val(10,14:15) = d_rural_far_suburban;
    demand.val(11,13) = d_rural_suburban; demand.val(11,17) = d_rural_suburban; demand.val(11,18) = d_rural_suburban;
    demand.val(11,14:16) = d_rural_far_suburban;
    demand.val(12,13) = d_rural_suburban; demand.val(12,14) = d_rural_suburban; demand.val(12,17) = d_rural_suburban; demand.val(12,18) = d_rural_suburban;
    demand.val(12,15:16) = d_rural_far_suburban;
    demand.val(13,13) = d_rural_suburban;
    demand.val(13,14:18) = d_rural_far_suburban;
    demand.val(14,14) = d_rural_suburban;
    demand.val(14,15:18) = d_rural_far_suburban; demand.val(14,13) = d_rural_far_suburban;
    demand.val(15,15) = d_rural_suburban;
    demand.val(15,16:18) = d_rural_far_suburban; demand.val(15,13:14) = d_rural_far_suburban;
    demand.val(16,16) = d_rural_suburban;
    demand.val(16,17:18) = d_rural_far_suburban; demand.val(16,13:15) = d_rural_far_suburban;
    demand.val(17,17) = d_rural_suburban;
    demand.val(17,18) = d_rural_far_suburban; demand.val(17,13:16) = d_rural_far_suburban;
    demand.val(18,18) = d_rural_suburban;
    demand.val(18,13:17) = d_rural_far_suburban;
    demand.val(19,19) = d_rural_suburban;
    demand.val(19,13:18) = d_rural_far_suburban;
else
    demand.val = zeros(19,19);
end