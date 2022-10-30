# @Author: Daniel Gomes
# @Date:   2022-09-20 16:59:53
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-29 22:59:49
import json
from typing import Dict, List
from exceptions.translator import InvalidQoSRange, InvalidPlacementInformation
from exceptions.domain import DomainNotFound
from schemas.nst import NST
from schemas.catalogue import CatalogueInfoTranslation, ParameterData, TranslationRules
import schemas.message as MessageSchemas
from redis.handler import RedisHandler
import aux.constants as Constants
import aux.utils as Utils
import logging
import schemas.auth as AuthSchemas

# Logger
logging.basicConfig(
    format="%(module)-20s:%(levelname)-15s| %(message)s",
    level=logging.INFO
)

class Arbitrator:
    def __init__(self,
                 redis_handler: RedisHandler) -> None:
        self.redis_handler = redis_handler

    async def processAction(self , data: MessageSchemas.Message):
        await self.redis_handler.set_hash_key(
            data.vsiId,
            data.msgType,
            json.dumps(data.dict(exclude_none=True, exclude_unset=True))
        )
        vsi_current_data = await self.redis_handler.get_hash_keys(data.vsiId)
        parsed_info = [ x.decode() for x in vsi_current_data]
        # First we Assert if we have the necessary data to carry on to the 
        # processing of the entities placement 
        if await self.redis_handler.has_required_placement_info(
            data.vsiId,
            parsed_info):
            logging.info("Got necessary info. Starting translation...")
            await self.redis_handler.update_vsi_running_data(data.vsiId)
            res = await self.processEntitiesPlacement(data.vsiId)
            return res
    
    
    async def processEntitiesPlacement(self, vsiId):
        allVsiData = {}
        # now that we have the necessary data, we retrieve it from Cache
        res = MessageSchemas.Message(vsiId=vsiId)

        try:
            cached_vsi_data = await self.redis_handler.hget_all(vsiId)
            for key,value in cached_vsi_data.items():
                key = key.decode()
                # skip createVSI request message 
                if key not in Constants.INFO_TOPICS:
                    logging.info("Skipping creatVSI request")
                    continue
                # Tenant Messsage
                if key == Constants.TOPIC_TENANTINFO:
                    print("ENTREI")
                    allVsiData[key] = AuthSchemas.Tenant(
                        **json.loads(value)
                    )
                else:
                    # load and parse data 
                    allVsiData[key] = MessageSchemas.Message(
                        **json.loads(value))
                    if allVsiData[key].error:
                        raise InvalidPlacementInformation()
                logging.info(f"Cached Data {json.loads(value)}")

            domainInfo = allVsiData["domainInfo"]
            catalogueInfo = allVsiData['catalogueInfo']
            logging.info("Starting translation...")
            translation = self.translateVSD(catalogueInfo.dict())
            logging.info("Translation done.. Verifying Domain Placement")
            self.verify_domain_placement(translation, domainInfo)
            logging.info("Domain Verifying Ok..")
            res.msgType = Constants.TOPIC_PLACEMENTINFO
            res.data = translation

        except Exception as e:
            logging.info(f"Error in translator {e}")
            res.msgType = Constants.TOPIC_ERROR
            res.message = str(e)
            res.error = True
        return res


    def translateVSD(self, payload) -> List[MessageSchemas.TranslationInfoData]:
        cat_data = CatalogueInfoTranslation(**payload['data'])
        qos_params_info = cat_data.vs_blueprint_info.vs_blueprint.parameters
        translation_rules = cat_data.vs_blueprint_info\
                                    .vs_blueprint.translation_rules
        qos_values = cat_data.vsd.qos_parameters
        domain_id = cat_data.vsd.domain_id
        translation_output = []
        for rule in translation_rules:
            self.verify_qos_params_range(
                rule,
                qos_params_info,
                qos_values)
            if rule.nst_id:
                translation_output = self.verify_nsts(
                    cat_data.nsts, domain_id, rule)
            elif rule.nsd_id:
                translation_output = self.verify_nsds(
                    rule, domain_id)
        return translation_output
    

    
    def verify_qos_params_range(self,
                                rule: TranslationRules,
                                qos_params: List[ParameterData],
                                qos_values: Dict
                                ):
        # tranform in dictionary since it simplifies to retrieve data
        qos_params_parsed = { o.parameter_id: o.dict() for o in qos_params}
        # for each input rule it will be verified if the parameters
        # its in the qos range defined
        for input_rule in rule.input:
            current_qos_param = qos_params_parsed[input_rule.parameter_id]
            current_qos_value = qos_values[input_rule.parameter_id]
            if current_qos_param['parameter_type'] == 'number':
                if not int(input_rule.max_value)\
                    > int(current_qos_value) > int(input_rule.min_value):
                    # error!
                    raise InvalidQoSRange(input_rule.parameter_id)


    def verify_nsts(self,
                    catalogue_nsts: List[NST],
                    domainId: str,
                    rule_nst: TranslationRules):
        translation = []
        #TODO: Recursive Verification
        externalNST = True
        for nst in catalogue_nsts:
            if nst.nst_id and nst.nst_id == rule_nst.nst_id:
                externalNST = False
                if nst.nsst_ids:
                    for nsst_id in nst.nsst_ids:
                        externalNSST = True
                        for nsst in nst.nsst:
                            if nsst_id == nsst.nst_id:
                                externalNST = False
                                translation = Utils.prepare_translation(
                                    domainId=domainId,
                                    sliceEnabled=False,
                                    nsdId=nsst.nsd_id,
                                    translation_set=translation)
                                break
                        if externalNSST:
                            translation = Utils.prepare_translation(
                                    domainId=domainId,
                                    sliceEnabled=True,
                                    nstId=nsst_id,
                                    translation_set=translation)   
                else:
                    translation = Utils.prepare_translation(
                                    domainId=domainId,
                                    sliceEnabled=True,
                                    nsdId=nst.nsd_id,
                                    translation_set=translation) 
        if externalNST:
            translation = Utils.prepare_translation(
                                    domainId=domainId,
                                    sliceEnabled=True,
                                    nstId=rule_nst.nst_id,
                                    translation_set=translation)
        logging.info(f"Translation: {translation}")
        return translation
            
    def verify_nsds(self, rule_nsd: TranslationRules, domainId: str):
        return Utils.prepare_translation(
            domainId=domainId,
            sliceEnabled=False,
            nsdId=rule_nsd.nsd_id
        )
    
    def verify_domain_placement(
        self,
        placement: List[MessageSchemas.TranslationInfoData],
        domainData: MessageSchemas.Message):

        for component in placement:
            if component.domainId not in domainData.data.domainIds:
                raise DomainNotFound(component.domainId)



        

