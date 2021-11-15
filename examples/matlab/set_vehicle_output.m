function [] = set_vehicle_output(target_velocity, acceleration)
%SET_VEHICLE_TARGET_VELOCITY Summary of this function goes here
%   Detailed explanation goes here
global hostname

str = 'http://' + hostname + '/api/set_vehicle_output?target_velocity=' + target_velocity + '&acceleration=' + acceleration;
webread(str);

end

