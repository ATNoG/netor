from werkzeug.exceptions import HTTPException
from api.serializers.vs_descriptor import VsDescriptorSerializer
from api.serializers.vs_blueprint import VsBlueprintInfoSerializer, VsbActionsSerializer
from api.serializers.ns_template import NstSerializer
from api.models.ns_template import Nst
from api.queries.vs_descriptor import get_vs_descriptors
from api.queries.vs_blueprint import get_vs_blueprints, VsbActions


def get_info(content):
    if content.get("msgType") == "createVSI" and (vsi_id := content.get('vsiId')) is not None:
        tenant_id, data = content.get('tenantId'), content.get('data')
        vsd_id = data.get('vsdId')

        requested_data = {'message': 'Success', 'vsiId': vsi_id, 'msgType': 'catalogueInfo', 'error': False, 'data': {}}

        
        vsd = VsDescriptorSerializer().dump(get_vs_descriptors(vsd_id=vsd_id, tenant_id=tenant_id)[0])

        vsb_id = vsd.get('vs_blueprint_id')
        vsbi = VsBlueprintInfoSerializer().dump(
            get_vs_blueprints(vsb_id=vsb_id, tenant_id=tenant_id, with_translation_rules=True)[0])

        nsts_id = [rule.get('nst_id') for rule in vsbi.get('vs_blueprint', {}).get('translation_rules', [])]
        _objs = Nst.objects.filter(nst_id__in=nsts_id)
        nsts = NstSerializer(many=True, exclude=('nsst',)).dump(_objs)


        # print("from_db", _objs[0].nsst)
        parsed_nsst_ids = set()
        for nst in nsts:
            for nsst_id in nst.get('nsst_ids', []):
                print(":::", nsst_id)
                nsst = Nst.objects.filter(nst_id=nsst_id)
                print("-->", nsst)
                if len(nsst) > 0 and nsst_id not in parsed_nsst_ids:
                    parsed_nsst_ids.add(nsst_id)
                    nst['nsst'] = []
                    for nested_nsst in nsst:
                        nst['nsst'].append(NstSerializer( exclude=('nsst',)).dump(nested_nsst))
        
        # for i in range(len(nsts)):
        #     _obj = _objs[i]
        #     nst = nsts[i]
        #     for nsst_id in nst.get('nsst_ids', []):
        #         nsst = _obj.nsst
        #         for nested_nsst in nsst:
        #                 nst['nsst'].append(NstSerializer( exclude=('nsst',)).dump(nested_nsst))
                    
        print("NST")
        print(nsts)
        vsb_actions = VsbActionsSerializer(many=True).dump(VsbActions.objects.filter(blueprint_id=vsb_id))

        requested_data['data'] = {
            'vsd': vsd,
            'vs_blueprint_info': vsbi,
            'nsts': nsts,
            'vsb_actions': vsb_actions
        }
        # except HTTPException as e:
        #     requested_data['message'] = e.get_description()
        #     requested_data['error'] = True

        # except Exception as e:
        #     requested_data['message'] = f"Internal Error {e}"
        #     requested_data['error'] = True

        return requested_data
