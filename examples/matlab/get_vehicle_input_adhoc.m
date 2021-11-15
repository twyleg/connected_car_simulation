function [input] = get_vehicle_input_adhoc()
%SET_VEHICLE_TARGET_VELOCITY Summary of this function goes here
%   Detailed explanation goes here
global hostname

str = 'http://' + hostname + '/api/get_vehicle_input_adhoc';
input = webread(str);

end