# @Author: Daniel Gomes
# @Date:   2022-10-12 23:51:55
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-12 23:52:04
import powerdns

class Netor_DNS_SD:

    def __init__(self, dns_ip, api_port, api_key, vsi_id):

        self.dns_ip = dns_ip
        self.api_port = api_port
        self.api_key = api_key
        self.vsi_id = vsi_id
        self.api_client = powerdns.PDNSApiClient(
            api_endpoint=f"http://{dns_ip}:{api_port}/api/v1",
            api_key=api_key
        )
        self.api = powerdns.PDNSEndpoint(self.api_client)
        self.zone = f"vsi-{vsi_id}.netor."

    def create_zone(self):
        ptr_rsets = []
        zone = self.api.servers[0].create_zone(
            name=self.zone,
            kind="Native",
            rrsets=ptr_rsets,
            nameservers=[]
        )

        print("[!] Zone Created [!]")
        print(f"Zone: {zone}")
        print("[-] Zone Details [-]")
        print(zone.details)

    def delete_zone(self):
        self.api.servers[0].delete_zone(self.zone)
        print(f"[!] Zone {self.zone} Deleted [!]")
