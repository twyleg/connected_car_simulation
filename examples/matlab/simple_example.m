global hostname
hostname = "localhost:8080"

while 1

    input = get_vehicle_input_adhoc();
    
    if size(input.traffic_lights)
    
        vehicle_position_on_route = input.vehicle_state.position_on_route;
        next_traffic_light_position = input.traffic_lights(1).position_on_route;
        
        distance_to_next_traffic_light = next_traffic_light_position - vehicle_position_on_route;
        fprintf('Distance to next traffic light: %f\n\r', distance_to_next_traffic_light)
        
        if input.traffic_lights(1).state == "red" && distance_to_next_traffic_light < 30
            set_vehicle_output(0.0, 8.0);
        else
            set_vehicle_output(50.0, 2.0);
        end
        
    else
        set_vehicle_output(50.0, 2.0);
    end
    
end