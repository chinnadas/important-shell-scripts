"""
This script is consolidated script used for Monitoring SOA Environment
File Name	: 	soaHealth.py
Author		: 	Vijay G
Initiated	:	2014
Updated		: 	06/24/2015
"""

from java.util import Date
from java.io import FileInputStream
import java.lang
import os
import string
import httplib

propInputStream = FileInputStream("/oracle/ops/domain.properties")
configProps = Properties()
configProps.load(propInputStream)
healthURL = configProps.get("health.url")
EmailList = configProps.get("email")
EnvironmentName = configProps.get("environment.name")

#send mail module
def sendMailString():
        os.system('mail -s " Middleware ' + EnvironmentName + ' Status " ' + EmailList + ' < serverState_file')
        print '*********  ALERT MAIL HAS BEEN SENT FOR SERVER STATE ***********'
        print ''

#DataSource Status module
def dataSource():
        cmd = "echo \"Below are the Status of Datasource targeted to " + server.getName() + " \n" + "\" >> serverState_file"
        os.system(cmd)
        runningServers = domainRuntimeService.getServerRuntimes()
        for servers in runningServers:
          if(server.getName() == servers.getName()):
            global check
            check = "noissues"
            dataSources = servers.getJDBCServiceRuntime().getJDBCDataSourceRuntimeMBeans()
            for dataSource in dataSources:
              Name = dataSource.getName()
              state = dataSource.getState()
              testPool = dataSource.testPool()
              #cmd = "echo \"Datasource " + str(Name) + "  " + str(state) + "  " + str(testPool) + " \n" + "\" >> serverState_file"
              #os.system(cmd)
              #check = false
              if (str(state) != "Running"):
                cmd = "echo \"Datasource Name " + str(Name) +  " on Server " + str(server.getName()) + " State : " + str(state) + " and TestConnection : " + str(testPool) + " \n" + "\" >> serverState_file"
                os.system(cmd)
                check = "issuess"
                print check
                continue
              if (str(testPool) != "None"):
                cmd = "echo \"Datasource Name " + str(Name) +  " on Server " + str(server.getName()) + " State : " + str(state) + " and TestConnection : " + str(testPool) + " \n" + "\" >> serverState_file"
                os.system(cmd)
                check = "issuess"
                print check
                continue
            if ( check == "noissues" ):
                  cmd = "echo \" All Datasources are running successfully " + " \n" + "\" >> serverState_file"
                  os.system(cmd)

#SOA Application Status module
def soaStatus():
      cmd = "echo \" ******* SOA Applications Status on " + server.getName() + " *********  \n " + "\" >> serverState_file"
      os.system(cmd)
      serverRuntime()
      cd('domainRuntime:/AppRuntimeStateRuntime/AppRuntimeStateRuntime')
      currentState = cmo.getCurrentState("soa-infra", server.getName())
      cmd = "echo \" Current state of soa-infra on " + server.getName() + "   ==>> " + currentState + "\n " + "\" >> serverState_file"
      os.system(cmd)
      print 'Current state of soa-infra on '+ server.getName() + ' ==>> ' + currentState
      cd('domainRuntime:/ServerRuntimes/' + server.getName() + '/ApplicationRuntimes/soa-infra')
      stringStatus = get('HealthState')
      soainfraHealth = str(stringStatus).split(',')
      cmd = "echo \" Current Health of soa-infra on " + server.getName() + "   ==>> " + soainfraHealth[1] + "\n " + "\" >> serverState_file"
      os.system(cmd)
      cd('domainRuntime:/AppRuntimeStateRuntime/AppRuntimeStateRuntime')
      currentState = cmo.getCurrentState("soastatus", server.getName())
      cmd = "echo \" Current state of soastatus on " + server.getName() + "   ==>> " + currentState + "\n " + "\" >> serverState_file"
      os.system(cmd)
      print 'Current state in soastatus on '+ server.getName() + ' ==>> ' + currentState
      cd('domainRuntime:/ServerRuntimes/' + server.getName() + '/ApplicationRuntimes/soastatus')
      stringStatus = get('HealthState')
      soastausHealth = str(stringStatus).split(',')
      cmd = "echo \" Current Health of soastatus on " + server.getName() + "   ==>> " + soastausHealth[1] + "\n " + "\" >> serverState_file"
      os.system(cmd)

def soahealthURL():
      listenAddress = str(server.getListenAddress()).split('/')[0] + ":" + str(server.getListenPort())
      soaurl = healthURL
      conn = httplib.HTTPConnection(listenAddress)
      conn.request('GET',soaurl)
      response = conn.getresponse()
      statusresp = response.status
      #print response.read(10 *1024 *1024)
      conn.close()

      if(statusresp == 200 or statusresp == 302):
          string = str(statusresp)
          cmd = "echo \" SOA status webapp HTTP Test connection on  " + server.getName() + "  is SUCCESS and Response is : " + string + " \n " + "\" >> serverState_file"
          os.system(cmd)
          cmd = "echo \" 302 Response means its Redirecting to Load Balancer URL  \n " + "\" >> serverState_file"
          os.system(cmd)

      else:
          string = str(statusresp)
          cmd = "echo \" SOA status webapp HTTP Test connection on  " + server.getName() + "  is FAILED and Response is : " + string + " \n " + "\" >> serverState_file"
          os.system(cmd)

#Stuck Thread monitoring module
def stuckThread():
      cd('domainRuntime:/ServerRuntimes/' + server.getName() + '/ThreadPoolRuntime/ThreadPoolRuntime')
      healthState=cmo.getHealthState()
      status = str(healthState)
      #print status
      #check = string.find(status,"HEALTH_WARN")
      #if check != -1:
      if "HEALTH_OK" in str(status):
            cmd = "echo \" There are !!!! NO STUCK THREADS !!!! on  " + server.getName() + " \n " + "\" >> serverState_file"
            os.system(cmd)

      else:
          health = str(healthState).split(',')
          cmd = "echo \" !!!! ALERT !!!! Thread Pool Health is in WARNING State on  " + server.getName() + " and warnning is : " + health[3] + " \n " + "\" >> serverState_file"
          os.system(cmd)

def jmsModule():
      cmd = "echo \"Below are the Status of JMS Module Status targeted to " + server.getName() + " \n" + "\" >> serverState_file"
      os.system(cmd)
      runningServers = domainRuntimeService.getServerRuntimes()
      for servers in runningServers:
          if(server.getName() == servers.getName()):
             global check
             check = "noissues"
             jmsRunTime = servers.getJMSRuntime()
             jmsServers = jmsRunTime.getJMSServers()
             for jmsServer in jmsServers:
                destinations = jmsServer.getDestinations()
                for destination in destinations:
                    name = destination.getName()
                    messagesCurrent = destination.getMessagesCurrentCount()
                    messagesPending = destination.getMessagesPendingCount()
                    if messagesCurrent > 0 or messagesPending > 0:
                      cmd = "echo \"JMSQueueName " + str(name) + " Messages Current " + str(messagesCurrent) + " Messages Pending " + str(messagesPending) + " \n" + "\" >> serverState_file"
                      os.system(cmd)
                      check = "issues"
                      print check
             if ( check == "noissues" ):
                  cmd = "echo \" There are no Pending Messages in JMS Modules " + " \n" + "\" >> serverState_file"
                  os.system(cmd)

def heap():
        cd('domainRuntime:/ServerRuntimes/' + server.getName() + '/JVMRuntime/' + server.getName())
        freeMemPercent  = get('HeapFreePercent')
        cmd = "echo \" Percentage Heap free for server " + server.getName() + " : " + str(freeMemPercent) + " \n" + "\" >> serverState_file"
        os.system(cmd)



disconnect()
today=Date()
check="noissues"
serverState=""
serverName =""
cmd = "echo \"Script Execution time " + today.toString() + " \n\n"+ "\" > serverState_file"
os.system(cmd)
try:
  connect(userConfigFile='/oracle/ops/monitor/AppServer/soab2bprd_userConfig.file' , userKeyFile='/oracle/ops/monitor/AppServer/soab2bprd_userkey.file' , url='t3://soab2badm1.strykercorp.com:7001')
  serverNames = cmo.getServers();
  try:

      for server in serverNames:
        domainRuntime()
        serverName = server.getName()
        print serverName
        try:
          cd("/ServerRuntimes/" + server.getName())

        except:
             if "SOA" in server.getName():
                cmd = "echo \" *****  " + server.getName() + "  is NOT RUNNING Verify Immedietaly  ***** \n " + "\" >> serverState_file"
                os.system(cmd)
             continue

        serverhealth = cmo.getHealthState()
        print serverhealth
        if "HEALTH_OK" in str(serverhealth):
             cmd = "echo \" *****  " + server.getName() + "  is RUNNING and Health OK  ***** \n " + "\" >> serverState_file"
             os.system(cmd)

        else:
          health = str(serverhealth).split(',')
          cmd = "echo \" *****  " + server.getName() + " Health Status is NOT OK and REASON  is : " + health[3] + "***** \n " + "\" >> serverState_file"
          os.system(cmd)
        stuckThread()
        dataSource()
        jmsModule()
        if "SOA" in server.getName():
          heap()
          soaStatus()
          soahealthURL()
      sendMailString()

  except:

        print 'Oops! Unable to get server application status ' , server.getName()
        stateMessage = 'The ' + server.getName() + ' is not Accesable ' + ' at Time: ' + today.toString() + ' review server manually'
        cmd = "echo " + stateMessage +" >> serverState_file"
        os.system(cmd)
        sendMailString()

except:
                print 'Sorry !!! Unable to Connect to Admin Server '
                today = Date()
                stateMessage = 'Sorry !!! Unable to Connect to Admin Server ' + ' at Time: ' + today.toString() + ' review server manually'
                cmd = "echo " + stateMessage +" >> serverState_file"
                os.system(cmd)
                sendMailString()
                sys.exit(99)

