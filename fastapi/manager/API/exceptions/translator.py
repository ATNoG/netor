# @Author: Daniel Gomes
# @Date:   2022-09-24 15:05:34
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-09-24 15:13:51

class InvalidPlacementInformation(Exception):
    def __init__(self,):
        self.message = "Error in Placement: Invalid Necessary Information"
        super().__init__(self.message)

    def __str__(self):
        return self.message

class InvalidQoSRange(Exception):
    def __init__(self, rule_id=None):
        if rule_id:
            self.rule_id = rule_id
            self.message = f"The Qos Parameter '{self.rule_id}' is not in"\
                           + " the defined Rules'Range"
        else:
            self.message = "A Qos Parameter is not in"\
                           + " the defined Rules'Range"
        super().__init__(self.message)

    def __str__(self):
        return self.message
