#!/usr/bin/python

import utils.PortFinder
import sys
import subprocess
import os
import time
import signal
from optparse import OptionParser

def main(argv=None):
    
    start_port = 50000
    end_port = 50100
    used_port = None
    nobin = True

    hostname = os.uname()[1]
    if (hostname == "dieb-sse.jpl.nasa.gov") :
        addr = "192.168.0.1"
    else :
        addr = "192.168.0.33"
    print ("Using address %s"%addr)

    python_bin = os.environ["PYTHON_BASE"] + "/bin/python"
    
    for port in range(start_port,end_port):
        if not utils.PortFinder.IsPortUsed(port):
            used_port = port
            print("Using port %d"%used_port)
            break;
        
    if (used_port == None):
        print("Could not find port in range %d to %d",start_port,end_port)
        return -1
    
    build_root = os.environ["BUILD_ROOT"]
    
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port", action="store", type="int", help="Set the threaded TCP socket server port [default: %default]", default=used_port)
    parser.add_option("-a", "--addr", dest="addr", action="store", type="string", help="set the threaded TCP socket server address [default: %default]", default=addr)
    parser.add_option("-n", "--nobin", dest="nobin", action="store_true", help="Disables the binary app from starting [default: %default]", default=False)
    parser.add_option("-t", "--twin", dest="twin", action="store_true", help="Runs Threaed TCP Server in window, otherwise backgrounds [default: %default]", default=False)

    (opts, args) = parser.parse_args(argv)
    used_port = opts.port
    #nobin = opts.nobin
    addr = opts.addr
    twin = opts.twin
#     print 'nobin =', nobin
#     print 'port = ', used_port
#     print 'addr = ', addr 

    # run ThreadedTCPServer
    if twin:
        TTS_args = [python_bin,"%s/Gse/bin/pexpect_runner.py"%build_root,"ThreadedTCP.log","Threaded TCP Server",python_bin,"%s/Gse/bin/ThreadedTCPServer.py"%build_root,"--port","%d"%used_port, "--host",addr]
        TTS = subprocess.Popen(TTS_args)
    else:
        tts_log = open("ThreadedTCP.log",'w')
        TTS_args = [python_bin, "-u", "%s/Gse/bin/ThreadedTCPServer.py"%build_root,"--port","%d"%used_port, "--host",addr]
        TTS = subprocess.Popen(TTS_args,stdout=tts_log,stderr=subprocess.STDOUT)
    
    # wait for TCP Server to start
    time.sleep(2)
    
    # run Gse GUI
    GUI_args = [python_bin,"%s/Gse/bin/gse.py"%build_root,"--port","%d"%used_port,"--dictionary","%s/Gse/generated/Ref"%build_root,"--connect","--addr",addr,"-L","%s/Ref/logs"%build_root]
    #print ("GUI: %s"%" ".join(GUI_args))
    GUI = subprocess.Popen(GUI_args)
    
    # run Ref app
    
    op_sys = os.uname()[0]
    
    ref_bin = "%s/Ref/%s/Ref"%(build_root,os.environ["OUTPUT_DIR"])
    
    if not nobin:
        REF_args = [python_bin,"%s/Gse/bin/pexpect_runner.py"%build_root,"Ref.log","Ref Application",ref_bin,"-p","%d"%used_port,"-a",addr]
        REF = subprocess.Popen(REF_args)
    
    GUI.wait()

    if not nobin:
        try:
            REF.send_signal(signal.SIGTERM)
        except:
            pass
            
        try:
            REF.wait()
        except:
            pass
            
    try:
        TTS.send_signal(signal.SIGINT)
    except:
        pass
        
    try:
        TTS.wait()
    except:
        pass
            
    # Run Gse interface
    
            
         

if __name__ == "__main__":
    sys.exit(main())
