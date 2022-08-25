class input_proc:

  def sensor_status(n, num_sensors=16):
    bool_list = [True if digit == '1' else False for digit in bin(n)[2:]]
    bool_list.reverse()
    for i in range(len(bool_list),num_sensors):
      bool_list.append(False)
    return bool_list
  
  def diff_values(current_status, past_status):
    diff = {}
    i = 0
    while i < 16:
      if current_status[i] != past_status[i]:
        diff[(i+1)] = current_status[i]
      i += 1
    return diff

