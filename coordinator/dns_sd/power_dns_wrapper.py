# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-08-19 18:23:58
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-08-19 18:38:47
import powerdns


class PowerDNSWrapper:

    def __init__(self, api_endpoint, api_key):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.client = powerdns.PDNSEndpoint(
            powerdns.PDNSApiClient(
                api_endpoint=api_endpoint,
                api_key=api_key
            )
        )

    def create_dns_zone(self, vsiId, dns_additional_info):
        zone = f"vsi-{vsiId}.netor."
        ptr_rsets = []
        for component_dns_sd in dns_additional_info:
            service_type = component_dns_sd['service_type']
            service_name = component_dns_sd['service_name']
            protocol = component_dns_sd['protocol']
            ptr_rsets.append(
                powerdns.RRSet(
                    name=f"_{service_type}._{protocol}.{zone}",
                    rtype="PTR",
                    records=[(
                        f"_{service_name}._{service_type}._{protocol}.{zone}",
                        False
                    )]
                )
            )
        zone = self.client.servers[0].create_zone(
            name=zone,
            kind="Native",
            rrsets=ptr_rsets,
            nameservers=[]
        )

        print(f"Created Zone in DNS: {zone}\nDetaisl: {zone.details}")
