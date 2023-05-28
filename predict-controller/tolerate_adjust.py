# scaling up 
predict_value = 61000
current_num_replicas = 6
target_value = 10000
def tolerate_handler(predict_value, current_num_replicas, target_value, tolerate=10):
    if predict_value > target_value*current_num_replicas:
        percent_diff = 100*abs(predict_value/current_num_replicas - target_value)/target_value
        percent_require = tolerate - percent_diff
        num_require_add = percent_require*0.01*current_num_replicas*target_value
        return { 
            "predict_require_trigger_scaleup": predict_value + num_require_add,
            "predict_require_add_more_trigger_scaleup": num_require_add,
            "percent_diff": percent_diff
        }
    return {}

print(tolerate_handler(predict_value, current_num_replicas, target_value))