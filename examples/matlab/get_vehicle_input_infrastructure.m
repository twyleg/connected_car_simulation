function [input] = get_vehicle_input_infrastructure()
%GET_VEHICLE_INPUT_INFRASTRUCTURE Summary of this function goes here
%   Detailed explanation goes here
global hostname

str = 'http://' + hostname + '/api/get_vehicle_input_infrastructure';
input = webread(str);

end