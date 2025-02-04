from osmclient import client
from osmclient.common.exceptions import ClientException
import io
import requests
import time
import logging

def getNS(domainIp, nsId,domainLayerObj):
    tmpClient = client.Client(host=domainIp,user=domainLayerObj.username,password=domainLayerObj.password, project=domainLayerObj.project)
    return tmpClient.ns.get(nsId)

def instantiateNS(domainIp, nsName, nsdName, domainLayerObj, additionalConf=None):
    vim_acc = domainLayerObj.vimAccount

    tmpClient = client.Client(host=domainIp,user=domainLayerObj.username,password=domainLayerObj.password, project=domainLayerObj.project)
    #valueExtraction
    # requests.post("http://192.168.0.100:9999/stopTimer/1", data={"timestamp":str(round(time.time()*1000))})
    return tmpClient.ns.create(nsd_name=nsdName, nsr_name=nsName, account=vim_acc, config=additionalConf)

def sendActionNS(domainIp, nsId, domainLayerObj, additionalConf=None):
    tmpClient = client.Client(host=domainIp,user=domainLayerObj.username,password=domainLayerObj.password, project=domainLayerObj.project)
    actionId=tmpClient.ns.exec_op(nsId, "action", op_data=additionalConf, wait=True)
    actionInfo=tmpClient.ns.get_op(actionId)
    return actionInfo

def modifyNS(domainIp):
    return

def terminateNS(domainIp, nsName):
    tmpClient = client.Client(host=domainIp)
    #valueExtraction
    # requests.post("http://192.168.0.100:9999/stopTimer/2", data={"timestamp":str(round(time.time()*1000))})
    return tmpClient.ns.delete(nsName)

def getNSI(domainIp, domainLayerObj, nsiId):
    logging.info(f"domainIp: {domainIp}, user: {domainLayerObj.username} password: {domainLayerObj.password}, project: {domainLayerObj.project} ")
    tmpClient = client.Client(host=domainIp,user=domainLayerObj.username,password=domainLayerObj.password, project=domainLayerObj.project)
    #logging.info("host:", tmpClient.host)
    return tmpClient.nsi.get(nsiId)

def instantiateNSI(domainIp,nsiName,nstName,domainLayerObj, additionalConf=None):
    vim_acc = domainLayerObj.vimAccount

    logging.info(f"domainIp: {domainIp}, user: {domainLayerObj.username} password: {domainLayerObj.password}, project: {domainLayerObj.project} ")
    tmpClient = client.Client(host=domainIp,user=domainLayerObj.username,password=domainLayerObj.password, project=domainLayerObj.project)
    #logging.info(tmpClient._user)
    #valueExtraction
    # requests.post("http://192.168.0.100:9999/stopTimer/1", data={"timestamp":str(round(time.time()*1000))})
    tmpClient.nsi.create(nst_name=nstName,nsi_name=nsiName,account=vim_acc,config=additionalConf)
    #logging.info(nsiName)
    nsiId=tmpClient.nsi.get(nsiName)["id"]
    return nsiId

def sendActionNSI(domainIp, nsiId,domainLayerObj, additionalConf):
    tmpClient = client.Client(host=domainIp,user=domainLayerObj.username,password=domainLayerObj.password, project=domainLayerObj.project)
    actionId=tmpClient.nsi.exec_op(nsiId, "action", op_data=additionalConf)
    actionInfo=tmpClient.nsi.get_op(actionId)
    return actionInfo

def modifyNSI(domainIp):
    return

def terminateNSI(domainIp,nsiName):
    tmpClient = client.Client(host=domainIp)
    #valueExtraction
    # requests.post("http://192.168.0.100:9999/stopTimer/2", data={"timestamp":str(round(time.time()*1000))})
    return tmpClient.nsi.delete(nsiName)
