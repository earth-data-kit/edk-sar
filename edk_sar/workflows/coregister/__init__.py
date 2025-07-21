import edk_sar as es

def run():
    output = es.frameworks.isce2.run_cmd("bash /workspace/workflows/coregister/run.sh")
    print (output)