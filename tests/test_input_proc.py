import yaml, input_proc 

def getYaml(file):
    with open(r'./tests/{}.yaml'.format(str(file))) as yaml_file:
      content = yaml.load(yaml_file, Loader=yaml.FullLoader)

    return content

def get_test_values():
  values = getYaml('input_proc')
  return values

if __name__ == "__main__":
  #print("get test values")
  values = get_test_values()
  #print("Set initial prevStatus")
  prevStatus = [True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True]
  #print("Loop over test values")
  for v in values:
    #print("value: {}, get status".format(v))
    status = input_proc.sensor_status(v['value'])
    #print("Diff the values")
    diff = input_proc.diff_values(status,prevStatus)
    #print("set current state as previous")
    prevStatus = status
    print("{}:{} = {} Diff: {}".format(status,v['expect'],v['value'],diff))
