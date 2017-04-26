#!/usr/bin/python
def qp():
  # save encrypted password for user
  import os
  from simplecrypt import encrypt,decrypt
  from getpass import getpass
  #
  u=raw_input('user:')
  c=encrypt(os.environ['computername'],getpass('pw:'))
  f=open('c:\Python27\\'+u+'.cod','w')
  f.write(c)
  f.close()
  #
  if decrypt(os.environ['computername'],c)==getpass('again:'):
	  print 'ok'
  else:
	  f.erase()
	  print 'try again'
  f=open('c:\Python27\\'+u+'.cod','r')
  c2=f.read()
  print f,c2
  f.close()
# cisco ssh interface
def csshpw(username='tgraham'):
  from simplecrypt import encrypt,decrypt
  import os
  import sys
  try:
      fp=open('c:\Python27\\'+username+'.cod','r')
  except:
      print "don't know you: ",username
      sys.exit()
  else:
      cry=fp.read()
      fp.close()
      return(decrypt(os.environ['computername'],cry))
#
class cssh(object):
  #
  def __init__ (self,myuid,mypw,myip):
    #print 'starting cssh'
    self.ip=myip
    self.username=myuid
    self.password=mypw
    self.routerid=' '
    self.connected=False
    self.config=False
    #paramiko.util.log_to_file("paramiko-" + \
                            # time.strftime("%Y-%m-%d-%H:%M:%S"))
    self.cssh_client()
    session=self.cssh_remote_connection()
    if session== False:
             print 'remote session failed'

    else:
      self.rshell = self.cssh_shell()
      self.connected = True
	  
  def cssh_client(self):
    ''' create an ssh client '''
    import paramiko
    # Create instance of SSHClient object
    self.rclient = paramiko.SSHClient()

    # Automatically add untrusted hosts
    self.rclient.set_missing_host_key_policy(
               paramiko.AutoAddPolicy())
  
  
  def cssh_remote_connection(self):
    ''' establish ssh connection for (user,pswd) '''
    # initiate SSH connection
    try:
      self.rc=self.rclient.connect( self.ip, username=self.username, \
      password=self.password, look_for_keys=False, allow_agent=False)

    except:
      print "SSH connection failed to %s" % self.ip
      return False
    else:
      print "SSH connection established to %s" % self.ip
    return True
      
  def cssh_shell (self):
    ''' start cisco shell for interactive CLI '''
    import time
    # Use invoke_shell to establish an 'interactive session'
    self.rs = self.rclient.invoke_shell()
    time.sleep(1)

    # Strip the initial router prompt
    output = self.rs .recv(1000)

    # See what we have
    outlines=output.split()

    self.rs.send('terminal len 0\n')
    time.sleep(.5)
    output = self.rs.recv(1000)
    #
    self.rs.send('\n')
    time.sleep(.5)
    output = self.rs.recv(1000)
    outlines = output.split()
    try:
      self.routerid=outlines[0].split('#')[0]
    except:
      for line in outlines:
                      print line
      self.routerid=outlines[0].split('>')[0]
    #print 'routerid:',self.routerid
	
  def configT(self):
    import time
    self.rs.send('config t\n')
    time.sleep(.5)
    self.rs.config=True
    return self.rs.recv(1000)

  def configEnd(self):
    import time
    self.rs.send('end\n')
    time.sleep(.5)
    self.rs.config=False
    return self.rs.recv(1000)

  def configSend(self,cmd):
    import time
    import sys
    if self.rs.config:
      self.rs.send('%s\n' % cmd)
      time.sleep(.5)
    else:
      print 'not in config mode',cmd
      sys.exit()

    return self.rs.recv(1000)

  def send_command(self, \
      command,cwait=.5,cbuff=1,maxwait=5,outlen=1):
    
    ''' send a command, returns a dictionary [command,result,prompt] '''
    # outlen == 0 means we don't expect/require any output
    import time
    mywait=cwait
    mybuff=cbuff*1000
    output={}
    output['prompt']=''

    while ( output['prompt']<> (self.routerid+"#") ):
      # don't go forever
      if (mywait > maxwait) or (mybuff > 904800):
        print 'max tries exceeded',mywait,mybuff
        break
      #print mywait,mybuff
      # use ssh to send command
      self.rs.send(command+'\n')
      time.sleep(mywait)
      # obtain output
      recv = self.rs.recv(mybuff)
    #
      if len(recv) < mybuff:
        recvlines=recv.split('\r\n')
        output['command']=recvlines[0]
        output['prompt']=recvlines[-1]
        output['result']=recvlines[1:-1]
         
        if len(output['result'])<outlen:
          #print 'no result:',recvlines
          output['prompt']=' '
          mywait+=.5
          #print 'retry:', mywait

      else:
        # increase buffer and try again
        #print 'buffsize:', recv
        mybuff*=2
  #
    if (outlen>0) & (len(output['result']) == 0) :
      print 'send_command:',output,len(output['result'])
      output['result']='Error-send_command'

    return output

  def close(self):
    ''' close the session '''
    self.rs.send('exit\r\n')
    self.rs.close()
    self.connected=False



